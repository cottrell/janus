#!/usr/bin/env bash
# code-server — VS Code in browser, port 9321
# config: ~/.config/code-server/config.yaml (auth: none, TLS certs already set)
# disable: remove window from ide/ops.yaml or set ops_up: false in data/ide-tools.json
exec code-server ~/dev
