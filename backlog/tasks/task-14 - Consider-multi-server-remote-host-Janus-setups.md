---
id: TASK-14
title: Consider multi-server / remote-host Janus setups
status: To Do
assignee: []
created_date: '2026-07-12 13:51'
updated_date: '2026-07-14 12:33'
labels:
  - consider
  - architecture
  - muxpod
dependencies: []
references:
  - server.py
  - data/janus.json
  - data/*.json
  - README.md
  - backlog/tasks/task-3 - Tmuxhop.md
  - backlog/tasks/task-10 - muxpod-direct-links.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Janus currently assumes a single dev machine: the host where `server.py` runs is the same machine that hosts all project tmux sessions, local paths, git repos, and MuxPod SSH targets.

**Today (implicit assumptions):**
- `local_path` resolves on the Janus host
- `/api/status` reads local tmux/nudge state on the Janus host
- `muxpod_server_id` identifies one MuxPod SSH connection (Deep Link ID) for that same machine
- Dashboard URL rewrite uses `window.location.hostname` (phone reaches Janus over mesh/VPN (e.g. Tailscale or Yggdrasil))

**Not supported yet:**
- Projects whose code/tmux sessions live on a different machine than Janus
- Per-project MuxPod server IDs or per-project SSH targets
- Janus as a central dashboard aggregating multiple dev boxes

**Questions to explore:**
- Per-project `muxpod_server_id` vs global config vs machine registry in `data/janus.json`
- How status/links would work when `local_path` is remote or absent
- Whether MuxPod deep links are enough for multi-host hop vs needing per-host Janus instances
- Relationship to mesh/VPN / multiple host endpoints

**Scope for now:** document the single-host assumption; defer design until a concrete multi-machine need appears.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Single-host assumption documented in README or task-3 notes
- [ ] #2 Sketch of per-project vs global server-id options captured for future design
- [ ] #3 No breaking change to current single-machine workflow
<!-- AC:END -->
