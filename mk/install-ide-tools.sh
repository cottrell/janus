#!/usr/bin/env bash
# Optional IDE helpers only — not required for Janus dashboard.
# Currently Debian/Ubuntu-oriented (apt). On other systems install ttyd /
# filebrowser / micro yourself and skip this script.
set -euo pipefail

if ! command -v apt &>/dev/null; then
    echo "This script uses apt. Install ttyd, filebrowser, and micro manually on non-Debian systems."
    exit 1
fi

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
