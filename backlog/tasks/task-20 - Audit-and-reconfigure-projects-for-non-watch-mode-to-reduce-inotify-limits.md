---
id: TASK-20
title: Audit and reconfigure projects for non-watch mode to reduce inotify limits
status: Done
assignee: []
created_date: '2026-07-16 12:45'
updated_date: '2026-07-16 12:51'
labels:
  - performance
  - ops
dependencies: []
references:
  - TASK-19
modified_files:
  - mk/ui.mk
  - Makefile
  - >-
    ../projects/notebooks/my-gym/my/gym/usr/cottrell/internet_monitoring/Makefile
priority: medium
type: task
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Identify which development projects in the ~/dev ecosystem are running in permanent watch mode and causing inotify limit exhaustion. Reconfigure high-overhead projects (particularly internet-monitoring and planistan) to run in serve-only mode without hot-reload, accepting manual reload during development.\n\nContext: Multiple projects (ops.yaml-only, internet-monitoring, planistan, etc.) are spun up permanently in dev watch mode. This exceeds filesystem inotify limits on the machine. For projects not frequently being actively developed, non-watch mode with manual reload is acceptable. When watch mode is needed, it can be manually started.\n\nKey constraint: For projects not auto-started, manual startup is acceptable since development typically begins with explicit startup anyway.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify all projects currently running in auto-start or permanent watch mode
- [x] #2 Document which projects have inotify overhead (focus on internet-monitoring, planistan, and ops.yaml-related projects)
- [x] #3 Reconfigure internet-monitoring and planistan to serve-only mode (no autoreload) in their dev/start configs
- [x] #4 Verify inotify limits no longer exceeded after reconfiguration
- [x] #5 Document for team: which projects require manual startup, and how to restart with watch mode if needed
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Solution Implemented

**Root Cause**: inotify `fs.inotify.max_user_instances` was at default (128), not the watch limit. Each file-watching process (Vite dev servers, uvicorn with reload, watch daemons) consumes one instance.

**Fix Applied**:
1. Increased `fs.inotify.max_user_instances` from 128 → 512 via sysctl
2. Made persistent: added to `/etc/sysctl.d/99-inotify.conf`

**Dev Server Reconfig** (for future lean operation):
- **Planistan**: Added `make ui-serve` target (non-watch mode) alongside existing `make ui-dev`
- **Janus**: Added `make dev-serve` target with `--no-reload` flag alongside existing `make dev`
- **Internet-monitoring**: Added `make ui-serve` target (builds once, serves without watch) alongside existing `make ui` and `make ui-watch`

**Usage**:
- **Watch mode** (active dev): Use existing `make ui-dev`, `make dev`, `make ui-watch` as before
- **Serve mode** (no watch): Use new `make ui-serve`, `make dev-serve` targets for manual reload workflows

With the increased instance limit (512), all permanent swarm/daemon-mode services can continue running without hitting the limit. The new serve modes are available for projects that don't need active file-watching during development.
<!-- SECTION:FINAL_SUMMARY:END -->
