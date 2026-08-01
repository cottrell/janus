---
id: TASK-22
title: 'Compress the ops, swarm and tasks buttons in tiles'
status: Done
assignee:
  - 'aiswarm:janus:0.5'
created_date: '2026-08-01 15:32'
updated_date: '2026-08-01 15:34'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
I think we can just have one button for [ops up] that just toggles state and get rid of the down button. You could perhaps make the up toggle to down when off to help people who are more colour blind etc I guess if you think that makes sense. Keep the bounce button.  I think it will save on real estate and look better.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ops/swarm tiles show one toggle + bounce (no separate down)
- [x] #2 toggle label switches to down/off when service is up
- [x] #3 tasks/babysit tiles show one toggle (no separate off)
- [x] #4 bounce still works for ops and swarm
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Compressed tile action groups:
- ops/swarm: single toggle (label 'up'↔'down' by state) + bounce; removed separate down button
- tasks/babysit: single toggle ('on'↔'off'); removed separate off button
- CSS: only apply joined-radius rules when group has 2+ buttons; dropped unused .down styles
Colorblind: label text reflects next/current stop vs start state in addition to .up color.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Tile action groups compressed in index.html: ops/swarm are toggle+bounce (label flips up↔down); tasks/babysit are single on/off toggles. Separate down/off buttons and unused .down CSS removed.
<!-- SECTION:FINAL_SUMMARY:END -->
