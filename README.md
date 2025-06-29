# DevTransfer

DevTransfer is a small file transfer tool with a FastAPI backend and a simple command line interface. Files are uploaded with bearer tokens and downloaded through single-use links. Administrators manage tokens in a web panel.

## Features

- CLI uploads and downloads
- FastAPI server storing metadata in SQLite
- Web admin panel to create and revoke tokens
- Installer scripts for Linux and Windows

## Server Setup

Choose one of the following methods to start the FastAPI server.

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
