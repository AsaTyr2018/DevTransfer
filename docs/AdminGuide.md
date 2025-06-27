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

Admin credentials are defined under `admin_users` in `server.yml`. The Web Admin Panel uses HTTP Basic authentication.

## Web Admin Panel

Open `http://localhost:8000/admin` in your browser and log in with an admin account.

The panel lists existing upload tokens. You can:

- **Create Token** – enter a name and submit to generate a new token.
- **Delete Token** – remove a token which immediately invalidates it for future uploads.

## Preloaded Tokens

You can preload tokens by listing them under the `tokens` section of `server.yml`.
These tokens will be inserted into the database when the server starts.

## Database Location

The server stores metadata in `server.db` (SQLite) in the project root. Remove this file if you need to reset all tokens and uploaded file entries.

