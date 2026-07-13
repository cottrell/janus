#!/usr/bin/env python3
import json, re, sys, yaml
from collections import defaultdict
from pathlib import Path

from paths import get_data_dir

KNOWN_FIELDS = {'project', 'local_path', 'github_url', 'gitlab_url',
                'tmuxp_ops', 'tmuxp_swarm', 'description', 'links',
                'port_scope', 'is_own_repo', 'skip_clone', 'ops_up', 'swarm_up',
                'ide_links', 'autostart', 'meta', 'muxpod_server_id'}

# port_scope values: "global" (default) = checked for cross-project conflicts
#                    "compose" or other  = exempt (isolated network)
KNOWN_LINK_FIELDS = {'label', 'url', 'description', 'status', 'kind'}

errors = []
port_index = defaultdict(list)  # port -> [(file, label, url)]

def err(f, msg):
    errors.append(f"  {f.name}: {msg}")

data_dir = get_data_dir()

for f in sorted(data_dir.glob('*.json')):
    d = json.loads(f.read_text())

    # unknown fields
    unknown = set(d) - KNOWN_FIELDS
    if unknown:
        err(f, f"unknown fields: {sorted(unknown)}")

    # required
    if 'project' not in d:
        err(f, "missing 'project'")

    # local_path exists
    local_path = d.get('local_path', '')
    if local_path:
        resolved = Path(local_path.replace('~', str(Path.home())))
        if not resolved.is_dir():
            err(f, f"local_path not found: {local_path}")
        else:
            # tmuxp_ops exists relative to local_path
            if ops := d.get('tmuxp_ops'):
                p = resolved / ops
                if not p.exists():
                    err(f, f"tmuxp_ops not found: {ops}")
            # tmuxp_swarm exists relative to local_path
            if swarm := d.get('tmuxp_swarm'):
                p = resolved / swarm
                if not p.exists():
                    err(f, f"tmuxp_swarm not found: {swarm}")
                else:
                    try:
                        y = yaml.safe_load(p.read_text())
                        for win in y.get('windows', []):
                            for pane in win.get('panes', []):
                                if not isinstance(pane, dict):
                                    err(f, f"swarm {swarm} has invalid pane (must be dict): {pane}")
                    except Exception as e:
                        err(f, f"failed to parse swarm {swarm}: {e}")
    elif d.get('tmuxp_ops') or d.get('tmuxp_swarm'):
        err(f, "tmuxp_ops/tmuxp_swarm set but no local_path to resolve against")

    # links
    seen_ports = set()
    for i, l in enumerate(d.get('links', [])):
        unknown_lf = set(l) - KNOWN_LINK_FIELDS
        if unknown_lf:
            err(f, f"links[{i}] unknown fields: {sorted(unknown_lf)}")
        if 'label' not in l:
            err(f, f"links[{i}] missing 'label'")
        if 'url' not in l:
            err(f, f"links[{i}] missing 'url'")
        url = l.get('url') or ''
        if m := re.search(r':(\d+)', url):
            port = m.group(1)
            if port not in seen_ports and d.get('port_scope', 'global') == 'global':
                port_index[port].append((f.name, l.get('label', '?'), url))
                seen_ports.add(port)

conflicts = {}
for port, entries in port_index.items():
    if len(entries) > 1:
        # If all entries have the same URL, it's a shared service, not a conflict
        urls = {e[2] for e in entries}
        labels = {e[1].lower() for e in entries}
        if len(urls) > 1 or 'backlog' in labels:
            conflicts[port] = entries
if conflicts:
    for port, entries in sorted(conflicts.items(), key=lambda x: int(x[0])):
        errors.append(f"  port :{port} used by multiple projects:")
        for fname, label, url in entries:
            errors.append(f"    {fname} — {label} ({url})")

if errors:
    print("VALIDATION ERRORS:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"OK — {len(list(data_dir.glob('*.json')))} files valid")
