# DevTransfer

A simple API transfer tool for small or bulk data.

This repository contains the foundation for **DevTrans**, including a FastAPI
server and a placeholder web admin panel styled with Bootstrap's Darkly theme.

## Running the Server

Install the dependencies and start the development server:

```bash
pip install -r requirements.txt
uvicorn server.main:app --reload
```

Visit `http://localhost:8000/admin` and authenticate with the credentials from
`server.yml` to see the placeholder admin UI.
