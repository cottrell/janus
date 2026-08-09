---
id: TASK-23
title: matrix/rows button is inverted
status: Done
assignee:
  - 'aiswarm:janus:0.5'
created_date: '2026-08-09 07:49'
updated_date: '2026-08-09 07:51'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
I think like curated/filter/jump button we should show in the button the state we are in not the "other state". It is too confusing. Currenly I think it shows matrix when we are in rows mode and rows when we are in matrix mode.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Button label shows current layout state (matrix when matrix, rows when rows)
- [x] #2 Title tooltip describes current view and click-to-switch
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fixed: topView toggle now labels current state (matrix/rows), matching clickMode (filter/jump/curate). Was inverted — showed the other state.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Inverted matrix/rows header button so it shows the current view state (⊞ matrix / ☰ rows), consistent with filter/jump/curate. Tooltip also reflects current state with click-to-switch hint.
<!-- SECTION:FINAL_SUMMARY:END -->
