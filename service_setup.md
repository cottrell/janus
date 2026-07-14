# User systemd unit (optional)

Templates in repo → install once; real paths stay on the machine.

```sh
# 1) Local tmuxp layout (gitignored)
cp ops.yaml.template ops.yaml
# edit ops.yaml (backlog port, optional JANUS_DATA_DIR=… before make dev)

# 2) User unit (not root; not committed)
cp janus.service.template ~/.config/systemd/user/janus.service
# edit WorkingDirectory (+ optional Environment=JANUS_DATA_DIR=…)

systemctl --user daemon-reload
systemctl --user enable --now janus.service

# keep user services after logout
loginctl enable-linger "$USER"
loginctl show-user "$USER" | grep Linger
```

Installed unit path: `~/.config/systemd/user/janus.service`  
Registry: `JANUS_DATA_DIR`, or gitignored `./data` (e.g. symlink to your registry).
