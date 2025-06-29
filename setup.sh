#!/bin/bash
set -e

INSTALL_DIR="/opt/DevTransfer"
VENVDIR="$INSTALL_DIR/venv"
SERVICE_FILE="/etc/systemd/system/devtransfer.service"

usage() {
    echo "Usage: $0 {install|update}" >&2
    exit 1
}

install_devtransfer() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Please run as root" >&2
        exit 1
    fi

    SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

    echo "Installing DevTransfer to $INSTALL_DIR"
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "Existing git repo detected in $INSTALL_DIR" >&2
    else
        if [ -d "$INSTALL_DIR" ]; then
            echo "Copying files to existing directory" >&2
        else
            mkdir -p "$INSTALL_DIR"
        fi
        rsync -a --delete "$SRC_DIR/" "$INSTALL_DIR/"
    fi

    if [ ! -d "$VENVDIR" ]; then
        python3 -m venv "$VENVDIR"
    fi
    "$VENVDIR/bin/pip" install --upgrade pip
    "$VENVDIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    if command -v go >/dev/null 2>&1; then
        echo "Building CLI binary"
        go build -o "$INSTALL_DIR/cli/devtrans" "$INSTALL_DIR/cli"
    fi

    cat > "$SERVICE_FILE" <<EOUNIT
[Unit]
Description=DevTransfer Server
After=network.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENVDIR/bin/uvicorn server.main:app --host 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOUNIT

    systemctl daemon-reload
    systemctl enable --now devtransfer.service
    echo "DevTransfer installed and service started"
}

update_devtransfer() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Please run as root" >&2
        exit 1
    fi

    echo "Updating DevTransfer at $INSTALL_DIR"
    systemctl stop devtransfer.service || true
    if [ -d "$INSTALL_DIR/.git" ]; then
        git -C "$INSTALL_DIR" pull
    else
        SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
        rsync -a --delete "$SRC_DIR/" "$INSTALL_DIR/"
    fi

    "$VENVDIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    if command -v go >/dev/null 2>&1; then
        echo "Building CLI binary"
        go build -o "$INSTALL_DIR/cli/devtrans" "$INSTALL_DIR/cli"
    fi
    systemctl start devtransfer.service
    echo "Update completed"
}

case "$1" in
    install)
        install_devtransfer
        ;;
    update)
        update_devtransfer
        ;;
    *)
        usage
        ;;
esac
