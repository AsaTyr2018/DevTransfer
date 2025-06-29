# DevTrans Admin Guide

This guide describes how to run the DevTrans server and manage upload tokens.

## Running the Server

Install dependencies from `requirements.txt` and start the FastAPI server:

```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --reload
```

The server reads configuration from `server.yml` located in the repository root.
Adjust `base_url`, `storage_dir` and `expiry_hours` as needed.

## Admin Authentication

Admin credentials are defined under `admin_users` in `server.yml`. Unauthenticated visitors to `/admin` are redirected to a login form. After entering a valid username and password they receive a session cookie allowing access to the panel.

## Web Admin Panel

Open `http://localhost:8000/admin` in your browser and log in with an admin account.

The panel lists existing upload tokens. You can:

- **Create Token** – enter a name and submit to generate a new token.
- **Delete Token** – remove a token which immediately invalidates it for future uploads.

Additional sections under **Users** and **Files** are available after logging in:

- **Users** – add or remove extra administrator accounts. The first admin configured in `server.yml` remains hard coded.
- **Files** – review uploaded files, see which token uploaded them and delete entries manually if required.

## Preloaded Tokens

You can preload tokens by listing them under the `tokens` section of `server.yml`.
These tokens will be inserted into the database when the server starts.

## Database Location

The server stores metadata in `server.db` (SQLite) in the project root. Remove this file if you need to reset all tokens and uploaded file entries.

