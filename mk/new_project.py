#!/usr/bin/env python3
"""Interactive new-project setup for Janus.

Each step can be accepted/declined interactively, pre-set via config, or
overridden with --yes-<step> / --no-<step>. Use --yes-all to skip prompts.

Only the new project directory gets git init / commits / gh push. Janus
registration writes data/<name>.json locally — it is never committed to the
janus repo by this script.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    from mk.paths import JANUS_ROOT, get_data_dir
except ImportError:
    from paths import JANUS_ROOT, get_data_dir

JANUS_DIR = JANUS_ROOT
DEFAULTS_PATH = Path(__file__).parent / "new_project.defaults.json"
NUDGE_CLI = Path.home() / "dev/nudge/swarm/cli.py"

STEP_KEYS = (
    "create_dir",
    "git_init",
    "readme",
    "backlog_init",
    "swarm_init",
    "ops_yaml",
    "janus_register",
    "janus_repo_list",
    "gh_repo",
)


def say(msg, log=None):
    text = str(msg)
    print(text)
    if log is not None:
        log.append(text)


def step_context(name, project_path, local_path, backlog_port, gh_visibility, gh_repo_name):
    return {
        "name": name,
        "project_path": str(project_path),
        "local_path": local_path,
        "backlog_port": backlog_port,
        "gh_visibility": gh_visibility,
        "gh_repo_name": gh_repo_name,
        "janus_json": str(get_data_dir() / f"{name}.json"),
    }


def describe_step(key, ctx):
    d = ctx["local_path"]
    name = ctx["name"]
    project_path = ctx["project_path"]
    if key == "create_dir":
        return f"Create directory {d}", f"mkdir -p {project_path}"
    if key == "git_init":
        return f"Initialize git in {d} (not janus)", f"cd {d} && git init"
    if key == "readme":
        return f"Create {d}/README.md", f"write {d}/README.md"
    if key == "backlog_init":
        return f"Initialize Backlog in {d}", f"cd {d} && backlog init {name} --defaults"
    if key == "swarm_init":
        return (
            f"Initialize AI swarm in {d}",
            f"cd {d} && python {NUDGE_CLI} init {name} --root {project_path}",
        )
    if key == "ops_yaml":
        port = ctx["backlog_port"]
        return (
            f"Create {d}/ops.yaml (backlog browser port {port})",
            f"write {d}/ops.yaml  # backlog browser -p {port}",
        )
    if key == "janus_register":
        return (
            f"Register '{name}' in Janus ({ctx['janus_json']}) — local only, do not commit to janus",
            f"write {ctx['janus_json']}",
        )
    if key == "janus_repo_list":
        return (
            f"Add {d} to global git config janus.repo",
            f"git config --global --add janus.repo {project_path}",
        )
    if key == "gh_repo":
        repo = ctx["gh_repo_name"]
        vis = ctx["gh_visibility"]
        same = "same as project name" if repo == name else f"project name is '{name}'"
        return (
            f"Create GitHub repo '{repo}' ({same}) and push from {d}",
            f"cd {d} && gh repo create {repo} --source=. --{vis} --push",
        )
    return key, key


def format_prompt(key, ctx):
    title, cmd = describe_step(key, ctx)
    return f"{title}\n  run: {cmd}"


def load_config(path=None):
    cfg = json.loads(DEFAULTS_PATH.read_text())
    if path:
        user = json.loads(Path(path).expanduser().read_text())
        if "steps" in user:
            cfg["steps"].update(user["steps"])
        for key in ("dev_root", "backlog_port_start", "gh_visibility"):
            if key in user:
                cfg[key] = user[key]
    return cfg


def display_path(path):
    path = Path(path).expanduser().resolve()
    try:
        rel = path.relative_to(Path.home())
        return f"~/{rel}"
    except ValueError:
        return str(path)


def slugify(name):
    return name.replace(" ", "-").lower()


def allocate_backlog_port(start=6430):
    ports = set()
    for f in get_data_dir().glob("*.json"):
        try:
            d = json.loads(f.read_text())
            for link in d.get("links", []):
                url = link.get("url", "")
                if "localhost:" in url:
                    port_str = url.split("localhost:")[-1].split("/")[0]
                    if port_str.isdigit():
                        ports.add(int(port_str))
        except Exception:
            pass
    port = start
    while port in ports:
        port += 1
    return port


def prepare_project(name, path=None, description="", gh_repo_name=None, config_path=None):
    cfg = load_config(config_path)
    slug = slugify(name)
    if not slug:
        raise ValueError("project name is required")
    dev_root = Path(cfg["dev_root"]).expanduser()
    if path:
        project_path = Path(path).expanduser().resolve()
    else:
        project_path = (dev_root / slug).resolve()
    repo_name = slugify(gh_repo_name) if gh_repo_name else slug
    backlog_port = allocate_backlog_port(cfg.get("backlog_port_start", 6430))
    gh_visibility = cfg.get("gh_visibility", "private")
    local_path = display_path(project_path)
    ctx = step_context(slug, project_path, local_path, backlog_port, gh_visibility, repo_name)
    return {
        "name": slug,
        "project_path": project_path,
        "local_path": local_path,
        "description": description or "",
        "gh_repo_name": repo_name,
        "backlog_port": backlog_port,
        "gh_visibility": gh_visibility,
        "ctx": ctx,
        "cfg": cfg,
    }


def build_step_schema(ctx, cfg):
    steps = []
    for key in STEP_KEYS:
        title, cmd = describe_step(key, ctx)
        steps.append({
            "key": key,
            "title": title,
            "cmd": cmd,
            "default": bool(cfg["steps"].get(key, False)),
        })
    return steps


def prompt_step(prompt_text, default, yes_all):
    if yes_all:
        return default
    if not sys.stdin.isatty():
        return default
    while True:
        hint = "Y" if default else "n"
        ans = input(f"{prompt_text}\n  [{hint}/n/a/q] ").strip().lower()
        if ans in ("", "y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        if ans in ("a", "all"):
            return "all"
        if ans in ("q", "quit"):
            print("Aborted.")
            sys.exit(0)
        print("  Enter y/n, a=yes-to-all, or q=quit")


def resolve_steps(cfg, args, ctx):
    decisions = dict(cfg["steps"])
    for key in STEP_KEYS:
        flag_yes = getattr(args, f"yes_{key}", False)
        flag_no = getattr(args, f"no_{key}", False)
        if flag_yes and flag_no:
            raise SystemExit(f"Cannot set both --yes-{key} and --no-{key}")
        if flag_yes:
            decisions[key] = True
        elif flag_no:
            decisions[key] = False

    yes_all = args.yes_all
    for key in STEP_KEYS:
        if getattr(args, f"yes_{key}", False) or getattr(args, f"no_{key}", False):
            continue
        if args.yes_all:
            continue
        if not sys.stdin.isatty():
            continue
        result = prompt_step(format_prompt(key, ctx), decisions.get(key, False), yes_all)
        if result == "all":
            yes_all = True
            decisions[key] = True
        else:
            decisions[key] = result
    return decisions


def step_create_dir(project_path, log=None):
    project_path.mkdir(parents=True, exist_ok=True)
    say(f"  Directory ready: {project_path}", log)


def step_git_init(project_path, log=None):
    if (project_path / ".git").exists():
        say("  Git already initialized — skipping", log)
        return
    subprocess.run(["git", "init"], cwd=project_path, check=True)
    say("  git init", log)


def step_readme(project_path, name, description, log=None):
    readme_path = project_path / "README.md"
    if readme_path.exists():
        say("  README.md already exists — skipping", log)
        return
    readme_path.write_text(
        f"# {name}\n\n{description or 'A new project managed by Janus.'}\n"
    )
    say("  Created README.md", log)


def step_backlog_init(project_path, name, log=None):
    if (project_path / "backlog").exists():
        say("  backlog/ already exists — skipping", log)
        return
    subprocess.run(["backlog", "init", name, "--defaults"], cwd=project_path, check=True)
    say("  backlog init", log)


def step_swarm_init(project_path, name, log=None):
    if (project_path / "swarm").exists():
        say("  swarm/ already exists — skipping", log)
        return
    if not NUDGE_CLI.is_file():
        say(f"  Warning: nudge CLI not found at {NUDGE_CLI} — skipping", log)
        return
    subprocess.run(
        [sys.executable, str(NUDGE_CLI), "init", name, "--root", str(project_path)],
        check=True,
    )
    say("  nudge swarm init", log)


def step_ops_yaml(project_path, name, backlog_port, log=None):
    ops_path = project_path / "ops.yaml"
    if ops_path.exists():
        say("  ops.yaml already exists — skipping write", log)
        return backlog_port
    ops_path.write_text(
        f"""session_name: ops-{name}
start_directory: ./
windows:
  - window_name: dev
    panes:
      - bash
  - window_name: backlog-browser
    panes:
      - backlog browser -p {backlog_port} --no-open
"""
    )
    say(f"  Created ops.yaml (backlog port {backlog_port})", log)
    return backlog_port


def read_backlog_port_from_ops(project_path):
    ops_path = project_path / "ops.yaml"
    if not ops_path.is_file():
        return None
    for line in ops_path.read_text().splitlines():
        if "backlog browser -p" in line:
            parts = line.split("-p", 1)[-1].strip().split()
            if parts and parts[0].isdigit():
                return int(parts[0])
    return None


def build_janus_config(name, local_path, description, backlog_port, github_url=None):
    cfg = {
        "project": name,
        "local_path": local_path,
        "tmuxp_ops": "ops.yaml",
        "tmuxp_swarm": f"swarm/{name}.yaml",
        "description": description,
        "ide_links": True,
        "links": [
            {"label": "Backlog", "url": f"http://localhost:{backlog_port}"}
        ],
    }
    if github_url:
        cfg["github_url"] = github_url
    return cfg


def step_janus_register(name, local_path, description, backlog_port, github_url=None, log=None):
    janus_json = get_data_dir() / f"{name}.json"
    if janus_json.exists():
        say(f"  {janus_json.name} already exists — skipping", log)
        return
    cfg = build_janus_config(name, local_path, description, backlog_port, github_url)
    janus_json.write_text(json.dumps(cfg, indent=2) + "\n")
    say(f"  Wrote {janus_json}", log)
    say("  Note: this file is local only — do not commit it to the janus repo unless you intend to.", log)


def update_janus_github_url(name, github_url, log=None):
    janus_json = get_data_dir() / f"{name}.json"
    if not janus_json.is_file():
        return
    cfg = json.loads(janus_json.read_text())
    cfg["github_url"] = github_url
    janus_json.write_text(json.dumps(cfg, indent=2) + "\n")
    say(f"  Updated {janus_json.name} with github_url", log)


def step_janus_repo_list(project_path, log=None):
    subprocess.run(
        ["git", "config", "--global", "--add", "janus.repo", str(project_path)],
        check=True,
    )
    say("  Added to git config janus.repo", log)


def step_gh_repo(project_path, repo_name, visibility, log=None):
    if not shutil_which("gh"):
        say("  Warning: gh CLI not found — skipping GitHub repo creation", log)
        return None
    status = subprocess.run(["git", "status", "--porcelain"], cwd=project_path, capture_output=True, text=True)
    if status.stdout.strip():
        subprocess.run(["git", "add", "-A"], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_path, check=True)
        say("  Committed initial project files", log)
    elif not (project_path / ".git").exists():
        say("  Warning: no git repo — run git_init first", log)
        return None
    else:
        log_check = subprocess.run(["git", "log", "-1"], cwd=project_path, capture_output=True)
        if log_check.returncode != 0:
            subprocess.run(["git", "add", "-A"], cwd=project_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit", "--allow-empty"], cwd=project_path, check=True)
            say("  Created empty initial commit", log)

    cmd = ["gh", "repo", "create", repo_name, "--source=.", f"--{visibility}", "--push"]
    subprocess.run(cmd, cwd=project_path, check=True)
    remote = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True,
    )
    url = remote.stdout.strip()
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.removeprefix("git@github.com:").removesuffix(".git")
    say(f"  GitHub repo created: {url}", log)
    return url


def shutil_which(cmd):
    from shutil import which
    return which(cmd)


def execute_steps(plan, decisions, log=None):
    """Run approved setup steps. Returns result dict for CLI or API."""
    log = [] if log is None else log
    name = plan["name"]
    project_path = plan["project_path"]
    local_path = plan["local_path"]
    description = plan["description"]
    gh_repo_name = plan["gh_repo_name"]
    gh_visibility = plan["gh_visibility"]
    ctx = plan["ctx"]
    backlog_port = plan["backlog_port"]
    github_url = None

    for key in STEP_KEYS:
        if not decisions.get(key):
            continue
        title, cmd = describe_step(key, ctx)
        say(f"→ {title}", log)
        say(f"  run: {cmd}", log)

        if key == "create_dir":
            step_create_dir(project_path, log)
        elif key == "git_init":
            step_git_init(project_path, log)
        elif key == "readme":
            step_readme(project_path, name, description, log)
        elif key == "backlog_init":
            step_backlog_init(project_path, name, log)
        elif key == "swarm_init":
            step_swarm_init(project_path, name, log)
        elif key == "ops_yaml":
            existing = read_backlog_port_from_ops(project_path)
            if existing:
                backlog_port = existing
            step_ops_yaml(project_path, name, backlog_port, log)
        elif key == "janus_register":
            existing = read_backlog_port_from_ops(project_path)
            if existing:
                backlog_port = existing
            step_janus_register(name, local_path, description, backlog_port, github_url, log)
        elif key == "janus_repo_list":
            step_janus_repo_list(project_path, log)
        elif key == "gh_repo":
            github_url = step_gh_repo(project_path, gh_repo_name, gh_visibility, log)
            if github_url and decisions.get("janus_register"):
                update_janus_github_url(name, github_url, log)

    reminder = None
    if decisions.get("janus_register"):
        reminder = f"data/{name}.json is local; only commit it to janus if you want it shared."

    say(f"Done — project '{name}' at {project_path}", log)
    if reminder:
        say(f"Reminder: {reminder}", log)

    return {
        "ok": True,
        "name": name,
        "path": local_path,
        "project_path": str(project_path),
        "github_url": github_url,
        "log": log,
        "reminder": reminder,
    }


def build_parser():
    parser = argparse.ArgumentParser(description="Interactive new-project setup for Janus.")
    parser.add_argument("name", help="Project name (slugified: spaces → hyphens, lowercased)")
    parser.add_argument("--path", help="Project directory (default: ~/dev/{name})")
    parser.add_argument("--description", default="", help="One-line project description")
    parser.add_argument(
        "--gh-repo-name",
        help="GitHub repo name (default: same as project slug). Directory name is unchanged.",
    )
    parser.add_argument("--config", help="JSON config overriding mk/new_project.defaults.json")
    parser.add_argument("-y", "--yes-all", action="store_true", help="Accept all enabled steps without prompting")
    for key in STEP_KEYS:
        parser.add_argument(f"--yes-{key.replace('_', '-')}", dest=f"yes_{key}", action="store_true")
        parser.add_argument(f"--no-{key.replace('_', '-')}", dest=f"no_{key}", action="store_true")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    plan = prepare_project(
        args.name,
        path=args.path,
        description=args.description,
        gh_repo_name=args.gh_repo_name,
        config_path=args.config,
    )
    ctx = plan["ctx"]

    print(f"Project:     {plan['name']}")
    print(f"Path:        {plan['local_path']}")
    if plan["gh_repo_name"] != plan["name"]:
        print(f"GitHub repo: {plan['gh_repo_name']} (override)")
    else:
        print(f"GitHub repo: {plan['gh_repo_name']} (same as project)")
    print()

    decisions = resolve_steps(plan["cfg"], args, ctx)
    execute_steps(plan, decisions)


if __name__ == "__main__":
    main()