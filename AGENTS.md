# DevTrans – CLI File Transfer Tool with Authenticated Uploads and Web Admin Panel

## Purpose

**DevTrans** is a command-line utility that lets developers and sysadmins move files or folders from any shell (including SSH) to a remote server and receive a short, single-use download link.
A built-in Web Admin Panel allows designated administrators to create and manage upload tokens.

---

## Components

### 1. DevTrans CLI Tool

A single cross-platform binary.

| Capability | Details                                                                                                     |
| ---------- | ----------------------------------------------------------------------------------------------------------- |
| Upload     | `devtrans put <file>` — uploads a file<br>`devtrans put *` — streams the current folder as an in-memory ZIP |
| Download   | `devtrans get <code>` — retrieves the file, deletes it if onetime                                           |
| Auth       | Requires environment variable `DEVTRANS_TOKEN`                                                              |
| Output     | Prints code, URL, and expiry timestamp                                                                      |

```bash
export DEVTRANS_TOKEN=your-auth-token
devtrans put ./report.log             # → https://transfer.domain/d/7K9MvX
devtrans get 7K9MvX                   # downloads & deletes (oneshot)
```

---

### 2. DevTrans Server

#### API Endpoints

| Method | Path               | Purpose                 |
| ------ | ------------------ | ----------------------- |
| `PUT`  | `/upload`          | Authenticated upload    |
| `GET`  | `/download/{code}` | Single download by code |

*Uploads send `Authorization: Bearer <token>` and multipart field `file` (plus header `X-Filename`).*

#### File Handling

* Directories are zipped client-side (streamed).
* Files stored on server’s filesystem under a generated code.
* Metadata (code, filename, path, expiry, oneshot flag) stored in SQLite.
* Files expire at a fixed time or immediately after the first successful download.

---

### 3. Web Admin Panel

| Feature      | Behaviour                                                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------------------- |
| Login        | Admin accounts listed in a server-side YAML/INI config file.                                                   |
| Dashboard    | Shows a table of existing **Auth Tokens** (Name + Token string).                                               |
| Create Token | Form field **“Name”** → generates a cryptographically strong random token → instantly adds a row to the table. |
| Delete Token | “Delete” button removes the token, invalidating future uploads that use it.                                    |

*The panel is served at `/admin`, protected by HTTP Basic Auth with the credentials from the config.*

---

## Authentication

* **Uploads** → Bearer token (must match a token issued via the Admin Panel).
* **Downloads** → Possession of the file **code** is sufficient; no additional auth.

---

## Server Configuration File (`server.yml`)

```yaml
server:
  base_url: https://transfer.domain
  storage_dir: /opt/devtrans/store
  expiry_hours: 24

admin_users:
  - username: alice
    password: "sha256:..."   # hashed
  - username: bob
    password: "sha256:..."

```

---

## Technical Stack

| Layer         | Technology                                   |
| ------------- | -------------------------------------------- |
| CLI Tool      | Go (static binary)                           |
| Web API       | Python 3.12 + FastAPI                        |
| Web Admin     | FastAPI templating + HTMX/Alpine.js          |
| Database      | SQLite for metadata & tokens                 |
| File Store    | Local filesystem                             |
| Auth (admin)  | HTTP Basic (hashed passwords in config)      |
| Auth (upload) | Random 32-byte tokens created in Admin Panel |

---

This document defines the minimal, fixed scope for **DevTrans**:
CLI uploads/downloads with Bearer-token auth, a FastAPI backend, onetime links with expiry, and a Web Admin Panel for token management driven by a static admin-user config file.
