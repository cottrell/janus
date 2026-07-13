#!/usr/bin/env bash
# filebrowser — web file manager + editor, port 9323
# disable: remove window from ide/ops.yaml or set ops_up: false in data/ide-tools.json
if ! command -v filebrowser &>/dev/null; then
    echo "filebrowser not installed — run: bash ~/dev/janus/mk/install-ide-tools.sh"
    exit 1
fi
FB=filebrowser
DB="$(dirname "$0")/filebrowser.db"
if [[ ! -f "$DB" ]]; then
    filebrowser config init --auth.method=noauth -d "$DB"
    filebrowser config set --auth.method=noauth --signup=false -d "$DB"
    filebrowser users add admin "placeholder-password-noauth" --perm.admin -d "$DB"
fi
exec $FB --address "" -p 9323 -r ~/dev -d "$DB"
