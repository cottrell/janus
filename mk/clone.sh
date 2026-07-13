#!/usr/bin/env bash
# Usage: clone.sh
set -euo pipefail
JANUS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="${JANUS_DATA_DIR:-$JANUS_ROOT/data}"

for f in "$DATA"/*.json; do
    # Extract fields using a single python call for efficiency
    eval "$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    skip = d.get('skip_clone', False)
    local = d.get('local_path', '')
    url = d.get('github_url') or d.get('gitlab_url') or d.get('url') or ''
    own = d.get('is_own_repo', True)
    # Mangle HTTPS to SSH if it looks like github or gitlab and it's our own repo
    if own:
        if url.startswith('https://github.com/'):
            url = url.replace('https://github.com/', 'git@github.com:')
            if not url.endswith('.git'): url += '.git'
        elif url.startswith('https://gitlab.com/'):
            url = url.replace('https://gitlab.com/', 'git@gitlab.com:')
            if not url.endswith('.git'): url += '.git'
    print(f'skip_clone=\"{skip}\"')
    print(f'local_path=\"{local}\"')
    print(f'url=\"{url}\"')
except Exception as e:
    sys.exit(1)
" "$f")"

    [[ "$skip_clone" == "True" ]] && echo "skipping clone for $f" && continue
    [[ -z "$local_path" || -z "$url" ]] && continue
    
    full_path="${local_path/#\~/$HOME}"
    if [[ -d "$full_path" ]]; then
        echo "exists: $full_path"
    else
        echo "cloning: $url to $full_path"
        mkdir -p "$(dirname "$full_path")"
        git clone "$url" "$full_path"
    fi
done
