import os
import secrets
import sqlite3
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Request, Form
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from starlette.background import BackgroundTask
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
import yaml

app = FastAPI(title="DevTrans Server")

app.add_middleware(SessionMiddleware, secret_key="dev-secret")
bearer_security = HTTPBearer()

CONFIG_PATH = "server.yml"
DB_PATH = "server.db"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


config = load_config()

templates = Jinja2Templates(directory="server/templates")


# Database helpers ----------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS files (code TEXT PRIMARY KEY, filename TEXT, path TEXT, expiry INTEGER, oneshot INTEGER, uploaded_by TEXT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tokens (name TEXT, token TEXT UNIQUE)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS admins (username TEXT UNIQUE, password TEXT)"
    )
    # add uploaded_by column for older databases
    cur.execute("PRAGMA table_info(files)")
    cols = [r[1] for r in cur.fetchall()]
    if "uploaded_by" not in cols:
        cur.execute("ALTER TABLE files ADD COLUMN uploaded_by TEXT")
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


init_db()

# preload tokens from config
def load_tokens():
    conn = get_db()
    cur = conn.cursor()
    for t in config.get("tokens", []):
        cur.execute(
            "INSERT OR IGNORE INTO tokens(name, token) VALUES(?, ?)",
            (t.get("name"), t.get("token")),
        )
    conn.commit()
    conn.close()


load_tokens()


# Authentication ------------------------------------------------------------
def authenticate_user(username: str, password: str) -> bool:
    for user in config.get("admin_users", []):
        if username == user.get("username") and password == user.get("password"):
            return True
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM admins WHERE username=? AND password=?",
        (username, password),
    )
    row = cur.fetchone()
    conn.close()
    return row is not None


def require_admin(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def verify_token(token: str) -> bool:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT token FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    conn.close()
    return row is not None


# Routes -------------------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if authenticate_user(username, password):
        request.session["user"] = username
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"},
        status_code=400,
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse("/login")


@app.put("/upload")
async def upload_file(
    file: UploadFile = File(...),
    token: HTTPAuthorizationCredentials = Depends(bearer_security),
):
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    storage_dir = config["server"]["storage_dir"]
    os.makedirs(storage_dir, exist_ok=True)
    code = secrets.token_urlsafe(6)
    dest_path = os.path.join(storage_dir, code)
    with open(dest_path, "wb") as out:
        out.write(await file.read())

    expiry = datetime.utcnow() + timedelta(hours=config["server"].get("expiry_hours", 24))

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files(code, filename, path, expiry, oneshot, uploaded_by) VALUES(?,?,?,?,1,?)",
        (code, file.filename, dest_path, int(expiry.timestamp()), token.credentials),
    )
    conn.commit()
    conn.close()

    return {
        "code": code,
        "url": f"{config['server']['base_url']}/download/{code}",
        "expiry": expiry.isoformat(),
    }


@app.get("/download/{code}")
async def download_file(code: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE code=?", (code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found")

    expiry = datetime.utcfromtimestamp(row["expiry"])
    if datetime.utcnow() > expiry:
        os.remove(row["path"])
        cur.execute("DELETE FROM files WHERE code=?", (code,))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=404, detail="File expired")

    filename = row["filename"]
    path = row["path"]
    oneshot = row["oneshot"] == 1

    headers = {"X-Filename": filename}

    if oneshot:
        # remove file and DB entry after the response is sent
        def cleanup():
            os.remove(path)
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM files WHERE code=?", (code,))
            conn.commit()
            conn.close()

        conn.close()
        return FileResponse(
            path,
            filename=filename,
            media_type="application/octet-stream",
            headers=headers,
            background=BackgroundTask(cleanup),
        )

    conn.close()
    return FileResponse(path, filename=filename, media_type="application/octet-stream", headers=headers)


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, token FROM tokens")
    tokens = cur.fetchall()
    conn.close()
    return templates.TemplateResponse(
        "admin.html", {"request": request, "tokens": tokens}
    )


@app.post("/admin/create")
async def create_token(request: Request, name: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    token = secrets.token_hex(16)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tokens(name, token) VALUES(?, ?)",
        (name, token),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/delete")
async def delete_token(request: Request, token: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tokens WHERE token=?", (token,))
    conn.commit()
    conn.close()
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/users", response_class=HTMLResponse)
async def user_admin(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT username FROM admins")
    users = cur.fetchall()
    conn.close()
    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users, "static_users": config.get("admin_users", [])}
    )


@app.post("/admin/users/create")
async def create_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO admins(username, password) VALUES(?, ?)", (username, password))
    conn.commit()
    conn.close()
    return RedirectResponse("/admin/users", status_code=303)


@app.post("/admin/users/delete")
async def delete_user(request: Request, username: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM admins WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return RedirectResponse("/admin/users", status_code=303)


@app.get("/admin/files", response_class=HTMLResponse)
async def files_admin(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT code, filename, expiry, uploaded_by, path FROM files")
    rows = cur.fetchall()
    files = [
        {
            "code": r["code"],
            "filename": r["filename"],
            "expiry": datetime.utcfromtimestamp(r["expiry"]).isoformat(),
            "uploaded_by": r["uploaded_by"],
        }
        for r in rows
    ]
    conn.close()
    return templates.TemplateResponse(
        "files.html", {"request": request, "files": files}
    )


@app.post("/admin/files/delete")
async def delete_file_admin(request: Request, code: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT path FROM files WHERE code=?", (code,))
    row = cur.fetchone()
    if row:
        if os.path.exists(row["path"]):
            os.remove(row["path"])
        cur.execute("DELETE FROM files WHERE code=?", (code,))
        conn.commit()
    conn.close()
    return RedirectResponse("/admin/files", status_code=303)


# Public frontpage and user dashboard ------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if request.session.get("token"):
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/token/login")
async def token_login(request: Request, token: str = Form(...)):
    if not verify_token(token):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Invalid token"},
            status_code=400,
        )
    request.session["token"] = token
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    token = request.session.get("token")
    if not token:
        return RedirectResponse("/")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT code, filename, expiry FROM files WHERE uploaded_by=?", (token,)
    )
    rows = cur.fetchall()
    conn.close()
    files = [
        {
            "filename": r["filename"],
            "url": f"{config['server']['base_url']}/download/{r['code']}",
            "expiry": datetime.utcfromtimestamp(r["expiry"]).isoformat(),
        }
        for r in rows
    ]
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "files": files}
    )


@app.post("/dashboard/upload")
async def dashboard_upload(
    request: Request, file: UploadFile = File(...)
):
    token = request.session.get("token")
    if not token or not verify_token(token):
        return RedirectResponse("/")
    storage_dir = config["server"]["storage_dir"]
    os.makedirs(storage_dir, exist_ok=True)
    code = secrets.token_urlsafe(6)
    dest_path = os.path.join(storage_dir, code)
    with open(dest_path, "wb") as out:
        out.write(await file.read())
    expiry = datetime.utcnow() + timedelta(hours=config["server"].get("expiry_hours", 24))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files(code, filename, path, expiry, oneshot, uploaded_by) VALUES(?,?,?,?,1,?)",
        (code, file.filename, dest_path, int(expiry.timestamp()), token),
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/token/logout")
async def token_logout(request: Request):
    request.session.pop("token", None)
    return RedirectResponse("/")
