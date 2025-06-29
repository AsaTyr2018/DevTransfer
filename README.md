# DevTransfer

A simple API transfer tool for small or bulk data.

This repository contains the foundation for **DevTrans**, including a FastAPI
server, a web admin panel and a minimal CLI written in Go.

## Running the Server

Install the dependencies and start the development server:

```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --reload
```

Visit `http://localhost:8000/admin` and authenticate with the credentials from
`server.yml`.

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
commands. Use `./devtrans` on Linux/macOS or `devtrans.exe` on Windows:

```bash
export DEVTRANS_TOKEN=deadbeefdeadbeefdeadbeefdeadbeef
# Linux / macOS
./devtrans put path/to/file
# Windows
devtrans.exe put path\to\file
```

## System-Wide Setup

The `installer/` directory contains helper scripts for installing the CLI and
configuring environment variables globally.

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

## Documentation

Detailed usage instructions are available in the [docs](./docs/) directory:

- [User Guide](docs/UserGuide.md) explains how to build the CLI and transfer files.
- [Admin Guide](docs/AdminGuide.md) covers running the server and managing tokens.
