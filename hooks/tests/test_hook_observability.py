#!/usr/bin/env python3
"""Behavior tests for fail-open observability in Python hooks."""

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


HOOKS_DIR = Path(__file__).resolve().parent.parent
FIXTURES = json.loads(
    Path(__file__)
    .with_name("hook-observability-fixtures.json")
    .read_text(encoding="utf-8")
)


def load_guard_module():
    path = HOOKS_DIR / "guard-destructive-and-resolution.py"
    spec = importlib.util.spec_from_file_location("guard_destructive", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GUARD = load_guard_module()


class HookObservabilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hook-observability-")
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.state_home = self.root / "state"
        self.file_revert_state = self.root / "file-revert-state"
        self.config_path = self.root / "file-revert-config.json"
        self.config_path.write_text('{"mode":"audit"}\n', encoding="utf-8")
        self.environ = {
            **os.environ,
            "HOME": str(self.home),
            "XDG_STATE_HOME": str(self.state_home),
            "CLAUDE_HOOK_STATE_DIR": str(self.file_revert_state),
            "CLAUDE_FILE_REVERT_CONFIG": str(self.config_path),
        }

    def tearDown(self):
        self.temporary.cleanup()

    @property
    def event_log(self):
        return self.state_home / "claude-hooks" / "dispatch-events.jsonl"

    def fixture_bytes(self, fixture):
        if "stdin_hex" in fixture:
            return bytes.fromhex(fixture["stdin_hex"])
        if "stdin_text" in fixture:
            return fixture["stdin_text"].encode()
        return json.dumps(fixture["payload"]).encode()

    def run_fixture(self, name, environ=None):
        fixture = FIXTURES[name]
        return subprocess.run(
            [sys.executable, str(HOOKS_DIR / fixture["script"])],
            input=self.fixture_bytes(fixture),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environ or self.environ,
            cwd=self.root,
            check=False,
        )

    def events(self):
        if not self.event_log.exists():
            return []
        return [
            json.loads(line)
            for line in self.event_log.read_text(encoding="utf-8").splitlines()
        ]

    def test_guard_invalid_inputs_allow_and_record_machine_readable_events(self):
        for name in (
            "guard_invalid_json",
            "guard_invalid_encoding",
            "guard_non_string_command",
        ):
            with self.subTest(name=name):
                before = len(self.events())
                result = self.run_fixture(name)
                event = self.events()[-1]
                self.assertEqual(0, result.returncode)
                self.assertEqual(b"", result.stdout)
                self.assertEqual(before + 1, len(self.events()))
                self.assertEqual("guard-destructive-and-resolution", event["target"])
                self.assertEqual("fail-open", event["kind"])
                self.assertEqual(FIXTURES[name]["expected_detail"], event["detail"])
                self.assertIn("timestamp", event)

    def test_guard_normal_allow_and_deny_do_not_record(self):
        allow_result = self.run_fixture("guard_allow")
        policy_fixture = json.loads(
            Path(__file__)
            .with_name("guard-policy-fixtures.json")
            .read_text(encoding="utf-8")
        )
        deny_command = next(item["command"] for item in policy_fixture if item["id"] == "A1")
        deny_result = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "guard-destructive-and-resolution.py")],
            input=json.dumps({"tool_input": {"command": deny_command}}).encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environ,
            check=False,
        )

        self.assertEqual(0, allow_result.returncode)
        self.assertEqual(0, deny_result.returncode)
        self.assertEqual("deny", json.loads(deny_result.stdout)["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual([], self.events())

    def test_event_log_is_outside_claude_configuration_directory(self):
        self.run_fixture("guard_invalid_json")

        self.assertTrue(self.event_log.exists())
        self.assertFalse(self.event_log.is_relative_to(self.home / ".claude"))

    def test_unwritable_event_directory_stays_fail_open(self):
        blocked = self.root / "blocked-state"
        blocked.mkdir()
        blocked.chmod(0o500)
        environ = {**self.environ, "XDG_STATE_HOME": str(blocked)}

        result = self.run_fixture("guard_invalid_json", environ)

        self.assertEqual(0, result.returncode)
        self.assertEqual(b"", result.stdout)
        self.assertEqual(b"", result.stderr)

    def test_snapshot_and_revert_invalid_input_record_without_changing_fail_open(self):
        for name, target in (
            ("snapshot_invalid_json", "record-file-snapshot"),
            ("revert_invalid_json", "guard-file-revert"),
        ):
            with self.subTest(name=name):
                before = len(self.events())
                result = self.run_fixture(name)
                event = self.events()[-1]
                self.assertEqual(0, result.returncode)
                self.assertEqual(b"", result.stdout)
                self.assertEqual(before + 1, len(self.events()))
                self.assertEqual(target, event["target"])
                self.assertEqual("fail-open", event["kind"])

    def test_snapshot_state_write_failure_is_recorded_and_remains_fail_open(self):
        state_file = self.root / "state-is-a-file"
        state_file.write_text("not a directory", encoding="utf-8")
        environ = {**self.environ, "CLAUDE_HOOK_STATE_DIR": str(state_file)}
        payload = {
            "session_id": "observability-test",
            "tool_name": "Bash",
            "tool_input": {"command": "printf observed"},
        }

        result = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "record-file-snapshot.py")],
            input=json.dumps(payload).encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environ,
            check=False,
        )
        event = self.events()[-1]

        self.assertEqual(0, result.returncode)
        self.assertEqual(b"", result.stdout)
        self.assertEqual("record-file-snapshot", event["target"])
        self.assertEqual("state-write-error", event["detail"])

    def test_snapshot_and_revert_normal_events_do_not_log_fail_open(self):
        for name in ("snapshot_valid", "revert_valid"):
            with self.subTest(name=name):
                result = self.run_fixture(name)
                self.assertEqual(0, result.returncode)
        self.assertEqual([], self.events())

    def test_guard_unexpected_exception_is_recorded_and_remains_fail_open(self):
        payload = FIXTURES["guard_allow"]["payload"]
        with (
            mock.patch.object(GUARD, "shell_tokens", side_effect=RuntimeError("fixture failure")),
            mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))),
            mock.patch.dict(os.environ, self.environ, clear=True),
        ):
            result = GUARD.main()

        event = self.events()[-1]
        self.assertEqual(0, result)
        self.assertEqual("unexpected-error", event["detail"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
