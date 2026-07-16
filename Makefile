all:
	cat Makefile
# Registry: default ./data (JANUS_DATA_DIR). Extra server flags: make dev ARGS='--port 8080'
# Raise fd limit when the shell allows it (no-op if capped); then start dashboard.
dev:
	@bash -c 'ulimit -n 65536 2>/dev/null || true; exec uv run python server.py $(ARGS)'
dev-serve:
	@bash -c 'ulimit -n 65536 2>/dev/null || true; exec uv run python server.py --no-reload $(ARGS)'
validate:
	uv run python mk/validate.py
ops-up:
	uv run python mk/ops.py up
ops-down:
	uv run python mk/ops.py down
swarm-up:
	uv run python mk/swarm.py up
swarm-down:
	uv run python mk/swarm.py down
clone:
	bash mk/clone.sh
# Backfill github_url/gitlab_url from git remote origin. ARGS=--dry-run or --force
sync-repo-urls:
	uv run python mk/sync_repo_urls.py $(ARGS)
new-project:
	uv run python mk/new_project.py $(name)
autostart:
	uv run python mk/autostart.py
sync:
	uv sync


do:
	@bash mk/do.sh "$(c)"

# Catch-all target to silence "No rule to make target" for arguments
%:
	@:
