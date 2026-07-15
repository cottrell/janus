"""Shared Janus paths and defaults.

Dashboard listen: prefer CLI on server.py (`--host` / `--port`); env JANUS_HOST /
JANUS_PORT are fallbacks for make/systemd.

IDE ports: used by both server.py (link URLs) and ide/*/run.sh (listeners), so
env JANUS_IDE_* is the shared knob — not CLI-only.
"""
import json
import logging
import os
import shutil
from pathlib import Path

JANUS_ROOT = Path(__file__).resolve().parent.parent

# Defaults (single place to read)
DEFAULT_HOST = "::"
DEFAULT_PORT = 7890
DEFAULT_IDE_CODE_SERVER_PORT = 9321
DEFAULT_IDE_FILEBROWSER_PORT = 9323
DEFAULT_IDE_TTYD_PORT = 9322
DEFAULT_IDE_TTYD_BACKEND_PORT = 19322


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return default if v is None or v == "" else v


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return int(v)


_logged_data_dir = False


def get_data_dir() -> Path:
    global _logged_data_dir
    raw = os.environ.get("JANUS_DATA_DIR")
    if raw:
        path = Path(raw).expanduser()
    else:
        path = JANUS_ROOT / "data"

    resolved = path.resolve()

    if not _logged_data_dir:
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        
        info = {
            "env_var_set": raw is not None,
            "env_var_value": raw,
            "raw_path": str(path),
            "is_symlink": path.is_symlink(),
            "symlink_target": str(os.readlink(path)) if path.is_symlink() else None,
            "resolved_path": str(resolved),
        }
        logging.info("Using data directory: %s", resolved)
        logging.info("Data directory resolution details: %s", json.dumps(info))
        _logged_data_dir = True

    return resolved


def get_dev_root() -> Path:
    """Project tree root for IDE deep-links (default: home). Override JANUS_DEV_ROOT."""
    return Path(_env("JANUS_DEV_ROOT", str(Path.home()))).expanduser().resolve()


def get_listen_host() -> str:
    return _env("JANUS_HOST", DEFAULT_HOST)


def get_listen_port() -> int:
    return _env_int("JANUS_PORT", DEFAULT_PORT)


def get_ide_code_server_port() -> int:
    return _env_int("JANUS_IDE_CODE_SERVER_PORT", DEFAULT_IDE_CODE_SERVER_PORT)


def get_ide_filebrowser_port() -> int:
    return _env_int("JANUS_IDE_FILEBROWSER_PORT", DEFAULT_IDE_FILEBROWSER_PORT)


def get_ide_ttyd_port() -> int:
    return _env_int("JANUS_IDE_TTYD_PORT", DEFAULT_IDE_TTYD_PORT)


def get_ide_ttyd_backend_port() -> int:
    return _env_int("JANUS_IDE_TTYD_BACKEND_PORT", DEFAULT_IDE_TTYD_BACKEND_PORT)


def get_ide_code_server_url() -> str:
    """Base URL for code-server links (no trailing slash)."""
    if u := os.environ.get("JANUS_IDE_CODE_SERVER_URL"):
        return u.rstrip("/")
    scheme = _env("JANUS_IDE_CODE_SERVER_SCHEME", "https")
    return f"{scheme}://localhost:{get_ide_code_server_port()}"


def get_ide_filebrowser_url() -> str:
    if u := os.environ.get("JANUS_IDE_FILEBROWSER_URL"):
        return u.rstrip("/")
    return f"http://localhost:{get_ide_filebrowser_port()}"


def resolve_swarm_argv() -> list[str] | None:
    """Argv prefix for swarm CLI: `aiswarm` on PATH, or JANUS_NUDGE_CLI path to cli.py."""
    if p := shutil.which("aiswarm"):
        return [p]
    raw = os.environ.get("JANUS_NUDGE_CLI")
    if raw:
        fallback = Path(raw).expanduser()
        if fallback.is_file():
            return ["python3", str(fallback)]
    return None
