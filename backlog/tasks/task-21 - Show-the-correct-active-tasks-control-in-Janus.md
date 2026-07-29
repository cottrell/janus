---
id: TASK-21
title: Show the correct active tasks control in Janus
status: Done
assignee:
  - codex
created_date: '2026-07-29 14:46'
updated_date: '2026-07-29 14:52'
labels: []
dependencies: []
modified_files:
  - index.html
  - server.py
priority: medium
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Janus must visually agree with the live aiswarm tasks state so operators can tell whether task dispatch is enabled. The dag-patterns dispatcher is running and the status API reports it as up, but the project card also presents the off control as active.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 When aiswarm task dispatch is running, the Janus project card highlights the tasks-on control and does not highlight the off control
- [x] #2 When task dispatch is stopped, the Janus project card highlights the off control and does not highlight the tasks-on control
- [x] #3 Existing Janus validation succeeds
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read the tasks enabled marker path from the swarm runtime map. 2. Report tasks as running only when the marker explicitly contains enabled=true and the shared session worker PID is live; report missing/disabled markers as stopped. 3. Verify against live enabled and disabled swarms, then run Janus validation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Diagnosis: /api/status currently reports dag-patterns tasks as {state: running, up: true}. The card's tasks-off button incorrectly marks itself active when isUp(...) is true, so both controls appear active.

Verification: a Bun UI-state assertion proved running=>off inactive and stopped=>off active; the live /api/status response reports dag-patterns tasks as running/up; make validate passed all 27 registry files; git diff --check passed.

Regression report: the prior UI-only fix made controls exclusive but exposed that backend tasks_status treats any live shared session worker as task dispatch running. aiswarm uses tasks/enabled.json as the explicit tasks-group marker; it exists with {enabled:true} for dag-patterns and is absent for the disabled janus tasks group.

Backend verification after regression fix: tasks_status returned running/up for live dag-patterns (enabled marker present) and stopped/down for live janus (shared worker running but enabled marker absent), matching `aiswarm tasks status`. `make validate` passed all 27 registry files and `git diff --check` passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Made Janus task-dispatch status match aiswarm end to end. The project-card on/off controls are mutually exclusive, and the backend now checks the runtime tasks enabled marker before treating the shared session worker as an active dispatcher. This prevents unrelated session-worker activity from displaying tasks as on. Verified against live enabled dag-patterns and disabled janus swarms; `make validate` and `git diff --check` pass.
<!-- SECTION:FINAL_SUMMARY:END -->
