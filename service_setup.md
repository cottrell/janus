# User systemd unit (optional)

```sh
# copy/edit janus.service for your paths first
systemctl --user enable --now janus.service

# keep user services after logout (replace $USER if needed)
loginctl enable-linger "$USER"
loginctl show-user "$USER" | grep Linger
```
