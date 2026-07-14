# Janus

<p align="center">
  <img src="logo.png" alt="Janus" width="160" height="160">
</p>

Local dev homepage and ops dashboard: project link cards, optional tmuxp session controls, and optional AI-agent swarm hooks. The **dashboard alone** needs only Python and a registry of JSON files. Extra integrations are additive (per-project registry fields).

## Running

```sh
uv sync
cp -r data.example data   # or: export JANUS_DATA_DIR=/path/to/registry
make dev
make validate             # errors if the registry is empty/missing
```

`make` targets use `uv run`. Default registry is `./data` (`JANUS_DATA_DIR` to override). See `data.example/`.

```sh
make dev ARGS='--port 8080'              # or: uv run python server.py --help
```

Open the printed/local URL (default port is in `server.py --help` / `mk/paths.py`).

## Dependencies (dashboard)

| Dependency | Notes |
|------------|--------|
| **Python** ≥3.11 | `requires-python` in `pyproject.toml` |
| **[uv](https://github.com/astral-sh/uv)** | Recommended (`uv sync` / `make`). Or `pip install -e .` |
| **fastapi**, **uvicorn**, **pyyaml** | Via `uv sync` |
| **Browser** | `index.html` + Vue 3 from CDN (no npm build) |

No database, Docker, or systemd required for the core app.

## Optional features

If a tool is missing, that button/link simply does nothing; the rest still loads.

| Tool | Role |
|------|------|
| **git** | Card last-updated; `janus.repo` list; new-project init |
| **tmux** / **[tmuxp](https://github.com/tmux-python/tmuxp)** | Ops up/down/bounce (`make ops-up` / `ops-down`) |
| **[nudge](https://github.com/cottrell/nudge)** / **`aiswarm`** | **Optional** — agent swarms / babysit / autostart only if you want them |
| **[Backlog.md](https://github.com/MrLesk/Backlog.md)** | New-project init; backlog browser links |
| **GitHub CLI** (`gh`) | Optional new-project `gh repo create` (off by default) |
| **graphify** | Graph icon when output exists under `local_path` |
| **[MuxPod](https://github.com/moezakura/mux-pod)** | Mobile tmux deep links (`muxpod_server_id` / `MUXPOD_SERVER_ID`) |

## Adding links

One JSON file per project in the registry dir (`data/myproject.json` or under `JANUS_DATA_DIR`):

```json
{
  "project": "myproject",
  "local_path": "~/myproject",
  "github_url": "https://github.com/you/myproject",
  "tmuxp_ops": "ops.yaml",
  "tmuxp_swarm": "swarm/myproject.yaml",
  "description": "optional one-liner",
  "links": [
    {"label": "Dev server", "url": "http://localhost:3000"}
  ]
}
```

Only **`project`** is required. Use **`localhost`** in URLs — the UI rewrites the host from `window.location.hostname`. Other fields are optional enrichment; registry re-reads each request (no restart).

## New project

```sh
make new-project name=myproject
# or: uv run python mk/new_project.py myproject --description "One-liner"
# -y / --yes-all, --no-gh-repo, --path DIR, …  see --help
```

Also **+ new** in the dashboard. Steps and defaults: `mk/new_project.defaults.json` and `uv run python mk/new_project.py --help`.

## Notes

```sh
git config --global --add janus.repo ~/myproject
git for-each-repo --config=janus.repo status --short --branch
```

Optional user systemd: `janus.service` + `service_setup.md`. Knobs for less common setup live in `mk/paths.py` and `uv run python server.py --help`.

## For agents

See `AGENTS.md` (Claude/Gemini load it via symlink).

```sh
REG="${JANUS_DATA_DIR:-./data}"
cat > "$REG/$(basename $PWD).json" <<'EOF'
{
  "project": "myproject",
  "links": [{"label": "Dev server", "url": "http://localhost:PORT"}]
}
EOF
```
