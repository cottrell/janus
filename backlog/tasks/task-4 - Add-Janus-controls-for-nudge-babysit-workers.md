---
id: TASK-4
title: Add Janus controls for nudge babysit workers
status: Done
assignee:
  - Codex
created_date: '2026-05-24 07:43'
updated_date: '2026-05-24 09:03'
labels:
  - ui
  - nudge
  - swarm
dependencies: []
references:
  - ./server.py
  - ./index.html
  - aiswarm
  - /tmp/nudge-swarm/janus/runtime.json
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expose lightweight babysit controls for projects with configured swarm files and babysit-enabled panes. Janus should let the user apply/start, stop, and inspect status for nudge babysit workers without adding detailed swarm internals to the basic project tile. Use `aiswarm` as the command surface: `babysit apply`, `babysit stop`, and `babysit status` against the project's `tmuxp_swarm` config. Keep the card UI compact: the main visible addition should be on/off style babysit controls near the existing ops/swarm buttons, with richer swarm details only behind links or a small modal/dialog if that proves useful.

Relevant local context: Janus currently reads project metadata from `data/*.json`; `server.py` resolves `tmuxp_ops` and `tmuxp_swarm`, exposes ops/swarm start/stop/bounce endpoints, and generates filebrowser/code-server links for project roots. `index.html` renders the project cards and action buttons. Nudge swarm CLI commands are in `aiswarm`; `aiswarm babysit --help` shows `apply`, `status`, and `stop` subcommands.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Projects with `local_path` and `tmuxp_swarm` expose compact babysit apply/start and stop controls on the project card without adding verbose pane or swarm details to the tile.
- [x] #2 The backend invokes `aiswarm babysit apply <config>`, `babysit stop <config>`, and `babysit status <config>` using the resolved swarm config path, with clear API errors when the config or CLI is missing.
- [x] #3 The status response includes enough babysit state for the UI to show whether babysit is off, stopped, running, or errored for a configured swarm.
- [x] #4 Swarm and ops config names in the project metadata are usable as links when practical, preferably to the existing filebrowser or code-server targets, while preserving the existing compact metadata layout.
- [x] #5 If a swarm-structure explanation is added, it lives behind an explicit modal/dialog or similar secondary affordance and does not pollute the default card view.
- [x] #6 Relevant manual checks are documented, including at least one project with babysit-enabled panes and one project without babysit configuration.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend `server.py` with helpers for config-file IDE links and babysit status parsing, keeping all path resolution under existing `local_path` safeguards.
2. Add backend endpoints for `POST /api/projects/{project}/babysit/apply`, `POST /api/projects/{project}/babysit/stop`, and status integration using `aiswarm babysit ... <config>`.
3. Update `index.html` so ops/swarm config metadata labels can link to filebrowser/code-server when possible, and add compact babysit apply/stop controls only for projects with swarm configs.
4. Avoid a swarm-structure modal unless the first pass needs it; keep richer detail out of the tile.
5. Validate with Python syntax checks, existing `make validate`, direct API/status checks where safe, and document manual-check coverage in the task notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented compact babysit controls without adding pane details to the project tiles. Backend status maps empty `babysit status` output to `off`, desired-but-not-running panes to `stopped`, running panes to `running`, and command/stale/timeout failures to `errored`. The optional swarm-structure modal was intentionally not added in this pass because links plus compact controls satisfy the immediate need without clutter.

Validation run: `python3 -m py_compile server.py mk/validate.py`; `make validate`; FastAPI TestClient smoke check for `/api/links` and `/api/status`; served app on `http://localhost:7891` and checked `/`, `/api/status`, and `/api/links` via curl. Status smoke check saw `{'off': 10, 'stopped': 3}`, covering projects without babysit-enabled panes and projects with babysit-enabled panes that are currently stopped. Did not click live apply/stop because that would mutate babysit workers across real local projects.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented lightweight Janus babysit support for nudge swarm projects.

Changes:
- Added backend babysit status integration and `babysit apply` / `babysit stop` endpoints using `aiswarm`.
- Added compact `babysit on` / `off` controls that only appear for swarm projects where babysit is configured by status output.
- Added filebrowser links for ops/swarm config metadata when Janus can safely derive them from `local_path`.

Validation:
- `python3 -m py_compile server.py mk/validate.py`
- `make validate`
- FastAPI smoke checks for `/api/links` and `/api/status`
- Served app at `http://localhost:7891` and checked `/`, `/api/status`, and `/api/links` with curl.

Risk:
- Live apply/stop button clicks were not executed during validation because they intentionally mutate babysit workers for real local projects.
<!-- SECTION:FINAL_SUMMARY:END -->
