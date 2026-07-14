#!/usr/bin/env bash
# code-server — VS Code in browser (default port 9321)
# Override: JANUS_IDE_CODE_SERVER_PORT, JANUS_DEV_ROOT
# Prefer matching JANUS_IDE_CODE_SERVER_URL / scheme in the dashboard env if non-default.
set -euo pipefail
PORT="${JANUS_IDE_CODE_SERVER_PORT:-9321}"
ROOT="${JANUS_DEV_ROOT:-$HOME/dev}"
ROOT="${ROOT/#\~/$HOME}"

exec code-server --bind-addr "0.0.0.0:${PORT}" "$ROOT"
