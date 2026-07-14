---
id: TASK-12
title: Consider making a contentless version public?
status: Done
assignee: []
created_date: '2026-07-12 06:10'
updated_date: '2026-07-14 11:13'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Think about how you would organize that  ...

Would have the new project creation step in it for convenience.

What else?

dependencies? installations?

Perhaps the ./data would be it's own repo ... i.e. janus_personal?

Janus is becoming a kind of pre git thing almost like sitting above it all.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-14: Closed as done/superseded by TASK-16 and subsequent public-readiness work.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded by TASK-16 (public release prep) and the contentless split:
- Registry lives outside the repo (`JANUS_DATA_DIR` / private janus-data)
- main is a single clean commit; personal project inventory scrubbed
- LICENSE, data/ gitignore, aiswarm resolve, smoke path, GitHub meta done
- Repo still private until explicitly opened

No further work under this ticket.
<!-- SECTION:FINAL_SUMMARY:END -->
