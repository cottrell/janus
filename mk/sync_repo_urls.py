#!/usr/bin/env python3
"""Backfill github_url / gitlab_url from git remote origin when missing.

Usage:
  uv run python mk/sync_repo_urls.py           # apply
  uv run python mk/sync_repo_urls.py --dry-run # report only
  make sync-repo-urls
  make sync-repo-urls ARGS=--dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

from paths import get_data_dir

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# git@host:path.git  or  https://host/path(.git)  or  ssh://git@host/path
_SSH = re.compile(r"^git@([^:]+):(.+)$")
_SSH_URL = re.compile(r"^ssh://git@([^/]+)/(.+)$")
_HTTPS = re.compile(r"^https?://([^/]+)/(.+)$")


def origin_url(local_path: Path) -> str | None:
    if not (local_path / ".git").exists():
        return None
    r = subprocess.run(
        ["git", "-C", str(local_path), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def to_https_field(remote: str) -> tuple[str, str] | None:
    """Return (field_name, https_url) or None if not github/gitlab."""
    host, path = None, None
    m = _SSH.match(remote)
    if m:
        host, path = m.group(1), m.group(2)
    else:
        m = _SSH_URL.match(remote)
        if m:
            host, path = m.group(1), m.group(2)
        else:
            m = _HTTPS.match(remote)
            if m:
                host, path = m.group(1), m.group(2)
    if not host or not path:
        return None
    path = path.removesuffix(".git")
    host_l = host.lower()
    if host_l in ("github.com", "www.github.com"):
        return "github_url", f"https://github.com/{path}"
    if host_l in ("gitlab.com", "www.gitlab.com"):
        return "gitlab_url", f"https://gitlab.com/{path}"
    # self-hosted: stash as github_url only if user already uses that field? skip
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print actions only")
    ap.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing github_url/gitlab_url when origin differs",
    )
    args = ap.parse_args()

    data_dir = get_data_dir()
    files = sorted(data_dir.glob("*.json"))
    if not files:
        logging.error("No project JSON in %s", data_dir)
        return 1

    updated = skipped = missing = 0
    for f in files:
        d = json.loads(f.read_text())
        name = d.get("project") or f.stem
        has_gh = bool(d.get("github_url"))
        has_gl = bool(d.get("gitlab_url"))
        if (has_gh or has_gl) and not args.force:
            skipped += 1
            continue

        lp = d.get("local_path")
        if not lp:
            logging.info("%s: no local_path", name)
            missing += 1
            continue
        local = Path(os.path.expanduser(lp))
        remote = origin_url(local)
        if not remote:
            logging.info("%s: no origin at %s", name, local)
            missing += 1
            continue

        parsed = to_https_field(remote)
        if not parsed:
            logging.info("%s: origin not github/gitlab: %s", name, remote)
            missing += 1
            continue
        field, url = parsed

        if d.get(field) == url:
            skipped += 1
            continue

        logging.info("%s: set %s=%s%s", name, field, url, " (dry-run)" if args.dry_run else "")
        if not args.dry_run:
            if field in d:
                d[field] = url
            else:
                # insert after local_path when present, else after project
                out = {}
                placed = False
                for k, v in d.items():
                    out[k] = v
                    if k in ("local_path", "project") and not placed:
                        if k == "local_path" or "local_path" not in d:
                            out[field] = url
                            placed = True
                if not placed:
                    out[field] = url
                d = out
            f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        updated += 1

    logging.info(
        "done: updated=%d skipped=%d no-remote=%d dry_run=%s",
        updated,
        skipped,
        missing,
        args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
