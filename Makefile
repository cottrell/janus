all:
	cat Makefile
# Personal registry at ~/dev/janus-data when present; override: make dev JANUS_DATA_DIR=./data
ifeq ($(wildcard $(HOME)/dev/janus-data/*.json),)
else
export JANUS_DATA_DIR ?= $(HOME)/dev/janus-data
endif
# Raise fd limit when the shell allows it (no-op if capped); then start dashboard.
dev:
	@bash -c 'ulimit -n 65536 2>/dev/null || true; exec uv run python server.py'
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
