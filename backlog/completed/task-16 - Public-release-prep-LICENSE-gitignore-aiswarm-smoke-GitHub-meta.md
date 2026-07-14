---
id: TASK-16
title: 'Public release prep (LICENSE, gitignore, aiswarm, smoke, GitHub meta)'
status: Done
assignee: []
created_date: '2026-07-13 22:53'
updated_date: '2026-07-13 22:54'
labels:
  - public
  - release
dependencies: []
modified_files:
  - LICENSE
  - .gitignore
  - mk/paths.py
  - mk/swarm.py
  - mk/autostart.py
  - mk/new_project.py
  - server.py
  - README.md
  - data.example/janus.json
  - data.example/myproject.json
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finish contentless public readiness for Janus without flipping repo visibility yet.

Already done (context):
- Registry moved to janus-data / JANUS_DATA_DIR
- Personal project names scrubbed; main is single clean commit
- origin archive/full-history deleted; local archive only

Steps for this task (do NOT make the GitHub repo public):
1. Add LICENSE (MIT)
2. Restore data/ in .gitignore (keep data.example tracked)
3. Clean-clone smoke: uv sync, copy data.example → data, make dev, hit /
4. Prefer aiswarm on PATH for swarm CLI; fall back to aiswarm on PATH / JANUS_NUDGE_CLI; update README hardcoded assumptions
5. GitHub repo description (and topics if useful); LICENSE will be detected after push
6. OUT OF SCOPE: make repo public

References: task-12 discussion, public-release checklist.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 LICENSE present (MIT)
- [x] #2 data/ is gitignored; data.example/ still tracked
- [x] #3 aiswarm preferred for swarm CLI with documented fallback
- [x] #4 Clean-clone smoke path works (uv sync + data.example + make dev)
- [x] #5 GitHub repo has a non-empty description
- [x] #6 Repo remains private (visibility not flipped)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-13: Implemented steps 1-5. Repo remains private.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Steps 1–5 done; step 6 (make public) out of scope.

- LICENSE: MIT (David Cottrell 2026)
- .gitignore: data/
- aiswarm: resolve_swarm_argv() in mk/paths.py; server + mk/autostart/swarm/new_project use it; README updated
- data.example: no required local_path so clean clone validates
- Smoke: isolated tree + data.example → validate OK, GET / 200, /api/links has janus+myproject
- GitHub: description + topics set; isPrivate=true

Do not flip visibility until user is ready.
<!-- SECTION:FINAL_SUMMARY:END -->
