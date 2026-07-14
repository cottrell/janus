# Janus

Local dev homepage and ops dashboard: project link cards, optional tmuxp session controls, and optional AI-agent swarm hooks. The **dashboard alone** needs only Python + a registry of JSON files. Swarm / babysit / IDE / MuxPod features are additive and driven by per-project registry fields.

Default bind is all interfaces on port **7890** (see `server.py`). From another device (phone, laptop) use `http://<host>:7890` — LAN, or any private mesh/VPN you already use (e.g. Tailscale, Yggdrasil, WireGuard). Nothing in Janus requires a particular overlay.

## Running

Python deps are in `pyproject.toml` (FastAPI, uvicorn, PyYAML). Install/sync once:

```sh
uv sync
cp -r data.example data   # starter registry; or set JANUS_DATA_DIR (see below)
make dev
make validate             # fails clearly if registry is empty/missing
```

All `make` Python targets use `uv run` so the project venv stays consistent. The project registry directory defaults to `./data` but is usually a separate checkout — set **`JANUS_DATA_DIR`** to its path (see [Project registry](#project-registry-data)).

## Dependencies

### Required (dashboard only)

Enough to run `make dev` and serve the link dashboard from `data/*.json`:

| Dependency | Notes |
|------------|--------|
| **Python** ≥3.11 | See `requires-python` in `pyproject.toml` |
| **[uv](https://github.com/astral-sh/uv)** | Recommended — `uv sync` then `uv run` / `make` targets. Plain `pip install -e .` works if you skip uv. |
| **PyPI packages** | `fastapi`, `uvicorn[standard]`, `pyyaml` — installed via `uv sync` |
| **Browser** | Dashboard is `index.html` + **Vue 3** loaded from jsDelivr CDN (no npm build step) |

No database, Docker, or systemd required for the core app.

### Project registry (`data/`)

Janus reads one JSON file per project from a **registry directory** (default `./data`, usually overridden via `JANUS_DATA_DIR`). This is personal/local configuration — not part of the public janus repo. Keep it in a private git repo (e.g. `~/dev/janus-data`) and point Janus at it:

```sh
export JANUS_DATA_DIR=~/dev/janus-data
```

All `mk/*.py` helpers and `server.py` honour the same variable. One Janus per machine; one registry dir. See `data.example/` for starter JSON shapes.

Only `project` is required per file; everything else is optional enrichment (see [Adding links](#adding-links)).

### Optional — feature integrations

Features are additive: if a tool is missing, that button/link/status simply does not work; the rest of the dashboard still loads.

| Tool | Used for | Install / config |
|------|----------|------------------|
| **git** | `meta.last_git_ts` on cards; `git for-each-repo --config=janus.repo`; new-project `git_init` | System package |
| **tmux** | Session existence checks; ops/swarm kill | System package |
| **[tmuxp](https://github.com/tmux-python/tmuxp)** | Ops up/down/bounce (`tmuxp load`); `make ops-up` / `ops-down` | `pip install tmuxp` or system package |
| **[nudge](https://github.com/cottrell/nudge)** / **`aiswarm`** | Multi-agent tmux swarms, babysit, autostart | **Optional.** Separate project — see [Optional: nudge / aiswarm](#optional-nudge--aiswarm-agent-swarms) |
| **[Backlog.md](https://github.com/MrLesk/Backlog.md)** CLI (`backlog`) | New-project `backlog init`; backlog browser links on cards | Install `backlog` binary; optional per project |
| **GitHub CLI** (`gh`) | New-project optional `gh repo create --push` | [cli.github.com](https://cli.github.com/); wizard step off by default (`gh_repo: false` in `mk/new_project.defaults.json`) |
| **graphify** | Graph icon + `/projects/{name}/graph` when `graphify-out/graph.html` exists under `local_path` | External pipeline; Janus only checks for output files |
| **ide-tools** (code-server, filebrowser, ttyd) | `ide_links: true` on a project → filebrowser / code-server icons | **Optional.** Only enabled per project via registry JSON; see [Optional IDE tools](#optional-ide-tools-security) |
| **MuxPod** (Android/iOS app) | Mobile tmux hop icons (`muxpod://` deep links) | Phone app + Deep Link ID setup — see [MuxPod Integration](#muxpod-integration) |

### Optional: nudge / aiswarm (agent swarms)

Swarm start/stop/babysit buttons and `make autostart` are **optional**. Without them, Janus is still a useful multi-project link + ops (tmuxp) homepage.

**[nudge](https://github.com/cottrell/nudge)** is a separate tool: config-driven tmux layouts for AI coding agents (Claude, Codex, Grok, Antigravity, …), with monitoring and “babysit” idle nudges. Janus does not vendor nudge; it shells out to the CLI when a project JSON has `tmuxp_swarm` set.

Install (from a nudge checkout):

```sh
git clone https://github.com/cottrell/nudge.git ~/dev/nudge
cd ~/dev/nudge && make install-aiswarm   # puts `aiswarm` on PATH
```

Janus resolves the CLI via `mk/paths.resolve_swarm_argv()`: prefer **`aiswarm` on `PATH`**, else `python3 ~/dev/nudge/swarm/cli.py`. Runtime state lives under `/tmp/nudge-swarm/<project>/`.

This repo’s `swarm/janus.yaml` is only a sample grid for developing Janus itself (uses auto-approve agent flags — trusted machines only).

### Optional IDE tools (security)

IDE helpers under `ide/` (code-server, filebrowser, ttyd) are **not required** for the dashboard. Janus only shows icons when a project JSON sets `"ide_links": true` — pure registry config, no special server mode.

Those services currently run **with no application auth**. That is intentional only if access is limited by a **private mesh/VPN and/or host firewall** (examples: Tailscale, Yggdrasil, WireGuard — interchangeable for this purpose). Janus does not depend on any of them. Do **not** expose IDE ports on the public internet as-is.

Details and service table: [`ide/SECURITY.md`](ide/SECURITY.md). Install is optional (`bash mk/install-ide-tools.sh`).

### Optional — new-project wizard (`make new-project`)

The wizard can scaffold a full project stack. Each step is optional (prompted, or toggled in `mk/new_project.defaults.json` / `--no-*` flags):

| Step | External command | Default |
|------|------------------|---------|
| `git_init` | `git init` | on |
| `backlog_init` | `backlog init {name} --defaults` | on |
| `swarm_init` | `aiswarm init {name}` (fallback: python `~/dev/nudge/swarm/cli.py`) | on |
| `ops_yaml` | writes `ops.yaml` (tmuxp + backlog browser port from 6430+) | on |
| `janus_register` | writes `data/{name}.json` locally | on |
| `janus_repo_list` | `git config --global --add janus.repo {path}` | on |
| `gh_repo` | `gh repo create … --push` | **off** |

Requires **git** for most flows; **backlog**, [nudge](https://github.com/cottrell/nudge)/`aiswarm`, and **gh** only if those steps are enabled.

### Hardcoded assumptions (fork/portability)

These are not yet env-configurable — worth knowing before forking:

| Assumption | Where |
|------------|--------|
| Project dev tree under `~/dev` | `server.py` `DEV_ROOT`, `mk/new_project.py` `dev_root` |
| Swarm CLI: `aiswarm` on `PATH`, else `~/dev/nudge/swarm/cli.py` | `mk/paths.py` `resolve_swarm_argv()` |
| IDE URLs `https://localhost:9321`, `http://localhost:9323`, `http://localhost:9322` | `server.py`, `ide/` ops configs |
| Babysit/swarm runtime under `/tmp/nudge-swarm/{project}/` | `server.py` status polling |
| Single host | Janus, tmux, and MuxPod SSH target on one machine — TASK-14 for multi-server |

## New project setup

Interactive CLI (`mk/new_project.py`) to scaffold a project directory, backlog, swarm, ops.yaml, and optional GitHub repo.

```sh
make new-project name=myproject
# or
uv run python mk/new_project.py myproject --description "One-liner"
```

### What you see

Header shows project slug, directory, and GitHub repo name (usually the same):

```
Project:     myproject
Path:        ~/dev/myproject
GitHub repo: myproject (same as project)
```

Each step shows what will run, then prompts:

```
Create GitHub repo 'myproject' (same as project name) and push from ~/dev/myproject
  run: cd ~/dev/myproject && gh repo create myproject --source=. --private --push
  [n/n/a/q]
```

- **Y** / Enter — run this step
- **n** — skip
- **a** — yes to this and all remaining steps
- **q** — abort

Non-interactive: `-y` / `--yes-all`, or per-step `--yes-gh-repo` / `--no-janus-register`, etc.

### Steps

| Step | What it does |
|------|----------------|
| `create_dir` | `mkdir` project directory (`~/dev/{name}` or `--path`) |
| `git_init` | `git init` in the **new project** (never in janus) |
| `readme` | Minimal `README.md` |
| `backlog_init` | `backlog init {name} --defaults` |
| `swarm_init` | `aiswarm init {name}` |
| `ops_yaml` | `ops.yaml` with auto-assigned backlog browser port (6430+) |
| `janus_register` | Writes `data/{name}.json` for the dashboard — **local only**; script does not commit to janus |
| `janus_repo_list` | `git config --global --add janus.repo {path}` |
| `gh_repo` | Initial commit if needed, then `gh repo create --private --push` |

Only the **new project** gets git commits and `gh push`. Commit `data/{name}.json` to janus yourself if you want it in the repo.

### Config

Defaults: `mk/new_project.defaults.json`. Copy and pass `--config ~/.config/janus/new-project.json` to override. Example — enable GitHub by default:

```json
{
  "steps": {
    "gh_repo": true
  },
  "gh_visibility": "private"
}
```

### Useful flags

| Flag | Purpose |
|------|---------|
| `--path DIR` | Project directory (default `~/dev/{name}`) |
| `--description TEXT` | One-liner for README and Janus card |
| `--gh-repo-name NAME` | GitHub repo name if different from project slug |
| `-y` / `--yes-all` | Accept all enabled steps without prompting |
| `--no-gh-repo` | Skip GitHub repo creation |
| `--yes-janus-register` | Force Janus registration |

### Dashboard UI

Click **+ new** in the Janus header (or use the CLI above). The wizard shows each step with the exact `run:` command, then **Yes / No / Yes to all / Quit** buttons. On desktop: **Y**, **N**, **A**, **Q**, or **Esc** work when the step view is focused (not while typing in a form field).

### Examples

```sh
# Interactive CLI (recommended first time)
make new-project name=foo

# Fully automatic, no GitHub
uv run python mk/new_project.py foo -y --no-gh-repo

# Custom path, create private GitHub repo
uv run python mk/new_project.py my-app --path ~/dev/experiments/my-app --yes-gh-repo
```

## Adding links

Drop a JSON file in `data/` named after your project (e.g. `data/myproject.json`):

```json
{
  "project": "myproject",
  "local_path": "~/dev/myproject",
  "github_url": "https://github.com/you/myproject",
  "tmuxp_ops": "myprojectops.yaml",
  "tmuxp_swarm": "swarm/myproject.yaml",
  "description": "optional one-liner",
  "links": [
    {
      "label": "Dev server",
      "url": "http://localhost:3000"
    },
    {
      "label": "API docs",
      "url": "http://localhost:8000/docs",
      "description": "FastAPI swagger"
    }
  ]
}
```

Always use `localhost` in URLs. The dashboard rewrites the host in the browser using `window.location.hostname`, so links work when you open the dashboard from localhost or via any remote host name (LAN, Tailscale, Yggdrasil, etc.).

Only `project` is required. `local_path`, `github_url`/`gitlab_url`, `tmuxp_ops`, and `tmuxp_swarm` are optional. `local_path` + urls are shown in the card meta; `tmuxp_*` are used for action buttons (and `mk/*.py`) but not currently shown in the meta row. `ops_up` and `swarm_up` default to `true` when their corresponding config keys are set, but can be explicitly set to `false` to disable. The dashboard re-reads `data/` on every request (no restart needed) and refreshes when you switch back to the tab.

## Notes

Git can keep a named list of local repos in config:

```sh
git config --global --add janus.repo ~/dev/myproject
```

Run a Git command across that list with:

```sh
git for-each-repo --config=janus.repo status --short --branch
git for-each-repo --config=janus.repo push
```

## MuxPod Integration

Janus supports mobile deep-linking to active tmux session(s) via [MuxPod](https://github.com/moezakura/mux-pod).

**Single-machine assumption:** Janus, all project tmux sessions, and the MuxPod SSH target are the same physical machine (the box where `make dev` runs). Multi-server setups are not supported yet — see backlog TASK-14.

MuxPod has **two separate settings** on each saved SSH connection:

| Field | What it is | Example |
|-------|------------|---------|
| **Host / address** | How SSH actually connects | Hostname, Tailscale name, Yggdrasil IPv6, LAN IP, … |
| **Deep Link ID** | Short nickname for `muxpod://` URLs only | Any string you choose (e.g. `dev-box`) |

The Deep Link ID is **any stable label** you pick in MuxPod — it does not have to be your hostname, IPv6, or SSH host. It is **not** the address you enter for SSH. MuxPod uses this ID only to match `muxpod://connect?server=…` links to the right saved connection.

**Setup:**

1. In MuxPod, edit your existing SSH connection. Leave host/port/username alone. Set **Deep Link ID** to any short label you like.
2. In Janus, set the **same** string in `data/janus.json` (`"muxpod_server_id": "…"`) or via `MUXPOD_SERVER_ID`. If unset, Janus falls back to `socket.gethostname()` on the machine where it runs.
3. On mobile, when tmux sessions are up, a terminal icon appears on each card. The tooltip shows session name and `server …` (the Deep Link ID Janus sends).

**"Server not found" in MuxPod:** the `server=` in the link does not match any connection's Deep Link ID (MuxPod also falls back to connection display name, case-insensitive). The SSH host address is irrelevant here. Fix: make Deep Link ID and `muxpod_server_id` identical.

## For agents

To register a dev server from another project, write a file into the Janus registry dir (`JANUS_DATA_DIR` or `./data`):

```sh
REG="${JANUS_DATA_DIR:-./data}"
cat > "$REG/$(basename $PWD).json" <<'EOF'
{
  "project": "myproject",
  "links": [{"label": "Dev server", "url": "http://localhost:PORT"}]
}
EOF
```
