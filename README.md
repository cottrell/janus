# Janus

Local dev homepage and ops dashboard: project link cards, optional tmuxp session controls, and optional AI-agent swarm hooks. The **dashboard alone** needs only Python and a registry of JSON files. Swarm, babysit, IDE, and MuxPod features are additive (per-project registry fields).

Listens on **port 7890** (all interfaces; see `server.py`). Open `http://localhost:7890` or `http://<host>:7890` from another device over LAN or a private mesh/VPN if you use one (e.g. Tailscale, Yggdrasil, WireGuard — none required).

## Running

```sh
uv sync
cp -r data.example data   # or: export JANUS_DATA_DIR=/path/to/registry
make dev
make validate             # errors if the registry is empty/missing
```

`make` targets use `uv run`. Default registry is `./data`; override with **`JANUS_DATA_DIR`** (often a private checkout such as `~/dev/janus-data`). See `data.example/`.

## Dependencies (dashboard)

| Dependency | Notes |
|------------|--------|
| **Python** ≥3.11 | `requires-python` in `pyproject.toml` |
| **[uv](https://github.com/astral-sh/uv)** | Recommended (`uv sync` / `make`). Or `pip install -e .` |
| **fastapi**, **uvicorn**, **pyyaml** | Via `uv sync` |
| **Browser** | `index.html` + Vue 3 from CDN (no npm build) |

No database, Docker, or systemd required for the core app.

## Optional features

Missing tools only disable their buttons/links; the rest still works.

| Tool | Role | Notes |
|------|------|--------|
| **git** | Card `last_git_ts`; `janus.repo` list; new-project `git_init` | System package |
| **tmux** / **[tmuxp](https://github.com/tmux-python/tmuxp)** | Ops up/down/bounce | `tmuxp load` |
| **[nudge](https://github.com/cottrell/nudge)** / **`aiswarm`** | Multi-agent tmux swarms, babysit, autostart | Separate project. `git clone … && make install-aiswarm`. Janus prefers `aiswarm` on `PATH`, else `~/dev/nudge/swarm/cli.py`. Runtime under `/tmp/nudge-swarm/<project>/`. Sample grid: `swarm/janus.yaml` (auto-approve flags — trusted machines only). |
| **[Backlog.md](https://github.com/MrLesk/Backlog.md)** | New-project init; backlog browser links | Optional binary |
| **GitHub CLI** (`gh`) | New-project `gh repo create` | Off by default |
| **graphify** | Graph icon when `local_path/graphify-out/graph.html` exists | External pipeline |
| **ide-tools** | Icons when `"ide_links": true` | **Optional.** No app auth — only for private mesh/VPN + firewall, not the public internet. Details: [`ide/SECURITY.md`](ide/SECURITY.md). Install: `bash mk/install-ide-tools.sh`. |
| **[MuxPod](https://github.com/moezakura/mux-pod)** | Mobile tmux deep links | Match **Deep Link ID** in the app to `muxpod_server_id` in `data/janus.json` (or `MUXPOD_SERVER_ID`). SSH host can be any reachable name/IP. Single machine only for now. |

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

Only **`project`** is required. Use **`localhost`** in URLs — the UI rewrites the host from `window.location.hostname` so the same links work on phone/remote. Optional: `local_path`, `github_url`/`gitlab_url`, `tmuxp_*`, `ops_up`/`swarm_up`, `ide_links`, `autostart`, `meta`, `muxpod_server_id`. Registry is re-read each request (no restart).

## New project

```sh
make new-project name=myproject
# or: uv run python mk/new_project.py myproject --description "One-liner"
# non-interactive: -y / --yes-all, --no-gh-repo, --path DIR, …
```

Steps (each y/n/a/q, or defaults in `mk/new_project.defaults.json`): create dir under `~/dev/{name}`, git init, README, backlog, `aiswarm init`, `ops.yaml`, Janus registry JSON (local only), `janus.repo` git config, optional `gh repo create`. Also available as **+ new** in the dashboard UI. Details: `uv run python mk/new_project.py --help`.

## Notes

```sh
git config --global --add janus.repo ~/dev/myproject
git for-each-repo --config=janus.repo status --short --branch
```

**Fork assumptions** (not yet env-configurable): projects under `~/dev`; swarm CLI as above; IDE URLs `https://localhost:9321`, `http://localhost:9323`, `http://localhost:9322`; single host for Janus/tmux/MuxPod.

## For agents

```sh
REG="${JANUS_DATA_DIR:-./data}"
cat > "$REG/$(basename $PWD).json" <<'EOF'
{
  "project": "myproject",
  "links": [{"label": "Dev server", "url": "http://localhost:PORT"}]
}
EOF
```
