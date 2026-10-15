---
id: TASK-16
title: 'Review: support make up/down/status and mk/down.sh in ops endpoints'
status: Done
assignee:
  - '@codex'
created_date: '2026-10-15 10:11'
updated_date: '2026-10-15 10:27'
labels:
  - review
  - ops
dependencies: []
priority: high
type: chore
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review the recent changes to `server.py` in janus that add support for `make up`, `make down`, `make status`, and `mk/{up,down,status}.sh` hooks before falling back to tmuxp session management.

Verify:
1. Status checking logic and timeout handling.
2. Teardown ordering (custom script/make target -> tmux kill-session).
3. Error resilience and backward compatibility with projects using standard tmuxp ops.yaml.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect recent server.py ops changes and surrounding tests.
2. Verify status, timeout, teardown, and tmuxp fallback behavior with focused checks.
3. Record actionable review findings and finalize the task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Review of commit 28fdea2 and server.py; AST parse passed. Findings:
1. High: _run_ops_down (740-755) propagates a failing or timed-out script/make hook before tmux cleanup; despite the comment, kill-session is not assured. This affects down and bounce.
2. Medium: _run_ops_down (742-749) runs both an executable down script and make down when both exist, unlike up which selects one hook. Duplicate teardown can fail or cause side effects.
3. Medium: status (675) calls tmux_session_exists before the custom status hook; tmux has no timeout (391-398) and FileNotFoundError is uncaught by the HTTPException handler. A project with a valid custom status hook can hang or make /api/status fail when tmux is unavailable. A custom status timeout is silently replaced with the tmux result (680-693).
4. Medium: ops_bounce (785-790) prefers make up, while ops_up (764-769) prefers executable scripts. A project defining both can bounce into a different startup path.
Standard tmuxp projects still fall through to tmuxp load and tmux kill-session when hooks are absent (764-770, 740-755); no runtime ops were invoked against a live project.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reviewed ops lifecycle change 28fdea2 and validated server.py syntax. Recorded four findings covering teardown resilience, duplicate down hooks, status timeout/error handling, and bounce/up priority mismatch. Standard tmuxp fallback remains present. No code changes made.
<!-- SECTION:FINAL_SUMMARY:END -->
