# DevTransfer

DevTransfer is a lightweight, self-hosted service for moving files between machines. A cross-platform CLI uploads data to a FastAPI backend which stores metadata in SQLite and serves one‑time download links. A browser-based admin panel lets authorised users create and revoke upload tokens.

## Features

- Cross-platform CLI for uploads and downloads
- FastAPI server storing files on disk with metadata in SQLite
- One-time download links with configurable expiry
- Web admin panel to create or revoke tokens and inspect uploads
- Installer scripts for Linux and Windows
- Admin interface disabled when the default credentials from `server.yml` are still in use

## Server Setup

Choose one of the following methods to start the FastAPI server.

**Important:** The admin panel is locked if `server.yml` still contains the bundled example credentials. Edit the file before deployment.

1. **Manual Install**

   ```bash
   git clone <repository-url>
   cd DevTransfer
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn server.main:app --host 0.0.0.0 --reload
   ```
   Visit `http://localhost:8000/admin` to create an upload token.

2. **setup.sh Script**

   ```bash
   git clone <repository-url>
   cd DevTransfer
   sudo ./setup.sh install
   ```
   This installs DevTransfer under `/opt/DevTransfer` with a systemd service.

See [docs/AdminGuide.md](docs/AdminGuide.md) for administration details.

## Client Setup

1. **Manual Build (not recommended)**

   ```bash
   cd cli
   go build -o devtrans
   ```

2. **Installer Scripts**

   - Linux: `sudo installer/linux_install.sh`
   - Windows: `installer/windows_install.ps1 -Token <YOUR_TOKEN>`

   The scripts build the binary, place it on your PATH and write a configuration file with your token. Configuration is saved to `/opt/DevTransClient/config` or `C:\DevTransClient\config`.

After installation you can transfer files:

```bash
devtrans put path/to/file
devtrans get CODE
```

See [docs/UserGuide.md](docs/UserGuide.md) for usage instructions.

## Documentation

See [docs/UserGuide.md](docs/UserGuide.md) and [docs/AdminGuide.md](docs/AdminGuide.md) for full usage and administration guides.
