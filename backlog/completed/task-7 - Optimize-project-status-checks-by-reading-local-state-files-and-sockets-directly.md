---
id: TASK-7
title: >-
  Optimize project status checks by reading local state files and sockets
  directly
status: Done
assignee: []
created_date: '2026-07-05 13:45'
updated_date: '2026-07-05 20:49'
labels: []
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current status endpoint (/api/status) sequentially spawns 'cli.py babysit status <config>' subprocesses for each project. This incurs significant CPU and I/O overhead on every poll (importing python modules, executing tmux commands, and spawning processes).\n\nSince the babysit workers write their live state to '/tmp/nudge-swarm/<project>/' files and the monitors expose UNIX sockets, we can parse this state directly in the server process without any process spawns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 FastAPI status endpoint reads '/tmp/nudge-swarm/<project>/runtime.json' and 'babysit-*.state.json' files directly.
- [x] #2 FastAPI status endpoint queries UNIX sockets directly in Python instead of calling external tmux/cli programs.
- [x] #3 FastAPI status endpoint checks PID aliveness using os.kill(pid, 0) in Python.
- [x] #4 Zero python subprocess spawns on status poll.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
We can choose between two main options to eliminate the subprocess overhead on status polling:

### Option A: Import Nudge Modules Directly
Instead of running `cli.py` as a separate shell process, add `nudge/swarm` to the `sys.path` in `server.py` at startup, and import `topology` / `common` directly:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "dev/nudge/swarm"))
import topology as swarm_topology
from common import load_config
```
Then, call Python functions like `swarm_topology.status_lines(cfg)` directly. 
*Note:* We will also need to refactor `status_lines` in the nudge codebase to avoid calling `tmux` CLI subprocesses (`tmux has-session`, `tmux list-panes`) by reading process states and files directly.

### Option B: Parse State Files & UNIX Sockets Directly in Janus
FastAPI's `server.py` can parse the `/tmp/nudge-swarm/<project>/` directory independently without importing or calling nudge CLI:
1. **Find active session**: Read `/tmp/nudge-swarm/<project>/runtime.json` to get the list of active panes.
2. **Check babysit PID**: For each pane, check if `babysit-<pane>.pid` is running using `os.kill(pid, 0)`.
3. **Parse state & spec**: Load `babysit-<pane>.state.json` and `babysit-<pane>.json` directly to determine active state (`on`, `stopped`, `stale`).
4. **Check live agent monitor state**: Connect directly to the monitor UNIX socket at `/tmp/{session}_{pane}.sock` and send `"status\n"` over the socket to receive `idle` or `working`.

This removes the dependency on the `nudge` CLI and external subprocesses entirely, making status checks sub-millisecond.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Option B directly in server.py. Polling status now reads active runtime.json/state files on disk and queries UNIX sockets directly in Python (zero subprocesses spawned for status checks). Query time dropped from multiple seconds to 300ms for all 20 local projects.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Zero-subprocess status check optimization successfully implemented via direct file/socket reads in Python.
<!-- SECTION:FINAL_SUMMARY:END -->
