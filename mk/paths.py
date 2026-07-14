"""Shared Janus paths and defaults — override with env vars (see README)."""
import os
import shutil
from pathlib import Path

JANUS_ROOT = Path(__file__).resolve().parent.parent


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return default if v is None or v == "" else v


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return int(v)


def get_data_dir() -> Path:
    raw = os.environ.get("JANUS_DATA_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return JANUS_ROOT / "data"


def get_dev_root() -> Path:
    """Project tree root for IDE deep-links (default: home directory). Override JANUS_DEV_ROOT."""
    return Path(_env("JANUS_DEV_ROOT", str(Path.home()))).expanduser().resolve()


def get_listen_host() -> str:
    return _env("JANUS_HOST", "::")


def get_listen_port() -> int:
    return _env_int("JANUS_PORT", 7890)


def get_ide_code_server_port() -> int:
    return _env_int("JANUS_IDE_CODE_SERVER_PORT", 9321)


def get_ide_filebrowser_port() -> int:
    return _env_int("JANUS_IDE_FILEBROWSER_PORT", 9323)


def get_ide_ttyd_port() -> int:
    return _env_int("JANUS_IDE_TTYD_PORT", 9322)


def get_ide_ttyd_backend_port() -> int:
    return _env_int("JANUS_IDE_TTYD_BACKEND_PORT", 19322)


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
