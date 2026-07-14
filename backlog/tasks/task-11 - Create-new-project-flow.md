---
id: TASK-11
title: Create "new project" flow
status: Done
assignee: []
created_date: '2026-07-12 06:08'
updated_date: '2026-07-12 10:14'
labels:
  - cli
  - scaffold
  - new-project
dependencies: []
references:
  - mk/new_project.py
  - mk/new_project.defaults.json
  - Makefile
  - README.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CLI (and eventually UI) flow to scaffold a new dev project and register it with Janus.

**Steps (each optional via y/n prompt, config, or flags):**
1. Create directory (`~/{name}` or `--path`)
2. `git init` in the **new project only** (never commits to janus)
3. README.md
4. `backlog init`
5. `nudge swarm init`
6. `ops.yaml` with auto-assigned backlog browser port
7. Janus `data/{name}.json` — local dashboard registration (**do not auto-commit to janus repo**)
8. `git config --global --add janus.repo`
9. GitHub repo: `gh repo create {name} --source=. --private --push` (content of gh_new_repo.sh)

**Interaction model:**
- Interactive: `[Y/n/a/q]` per step (yes / no / yes-to-all / quit)
- Config: `mk/new_project.defaults.json` or `--config`
- Flags: `--yes-all`, `--yes-<step>`, `--no-<step>`

**CLI entrypoint:** `make new-project name=foo` or `python3 mk/new_project.py foo`

**UI:** deferred follow-up.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 #1 Each setup step is individually skippable via interactive y/n, config defaults, or --yes/--no flags.
- [x] #2 #2 --yes-all and yes-to-all (a) during prompts skip remaining questions.
- [x] #3 #3 git init / commit / gh push happen only in the new project directory, never in janus.
- [x] #4 #4 Janus data/{name}.json registration works but script does not commit to janus git; user warned explicitly.
- [x] #5 #5 gh_repo step runs gh repo create --source=. --private --push (initial commit if needed).
- [x] #6 #6 backlog_port and local_path bugs fixed (--path respected; port resolved even if ops.yaml pre-exists).
- [x] #7 #7 make new-project target and README section document the flow.
- [x] #8 #8 UI flow (deferred — separate follow-up).
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-12: Reviewed Antigravity v1 (871881d). Marked prematurely Done — CLI only, bugs in backlog_port/local_path, no gh_repo, no y/n prompts.

2026-07-12: Rewrote mk/new_project.py with per-step y/n/a/q prompts, mk/new_project.defaults.json config, --yes-all and per-step flags, gh_repo step (gh repo create --private --push), fixed backlog_port/local_path/hardcoded nudge path. Added make new-project + README. Smoke-tested in /tmp (no janus register). Ready for user test project.

2026-07-12: Added UI wizard in index.html (+ new header button), server API endpoints, refactored new_project.py for shared execute_steps. Mobile-friendly large buttons; desktop keyboard shortcuts.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Delivered CLI (mk/new_project.py) and dashboard UI (+ new button) for creating projects. Both share prepare_project/build_step_schema/execute_steps. Each of 9 steps is skippable via y/n/a/q prompts (CLI) or Yes/No/All/Quit buttons + Y/N/A/Q keyboard (UI). API: GET /api/new-project/schema, POST /api/new-project. gh_repo step, config defaults, pyproject/uv run. Janus data/*.json registration is local-only (never committed by script).
<!-- SECTION:FINAL_SUMMARY:END -->
