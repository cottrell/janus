<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_backlog_instructions()` to load the tool-oriented overview. Use the `instruction` selector when you need `task-creation`, `task-execution`, or `task-finalization`.

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:
- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and finalization
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->

<!-- AISWARM/NUDGE GUIDELINES START -->
## Swarm

Swarm CLI: `aiswarm` (on PATH; `make install-aiswarm` from the nudge repo).

Read workflow first:
- `aiswarm` — common commands cheat sheet
- `aiswarm instructions overview` — required agent briefing
- `aiswarm instructions handoff` / `tasks` — peer send and backlog dispatch
- `aiswarm this` — this swarm's config + runtime.json path

After start, machine map (not git): `/tmp/nudge-swarm/janus/runtime.json`

Config: `.aiswarm/config.yaml` (cwd walk-up), `$AISWARM_CONFIG`, or explicit path.
Messaging: `aiswarm send <pane> "msg"` (durable log). Do NOT raw `tmux send-keys`.
<!-- AISWARM/NUDGE GUIDELINES END -->
