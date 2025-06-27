#!/bin/bash
# Installs DevTrans CLI on Linux and configures system-wide environment variables
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

cat >/etc/profile.d/devtrans.sh <<EOVARS
export DEVTRANS_TOKEN="${DEVTRANS_TOKEN}"
export DEVTRANS_BASE_URL="${DEVTRANS_BASE_URL}"
EOVARS

chmod 644 /etc/profile.d/devtrans.sh

echo "DevTrans installed. Open a new shell to use 'devtrans'."
