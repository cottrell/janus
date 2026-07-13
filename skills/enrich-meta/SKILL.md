---
name: enrich-meta
description: Add high-level intent summaries to Janus data/*.json project metadata for orchestrator agents deciding what to kick along.
trigger: /enrich-meta
---

# /enrich-meta

Populate canned `meta.summaries[]` on Janus project registry entries (`data/<project>.json`). Goal: **intent**, not architecture — help a top-level orchestrator decide which projects deserve attention.

## Schema (canonical: `server.py` comment block)

Add or extend `meta` on each `data/<project>.json`:

```json
"meta": {
  "summaries": [
    {
      "source": "agy",
      "model": "Gemini 3.5 Flash (Low)",
      "kind": "high_level_intent",
      "content": "One or two sentences: what is this project for, why would an orchestrator care.",
      "generated_at": "2026-07-09T12:00:00Z",
      "based_on": ["description", "README.md"]
    }
  ]
}
```

- `kind`: use **`high_level_intent`** (orchestrator-facing), not `high_level_description` or graphify `god_nodes`.
- `source`: agent id — `agy`, `codex`, `grok`, `claude`, etc.
- Append to existing `summaries[]`; do not overwrite other authors.
- Preserve all other JSON fields. `meta` may already exist empty or with other keys.
- Live keys (`last_git_ts`, `graphify`) are computed by `server.get_links()` — **never** write those to JSON.

## Skip conditions

Use `server.has_any_ai_summary(meta)` logic before calling an LLM:

- Skip if `meta.summaries` already has any entry with `kind: "high_level_intent"`.
- Optionally skip if only stale intent exists and `last_git_ts` is old (orchestrator refresh policy — not implemented yet).

Do **not** treat live `graphify` alone as sufficient intent text.

## Inputs per project

1. `description` field in `data/<project>.json` (if present)
2. `README.md` at `local_path` (first ~100 lines; fall back to `CLAUDE.md` / `AGENTS.md` if no README)
3. Optional: recent backlog task titles (low priority for v1)

## Agent assignment (mini / flash models)

| Agent | CLI | Model flag |
|-------|-----|------------|
| agy | `agy --model "Gemini 3.5 Flash (Low)" --dangerously-skip-permissions --print "PROMPT"` | must put `--model` **before** `--print` |
| codex | `codex exec -m gpt-5.4-mini --dangerously-bypass-approvals-and-sandbox "PROMPT"` | |
| grok | `grok -m grok-composer-2.5-fast --always-approve -p "PROMPT"` | use `grok-composer-2.5-fast` to save quota; **run from project cwd** or paths may fail Read tool |

**Caveat:** `ide-tools` shares `local_path` with janus — agents may conflate them; prefer `description` field for that entry.

**Prompt template** (substitute PROJECT, PATH, EXISTING_DESC):

```
Read the project at PATH (start with README.md; also see existing one-liner: "EXISTING_DESC").
Write 1-2 sentences (max 50 words total) describing high-level INTENT for an orchestrator deciding what to kick along.
Focus on purpose and activity, not file structure. Output only the summary text, no quotes or preamble.
```

For agy, `cd` to project dir or `--add-dir PATH` so README is readable.

## Parallel batching

Split `data/*.json` across three agents (~7 projects each). Run batches in parallel. After all complete:

```sh
make validate
python3 -c "import server; print(sum(1 for p in server.get_links() if (p.get('meta') or {}).get('summaries')))"
```

## Future UI

Summaries are not displayed yet. Intended for orchestrator consumption; later may surface as card hover tooltip (`meta.summaries[0].content` or preferred source).

## Anti-patterns

- Do not use graphify god-nodes as intent summary.
- Do not regenerate all projects on every run.
- Do not add scripts that hide the schema — agents edit JSON directly.