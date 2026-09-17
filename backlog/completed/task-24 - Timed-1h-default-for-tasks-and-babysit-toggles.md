---
id: TASK-24
title: Timed 1h default for tasks and babysit toggles
status: Done
assignee: []
created_date: '2026-08-31 05:56'
updated_date: '2026-08-31 05:59'
labels: []
dependencies: []
priority: medium
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
nudge now supports `aiswarm tasks start --for 1h` and `aiswarm babysit start --for 1h`. Janus currently starts those groups unbounded.

Keep a single on/off toggle (no extra duration buttons, dropdown, or start popup). Default click = 1h. Shift-click = run until stop. Remaining time on the card label when timed.

Popup/dropdown/forever buttons were considered and rejected as clutter on already-compressed tiles (TASK-22).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Clicking tasks/babysit start from Janus uses aiswarm --for 1h (no extra buttons)
- [x] #2 While running, the card toggle shows remaining time; click still stops and clears the timer
- [x] #3 Shift-click starts until manual stop (forever); tooltip documents both
- [x] #4 Status API exposes remaining_secs/until so matrix/rows tooltips can show the deadline
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Single toggle: click starts `aiswarm … start --for 1h`. Shift-click omits `--for` (until stop). Stop unchanged. Status reads `until` from tasks/enabled.json and babysit_until.json and exposes remaining_secs. Card label shows remaining when timed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Janus tasks/babysit stay one button. Click starts for 1h; the card shows time left; click again stops. Shift-click runs until stop. No extra buttons, dropdown, or start popup.
<!-- SECTION:FINAL_SUMMARY:END -->
