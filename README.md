# DevTransfer

A simple API transfer tool for small or bulk data.

This repository contains the foundation for **DevTrans**, including a FastAPI
server, a web admin panel and a minimal CLI written in Go. A small web
dashboard is available at the root URL. Users can log in with their API token to
upload files and review their own uploads.

## Running the Server

Install the dependencies and start the development server:

```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --reload
```

Visit `http://localhost:8000/admin` and log in with the credentials from
`server.yml` when prompted. The panel lets you manage upload tokens as well as
additional admin accounts and existing uploads.

## Building the CLI

The CLI lives under `cli/` and can be built with Go. On Unix systems the binary
will be called `devtrans`, while on Windows the executable needs the `.exe`
extension:

```bash
cd cli
# Linux / macOS
go build -o devtrans
# Windows
go build -o devtrans.exe
```

Set `DEVTRANS_TOKEN` and optionally `DEVTRANS_BASE_URL` before running the
commands or create `/opt/DevTransClient/config` (Windows: `C:\DevTransClient\config`)
with the keys `token` and `base_url`. Use `./devtrans` on Linux/macOS or
`devtrans.exe` on Windows:

```bash
# Linux / macOS
DEVTRANS_TOKEN=deadbeefdeadbeefdeadbeefdeadbeef ./devtrans put path/to/file
# Windows
$env:DEVTRANS_TOKEN="deadbeefdeadbeefdeadbeefdeadbeef"; devtrans.exe put path\to\file
```

## System-Wide Setup

The `installer/` directory contains helper scripts for installing the CLI
system-wide. They also create the configuration file described above.

- **Linux:** run `sudo installer/linux_install.sh` and follow the prompts.
- **Windows:** run `PowerShell installer\windows_install.ps1 -Token <token> [-BaseUrl <url>]`.

After installation open a new terminal session and you can invoke `devtrans` from
any directory.

### Server Install/Update

Use `setup.sh` to deploy the Python server under `/opt/DevTransfer` and run it as a
systemd service. Execute the script as root:

```bash
sudo ./setup.sh install    # initial install
sudo ./setup.sh update     # pull latest code and restart
```

The installation copies the entire repository, including its `.git` directory,
to `/opt/DevTransfer`. When you later run `sudo ./setup.sh update`, the script
executes `git pull` inside that directory to fetch updates and restart the
service.

## Documentation

Detailed usage instructions are available in the [docs](./docs/) directory:

- [User Guide](docs/UserGuide.md) explains how to build the CLI and transfer files.
- [Admin Guide](docs/AdminGuide.md) covers running the server and managing tokens.
