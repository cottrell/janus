---
id: TASK-19
title: Support production/non-watch mode for development servers
status: Done
assignee: []
created_date: '2026-07-16 09:50'
updated_date: '2026-07-16 13:00'
labels:
  - performance
  - ops
dependencies: []
priority: medium
type: enhancement
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add support for non-watch (production) mode in development servers (such as uvicorn and vite) to reduce file-watching inotify instance usage. Consider adding flags or environment variables to disable autoreload and hot module replacement, and allow manual reloading where applicable.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Did planistan, internet-monitoring and janus. Left rest. Set user watches higher 512 or somethig.
<!-- SECTION:NOTES:END -->
