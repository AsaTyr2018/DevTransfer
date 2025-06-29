# DevTrans Admin Guide

This document explains how to run the DevTrans server and manage upload tokens.

## Running the Server

Install the dependencies and start the FastAPI application:

```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --reload
```

The server reads its settings from `server.yml` in the repository root. Edit the `base_url`, `storage_dir` and `expiry_hours` values to suit your environment.

For a systemd deployment use the provided `setup.sh` script:

```bash
sudo ./setup.sh install    # install under /opt/DevTransfer
sudo ./setup.sh update     # pull updates and restart
```

## Admin Authentication

Administrator accounts are listed under `admin_users` in `server.yml`. Unauthenticated visitors to `/admin` receive a login form. After a successful login a session cookie grants access to the panel.

## Web Admin Panel

Open `http://localhost:8000/admin` and log in with an admin account. The panel allows you to:

- **Create Token** – generate a new bearer token for CLI uploads.
- **Delete Token** – revoke an existing token.
- **Users** – add or remove additional administrators (the users in `server.yml` cannot be deleted here).
- **Files** – review uploaded files, download them or remove entries manually.

## Preloading Tokens

List tokens under the `tokens` section of `server.yml` to have them inserted into the database when the server starts.

## Database Location

Metadata and tokens are stored in `server.db` (SQLite) in the project root. Delete this file to reset the database.
