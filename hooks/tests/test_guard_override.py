#!/usr/bin/env python3
"""Behavior tests for the auditable one-time guard override."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HOOKS_DIR = Path(__file__).resolve().parent.parent
OVERRIDE_TOOL = HOOKS_DIR / "guard_override.py"
FIXTURE = json.loads(
    Path(__file__).with_name("guard-override-fixtures.json").read_text(encoding="utf-8")
)
POLICY_FIXTURES = json.loads(
    Path(__file__).with_name("guard-policy-fixtures.json").read_text(encoding="utf-8")
)


class GuardOverrideTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="guard-override-")
        self.root = Path(self.temporary.name)
        self.state_home = self.root / "state"
        self.environ = {
            **os.environ,
            "HOME": str(self.root / "home"),
            "XDG_STATE_HOME": str(self.state_home),
            "USER": FIXTURE["requested_by"],
        }
        self.command = next(
            item["command"]
            for item in POLICY_FIXTURES
            if item["id"] == FIXTURE["policy_fixture_id"]
        )
        self.command_hash = hashlib.sha256(self.command.encode()).hexdigest()

    def tearDown(self):
        self.temporary.cleanup()

    @property
    def event_log(self):
        return self.state_home / "claude-hooks" / "dispatch-events.jsonl"

    def run_guard(self):
        return subprocess.run(
            [sys.executable, str(HOOKS_DIR / "guard-destructive-and-resolution.py")],
            input=json.dumps({"tool_input": {"command": self.command}}).encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environ,
            check=False,
        )

    def create_override(self):
        return subprocess.run(
            [
                sys.executable,
                str(OVERRIDE_TOOL),
                "create",
                "--rule",
                FIXTURE["rule"],
                "--command-hash",
                self.command_hash,
                "--reason",
                FIXTURE["reason"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environ,
            check=False,
        )

    def deny_reason(self, result):
        payload = json.loads(result.stdout)
        self.assertEqual("deny", payload["hookSpecificOutput"]["permissionDecision"])
        return payload["hookSpecificOutput"]["permissionDecisionReason"]

    def events(self):
        if not self.event_log.exists():
            return []
        return [
            json.loads(line)
            for line in self.event_log.read_text(encoding="utf-8").splitlines()
        ]

    def test_deny_message_has_exact_override_method_and_explicit_limit(self):
        result = self.run_guard()
        reason = self.deny_reason(result)

        self.assertIn("guard_override.py create", reason)
        self.assertIn(f"--rule {FIXTURE['rule']}", reason)
        self.assertIn(f"--command-hash {self.command_hash}", reason)
        self.assertIn("一回限り", reason)
        self.assertIn("偽造防止", reason)
        self.assertIn("摩擦と監査", reason)

    def test_override_allows_once_then_second_attempt_is_denied(self):
        created = self.create_override()
        self.assertEqual(0, created.returncode, created.stderr.decode())

        first = self.run_guard()
        second = self.run_guard()

        self.assertEqual(b"", first.stdout)
        self.assertIn("GUARD OVERRIDE USED", first.stderr.decode())
        self.deny_reason(second)

    def test_override_use_records_who_when_what_rule_and_reason(self):
        self.assertEqual(0, self.create_override().returncode)

        result = self.run_guard()
        event = self.events()[-1]

        self.assertEqual(b"", result.stdout)
        self.assertEqual("override-used", event["kind"])
        self.assertEqual(self.command, event["command"])
        self.assertEqual(self.command_hash, event["command_hash"])
        self.assertEqual(FIXTURE["rule"], event["rule"])
        self.assertEqual(FIXTURE["reason"], event["reason"])
        self.assertEqual(FIXTURE["requested_by"], event["requested_by"])
        self.assertIn("timestamp", event)

    def test_override_is_not_honored_when_audit_event_cannot_be_written(self):
        self.assertEqual(0, self.create_override().returncode)
        self.event_log.mkdir(parents=True)

        result = self.run_guard()

        self.deny_reason(result)
        self.assertNotIn("GUARD OVERRIDE USED", result.stderr.decode())

    def test_source_comment_states_override_is_not_an_unforgeable_boundary(self):
        if not OVERRIDE_TOOL.exists():
            self.fail("override implementation is missing")
        source = OVERRIDE_TOOL.read_text(encoding="utf-8")
        self.assertIn("not an unforgeable boundary", source)
        self.assertIn("friction and auditability", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
