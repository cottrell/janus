"""Shared Janus paths — override data dir with JANUS_DATA_DIR."""
import os
from pathlib import Path

JANUS_ROOT = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    raw = os.environ.get("JANUS_DATA_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return JANUS_ROOT / "data"