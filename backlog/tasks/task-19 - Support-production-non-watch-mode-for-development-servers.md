---
id: TASK-19
title: Support production/non-watch mode for development servers
status: To Do
assignee: []
created_date: '2026-07-16 09:50'
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
