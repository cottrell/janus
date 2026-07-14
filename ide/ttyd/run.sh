#!/usr/bin/env bash
# ttyd — terminal in browser (default public 9322, backend 19322)
# Override: JANUS_IDE_TTYD_PORT, JANUS_IDE_TTYD_BACKEND_PORT, JANUS_DEV_ROOT
# libwebsockets in ttyd releases has IPv6-off; socat bridges [::]:PUBLIC -> 127.0.0.1:BACKEND
set -euo pipefail
PUBLIC="${JANUS_IDE_TTYD_PORT:-9322}"
BACKEND="${JANUS_IDE_TTYD_BACKEND_PORT:-19322}"
ROOT="${JANUS_DEV_ROOT:-$HOME}"
ROOT="${ROOT/#\~/$HOME}"

TTYD="$(dirname "$0")/ttyd.x86_64"
"$TTYD" -p "$BACKEND" -W -- bash -c "cd \"$ROOT\" && exec bash" &
TTYD_PID=$!
trap "kill $TTYD_PID 2>/dev/null" EXIT
exec socat "TCP6-LISTEN:${PUBLIC},reuseaddr,fork" "TCP4:127.0.0.1:${BACKEND}"
