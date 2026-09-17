---
id: TASK-6
title: Add top-level babysit status row
status: Done
assignee: []
created_date: '2026-06-08 05:58'
updated_date: '2026-06-08 05:59'
labels:
  - ui
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the top status controls with a babysit row that only includes projects whose swarm YAML enables babysit, rather than showing all swarm-configured projects.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Projects with at least one babysit-enabled swarm pane appear in a top-level babysit row.
- [x] #2 Projects without babysit enabled in swarm YAML do not appear in the babysit row.
- [x] #3 Babysit tiles reflect running/stopped/error status using the existing status style.
- [x] #4 Clicking an unlit babysit tile starts babysit monitoring and refreshes status afterward.
- [x] #5 Existing per-project babysit controls use the same babysit-enabled detection.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added YAML-based babysit detection in /api/status and a top-level babysit row in the dashboard. The row only includes projects with at least one pane whose swarm YAML has nudge.babysit.enabled=true; tiles use existing status styling and start babysit via babysit/apply when unlit. Per-project babysit controls now use the same configured flag.
<!-- SECTION:FINAL_SUMMARY:END -->
