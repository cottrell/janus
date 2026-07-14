---
id: TASK-3
title: Tmuxhop
status: To Do
assignee: []
created_date: '2026-05-21 06:49'
updated_date: '2026-07-11 10:57'
labels:
  - tmux
  - mobile
  - muxpod
  - consider
dependencies: []
references:
  - server.py
  - index.html
  - data/*.json
  - ops.yaml
  - swarm/*.yaml
  - ide/ops.yaml
documentation:
  - 'https://github.com/moezakura/mux-pod#deep-linking'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add one-tap **tmux hop** links on Janus project cards so you can jump straight into the right tmux session (ops or swarm) without hunting in tmux or MuxPod manually.

**Context:** Janus already knows each project's `tmuxp_ops` / `tmuxp_swarm` configs and can resolve `session_name` from the yaml (see `server.session_name()`). The missing piece is surfacing deep links from the dashboard — especially useful on phone over mesh/VPN (e.g. Tailscale or Yggdrasil).

**Likely implementations (pick one or combine):**
1. **MuxPod deep links** (`muxpod://connect?server=<id>&session=<name>&window=<name>&pane=<index>`) — mobile-first; see TASK-10 for the concrete slice.
2. **ttyd attach helper** — browser terminal that runs `tmux attach -t <session>` (ide-tools already runs ttyd on :9322).
3. **Plain tmux attach script** — less useful from phone unless wrapped in (1) or (2).

**Per-project targets:**
- Ops session (e.g. `ops-myproject` → window `backend` or `frontend`)
- Swarm session (e.g. `myproject` → window `grid`, pane 0+)

**Open decisions:**
- One link per project (default session) vs separate ops/swarm hop buttons?
- Default window/pane when project has many panes?
- Where to store MuxPod server Deep Link ID (env var in janus, `data/janus.json`, or per-machine config)?
- Show hop links only when session is up (reuse `/api/status`)?

**Not in scope yet:** auto-generating window/pane names from live tmux state; babysit pane targeting.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-11: Filled in placeholder description. Umbrella feature for hopping from Janus cards into project tmux sessions. TASK-10 (muxpod:// links) is the most concrete/mobile slice; ttyd attach is a desktop/browser fallback already partially available via ide-tools.
<!-- SECTION:NOTES:END -->
