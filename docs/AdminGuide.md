# DevTrans Admin Guide

This guide explains how to install the Linux-based server and manage it through the web admin interface.

## Installing the Server

DevTrans currently runs on Linux only and requires Python 3.12. Clone the repository and start the service in a virtual environment for testing:

```bash
git clone <repository-url>
cd DevTransfer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0
```

Server settings reside in `server.yml` in the project root. Adjust `base_url`, `storage_dir` and `expiry_hours` before deployment.

### Systemd Service

For a persistent installation use the `setup.sh` script. It copies the project to `/opt/DevTransfer`, creates a virtual environment and registers a systemd unit:

```bash
sudo ./setup.sh install    # install and start devtransfer.service
sudo ./setup.sh update     # pull updates and restart
```

## Accessing the Admin Interface

Navigate to `<base_url>/admin` and log in with a username from the `admin_users` section of `server.yml`. A session cookie grants access after successful authentication.

### Dashboard Features

From the admin dashboard you can:

- **Create or revoke tokens** for CLI uploads.
- **View uploaded files**, download or delete them.
- **Manage additional administrators** created via the interface.

Tokens listed under `tokens` in `server.yml` are imported automatically at startup.

## Database and Storage

Metadata and tokens are stored in `server.db` (SQLite) in the project directory. Uploaded files are kept in the directory specified by `storage_dir`. Removing `server.db` resets the database.
