#!/usr/bin/env bash
# Optional IDE helpers — not required for the Janus dashboard. Uses apt.
set -euo pipefail

echo "==> ttyd + micro (apt)"
sudo apt install -y ttyd micro

echo "==> filebrowser"
if ! command -v filebrowser &>/dev/null; then
    curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | sudo bash
fi

echo "==> done"
filebrowser version 2>/dev/null || true
ttyd --version 2>/dev/null || true
micro --version 2>/dev/null || true
