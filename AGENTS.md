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


## Swarm

Swarm workflow: read first:
- Runtime map: `/tmp/nudge-swarm/janus/runtime.json`
- Self-awareness note: `/tmp/nudge-swarm/janus/self-awareness.txt`

Use as source of truth for:
- tmux pane targets
- monitor sockets, live state
- babysit pid/log/spec/state files

Swarm CLI: `aiswarm`

Messaging (durable, preferred):
- Use the comms log for reliability between agents: `aiswarm send <cfg> <pane> "msg"` or `log_broadcast`.
- Inspect: `aiswarm log <cfg> [--pending] [--pane 0.2]`, `aiswarm cursors <cfg>`.
- Direct/manual still works: `./tmux-send <target> "message"`.

Worker loop:
- `aiswarm start <cfg>` starts the base comms worker for `monitor: true` panes.
- The worker consumes the log and delivers via `tmux-send` when the pane is idle.
- Babysit prompt nudges are independent; use `aiswarm babysit start|stop <cfg>`.

Do NOT use raw `tmux send-keys ... Enter`.

Swarm scripts: `swarm/`.
