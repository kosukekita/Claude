#!/usr/bin/env python3
"""Behavior tests for the snapshot/revert hook pair."""

import json
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = HOOKS_DIR.parent
sys.path.insert(0, str(HOOKS_DIR))

import file_snapshot_common as snapshots  # noqa: E402


class SnapshotPairTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hooks-phase3-")
        self.root = Path(self.temporary.name)
        self.state_dir = self.root / "state"
        self.config_path = self.root / "config.json"
        self.config_path.write_text('{"mode":"block"}\n', encoding="utf-8")
        self.environ = {
            "CLAUDE_HOOK_STATE_DIR": str(self.state_dir),
            "CLAUDE_FILE_REVERT_CONFIG": str(self.config_path),
        }
        self.session_id = "phase3-test-session"

    def tearDown(self):
        self.temporary.cleanup()

    def payload(self, tool_name, file_path=None, command=None):
        tool_input = {}
        if file_path is not None:
            tool_input["file_path"] = str(file_path)
        if command is not None:
            tool_input["command"] = command
        return {
            "session_id": self.session_id,
            "cwd": str(self.root),
            "tool_name": tool_name,
            "tool_input": tool_input,
        }

    def test_read_unchanged_then_edit_is_allowed(self):
        target = self.root / "unchanged.txt"
        target.write_text("original", encoding="utf-8")
        snapshots.record_event(self.payload("Read", target), self.environ)

        result = snapshots.guard_event(self.payload("Edit", target), self.environ)

        self.assertEqual("allow", result["decision"])
        self.assertIsNone(result["classification"])

    def test_read_then_external_change_is_denied_in_block_mode(self):
        target = self.root / "external.txt"
        target.write_text("original", encoding="utf-8")
        snapshots.record_event(self.payload("Read", target), self.environ)
        target.write_text("changed outside hooks", encoding="utf-8")

        result = snapshots.guard_event(self.payload("Edit", target), self.environ)

        self.assertEqual("deny", result["decision"])
        self.assertEqual("user-edit", result["classification"])

    def test_write_or_edit_then_edit_is_agent_write_and_allowed(self):
        target = self.root / "agent-write.txt"
        target.write_text("written by tool", encoding="utf-8")
        snapshots.record_event(self.payload("Write", target), self.environ)

        result = snapshots.guard_event(self.payload("Edit", target), self.environ)

        self.assertEqual("allow", result["decision"])
        self.assertEqual("agent-write", result["classification"])

    def test_known_bash_write_is_agent_write_and_allowed(self):
        target = self.root / "bash-write.txt"
        target.write_text("original", encoding="utf-8")
        snapshots.record_event(self.payload("Read", target), self.environ)
        target.write_text("changed by bash", encoding="utf-8")
        command = f"printf updated > '{target}'"
        snapshots.record_event(self.payload("Bash", command=command), self.environ)

        result = snapshots.guard_event(self.payload("Edit", target), self.environ)

        self.assertEqual("allow", result["decision"])
        self.assertEqual("agent-write", result["classification"])

    def test_unparsed_bash_write_is_ambiguous_and_never_denied(self):
        target = self.root / "bash-ambiguous.txt"
        target.write_text("original", encoding="utf-8")
        snapshots.record_event(self.payload("Read", target), self.environ)
        target.write_text("changed by opaque bash", encoding="utf-8")
        snapshots.record_event(
            self.payload("Bash", command="python -c 'opaque file mutation'"),
            self.environ,
        )

        result = snapshots.guard_event(self.payload("Edit", target), self.environ)

        self.assertEqual("allow", result["decision"])
        self.assertEqual("ambiguous", result["classification"])

    def test_case_distinct_paths_have_distinct_state_keys_on_linux(self):
        upper = self.root / "Case.txt"
        lower = self.root / "case.txt"
        upper.write_text("upper", encoding="utf-8")
        lower.write_text("lower", encoding="utf-8")
        snapshots.record_event(self.payload("Read", upper), self.environ)
        snapshots.record_event(self.payload("Read", lower), self.environ)

        upper_state = snapshots.snapshot_path(upper, self.environ)
        lower_state = snapshots.snapshot_path(lower, self.environ)

        self.assertNotEqual(upper_state, lower_state)
        self.assertTrue(upper_state.exists())
        self.assertTrue(lower_state.exists())

    def test_new_file_is_allowed_without_error(self):
        target = self.root / "not-created-yet.txt"

        result = snapshots.guard_event(self.payload("Write", target), self.environ)

        self.assertEqual("allow", result["decision"])
        self.assertIsNone(result["classification"])

    def test_audit_mode_logs_user_edit_but_does_not_deny(self):
        self.config_path.write_text('{"mode":"audit"}\n', encoding="utf-8")
        target = self.root / "audit.txt"
        target.write_text("original", encoding="utf-8")
        snapshots.record_event(self.payload("Read", target), self.environ)
        target.write_text("external", encoding="utf-8")

        result = snapshots.guard_event(self.payload("Edit", target), self.environ)
        events = [
            json.loads(line)
            for line in snapshots.audit_log_path(self.environ)
            .read_text(encoding="utf-8")
            .splitlines()
        ]

        self.assertEqual("allow", result["decision"])
        self.assertEqual("user-edit", result["classification"])
        self.assertEqual("user-edit", events[-1]["classification"])
        self.assertEqual("audit", events[-1]["mode"])

    def test_audit_config_and_bash_matcher_are_installed(self):
        config = json.loads(
            (HOOKS_DIR / "file-revert-config.json").read_text(encoding="utf-8")
        )
        settings = json.loads((REPO_DIR / "settings.json").read_text(encoding="utf-8"))
        post_groups = settings["hooks"]["PostToolUse"]
        snapshot_group = next(
            group
            for group in post_groups
            if any("record-file-snapshot" in hook["command"] for hook in group["hooks"])
        )

        self.assertEqual("audit", config["mode"])
        self.assertIn("Bash", snapshot_group["matcher"].split("|"))
        self.assertTrue((HOOKS_DIR / "record-file-snapshot.py").exists())
        self.assertTrue((HOOKS_DIR / "guard-file-revert.py").exists())
        self.assertFalse((HOOKS_DIR / "record-file-snapshot.ps1").exists())
        self.assertFalse((HOOKS_DIR / "guard-file-revert.ps1").exists())
        self.assertTrue((HOOKS_DIR / "retired" / "record-file-snapshot.ps1").exists())
        self.assertTrue((HOOKS_DIR / "retired" / "guard-file-revert.ps1").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
