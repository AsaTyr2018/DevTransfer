# DevTrans User Guide

This guide explains how to transfer files using the DevTrans CLI.

## Prerequisites

- [Go](https://go.dev/) if you need to build the CLI from source.
- A valid upload token issued by your administrator.
- Optional: adjust the `base_url` in `/opt/DevTransClient/config` (or
  `C:\DevTransClient\config` on Windows) if the server is not running on
  `http://localhost:8000`.

## Building the CLI

Inside the `cli/` folder run:

```bash
cd cli
# Linux / macOS
go build -o devtrans
# Windows
go build -o devtrans.exe
```

This produces the `devtrans` binary in the same directory.

## Uploading Files

1. Create `/opt/DevTransClient/config` (Windows: `C:\DevTransClient\config`) containing:

   ```
   token=YOUR_TOKEN
   base_url=http://localhost:8000
   ```

   Environment variables `DEVTRANS_TOKEN` and `DEVTRANS_BASE_URL` override these values if set.
2. Run the upload command. Use `./devtrans` on Linux/macOS or `devtrans.exe` on
   Windows:

```bash
# Linux / macOS
./devtrans put path/to/file
# Windows
devtrans.exe put path\to\file
```

The command returns a file code, a full download URL and an expiry timestamp.

You can also stream the current directory as a ZIP archive using:

```bash
# Linux / macOS
./devtrans put *
# Windows
devtrans.exe put *
```

## Downloading Files

To retrieve a file, use the `get` command with the code you received after the upload:

```bash
# Linux / macOS
./devtrans get CODE
# Windows
devtrans.exe get CODE
```

The file is saved under its original filename. One‑time downloads are deleted after the first successful retrieval.

