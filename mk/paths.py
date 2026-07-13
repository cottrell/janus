"""Shared Janus paths — override data dir with JANUS_DATA_DIR."""
import os
import shutil
from pathlib import Path

JANUS_ROOT = Path(__file__).resolve().parent.parent
NUDGE_CLI_FALLBACK = Path.home() / "dev/nudge/swarm/cli.py"


def get_data_dir() -> Path:
    raw = os.environ.get("JANUS_DATA_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return JANUS_ROOT / "data"


def resolve_swarm_argv() -> list[str] | None:
    """Argv prefix for swarm CLI: prefer `aiswarm` on PATH, else python + nudge cli.py."""
    if p := shutil.which("aiswarm"):
        return [p]
    if NUDGE_CLI_FALLBACK.is_file():
        return ["python3", str(NUDGE_CLI_FALLBACK)]
    return None
