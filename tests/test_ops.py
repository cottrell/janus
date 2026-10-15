import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

import server


class OpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = self.root / "ops.yaml"
        self.config.write_text("session_name: test-ops\n")

    def script(self, action):
        script = self.root / "mk" / f"{action}.sh"
        script.parent.mkdir(exist_ok=True)
        script.write_text("#!/bin/sh\nexit 0\n")
        script.chmod(0o755)
        return script

    def test_down_selects_script_and_cleans_up_after_hook_failure(self):
        script = self.script("down")
        with patch.object(server, "has_make_target", return_value=True), \
             patch.object(server, "tmux_session_exists", return_value=True), \
             patch.object(server, "run_command") as run:
            run.side_effect = [HTTPException(status_code=504, detail="timed out"), {"ok": True}]
            with self.assertRaises(HTTPException) as error:
                server._run_ops_down(self.root, self.config)
        self.assertEqual(error.exception.status_code, 504)
        self.assertEqual(run.call_args_list[0].args[0], [str(script)])
        self.assertEqual(run.call_args_list[1].args[0], ["tmux", "kill-session", "-t", "=test-ops"])
        self.assertEqual(run.call_count, 2)

    def test_status_uses_custom_hook_without_tmux(self):
        script = self.script("status")
        project = {"project": "test", "local_path": str(self.root), "tmuxp_ops": "ops.yaml"}
        with patch.object(server, "get_links", return_value=[project]), \
             patch.object(server, "tmux_session_exists", side_effect=AssertionError("tmux called")), \
             patch.object(server.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            result = server.status()
        self.assertTrue(result["test"]["ops"]["up"])
        self.assertEqual(run.call_args.args[0], [str(script)])
        self.assertEqual(run.call_args.kwargs["timeout"], 5)

    def test_status_timeout_reports_error(self):
        self.script("status")
        project = {"project": "test", "local_path": str(self.root), "tmuxp_ops": "ops.yaml"}
        with patch.object(server, "get_links", return_value=[project]), \
             patch.object(server.subprocess, "run", side_effect=subprocess.TimeoutExpired("status", 5)):
            result = server.status()
        self.assertFalse(result["test"]["ops"]["up"])
        self.assertIn("status check failed", result["test"]["ops"]["error"])

    def test_bounce_uses_same_script_priority_as_up(self):
        script = self.script("up")
        project = {"local_path": str(self.root), "tmuxp_ops": "ops.yaml"}
        with patch.object(server, "load_project", return_value=project), \
             patch.object(server, "_run_ops_down"), \
             patch.object(server, "has_make_target", return_value=True), \
             patch.object(server, "run_command", return_value={"ok": True}) as run, \
             patch.object(server.time, "sleep"):
            server.ops_up("test")
            server.ops_bounce("test")
        self.assertEqual([call.args[0] for call in run.call_args_list], [[str(script)], [str(script)]])

    def test_tmuxp_fallback(self):
        project = {"local_path": str(self.root), "tmuxp_ops": "ops.yaml"}
        with patch.object(server, "load_project", return_value=project), \
             patch.object(server, "run_command", return_value={"ok": True}) as run:
            server.ops_up("test")
        self.assertEqual(run.call_args.args[0], ["tmuxp", "load", "-d", str(self.config)])

    def test_down_without_hook_kills_tmux_session(self):
        with patch.object(server, "tmux_session_exists", return_value=True), \
             patch.object(server, "run_command", return_value={"ok": True}) as run:
            server._run_ops_down(self.root, self.config)
        run.assert_called_once_with(["tmux", "kill-session", "-t", "=test-ops"], self.root)

    def test_tmux_status_check_is_bounded(self):
        with patch.object(server.subprocess, "run", side_effect=subprocess.TimeoutExpired("tmux", 5)) as run:
            self.assertFalse(server.tmux_session_exists("test-ops"))
        self.assertEqual(run.call_args.kwargs["timeout"], 5)


if __name__ == "__main__":
    unittest.main()
