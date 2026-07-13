# IDE Tools — Security Notes

## Network model

Access is intended for a private network (e.g. Yggdrasil IPv6 overlay on `tun0`)
with a host firewall whitelist — not the public internet.

Example posture (nftables or equivalent):
- Default DROP on the overlay interface
- Established/related connections accepted
- Only known peer addresses whitelisted — all ports open to them

With that model, no auth on filebrowser/ttyd/code-server is acceptable — only
whitelisted devices can reach these ports at all. Without a firewall, enable auth.

## Per-service notes

| Service | Auth | Transport |
|---|---|---|
| code-server | none | HTTPS (self-signed, cert warning on first visit) |
| filebrowser | none (noauth) | HTTP |
| ttyd | none | HTTP |

## If you add a new device

Run `firewall_setup.sh` with the new device's Yggdrasil address added to the
whitelist, then reload: `sudo bash firewall_setup.sh`

## If firewall rules are lost (e.g. reboot)

Check: `sudo nft list ruleset` — if the `ip6 ygg` table is missing, re-run
`firewall_setup.sh`. Consider adding it to a systemd service or `@reboot` cron
if it's not already persistent.
