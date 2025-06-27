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

The CLI lives under `cli/` and can be built with Go:

```bash
cd cli
go build -o devtrans
```

Set `DEVTRANS_TOKEN` and optionally `DEVTRANS_BASE_URL` before running the
commands:

```bash
export DEVTRANS_TOKEN=deadbeefdeadbeefdeadbeefdeadbeef
./devtrans put path/to/file
```
