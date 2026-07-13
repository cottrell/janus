---
id: TASK-13
title: Speed up initial dashboard load of data/ projects
status: In Progress
assignee: []
created_date: '2026-07-12 10:23'
updated_date: '2026-07-12 13:21'
labels:
  - performance
  - frontend
  - data
  - consider
dependencies: []
references:
  - server.py
  - index.html
  - data/
  - >-
    backlog/completed/task-7 -
    Optimize-project-status-checks-by-reading-local-state-files-and-sockets-directly.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Janus dashboard feels janky on initial load (especially on phone over yggdrasil). The main blocker is `GET /api/links`, called from `index.html` `load()` on mount and tab refocus — the page stays empty until it returns.

**Measured baseline (2026-07-12, 23 projects):** `server.get_links()` ≈ **1.3s** per request (3-run average). `/api/status` was already optimized in TASK-7; this task focuses on links/data enrichment.

**What `get_links()` does per project today** (see `server.py`):
- Read `data/*.json`
- Derive ide/config/muxpod links (path resolves, yaml read for session names)
- Live meta: `_get_last_git_ts()` → **subprocess `git log` per project** (likely dominant cost)
- Live meta: `_get_graphify_info()` → fs/json reads under `graphify-out/`
- Merge canned + live `meta`, sort, return full payload

Frontend currently waits for the full enriched payload before rendering cards.

**Goal:** Explore and implement ways to make first paint feel fast while keeping useful live fields (especially `last_git_ts` surfaced on cards).

**Directions to consider (not prescriptive):**
1. **Split fast vs slow path** — `/api/links` returns static/canned data immediately; lazy `/api/links/meta` or per-card fetch for live git/graphify fields
2. **Caching** — in-process TTL or mtime-based cache for git ts / graphify / yaml session names; invalidate on `data/*.json` change
3. **Parallelize** — thread pool for per-project git/fs work instead of sequential subprocesses
4. **Batch git** — single `git for-each-repo` or one multi-repo command vs N `git log` spawns
5. **UI skeleton** — render project names/cards from cached/previous payload while refresh completes (localStorage or stale-while-revalidate)
6. **Move work off hot path** — optional background job populates cache file; dashboard reads cache + shows “stale” indicator
7. **Parallel frontend fetch** — start `/api/status` alongside `/api/links` (small win; status is cheaper now)

**Constraints:** Keep `make validate` passing; minimal deps; phone/yggdrasil latency matters; don't break new-project registration or muxpod links.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 #1 Baseline documented: where time is spent in `/api/links` (measurement or profiling notes in task).
- [ ] #2 #2 At least two approaches evaluated with tradeoffs (latency, freshness, complexity, mobile UX).
- [ ] #3 #3 First paint or perceived load is noticeably faster on ~20+ projects (target: sub-500ms for static card shell, or equivalent UX improvement with documented rationale).
- [ ] #4 #4 Live fields (`last_git_ts`, graphify badge) remain available — immediately or via progressive/lazy load without regressing current card behaviour.
- [ ] #5 #5 No new mandatory deps unless strongly justified; `make validate` passes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-12: Quick wins shipped. Profiling: graphify graph.json parse ~923ms (myproject 4.3MB), git ~51ms, yaml ~60ms for 23 projects. Added mtime-keyed caches for graphify/git/session yaml; 30s TTL whole-response cache keyed on data/*.json mtime; parallel ThreadPool enrichment; muxpod server_id hoisted out of loop; frontend Promise.all links+status. Warm /api/links ~0ms; cold still ~1.3s first hit.
<!-- SECTION:NOTES:END -->
