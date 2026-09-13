#!/usr/bin/env python3
"""One-shot enrich data/*.json with meta.summaries[] high_level_intent via mini agents."""

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from paths import get_data_dir

DATA = get_data_dir()

# (source, model label for meta.summaries, argv prefix before the prompt)
AGENTS = [
    ("agy", "Gemini 3.6 Flash (Low)", ["agy", "--model", "Gemini 3.6 Flash (Low)", "--dangerously-skip-permissions", "--print"]),
    ("codex", "gpt-5.6-luna", ["codex", "exec", "-m", "gpt-5.6-luna", "--dangerously-bypass-approvals-and-sandbox"]),
    ("grok", "grok-4.6", ["grok", "-m", "grok-4.6", "--always-approve", "-p"]),
    ("claude", "haiku", ["claude", "--model", "haiku", "--dangerously-skip-permissions", "-p"]),
]

PROMPT = """Read the project at {path} (start with README.md; also CLAUDE.md or AGENTS.md if no README).
Existing one-liner: {desc}
Write 1-2 sentences (max 50 words) describing high-level INTENT for an orchestrator deciding what projects to kick along.
Focus on purpose and current activity, not file structure. Output only the summary text."""


def has_intent(meta):
    if not meta:
        return False
    for s in meta.get("summaries") or []:
        if s.get("kind") == "high_level_intent":
            return True
    return False


def resolve_path(local_path):
    if not local_path:
        return None
    p = Path(local_path).expanduser()
    return p if p.is_dir() else None


def run_agent(agent_name, cmd_prefix, path, desc):
    prompt = PROMPT.format(path=path, desc=desc or "(none)")
    cmd = [*cmd_prefix, prompt]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=path, timeout=180)
    out = (res.stdout or "") + (res.stderr or "")
    if res.returncode != 0:
        raise RuntimeError(f"exit {res.returncode}: {out[-500:]}")
    return clean_output(out, agent_name)


def clean_output(text, agent_name):
    # Strip ANSI escape sequences (e.g. from TUI output)
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    skip_prefixes = (
        "tokens used", "I am running", "### Summary", "I'll ", "I will ",
        "Let me ", "Running ", "Usage:", "Error:",
    )
    candidates = []
    for ln in reversed(lines):
        if any(ln.startswith(p) for p in skip_prefixes):
            continue
        if ln.startswith("- ") or ln.startswith("* "):
            continue
        if "ERROR" in ln or "tool_error" in ln:
            continue
        if len(ln) < 20:
            continue
        candidates.append(ln)
    if not candidates:
        # Fallback: take last non-empty line
        if lines:
            candidates = [lines[-1]]
        else:
            raise RuntimeError(f"no summary parsed from {agent_name} output: {text[-300:]}")
    summary = candidates[0]
    # If grok concatenated prompt repetition into the summary line, split at sentence boundary if needed
    if summary.count('.') > 1:
        # If line starts with lower case or prompt fragment, clean leading fragment up to sentence start
        summary = re.sub(r'^[a-z0-9\s.,;:!\'\(\)-]+?[.\?!]\s*(?=[A-Z])', '', summary)
    summary = re.sub(r"^[a-z0-9\s.,;:!-]+?(?:summary|intent|notes|layout|orchestrator)[.:\s]+\s*", "", summary, flags=re.IGNORECASE)
    summary = re.sub(r"^[\"']|[\"']$", "", summary)
    return summary


def enrich_one(project_file, agent_name, cmd_prefix, model):
    data = json.loads(project_file.read_text())
    if data.get("disabled"):
        return data.get("project", project_file.stem), "disabled"
    meta = data.get("meta") or {}
    if has_intent(meta):
        return data["project"], "skip"

    path = resolve_path(data.get("local_path"))
    if not path:
        return data["project"], "no_path"

    desc = data.get("description", "")
    content = run_agent(agent_name, cmd_prefix, path, desc)
    entry = {
        "source": agent_name,
        "model": model,
        "kind": "high_level_intent",
        "content": content,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "based_on": ["description", "README.md"],
    }
    summaries = list(meta.get("summaries") or [])
    summaries.append(entry)
    data["meta"] = {**meta, "summaries": summaries}
    project_file.write_text(json.dumps(data, indent=2) + "\n")
    return data["project"], "ok"


def main():
    files = sorted(DATA.glob("*.json"))
    jobs = []
    for i, f in enumerate(files):
        agent_name, model, cmd_prefix = AGENTS[i % len(AGENTS)]
        jobs.append((f, agent_name, cmd_prefix, model))

    results = {}
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(files)))) as pool:
        futs = {
            pool.submit(enrich_one, f, a, c, m): f.stem
            for f, a, c, m in jobs
        }
        for fut in as_completed(futs):
            name = futs[fut]
            try:
                proj, status = fut.result()
                results[proj] = status
                print(f"{proj}: {status}")
            except Exception as e:
                results[name] = f"error: {e}"
                print(f"{name}: error: {e}", file=sys.stderr)

    failed = [k for k, v in results.items() if v.startswith("error")]
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()