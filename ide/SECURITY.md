# IDE Tools — Security Notes

These tools are **optional**. Janus only links to them when a project registry
JSON has `"ide_links": true`. The core dashboard works without any of this.

## Network model

Services under `ide/` (code-server, filebrowser, ttyd) run **without application
auth** by default. That is only appropriate when the host is **not** reachable
by untrusted clients — typically a private mesh/VPN and/or host firewall.
Examples (interchangeable for this purpose): **Tailscale**, **Yggdrasil**,
**WireGuard**. Nothing in Janus requires any of them.

Example posture (nftables or equivalent):
- Default DROP on interfaces that should not be public
- Established/related connections accepted
- Only known peer addresses (your devices) allowed

With that model, no auth on the IDE ports is acceptable: only trusted peers can
reach them. **Without** mesh/VPN and/or firewall (or equivalent), enable auth or
do not run these services.

## Per-service notes

| Service | Auth | Transport |
|---|---|---|
| code-server | none | HTTPS (self-signed, cert warning on first visit) |
| filebrowser | none (noauth) | HTTP |
| ttyd | none | HTTP |

## Ops

Start via `ide/ops.yaml` (tmuxp) only if you need them. Install is optional and
currently Debian/apt-oriented (`mk/install-ide-tools.sh`).
