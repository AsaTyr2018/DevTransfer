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
        "CREATE TABLE IF NOT EXISTS files (code TEXT PRIMARY KEY, filename TEXT, path TEXT, expiry INTEGER, oneshot INTEGER)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tokens (name TEXT, token TEXT UNIQUE)"
    )
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
    return False


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
        "INSERT INTO files(code, filename, path, expiry, oneshot) VALUES(?,?,?,?,1)",
        (code, file.filename, dest_path, int(expiry.timestamp())),
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

