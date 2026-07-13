#!/usr/bin/env bash
# ttyd — terminal in browser, port 9322
# libwebsockets in ttyd releases has IPv6-off; socat bridges [::]:9322 -> 127.0.0.1:19322
# disable: remove window from ide/ops.yaml or set ops_up: false in data/ide-tools.json
TTYD="$(dirname "$0")/ttyd.x86_64"
"$TTYD" -p 19322 -W -- bash -c 'cd ~/dev && exec bash' &
TTYD_PID=$!
trap "kill $TTYD_PID 2>/dev/null" EXIT
exec socat TCP6-LISTEN:9322,reuseaddr,fork TCP4:127.0.0.1:19322
