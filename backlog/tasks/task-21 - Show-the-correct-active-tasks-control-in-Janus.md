---
id: TASK-21
title: Show the correct active tasks control in Janus
status: Done
assignee:
  - codex
created_date: '2026-07-29 14:46'
updated_date: '2026-07-29 14:47'
labels: []
dependencies: []
modified_files:
  - index.html
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
1. Correct the project-card off-button active predicate so it is mutually exclusive with the tasks-on state. 2. Run the existing Janus validation and inspect the focused diff. 3. Verify the live dag-patterns API state still maps to tasks-on.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Diagnosis: /api/status currently reports dag-patterns tasks as {state: running, up: true}. The card's tasks-off button incorrectly marks itself active when isUp(...) is true, so both controls appear active.

Verification: a Bun UI-state assertion proved running=>off inactive and stopped=>off active; the live /api/status response reports dag-patterns tasks as running/up; make validate passed all 27 registry files; git diff --check passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Corrected the tasks-off button's active-state binding so it is mutually exclusive with tasks-on. This fixes the misleading dag-patterns card where both controls appeared active despite aiswarm and the Janus API correctly reporting the dispatcher as running. Verified both state branches with a scripted assertion, confirmed the live dag-patterns API state, and ran `make validate` successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
