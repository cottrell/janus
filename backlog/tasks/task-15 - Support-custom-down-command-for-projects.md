---
id: TASK-15
title: Support custom down command for projects
status: To Do
assignee: []
created_date: '2026-10-15 09:55'
labels:
  - ops
  - architecture
dependencies: []
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Currently Janus only kills the tmux session on ops/down via `tmux kill-session -t =<session>`. For services managing background daemons (like docker compose or native systemd services), killing the tmux window leaves containers and daemons running as orphans in the background.

Janus needs an explicit, configurable teardown mechanism (e.g. `ops_down` hook, `make down`, or custom script) before or instead of bare `tmux kill-session`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Projects can specify a custom down command/hook in project json or ops configuration
- [ ] #2 ops down executes the custom down command before/upon session teardown
<!-- AC:END -->
