#!/usr/bin/env python3
import sys
import time
import json
import subprocess
from pathlib import Path
import yaml


def get_session_name(yaml_path):
    try:
        with open(yaml_path) as f:
            data = yaml.safe_load(f) or {}
            return data.get("session_name", "")
    except Exception:
        return ""

def tmux_session_exists(name):
    res = subprocess.run(["tmux", "has-session", "-t", f"={name}"], stderr=subprocess.DEVNULL)
    return res.returncode == 0

def main():
    delay = 5
    if len(sys.argv) > 1:
        try:
            delay = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid delay argument '{sys.argv[1]}'. Using default of 5 seconds.", file=sys.stderr)

    print(f"Waiting {delay} seconds before running autostart operations...")
    time.sleep(delay)

    from paths import get_data_dir, resolve_swarm_argv

    data_dir = get_data_dir()
    swarm_base = resolve_swarm_argv()

    for f in sorted(data_dir.glob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception as e:
            print(f"Warning: failed to parse {f.name}: {e}", file=sys.stderr)
            continue

        project = d.get("project", f.stem)
        if not d.get("autostart"):
            print(f"[{project}] autostart not enabled, skipping.")
            continue

        print(f"[{project}] autostart processing...")
        local_path = d.get("local_path")
        if not local_path:
            continue
        resolved_path = Path(local_path).expanduser()

        # Ops
        if ops := d.get("tmuxp_ops"):
            yaml_path = resolved_path / ops
            if yaml_path.is_file():
                sess = get_session_name(yaml_path)
                if sess:
                    if tmux_session_exists(sess):
                        print(f"[{project}] ops session '{sess}' already running.")
                    else:
                        print(f"[{project}] autostarting ops: {yaml_path}")
                        res = subprocess.run(["tmuxp", "load", "-d", str(yaml_path)], cwd=resolved_path)
                        if res.returncode != 0:
                            print(f"[{project}] Warning: failed to load ops session (exit code {res.returncode})", file=sys.stderr)
            else:
                print(f"[{project}] missing ops config file: {yaml_path}")

        # Swarm
        if swarm := d.get("tmuxp_swarm"):
            yaml_path = resolved_path / swarm
            if yaml_path.is_file():
                sess = get_session_name(yaml_path)
                if sess:
                    if tmux_session_exists(sess):
                        print(f"[{project}] swarm session '{sess}' already running.")
                    else:
                        if not swarm_base:
                            print(f"[{project}] swarm CLI not found: install aiswarm on PATH", file=sys.stderr)
                            continue
                        print(f"[{project}] autostarting swarm: {yaml_path}")
                        res = subprocess.run([*swarm_base, "start", str(yaml_path)], cwd=resolved_path)
                        if res.returncode != 0:
                            print(f"[{project}] Warning: failed to load swarm session (exit code {res.returncode})", file=sys.stderr)
            else:
                print(f"[{project}] missing swarm config file: {yaml_path}")

if __name__ == "__main__":
    main()
