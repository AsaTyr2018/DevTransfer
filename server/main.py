import hashlib
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import yaml

app = FastAPI(title="DevTrans Server")

security = HTTPBasic()

CONFIG_PATH = "server.yml"

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

templates = Jinja2Templates(directory="server/templates")

# Simple in-memory token list loaded from config
tokens = config.get("tokens", [])

# Basic auth dependency
async def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    for user in config.get("admin_users", []):
        if credentials.username == user.get("username") and credentials.password == user.get("password"):
            return credentials.username
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.put("/upload")
async def upload_file(file: UploadFile = File(...), token: str = Depends(security)):
    # Placeholder implementation
    return {"code": "placeholder"}

@app.get("/download/{code}")
async def download_file(code: str):
    # Placeholder implementation
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, user: str = Depends(get_current_admin)):
    return templates.TemplateResponse("admin.html", {"request": request, "tokens": tokens})
