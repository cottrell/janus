---
id: TASK-5
title: Add top-level ops and swarm status rows
status: Done
assignee: []
created_date: '2026-06-07 15:52'
updated_date: '2026-06-07 15:54'
labels:
  - ui
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Show compact top-level controls just below the project jump tiles so projects with configured ops or swarm can be seen and started quickly without opening each project card.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Projects with configured ops appear in a top-level ops row with a compact tile per project.
- [x] #2 Projects with configured swarm appear in a top-level swarm row with a compact tile per project.
- [x] #3 Each tile reflects current up/down status without bounce/down controls.
- [x] #4 Tiles can trigger the corresponding up action and refresh status afterward.
- [x] #5 The status display continues to update from the existing status polling path.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added top-level ops and swarm status rows beneath the project jump tiles. Each configured project now appears as a compact status tile using the existing /api/status polling data; unlit tiles start the corresponding service, lit tiles jump to the project card, and status polling now runs every 10 seconds with an additional delayed refresh after actions.
<!-- SECTION:FINAL_SUMMARY:END -->
