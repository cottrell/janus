---
id: TASK-9
title: >-
  Consider adding richer per-project metadata for data/ projects (git
  last-updated, AI descriptions, graphify status)
status: Done
assignee:
  - grok
created_date: '2026-07-09 05:59'
updated_date: '2026-07-14 12:34'
labels:
  - metadata
  - projects
  - consider
dependencies: []
references:
  - data/
  - server.py
  - mk/validate.py
documentation:
  - README.md describing data/ format
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
For each project listed in ./data/*.json we could add more metadata.

Some of it live, some of it canned:
- last-updated timestamp from git (git log on the local_path). Note: not always accurate because some things are part of a larger repo, but that's ok.
- AI based high level description. Per author/model? (e.g. claude, fable, haiku, grok?) Decide if run based on any or specific one. Largely based on 'any' so we are not re-summarizing all the time.
- Track if graphify has ever been run on the project. Does graphify produce useful summaries of the project? (inspect GRAPH_REPORT.md god nodes / summary etc.)

Do not immediately surface/display this information in the janus UI. Goal is to use janus (the project registry + helpers) to drive automatic workflows on the projects themselves eventually.

See also graphify skill outputs in graphify-out/ for projects that have it (e.g. nudge, myproject).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add 'meta' (and related) to KNOWN_FIELDS in mk/validate.py to support canned metadata without errors.
- [x] #2 Add minimal live metadata helpers in server.py: last git update ts and graphify run detection (has_run, nodes/edges if avail, last run info).
- [x] #3 In get_links(), compute live meta, merge over any canned 'meta' from the project json, attach as 'meta' on returned project dicts (available to future workflows, no UI impact).
- [x] #4 Support canned AI high-level desc etc by allowing arbitrary under 'meta' in data/*.json (no auto generation code yet).
- [x] #5 Changes are minimal diff, zero new files, no changes to index.html or current display logic, no new deps.
- [x] #6 Document the additions in the task (plan, notes) and optionally a one-line mention in README if diff minimal.
- [x] #7 Refine schema inside meta to support multi-author AI summaries (with source/author tracking) + 'any' trigger condition; support graphify as a summary source. (Implemented via documented schema + has_any_ai_summary helper.)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementation approach (minimal, follow prefs):
1. First, update the task record itself with ACs, this plan, before code edits.
2. Edit mk/validate.py (1-line): add 'meta' to KNOWN_FIELDS set. (allows future canned meta: {ai_summary:.., graphify:.., etc} or top level last_updated if wanted).
3. In server.py:
   - Add two small pure helper fns near other utils (e.g. after imports or before get_links):
     def _get_last_git_ts(local_path: str | None) -> int | None:
       if not local_path: return None
       try:
         p = str(Path(local_path).expanduser().resolve())
         res = subprocess.run(['git','-C',p,'log','-1','--format=%ct','--','.'], capture_output=True, text=True, timeout=3)
         if res.returncode==0 and res.stdout.strip(): return int(res.stdout.strip())
       except Exception: pass
       return None
     def _get_graphify_info(local_path: str | None) -> dict:
       if not local_path: return {'has_run': False}
       try:
         root = Path(local_path).expanduser().resolve()
         gout = root / 'graphify-out'
         if not gout.is_dir(): return {'has_run': False}
         info = {'has_run': True}
         gjson = gout / 'graph.json'
         if gjson.is_file():
           try:
             gd = json.loads(gjson.read_text())
             info['nodes'] = len(gd.get('nodes',[]))
             info['edges'] = len(gd.get('edges',[]))
           except: pass
         costf = gout / 'cost.json'
         if costf.is_file():
           try:
             cd = json.loads(costf.read_text())
             runs=cd.get('runs') or []
             if runs: info['last_run'] = runs[-1].get('date')
           except: pass
         report = gout / 'GRAPH_REPORT.md'
         if report.is_file():
           info['report_mtime'] = int(report.stat().st_mtime)
         return info
       except Exception: return {'has_run': False}
   - Modify inside get_links() after loading p and applying ide/config links:
     # live project metadata (for workflows; not displayed in UI yet)
     lp = p.get('local_path')
     live = {}
     ts = _get_last_git_ts(lp)
     if ts: live['last_git_ts'] = ts
     ginfo = _get_graphify_info(lp)
     if ginfo.get('has_run'): live['graphify'] = ginfo
     if live:
       canned = p.get('meta') or {}
       p['meta'] = {**canned, **live}  # live wins for overlapping keys like last_git_ts
4. After edits: run `make validate`, test by python -c "import server; print([pr.get('meta') for pr in server.get_links() if pr.get('meta')][:3])" or similar.
5. Use task_edit to append notes, check off ACs, add finalSummary when wrapping.
6. Do not edit data/ files, index.html, or introduce new modules/files. Keep git last-updated and graphify checks resilient (timeout, except).
Risks/mitigations: git may be slow or absent on some paths -> timeout+except; graphify json parse fail -> except; adding 'meta' field is backward compat.

Post-impl: the plan was followed exactly. No scope creep. git ts and graphify checks are live (cheap). Canned meta ready for authors to populate (or future script using pal MCP etc for summaries).

Schema addition (post user feedback):
- No change to merge logic needed (already supports nested structures).
- New helper + extensive inline doc is the 'schema'.
- Future: a mk/ script or pal-driven one could populate summaries[] entries without touching janus core.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented minimal live + canned support:
- 'meta' allowed in validate (AC1)
- helpers _get_last_git_ts (uses git log -1 -- . for dir-aware ts) and _get_graphify_info (detects graphify-out, parses nodes/edges/links, cost last_run, report mtime) (AC2)
- in get_links after config links: compute live, merge {**canned, **live}, attach p["meta"] (AC3)
- arbitrary under meta supported for ai_summary etc (AC4)
- no new files, no index.html touch, used existing imports, resilient excepts/timeouts (AC5)
Tested: make validate passes; all 20 projects get meta; nudge/myproject show graphify with correct 643 nodes/921 edges; janus etc get only last_git_ts.
Added one-line to README for discoverability.

Also inspected graphify GRAPH_REPORT (god nodes, summary) -- it does produce structured high-level views of project (communities, hubs) which could feed summaries later but not auto-run here.

For AI descs: support is there via e.g. "meta": {"ai_summary": "... (from any model)" }; no generation logic added as it would be heavier and re-summarize concern noted.

Future use: workflows can now do e.g. for p in get_links(): if p.get("meta",{}).get("graphify"): ... or use last_git_ts to decide refresh etc.

AC6 also satisfied (plan/notes + README one-liner). Task remains In Progress as this is the initial consideration + small impl slice. Next could populate sample canned meta, add a /api/meta endpoint if wanted, or drive a workflow script.

User follow-up: wants proper schema for AI summaries that records *source/author* (not just the text), supports *multiple* agents/models (claude, grok, haiku, fable, graphify, etc.), and allows 'any' check in triggers/workflows so we don't re-summarize.

Confirmed understanding. Refined the approach:
- meta remains free-form dict (merge of canned + live) for minimalism.
- Added documented recommended schema using meta.summaries[] array of objects.
- Each summary entry has: source, (optional)model, kind, content, generated_at, based_on.
- graphify (live or canned extracted) is a first-class source.
- Added has_any_ai_summary(meta) pure helper + schema comment block right next to the meta code.
- 'Any' trigger example: bool(m.get('summaries')) or bool(m.get('graphify')) -- works for 'check for any' regardless of specific author.

Small README update to mention summaries[] + has_any_ai_summary helper.

Tested: has_any_ai_summary returns True exactly when graphify present (nudge/myproject) or when canned summaries/ai_* would be. Janis (no graphify) is False until a summary is added.

Full schema now lives in server.py comment block + task notes + this response. Ready for canned population (by hand or future agent workflow).

User question (2026-07-09): Is there a script that generates the last_git_ts / graphify info? Is the AI summaries part only via agents? What am I supposed to run/check now? Also noted no commits yet.

Current reality:
- last_git_ts and graphify fields are *live-computed* inside server.get_links() (git log + fs checks on graphify-out/). No pre-generation, no cache file, no mk/ script writes them. They appear fresh every time the projects list is loaded (API or direct import).
- mk/*.py only iterate data/*.json for their narrow jobs (ops, swarm, autostart, clone, validate). No meta generation exists today.
- Canned summaries (with source/author) are manual or agent-driven edits to the data/*.json files. has_any_ai_summary() exists to let scripts decide whether to invoke an agent.
- Graphify data comes from you previously having run the external graphify tool/skill on a project's directory.

What to do now to observe:
  python3 -c 'import server, json; [print(p["project"], p.get("meta")) for p in server.get_links() if p.get("meta")][:5]'
  (or start server + curl /api/links)

Stage: live computation + multi-source schema + helper prototyped. Task is still exploratory. Changes left uncommitted for user review.

User requested to surface last_git_ts in the UI (reversing the earlier 'not immediately display' for this specific live field).
Added under card description: <div class="card-updated"> with relative time (Xm ago / Xh / Xd / short date) + ISO title tooltip.
Added .card-updated CSS, formatTs() helper (and exposed in return), inline template guard using p.meta.last_git_ts.
Live values from server now visible on dashboard cards.

2026-07-11: Verified implementation complete — all 7 ACs checked, server.py helpers live, UI shows last_git_ts, enrich-meta skill exists, make validate OK on 21 projects. Marked Done.

2026-07-14: Follow-up — Claude Haiku added to skills/enrich-meta + mk/enrich_meta.py (round-robin with agy/codex/grok). Skill docs cleaned (skip via has_intent, UI already shows intent). See TASK for haiku slice if present / commit message.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added per-project `meta` support: live-computed `last_git_ts` and `graphify` info merged with canned metadata from `data/*.json`. Introduced `has_any_ai_summary()` helper and documented `meta.summaries[]` schema for multi-author AI descriptions (claude, grok, graphify, etc.) with source/model/kind/content tracking. `mk/validate.py` allows `meta` field. `get_links()` attaches merged meta on every project dict for workflow use. Later surfaced `last_git_ts` in dashboard cards with relative timestamps. `skills/enrich-meta/SKILL.md` documents agent-driven summary population.

Tests: `make validate` passes (21 projects). Spot-check: `python3 -c 'import server; ...'` confirms meta on all projects; nudge/myproject show graphify node/edge counts.
<!-- SECTION:FINAL_SUMMARY:END -->
