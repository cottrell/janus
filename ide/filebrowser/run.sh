#!/usr/bin/env bash
# filebrowser — web file manager + editor (default port 9323)
# Override: JANUS_IDE_FILEBROWSER_PORT, JANUS_DEV_ROOT
# disable: remove window from ide/ops.yaml or set ops_up: false on the registry entry
set -euo pipefail
PORT="${JANUS_IDE_FILEBROWSER_PORT:-9323}"
ROOT="${JANUS_DEV_ROOT:-$HOME}"
ROOT="${ROOT/#\~/$HOME}"

if ! command -v filebrowser &>/dev/null; then
    echo "filebrowser not installed — run: bash mk/install-ide-tools.sh"
    exit 1
fi
FB=filebrowser
DB="$(dirname "$0")/filebrowser.db"
if [[ ! -f "$DB" ]]; then
    filebrowser config init --auth.method=noauth -d "$DB"
    filebrowser config set --auth.method=noauth --signup=false -d "$DB"
    filebrowser users add admin "placeholder-password-noauth" --perm.admin -d "$DB"
fi
exec $FB --address "" -p "$PORT" -r "$ROOT" -d "$DB"
