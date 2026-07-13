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

    from paths import get_data_dir

    data_dir = get_data_dir()

    for f in sorted(data_dir.glob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue

        if not d.get("ops_up", True):
            continue

        local_path = d.get("local_path")
        ops = d.get("tmuxp_ops")
        if not local_path or not ops:
            continue

        resolved_path = Path(local_path).expanduser()
        yaml_path = resolved_path / ops

        if not yaml_path.is_file():
            print(f"missing: {yaml_path}")
            continue

        if cmd == "up":
            print(f"ops up: {yaml_path}")
            res = subprocess.run(["tmuxp", "load", "-d", str(yaml_path)], cwd=resolved_path)
            if res.returncode != 0:
                print(f"Warning: failed to load ops session (exit code {res.returncode})", file=sys.stderr)
        elif cmd == "down":
            sess = get_session_name(yaml_path)
            if sess:
                print(f"ops down: {sess}")
                subprocess.run(["tmux", "kill-session", "-t", f"={sess}"], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
