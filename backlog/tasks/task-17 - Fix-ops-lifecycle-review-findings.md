---
id: TASK-17
title: Fix ops lifecycle review findings
status: Done
assignee:
  - '@codex'
created_date: '2026-10-15 10:31'
updated_date: '2026-10-15 10:32'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-16 identified failure handling and hook-priority bugs in the recent ops lifecycle change. The user requested fixes to those findings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Down and bounce attempt tmux cleanup even when a custom down hook fails or times out, and report the failure
- [x] #2 Down selects one custom teardown hook when both script and make target exist
- [x] #3 Custom ops status works when tmux is unavailable and status checks have bounded timeouts
- [x] #4 Bounce starts ops through the same hook priority as up
- [x] #5 Focused tests cover hook selection, failure paths, and tmuxp fallback
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Share hook selection across up, down, bounce, and status.
2. Bound status checks and let custom status run independently of tmux.
3. Guarantee tmux cleanup after a failed down hook while preserving errors.
4. Add focused unittest coverage, run checks, and record results.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented shared script-first hook selection for up/down/bounce/status, bounded tmux checks, custom status without tmux dependency, and cleanup after failed down hooks. Verification: uv run python -m unittest discover -s tests -v (7 passed); git diff --check passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed all four TASK-16 findings in server.py. Seven focused tests pass for failure cleanup, hook priority, custom status and timeouts, and tmuxp fallback.
<!-- SECTION:FINAL_SUMMARY:END -->
