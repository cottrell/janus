# Janus

<p align="center">
  <img src="logo.png" alt="Janus" width="160" height="160">
</p>

Local dev homepage and ops dashboard: project link cards, optional tmuxp session controls, and optional AI-agent swarm hooks. The **dashboard alone** needs only Python and a registry of JSON files. Extra integrations are additive (per-project registry fields).

Default listen: all interfaces (`::`) on port **7890**. Open `http://localhost:7890` or `http://<host>:7890` from another device over LAN or a private mesh/VPN if you use one (e.g. Tailscale, Yggdrasil, WireGuard — none required).

## Running

```sh
uv sync
cp -r data.example data   # or: export JANUS_DATA_DIR=/path/to/registry
make dev
make validate             # errors if the registry is empty/missing
```

`make` targets use `uv run`. Default registry is `./data`; override with **`JANUS_DATA_DIR`** (often a private checkout such as `~/dev/janus-data`). See `data.example/`.

```sh
JANUS_PORT=8080 make dev          # example override
```

## Configuration

Common env vars (optional; defaults match prior hardcodes). Full list: `mk/paths.py`.

| Variable | Default | Used for |
|----------|---------|----------|
| `JANUS_DATA_DIR` | `./data` | Project registry JSON directory |
| `JANUS_HOST` / `JANUS_PORT` | `::` / `7890` | Dashboard bind |
| `JANUS_DEV_ROOT` | `~/dev` | Default project tree root |

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
| **[nudge](https://github.com/cottrell/nudge)** / **`aiswarm`** | Agent swarms / babysit / autostart — install separately (`make install-aiswarm`) |
| **[Backlog.md](https://github.com/MrLesk/Backlog.md)** | New-project init; backlog browser links |
| **GitHub CLI** (`gh`) | Optional new-project `gh repo create` (off by default) |
| **graphify** | Graph icon when output exists under `local_path` |
| **[MuxPod](https://github.com/moezakura/mux-pod)** | Mobile tmux deep links (`muxpod_server_id` / `MUXPOD_SERVER_ID`) |

## Adding links

One JSON file per project in the registry dir (`data/myproject.json` or under `JANUS_DATA_DIR`):

```json
{
  "project": "myproject",
  "local_path": "~/dev/myproject",
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
git config --global --add janus.repo ~/dev/myproject
git for-each-repo --config=janus.repo status --short --branch
```

Optional user systemd: `janus.service` + `service_setup.md`.

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
