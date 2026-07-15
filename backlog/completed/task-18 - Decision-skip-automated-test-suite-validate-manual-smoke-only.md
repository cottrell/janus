---
id: TASK-18
title: 'Decision: skip automated test suite (validate + manual smoke only)'
status: Done
assignee: []
created_date: '2026-07-15 10:31'
labels:
  - testing
  - decision
dependencies: []
references:
  - server.py
  - mk/validate.py
  - mk/new_project.py
  - mk/paths.py
  - Makefile
  - index.html
priority: low
type: docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Context

Session discussion (2026-07-15): whether to implement automated tests for Janus. Current coverage is only `make validate` (registry schema/port conflicts) plus ad-hoc smokes noted in backlog (tasks 4, 8, 16).

## Decision

**Do not implement an automated test suite.** For this single-host ops dashboard, tests would be mostly **tricky and pointless**.

## Why tests are a poor fit

| Area | Why awkward / low value |
|------|-------------------------|
| `babysit_status` / `swarm_panes_status` | Real `tmux`, PIDs (`os.kill`), Unix sockets, `/tmp/nudge-swarm/...` layout |
| `/api/status`, ops/swarm POST | Shells out to `tmux` / `tmuxp` / `aiswarm` against real sessions |
| `get_links` enrichment | `git log`, graphify dirs, yaml under real `local_path`; mtime caches |
| Frontend (`index.html`) | Vue from CDN, no build — needs headless browser or extracted helpers |
| `new_project` E2E | Creates dirs/git/backlog/optional gh; easy to pollute real registry |

Mocking these either (a) doesn't catch real failures or (b) is so heavy it becomes its own product. Live babysit apply/stop must not run in automated tests (mutates real workers).

## What already works

- **`make validate`** — live registry check (required fields, paths, swarm yaml shape, port conflicts / shared-service exceptions, `port_scope`).
- **Manual smoke** when changing API/UI: TestClient or curl for `/api/links` and `/api/status`; occasional headless check for filters (task-8 style).
- Task notes already record one-off validation; no need to formalize that into CI.

## If something keeps regressing (narrow exception)

Only then consider **one-off pure asserts**, not a full suite:

- Port conflict rules in validate (shared URL vs real conflict; backlog label special-case)
- `_muxpod_link` / IDE deep-link URL shape (`JANUS_DEV_ROOT`, env ports)
- `build_janus_config` / `allocate_backlog_port` / `slugify` / `to_https_field`

Prefer a tiny script or a few asserts over pytest scaffolding, `tests/`, and `make test`.

## Explicitly out of scope

- Full browser automation for filters/Ctrl+K
- Integration tests against real tmux/aiswarm
- `enrich_meta` agent CLIs
- `autostart` / live `ops-up` / `swarm-up`

## Recommendation summary

Skip the suite. Keep **validate + manual smoke**. Revisit only for pure helpers that repeatedly break.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No pytest/test suite is required for Janus core
- [ ] #2 Keep make validate as the live-registry check
- [ ] #3 Use ad-hoc manual smoke when changing status/babysit/API/UI
- [ ] #4 Only reconsider tests if pure logic keeps regressing (port conflicts, muxpod URL shape, janus config builder)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reviewed whether Janus needs automated tests. Conclusion: mostly pointless. Real failures are live environment (tmux, aiswarm, local paths, registry JSON), not pure logic. Keep make validate + occasional manual smoke; do not invest in a pytest suite unless a pure helper repeatedly regresses.
<!-- SECTION:FINAL_SUMMARY:END -->
