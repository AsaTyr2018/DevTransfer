# DevTransfer

DevTransfer provides a small FastAPI server and a cross‑platform CLI to quickly share files with one‑time download links. Uploads are authenticated via bearer tokens that administrators create in a built‑in web panel. A lightweight web dashboard allows token holders to review their own uploads.

## Features

* **CLI Uploads and Downloads** – `devtrans put <file>` uploads a file (or directory via `*`) and prints a single‑use link with an expiry timestamp. `devtrans get <code>` retrieves the file.
* **FastAPI Server** – exposes `/upload` and `/download/{code}` endpoints and stores metadata in SQLite.
* **Web Admin Panel** – `/admin` lets admins log in, create/delete tokens, manage additional admin accounts and browse uploaded files.
* **User Dashboard** – token holders can log in at the root URL to upload through the browser and view their own files.
* **Configurable Storage** – `server.yml` controls base URL, storage directory and default expiry time.

## Quick Start

### 1. Run the Server

Install dependencies and start the development server:

```bash
pip install -r requirements.txt
uvicorn server.main:app --host 0.0.0.0 --reload
```

Visit `http://localhost:8000/admin` and log in with the credentials from `server.yml` to create upload tokens.

### 2. Build the CLI

```bash
cd cli
# Linux / macOS
go build -o devtrans
# Windows
go build -o devtrans.exe
```

Create `/opt/DevTransClient/config` (Windows: `C:\DevTransClient\config`) containing your token and optional base URL:

```
token=YOUR_TOKEN
base_url=http://localhost:8000
```

Environment variables `DEVTRANS_TOKEN` and `DEVTRANS_BASE_URL` override these values.

### 3. Upload a File

```bash
DEVTRANS_TOKEN=YOUR_TOKEN ./devtrans put path/to/file
```

The command prints the download code, full URL and expiry timestamp. Use `devtrans put *` to stream the current directory as a ZIP archive.

### 4. Download

```bash
./devtrans get CODE
```

The file is saved with its original name and removed from the server after the first successful download.

## Deployment

The `installer/` directory contains scripts to install the CLI system-wide. Use `setup.sh` to deploy the Python server under `/opt/DevTransfer` and manage it as a systemd service:

```bash
sudo ./setup.sh install    # initial install
sudo ./setup.sh update     # fetch updates and restart
```

## Documentation

More detailed instructions are available in the [docs](./docs/) directory:

- [User Guide](docs/UserGuide.md)
- [Admin Guide](docs/AdminGuide.md)
