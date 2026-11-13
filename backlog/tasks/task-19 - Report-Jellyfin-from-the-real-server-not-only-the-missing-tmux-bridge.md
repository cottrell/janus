---
id: TASK-19
title: 'Report Jellyfin from the real server, not only the missing tmux bridge'
status: To Do
assignee: []
created_date: '2026-11-13T10:14:00Z'
labels:
  - ops
dependencies: []
references:
  - server.py
  - /home/cottrell/dev/jellyfish/ops.yaml
  - /home/cottrell/dev/jellyfish/Makefile
  - /home/cottrell/dev/janus-data/jellyfish.json
  - >-
    backlog/tasks/task-18 -
    Fix-false-ops-status-from-generic-make-status-targets.md
priority: medium
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
On 2026-11-13 the Janus page for media-jellyfish said the project was not started. jellyfin.service was active the whole time: enabled, started at boot, PID 5701, listening on 0.0.0.0:8096 since 2026-10-29. The user could not tell whether Janus, the janus-data card, or both were wrong.

Facts from that check:

- ~/dev/janus-data/jellyfish.json only names the project, muxpod server, local_path ~/dev/jellyfish, and tmuxp_ops ops.yaml. It has no health command. janus-data has no backlog.
- ~/dev/jellyfish is its own git repo. ops.yaml session_name is ops-jellyfish and its only pane is `socat TCP6-LISTEN:8096,ipv6only,fork,reuseaddr TCP4:127.0.0.1:8096`. That tmux session was not running, and nothing was listening on IPv6 port 8096.
- The media server is the system unit jellyfin.service (package jellyfin 12.4+ubu2604, enabled 2026-09-21, WantedBy=multi-user.target). It is not a child of the tmux session.
- Janus GET /api/status treats a live tmux ops session as authoritative. If the session is absent it only runs mk/ops-status.sh, bin/ops-status, or ops-status.sh. ~/dev/jellyfish has none of those. Its Makefile status target runs `systemctl is-active --quiet jellyfin`, and Janus ignores generic make status on purpose (TASK-18) so a project like Planistan cannot be marked down by an unrelated Makefile target.
- Makefile down stops the systemd unit. There is no up target, so Janus up only tmuxp-loads the socat bridge. Down and the status light do not describe the same process. The card link is http://localhost:8096, which is the systemd server.

The page is faithful to the bridge session and unfaithful to the server. Decide which of janus, ~/dev/jellyfish, and janus-data must change. Do not undo TASK-18.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 With jellyfin.service active and tmux session ops-jellyfish absent, the Janus ops control for media-jellyfish reports the server up.
- [ ] #2 With jellyfin.service inactive, that same control reports the server down. A socat bridge session alone must not be presented as the media server.
- [ ] #3 Ops up and ops down change the same process the status light describes. Stopping from Janus stays stopped across reboot. A server systemd will start at boot is not shown as not started.
- [ ] #4 A live tmux ops session is still reported up when a generic Makefile status target fails (TASK-18 / Planistan).
- [ ] #5 The final summary names which of janus, ~/dev/jellyfish, and janus-data changed, and why the others did not.
<!-- AC:END -->
