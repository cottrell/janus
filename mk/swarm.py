#!/usr/bin/env python3
import sys
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

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "up"
    if cmd not in ("up", "down"):
        print(f"Usage: {sys.argv[0]} [up|down]")
        sys.exit(1)

    from paths import get_data_dir, resolve_swarm_argv

    data_dir = get_data_dir()
    swarm_base = resolve_swarm_argv()

    for f in sorted(data_dir.glob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue

        if not d.get("swarm_up", True):
            continue

        local_path = d.get("local_path")
        swarm = d.get("tmuxp_swarm")
        if not local_path or not swarm:
            continue

        resolved_path = Path(local_path).expanduser()
        yaml_path = resolved_path / swarm

        if not yaml_path.is_file():
            print(f"missing: {yaml_path}")
            continue

        if cmd == "up":
            if not swarm_base:
                print("swarm CLI not found: install aiswarm on PATH (or set JANUS_NUDGE_CLI)", file=sys.stderr)
                continue
            print(f"swarm up: {yaml_path}")
            res = subprocess.run([*swarm_base, "start", str(yaml_path)], cwd=resolved_path)
            if res.returncode != 0:
                print(f"Warning: failed to load swarm session (exit code {res.returncode})", file=sys.stderr)
        elif cmd == "down":
            if not swarm_base:
                print("swarm CLI not found: install aiswarm on PATH (or set JANUS_NUDGE_CLI)", file=sys.stderr)
                continue
            print(f"swarm down: {yaml_path}")
            res = subprocess.run([*swarm_base, "stop", str(yaml_path)], cwd=resolved_path)
            if res.returncode != 0:
                print(f"Warning: failed to stop swarm session (exit code {res.returncode})", file=sys.stderr)

if __name__ == "__main__":
    main()
