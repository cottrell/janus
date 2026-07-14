# Janus

<p align="center">
  <img src="logo.png" alt="Janus" width="160" height="160">
</p>

Local dev homepage and ops dashboard: project link cards, optional tmuxp session controls, and optional AI-agent swarm hooks. The **dashboard alone** needs only Python and a registry of JSON files. Swarm, babysit, IDE, and MuxPod features are additive (per-project registry fields).

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

Optional env vars (defaults = previous hardcodes). Implemented in `mk/paths.py`.

| Variable | Default | Used for |
|----------|---------|----------|
| `JANUS_DATA_DIR` | `./data` | Project registry JSON directory |
| `JANUS_HOST` / `JANUS_PORT` | `::` / `7890` | Dashboard bind |
| `JANUS_DEV_ROOT` | `~/dev` | Project tree root (new-project, IDE deep-links) |
| `JANUS_NUDGE_CLI` | `~/dev/nudge/swarm/cli.py` | Swarm CLI if `aiswarm` not on `PATH` |
| `MUXPOD_SERVER_ID` | hostname / registry | MuxPod Deep Link ID |

Optional IDE helpers under `ide/` also read `JANUS_IDE_*` port/URL vars (defaults 9321 / 9323 / 9322) — only relevant if you enable `"ide_links": true`. See `mk/paths.py` and [`ide/SECURITY.md`](ide/SECURITY.md).

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
| **tmux** / **[tmuxp](https://github.com/tmux-python/tmuxp)** | Ops up/down/bounce | `tmuxp load`; `make ops-up` / `ops-down` |
| **[nudge](https://github.com/cottrell/nudge)** / **`aiswarm`** | Multi-agent tmux swarms, babysit, autostart | Separate project. `git clone https://github.com/cottrell/nudge.git && make install-aiswarm`. Prefer `aiswarm` on `PATH`, else `JANUS_NUDGE_CLI`. Runtime under `/tmp/nudge-swarm/<project>/`. Sample grid: `swarm/janus.yaml` (auto-approve — trusted machines only). |
| **[Backlog.md](https://github.com/MrLesk/Backlog.md)** | New-project init; backlog browser links | Optional binary |
| **GitHub CLI** (`gh`) | New-project `gh repo create` | Off by default in `mk/new_project.defaults.json` |
| **graphify** | Graph icon when `local_path/graphify-out/graph.html` exists | External pipeline |
| **ide-tools** | Icons when `"ide_links": true` | **Optional.** No app auth — private mesh/VPN + firewall only, not public internet. See [`ide/SECURITY.md`](ide/SECURITY.md). Install: `bash mk/install-ide-tools.sh`. Default ports 9321 / 9323 / 9322 (overridable above). |
| **[MuxPod](https://github.com/moezakura/mux-pod)** | Mobile tmux deep links | Match app **Deep Link ID** to `muxpod_server_id` in registry or `MUXPOD_SERVER_ID`. SSH host = any reachable name/IP. Single machine for now (TASK-14). |

### IDE tools (optional)

Janus only shows filebrowser / code-server icons when a project sets `"ide_links": true`. Services are started via `ide/ops.yaml` if you use them.

| Service | Default port | Script |
|---------|--------------|--------|
| code-server | 9321 (https links) | `ide/code-server/run.sh` |
| filebrowser | 9323 | `ide/filebrowser/run.sh` |
| ttyd | 9322 (public) / 19322 (backend) | `ide/ttyd/run.sh` |

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

Only **`project`** is required. Use **`localhost`** in URLs — the UI rewrites the host from `window.location.hostname` so the same links work on phone/remote.

Optional fields: `local_path`, `github_url`/`gitlab_url`, `tmuxp_ops`/`tmuxp_swarm`, `ops_up`/`swarm_up` (default true when configs set), `ide_links`, `autostart`, `meta`, `muxpod_server_id`. Registry is re-read each request (no restart).

## New project

```sh
make new-project name=myproject
# or: uv run python mk/new_project.py myproject --description "One-liner"
# non-interactive: -y / --yes-all, --no-gh-repo, --path DIR, …
```

Also **+ new** in the dashboard. Defaults: `mk/new_project.defaults.json` (or `--config path`).

| Step | What it does | Default |
|------|----------------|---------|
| `create_dir` | `mkdir` under `~/dev/{name}` or `--path` | on |
| `git_init` | `git init` in the **new** project only | on |
| `readme` | Minimal README | on |
| `backlog_init` | `backlog init` | on |
| `swarm_init` | `aiswarm init` | on |
| `ops_yaml` | `ops.yaml` + backlog browser port from **6430+** (`backlog_port_start`) | on |
| `janus_register` | Writes registry JSON locally (not auto-committed to janus) | on |
| `janus_repo_list` | `git config --global --add janus.repo …` | on |
| `gh_repo` | `gh repo create --private --push` | **off** |

Prompts: **Y** / **n** / **a** (all remaining) / **q**. Details: `uv run python mk/new_project.py --help`.

## Notes

```sh
git config --global --add janus.repo ~/dev/myproject
git for-each-repo --config=janus.repo status --short --branch
```

Optional user systemd unit: `janus.service` + `service_setup.md` (edit paths for your machine).

## For agents

Project conventions: see `AGENTS.md` (Claude/Gemini load the same file via symlink).

```sh
REG="${JANUS_DATA_DIR:-./data}"
cat > "$REG/$(basename $PWD).json" <<'EOF'
{
  "project": "myproject",
  "links": [{"label": "Dev server", "url": "http://localhost:PORT"}]
}
EOF
```
