import json
import os
import shlex
import socket
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from mk.new_project import (
    STEP_KEYS,
    build_step_schema,
    execute_steps,
    prepare_project,
)
from mk.paths import (
    get_data_dir,
    get_dev_root,
    get_ide_code_server_url,
    get_ide_filebrowser_url,
    get_listen_host,
    get_listen_port,
    resolve_swarm_argv,
)

app = FastAPI()
DATA_DIR = get_data_dir()

# Per-source mtime caches for expensive enrichments (git, graphify, yaml).
_git_cache = {}
_graphify_cache = {}
_session_cache = {}


def _get_muxpod_server_id():
    if env_val := os.environ.get("MUXPOD_SERVER_ID"):
        return env_val
    janus_json = DATA_DIR / "janus.json"
    if janus_json.is_file():
        try:
            d = json.loads(janus_json.read_text())
            if val := d.get("muxpod_server_id"):
                return val
        except Exception:
            pass
    return socket.gethostname()


def _muxpod_link(server_id, session_name, window=None, pane=None):
    query = {"server": server_id}
    if session_name:
        query["session"] = session_name
    if window:
        query["window"] = window
    if pane is not None:
        query["pane"] = pane
    return f"muxpod://connect?{urllib.parse.urlencode(query)}"


def _git_cache_key(repo_path):
    for name in ("logs/HEAD", "HEAD"):
        p = repo_path / ".git" / name
        if p.is_file():
            try:
                return p.stat().st_mtime_ns
            except Exception:
                pass
    return None


def _graphify_cache_key(gout):
    parts = []
    for name in ("graph.json", "cost.json", "GRAPH_REPORT.md"):
        f = gout / name
        if f.is_file():
            try:
                parts.append((name, f.stat().st_mtime_ns, f.stat().st_size))
            except Exception:
                pass
    if parts:
        return tuple(parts)
    try:
        return ("dir", gout.stat().st_mtime_ns)
    except Exception:
        return None


def _get_session_name(project, kind):
    config_key = f"tmuxp_{kind}"
    if not project.get("local_path") or not project.get(config_key):
        return None
    try:
        root = Path(project["local_path"]).expanduser().resolve()
        config = (root / project[config_key]).resolve()
        if not config.is_file():
            return None
        config.relative_to(root)
        cache_key = str(config)
        sig = config.stat().st_mtime_ns
        hit = _session_cache.get(cache_key)
        if hit and hit[0] == sig:
            return hit[1]
        data = yaml.safe_load(config.read_text()) or {}
        name = data.get("session_name")
        _session_cache[cache_key] = (sig, name)
        return name
    except Exception:
        return None


def _dev_root_str() -> str:
    return str(get_dev_root())


def _ide_links(p):
    local_path = p.get("local_path", "")
    if not local_path:
        return []
    abs_path = str(Path(local_path).expanduser().resolve())
    dev_root = _dev_root_str()
    ide_fb = get_ide_filebrowser_url()
    ide_cs = get_ide_code_server_url()
    links = []
    if abs_path.startswith(dev_root + "/") or abs_path == dev_root:
        rel = abs_path[len(dev_root):]
        links.append({"label": "filebrowser", "url": f"{ide_fb}/files{rel}", "kind": "ide"})
    links.append({"label": "code-server", "url": f"{ide_cs}/?folder={abs_path}", "kind": "ide"})
    return links


def _filebrowser_link(path):
    abs_path = str(path.resolve())
    dev_root = _dev_root_str()
    if abs_path.startswith(dev_root + "/") or abs_path == dev_root:
        rel = abs_path[len(dev_root):]
        return f"{get_ide_filebrowser_url()}/files{rel}"
    return None


def _config_links(p):
    if not p.get("local_path"):
        return {}
    root = Path(p["local_path"]).expanduser().resolve()
    links = {}
    for kind in ("ops", "swarm"):
        key = f"tmuxp_{kind}"
        if not p.get(key):
            continue
        config = (root / p[key]).resolve()
        try:
            config.relative_to(root)
        except ValueError:
            continue
        url = _filebrowser_link(config)
        if url:
            links[key] = url
    return links


def _get_last_git_ts(local_path):
    if not local_path:
        return None
    try:
        repo = Path(local_path).expanduser().resolve()
        cache_key = str(repo)
        sig = _git_cache_key(repo)
        hit = _git_cache.get(cache_key)
        if hit and hit[0] == sig:
            return hit[1]
        res = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%ct", "--", "."],
            capture_output=True,
            text=True,
            timeout=3,
        )
        ts = None
        if res.returncode == 0 and res.stdout.strip():
            ts = int(res.stdout.strip())
        if sig is not None:
            _git_cache[cache_key] = (sig, ts)
        return ts
    except Exception:
        pass
    return None


def _get_graphify_info(local_path):
    if not local_path:
        return {"has_run": False}
    try:
        root = Path(local_path).expanduser().resolve()
        gout = root / "graphify-out"
        if not gout.is_dir():
            return {"has_run": False}
        cache_key = str(root)
        sig = _graphify_cache_key(gout)
        hit = _graphify_cache.get(cache_key)
        if hit and hit[0] == sig:
            return hit[1]
        info = {"has_run": True}
        gjson = gout / "graph.json"
        if gjson.is_file():
            # Presence only — parsing multi-MB graph.json on every load is too slow.
            # Node/edge counts belong in cost.json sidecar or a lazy meta endpoint if needed.
            info["graph_mtime"] = int(gjson.stat().st_mtime)
        costf = gout / "cost.json"
        if costf.is_file():
            try:
                cd = json.loads(costf.read_text())
                runs = cd.get("runs") or []
                if runs:
                    info["last_run"] = runs[-1].get("date")
            except Exception:
                pass
        report = gout / "GRAPH_REPORT.md"
        if report.is_file():
            info["report_mtime"] = int(report.stat().st_mtime)
        if sig is not None:
            _graphify_cache[cache_key] = (sig, info)
        return info
    except Exception:
        return {"has_run": False}


# Schema for project["meta"] (canned values from data/*.json + live values merged in).
# Purpose: support multiple AI (and other) high-level descriptions per project + graphify info
# without re-summarizing every time. Not displayed in current UI. Intended for workflow triggers.
#
# Example canned structure you can put in a data/foo.json:
#   "meta": {
#     "summaries": [
#       {
#         "source": "claude",                    # or "agy", "codex", "grok", "graphify", …
#         "model": "haiku",                      # optional finer grain
#         "kind": "high_level_intent",           # orchestrator-facing (skill: enrich-meta)
#         "content": "This project orchestrates ...",
#         "generated_at": "2026-07-09T12:00:00Z",
#         "based_on": ["description", "README.md"]
#       },
#       {
#         "source": "graphify",
#         "kind": "god_nodes",
#         "content": "SwarmConfig (49 edges), load_config() (29), ...",
#         "generated_at": "...",
#         "based_on": ["graphify-out/GRAPH_REPORT.md"]
#       }
#     ],
#     "preferred_summary_source": "claude"   # hint for "use any" vs specific
#   }
#
# Live keys that get merged (last_git_ts, graphify) coexist at the same level.
#
# "Any summary exists?" trigger condition (for workflows that want to skip if something is present):
#   m = p.get("meta") or {}
#   has_any = bool(m.get("summaries")) or bool(m.get("graphify"))
#   # (also tolerates legacy flat "ai_summary")
#
# Multiple sources/agents are explicitly supported; just append more objects to summaries[].


def has_any_ai_summary(meta):
    """True if there is at least one canned AI/graphify summary/description or live graphify run.
    Workflows can use this (or copy the logic) as a 'check for any' condition before re-summarizing.
    """
    if not meta:
        return False
    if meta.get("summaries"):
        return True
    if meta.get("ai_summary") or meta.get("ai_description"):
        return True
    g = meta.get("graphify") or {}
    if g.get("has_run"):
        return True
    return False


def _enrich_project(p, server_id):
    if p.get("ide_links"):
        p["links"] = _ide_links(p) + (p.get("links") or [])
    config_links = _config_links(p)
    if config_links:
        p["config_links"] = config_links

    muxpod_links = {}
    tmux_sessions = {}
    ops_session = _get_session_name(p, "ops")
    if ops_session:
        tmux_sessions["ops"] = ops_session
        muxpod_links["ops"] = _muxpod_link(server_id, ops_session)
    swarm_session = _get_session_name(p, "swarm")
    if swarm_session:
        tmux_sessions["swarm"] = swarm_session
        muxpod_links["swarm"] = _muxpod_link(server_id, swarm_session)
    if tmux_sessions:
        p["tmux_sessions"] = tmux_sessions
    if muxpod_links:
        muxpod_links["server"] = server_id
        p["muxpod_links"] = muxpod_links

    lp = p.get("local_path")
    live = {}
    ts = _get_last_git_ts(lp)
    if ts:
        live["last_git_ts"] = ts
    ginfo = _get_graphify_info(lp)
    if ginfo.get("has_run"):
        live["graphify"] = ginfo
    if live:
        canned = p.get("meta") or {}
        p["meta"] = {**canned, **live}
    return p


@app.get("/api/links")
def get_links():
    projects = []
    for f in DATA_DIR.glob("*.json"):
        try:
            projects.append(json.loads(f.read_text()))
        except Exception:
            pass

    server_id = _get_muxpod_server_id()
    if len(projects) > 1:
        with ThreadPoolExecutor(max_workers=min(8, len(projects))) as pool:
            result = list(pool.map(lambda p: _enrich_project(p, server_id), projects))
    else:
        result = [_enrich_project(p, server_id) for p in projects]

    result.sort(key=lambda x: x.get("project", ""))
    return result


def load_project(project):
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if data.get("project") == project:
            return data
    raise HTTPException(status_code=404, detail="project not found")


def resolve_config(project, kind):
    config_key = f"tmuxp_{kind}"
    if not project.get("local_path") or not project.get(config_key):
        raise HTTPException(status_code=400, detail=f"{config_key} is not configured")

    root = Path(project["local_path"]).expanduser().resolve()
    config = (root / project[config_key]).resolve()
    if not config.is_file():
        raise HTTPException(status_code=404, detail=f"config not found: {config}")
    try:
        config.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=400, detail="config must be below local_path")
    return root, config


def session_name(config):
    try:
        data = yaml.safe_load(config.read_text()) or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to parse {config}: {e}")
    name = data.get("session_name")
    if not name:
        raise HTTPException(status_code=400, detail=f"session_name missing in {config}")
    return name


def babysit_configured(config):
    try:
        return bool(get_babysit_enabled_panes(config))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to parse {config}: {e}")


def tmux_session_exists(name):
    result = subprocess.run(
        ["tmux", "has-session", "-t", f"={name}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def run_command(args, cwd):
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=90,
            check=False,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"command not found: {e.filename}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="command timed out")

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "command failed").strip()
        raise HTTPException(status_code=500, detail=detail)
    return {
        "ok": True,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def query_monitor_socket(socket_path):
    if not socket_path or not Path(socket_path).is_socket():
        return "unreachable"
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            s.connect(str(socket_path))
            s.sendall(b"status\n")
            res_str = s.recv(1024).decode().strip()
            try:
                return json.loads(res_str)
            except Exception:
                return res_str
    except Exception:
        return "unreachable"

def get_babysit_enabled_panes(config_path: Path) -> set[str]:
    try:
        data = yaml.safe_load(config_path.read_text()) or {}
    except Exception:
        return set()
    
    enabled_panes = set()
    for win_idx, window in enumerate(data.get("windows") or []):
        if not isinstance(window, dict):
            continue
        for pane_idx, pane in enumerate(window.get("panes") or []):
            if not isinstance(pane, dict):
                continue
            nudge = pane.get("nudge") or {}
            babysit = nudge.get("babysit") or {}
            if isinstance(babysit, dict) and bool(babysit.get("enabled", False)):
                enabled_panes.add(f"{win_idx}.{pane_idx}")
    return enabled_panes

def babysit_status(root, config):
    try:
        name = session_name(config)
    except Exception as e:
        return {"state": "errored", "up": False, "error": f"failed to parse config: {e}"}

    if not tmux_session_exists(name):
        return {"state": "stopped", "up": False}

    runtime_dir = Path("/tmp/nudge-swarm") / name
    runtime_file = runtime_dir / "runtime.json"
    if not runtime_file.is_file():
        return {"state": "stopped", "up": False}

    try:
        runtime_data = json.loads(runtime_file.read_text())
    except Exception as e:
        return {"state": "errored", "up": False, "error": f"failed to parse runtime map: {e}"}

    enabled_panes = get_babysit_enabled_panes(config)
    if not enabled_panes:
        return {"state": "off", "up": False}

    babysit_panes = {}
    for pane_id in enabled_panes:
        pane_key = pane_id.replace(".", "-")
        pid_file = runtime_dir / f"babysit-{pane_key}.pid"
        spec_file = runtime_dir / f"babysit-{pane_key}.json"

        pane_state = "stopped"
        if pid_file.is_file():
            try:
                pid = int(pid_file.read_text().strip())
                if is_pid_running(pid):
                    if spec_file.is_file():
                        try:
                            spec = json.loads(spec_file.read_text())
                        except Exception:
                            spec = {}
                        has_prompts = bool(spec.get("long_prompt") or spec.get("short_prompt"))
                        pane_state = "on" if has_prompts else "not started"
                    else:
                        pane_state = "not started"
                else:
                    pane_state = "stale"
            except Exception:
                pane_state = "stale"
        
        babysit_panes[pane_id] = pane_state

    if any(s == "stale" for s in babysit_panes.values()):
        return {"state": "errored", "up": False, "error": "one or more workers are stale"}

    if any(s == "on" for s in babysit_panes.values()):
        return {"state": "running", "up": True}

    return {"state": "stopped", "up": False}

def swarm_panes_status(root, config):
    try:
        name = session_name(config)
    except Exception:
        return {}
    runtime_file = Path("/tmp/nudge-swarm") / name / "runtime.json"
    if not runtime_file.is_file():
        return {}
    try:
        runtime_data = json.loads(runtime_file.read_text())
    except Exception:
        return {}
    
    panes_status = {}
    for pane_id, pane_info in runtime_data.get("panes", {}).items():
        sock = pane_info.get("socket")
        panes_status[pane_id] = {
            "state": query_monitor_socket(sock)
        }
    return panes_status

@app.get("/api/status")
def status():
    result = {}
    for project in get_links():
        project_status = {}
        for kind in ("ops", "swarm"):
            if not project.get("local_path") or not project.get(f"tmuxp_{kind}"):
                continue
            try:
                root, config = resolve_config(project, kind)
                name = session_name(config)
                project_status[kind] = {
                    "session": name,
                    "up": tmux_session_exists(name),
                }
                if kind == "swarm" and project_status[kind]["up"]:
                    project_status[kind]["panes"] = swarm_panes_status(root, config)
            except HTTPException as e:
                project_status[kind] = {
                    "error": e.detail,
                    "up": False,
                }
        if project.get("local_path") and project.get("tmuxp_swarm"):
            try:
                root, config = resolve_config(project, "swarm")
                configured = babysit_configured(config)
                if configured:
                    project_status["babysit"] = babysit_status(root, config)
                    project_status["babysit"]["configured"] = True
                else:
                    project_status["babysit"] = {
                        "state": "off",
                        "up": False,
                        "configured": False,
                    }
            except HTTPException as e:
                project_status["babysit"] = {
                    "state": "errored",
                    "error": e.detail,
                    "up": False,
                    "configured": False,
                }
        if project_status:
            result[project["project"]] = project_status
    return result


@app.post("/api/projects/{project}/ops/up")
def ops_up(project: str):
    root, config = resolve_config(load_project(project), "ops")
    return run_command(["tmuxp", "load", "-d", str(config)], root)


@app.post("/api/projects/{project}/ops/down")
def ops_down(project: str):
    root, config = resolve_config(load_project(project), "ops")
    name = session_name(config)
    return run_command(["tmux", "kill-session", "-t", f"={name}"], root)


@app.post("/api/projects/{project}/ops/bounce")
def ops_bounce(project: str):
    root, config = resolve_config(load_project(project), "ops")
    name = session_name(config)
    cmd = f"tmux kill-session -t '={name}' 2>/dev/null; sleep 1; tmuxp load -d {config}"
    subprocess.Popen(["bash", "-c", cmd], cwd=root, start_new_session=True)
    return {"ok": True}


def _swarm_argv(*args: str) -> list[str]:
    base = resolve_swarm_argv()
    if not base:
        raise HTTPException(
            status_code=500,
            detail="swarm CLI not found: install aiswarm on PATH (or set JANUS_NUDGE_CLI)",
        )
    return [*base, *args]


@app.post("/api/projects/{project}/swarm/up")
def swarm_up(project: str):
    root, config = resolve_config(load_project(project), "swarm")
    return run_command(_swarm_argv("start", str(config)), root)


@app.post("/api/projects/{project}/swarm/down")
def swarm_down(project: str):
    root, config = resolve_config(load_project(project), "swarm")
    # aiswarm stop tears down tasks/babysit/comms workers + tmux (not bare kill-session)
    return run_command(_swarm_argv("stop", str(config)), root)


@app.post("/api/projects/{project}/swarm/bounce")
def swarm_bounce(project: str):
    root, config = resolve_config(load_project(project), "swarm")
    stop_argv = _swarm_argv("stop", str(config))
    start_argv = _swarm_argv("start", str(config))
    cmd = (
        " ".join(shlex.quote(a) for a in stop_argv)
        + " 2>/dev/null; sleep 1; "
        + " ".join(shlex.quote(a) for a in start_argv)
    )
    subprocess.Popen(["bash", "-c", cmd], cwd=root, start_new_session=True)
    return {"ok": True}


@app.post("/api/projects/{project}/babysit/start")
def babysit_start(project: str):
    root, config = resolve_config(load_project(project), "swarm")
    return run_command(_swarm_argv("babysit", "start", str(config)), root)


@app.post("/api/projects/{project}/babysit/stop")
def babysit_stop(project: str):
    root, config = resolve_config(load_project(project), "swarm")
    return run_command(_swarm_argv("babysit", "stop", str(config)), root)

@app.get("/projects/{project}/graph", response_class=HTMLResponse)
def project_graph(project: str):
    p = load_project(project)
    lp = p.get("local_path")
    if not lp:
        raise HTTPException(status_code=404, detail="local_path not configured for this project")
    root = Path(lp).expanduser().resolve()
    graph_html_path = root / "graphify-out" / "graph.html"
    if not graph_html_path.is_file():
        raise HTTPException(status_code=404, detail="graph.html not found under graphify-out for this project")
    try:
        content = graph_html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to read graph.html: {e}")


class NewProjectRequest(BaseModel):
    name: str
    description: str = ""
    path: str | None = None
    gh_repo_name: str | None = None
    steps: dict[str, bool] = Field(default_factory=dict)


def _merge_step_decisions(defaults: dict, chosen: dict) -> dict:
    decisions = dict(defaults)
    unknown = set(chosen) - set(STEP_KEYS)
    if unknown:
        raise HTTPException(status_code=400, detail=f"unknown steps: {sorted(unknown)}")
    for key in STEP_KEYS:
        if key in chosen:
            decisions[key] = bool(chosen[key])
    return decisions


@app.get("/api/new-project/schema")
def new_project_schema(
    name: str,
    description: str = "",
    path: str | None = None,
    gh_repo_name: str | None = None,
):
    try:
        plan = prepare_project(
            name,
            path=path,
            description=description,
            gh_repo_name=gh_repo_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    steps = build_step_schema(plan["ctx"], plan["cfg"])
    return {
        "name": plan["name"],
        "path": plan["local_path"],
        "gh_repo_name": plan["gh_repo_name"],
        "steps": steps,
        "step_keys": list(STEP_KEYS),
    }


@app.post("/api/new-project")
def new_project_create(body: NewProjectRequest):
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="name is required")
    try:
        plan = prepare_project(
            body.name,
            path=body.path,
            description=body.description,
            gh_repo_name=body.gh_repo_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    decisions = _merge_step_decisions(plan["cfg"]["steps"], body.steps)
    log = []
    try:
        result = execute_steps(plan, decisions, log=log)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "log": log},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "log": log},
        )
    return result


# No StaticFiles mount — index is served as a string. These few root assets
# need an explicit route so <img src="/logo.png"> / favicon links work.
@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon-32.png", include_in_schema=False)
@app.get("/logo.png", include_in_schema=False)
def root_asset(request: Request):
    name = request.url.path.lstrip("/")
    path = Path(__file__).parent / name
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "index.html").read_text()


if __name__ == "__main__":
    import argparse

    # CLI preferred for listen bind (single process). Env JANUS_HOST/JANUS_PORT
    # still work as defaults when flags omitted (make/systemd).
    p = argparse.ArgumentParser(description="Janus local dev homepage")
    p.add_argument(
        "--host",
        default=get_listen_host(),
        help=f"bind address (default {get_listen_host()!r}, env JANUS_HOST)",
    )
    p.add_argument(
        "--port",
        type=int,
        default=get_listen_port(),
        help=f"listen port (default {get_listen_port()}, env JANUS_PORT)",
    )
    p.add_argument("--no-reload", action="store_true", help="disable uvicorn reload")
    args = p.parse_args()
    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        reload_excludes=[".venv/*", "backlog/*", "graphify-out/*"],
    )

