---
id: TASK-10
title: muxpod direct links?
status: Done
assignee: []
created_date: '2026-07-11 10:53'
updated_date: '2026-07-11 16:33'
labels:
  - mobile
  - muxpod
  - tmux
  - frontend
dependencies: []
references:
  - server.py
  - index.html
  - data/*.json
documentation:
  - 'https://github.com/moezakura/mux-pod#deep-linking'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add MuxPod deep links on Janus project cards so tapping from phone opens MuxPod directly to the project's tmux ops or swarm session.

MuxPod supports custom URL scheme:
```
muxpod://connect?server=<id>&session=<name>&window=<name>&pane=<index>
```
- `server` (required): MuxPod connection Deep Link ID (configured in MuxPod app under Servers > Edit)
- `session` (optional): tmux session name — Janus can read from `tmuxp_ops` / `tmuxp_swarm` yaml via existing `session_name()` helper
- `window` / `pane` (optional): target specific window/pane

**Feasibility: YES — small, well-scoped change.**

What Janus already has:
- `tmuxp_ops` / `tmuxp_swarm` per project in `data/*.json`
- `session_name(config)` parses yaml session names (e.g. `ops-myproject`, `myproject`)
- Card icon pattern for filebrowser/code-server/backlog/graphify
- Status endpoint knows if ops/swarm sessions are up

What needs adding (~30-50 lines):
1. Config for MuxPod server ID — e.g. `MUXPOD_SERVER_ID` env var or field in `data/janus.json`
2. `server.py`: `_muxpod_link(session_name, window=None, pane=None)` helper; expose `muxpod_links` dict on project dicts in `get_links()` (ops + swarm entries when configured)
3. `index.html`: card icon(s) for muxpod hop — e.g. terminal icon, tooltip shows session name; link only when session is up (optional polish)
4. README one-liner on MuxPod setup (Deep Link ID + SSH access from phone (LAN or mesh/VPN))

**Prerequisites (user-side, not code):**
- MuxPod installed on phone (Android/iOS)
- SSH connection configured in MuxPod with a stable Deep Link ID (e.g. `dev-box`)
- Phone can reach dev machine (mesh/VPN (e.g. Tailscale/Yggdrasil) or LAN)

**Open decisions:**
- One muxpod link (swarm preferred?) vs separate ops/swarm icons?
- Default window name (e.g. `grid` for swarms, first window for ops)?
- Hide link when session is down, or always show (MuxPod will attach/create)?
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 #1 MuxPod server Deep Link ID is configurable (env var or janus config) without hardcoding per-project.
- [x] #2 #2 Projects with tmuxp_ops/swarm get muxpod:// links with correct session_name from yaml.
- [x] #3 #3 Dashboard shows at least one muxpod hop icon per eligible project (same card-icon pattern as filebrowser/code-server).
- [x] #4 #4 make validate passes; no new dependencies.
- [x] #5 #5 README documents MuxPod Deep Link ID setup.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-11: Assessed feasibility — YES, can be done as a small server.py + index.html change. Janus already resolves session names from tmuxp yaml. Main prereq is user configuring MuxPod Deep Link ID on phone. Related umbrella: TASK-3 (Tmuxhop).

2026-07-11: Implemented. Configured `muxpod_server_id` via environment variable `MUXPOD_SERVER_ID` with fallback to `data/janus.json` (defaults to `dev-box`). Added session resolution logic and links generation in `server.py` `/api/links` endpoint. Added terminal icon links with dynamically updated tooltips (ops/swarm session name + offline status check) in `index.html`. Added `.disabled` style for offline tmux sessions. Documented setup instructions in `README.md`. All validation tests passed successfully.
<!-- SECTION:NOTES:END -->

