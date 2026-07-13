#!/usr/bin/env bash
# Usage: do.sh command arg1 arg2 ...
set -uo pipefail
JANUS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="${JANUS_DATA_DIR:-$JANUS_ROOT/data}"

for f in "$DATA"/*.json; do
    local_path=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('local_path',''))" "$f")
    [[ -z "$local_path" ]] && continue
    full_path="${local_path/#\~/$HOME}"
    if [[ ! -d "$full_path" ]]; then
        echo "skipping: $full_path (not a directory)"
        continue
    fi
    echo "==> $full_path"
    if [[ $# -eq 1 ]]; then
        (cd "$full_path" && eval "$1") || echo "FAILED in $full_path"
    else
        (cd "$full_path" && "$@") || echo "FAILED in $full_path"
    fi
done
