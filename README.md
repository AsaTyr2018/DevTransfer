# DevTransfer

DevTransfer is a small file transfer tool with a FastAPI backend and a simple command line interface. Files are uploaded with bearer tokens and downloaded through single-use links. Administrators manage tokens in a web panel.

## Features

- CLI uploads and downloads
- FastAPI server storing metadata in SQLite
- Web admin panel to create and revoke tokens
- Installer scripts for Linux and Windows

## Quick Start

1. **Run the Server (optional)**
   
   ```bash
   pip install -r requirements.txt
   uvicorn server.main:app --host 0.0.0.0 --reload
   ```
   Visit `http://localhost:8000/admin` to create an upload token.

2. **Install the CLI**
   
   Use the installer for your platform. It builds the binary, places it on your PATH and writes a configuration file with your token.

   - Linux: `sudo installer/linux_install.sh`
   - Windows: `installer/windows_install.ps1 -Token <YOUR_TOKEN>`

   Configuration is saved to `/opt/DevTransClient/config` or `C:\DevTransClient\config`.

3. **Transfer Files**
   
   ```bash
   devtrans put path/to/file
   devtrans get CODE
   ```
   The token and base URL are read from the config file.

## Documentation

See the [docs](./docs/) directory for detailed user and admin guides.
