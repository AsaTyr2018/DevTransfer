#!/bin/bash
# Installs DevTrans CLI on Linux and writes configuration under /opt/DevTransClient
# Requires root privileges.
set -e

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run as root" >&2
    exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "$0")/.." && pwd)
CLI_DIR="$SCRIPT_DIR/cli"

if ! command -v go >/dev/null 2>&1; then
    echo "Go is required to build DevTrans" >&2
    exit 1
fi

cd "$CLI_DIR"
echo "Building DevTrans CLI..."
go build -o /usr/local/bin/devtrans

read -p "Enter your DEVTRANS_TOKEN: " DEVTRANS_TOKEN
read -p "Enter DEVTRANS_BASE_URL [http://localhost:8000]: " DEVTRANS_BASE_URL
DEVTRANS_BASE_URL=${DEVTRANS_BASE_URL:-http://localhost:8000}

CONFIG_DIR=/opt/DevTransClient
mkdir -p "$CONFIG_DIR"
cat >"$CONFIG_DIR/config" <<EOF
token=${DEVTRANS_TOKEN}
base_url=${DEVTRANS_BASE_URL}
EOF

echo "DevTrans installed. Configuration written to $CONFIG_DIR/config"
