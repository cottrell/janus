---
id: TASK-18
title: Fix false ops status from generic make status targets
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29 12:28'
updated_date: '2026-10-29 12:30'
labels:
  - ops
dependencies: []
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Planistan ops session is running, but Janus reports it down because its generic Makefile status target describes pipeline workloads and fails when an optional reporting dependency is missing. Janus currently interprets any project make status target as the ops session health check.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A running tmux ops session is reported up regardless of generic project make status targets
- [x] #2 Planistan's live Janus status reports ops up while ops-planistan exists
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Make tmux session existence authoritative for ops status. 2. Reserve custom status fallback for explicitly prefixed ops-status scripts. 3. Confirm Planistan is reported up through the live API.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Changed ops status to trust a live tmux session and use only explicitly named status scripts as a fallback; generic make status targets no longer act as ops health checks.

Status fallback now requires mk/ops-status.sh, bin/ops-status, or ops-status.sh; generic or unprefixed status targets are ignored.

Restarted the actual Janus UI process in ops-janus window 1.0 after confirming the previous restart command had targeted a nonexistent window index. Live /api/status now reports planistan.ops.up=true and janus.ops.up=true.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Changed Janus ops status to use tmux session existence as authoritative; project Makefile status targets no longer affect the ops button. Custom status fallback uses explicitly prefixed ops-status scripts. Verified the live /api/status response reports Planistan ops up while ops-planistan exists; Janus UI class logic maps up=true to the green up class. git diff --check passed.
<!-- SECTION:FINAL_SUMMARY:END -->
