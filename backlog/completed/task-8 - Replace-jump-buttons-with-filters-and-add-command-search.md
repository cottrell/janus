---
id: TASK-8
title: Replace jump buttons with filters and add command search
status: Done
assignee: []
created_date: '2026-07-07 13:10'
updated_date: '2026-07-07 13:14'
labels:
  - frontend
dependencies: []
modified_files:
  - index.html
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Change the dashboard navigation buttons so selecting a tile label filters the visible tiles instead of jumping to that tile, with repeated selection clearing the filter. Add a Ctrl+K command/search UI that lets users type partial labels, see matching tiles, and select a result by click, arrow keys, or Enter.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Clicking a tile label button filters the visible dashboard tiles to that tile.
- [x] #2 Clicking the currently selected tile label clears the filter and shows all tiles again.
- [x] #3 The selected filter state is visually distinguishable from unselected buttons.
- [x] #4 Ctrl+K opens a search UI focused for typing partial tile labels.
- [x] #5 Search results update as the user types and can be selected by click, arrow keys, or Enter, defaulting Enter to the top/highlighted match.
- [x] #6 Selecting a search result applies the same tile filter behavior as clicking the tile label button.
- [x] #7 Existing dashboard behavior outside tile navigation remains unchanged.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace the top project jump row with project filter buttons that toggle an active project filter.
2. Render the dashboard card grid from the filtered project list while keeping the full project list available for filter controls and status rows.
3. Add a Ctrl+K command palette with text search, click selection, arrow key movement, Enter selection, and Escape/backdrop close.
4. Validate with the project validator and a headless browser smoke test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented as a single-file Vue change in index.html. Prefix matches rank before substring matches so typing `ti` lists `myproject` ahead of names that merely contain `ti`, while still showing all matches. Preserved the previous top status row behavior that scrolls to a project when an already-up babysit tile is clicked by clearing any active filter before scrolling.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the project jump buttons with filter buttons that toggle the visible project card. Added active styling for the selected filter and a Ctrl+K project search palette with focused input, live matching, click selection, arrow-key navigation, Enter selection, Escape close, and backdrop close. Search uses substring matching with prefix matches ranked first, so short queries like `ti` select `myproject` by default.

Validation: `make validate` passed. A headless Chrome smoke test against `uvicorn server:app --host '::' --port 7891` verified filter to `myproject`, unfilter back to all 20 cards, Ctrl+K focus, `ti` match ordering with `myproject` first, and Enter applying the `myproject` filter.
<!-- SECTION:FINAL_SUMMARY:END -->
