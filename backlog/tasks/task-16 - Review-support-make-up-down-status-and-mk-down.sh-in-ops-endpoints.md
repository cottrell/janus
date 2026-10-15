---
id: TASK-16
title: 'Review: support make up/down/status and mk/down.sh in ops endpoints'
status: To Do
assignee: []
created_date: '2026-10-15 10:11'
labels:
  - review
  - ops
dependencies: []
priority: high
type: chore
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review the recent changes to `server.py` in janus that add support for `make up`, `make down`, `make status`, and `mk/{up,down,status}.sh` hooks before falling back to tmuxp session management.

Verify:
1. Status checking logic and timeout handling.
2. Teardown ordering (custom script/make target -> tmux kill-session).
3. Error resilience and backward compatibility with projects using standard tmuxp ops.yaml.
<!-- SECTION:DESCRIPTION:END -->
