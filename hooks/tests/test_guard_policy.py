#!/usr/bin/env python3
"""Exercise guard policy cases exclusively through a fixture file."""

import json
import os
from pathlib import Path
import subprocess
import sys


HOOK = Path(__file__).resolve().parents[1] / "guard-destructive-and-resolution.py"
FIXTURES = Path(__file__).with_name("guard-policy-fixtures.json")


def run_fixture(fixture):
    payload = json.dumps({"tool_input": {"command": fixture["command"]}}).encode()
    environ = os.environ.copy()
    environ.pop("VIRTUAL_ENV", None)
    environ.pop("CONDA_PREFIX", None)
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environ,
        check=False,
    )
    stdout = result.stdout.decode().strip()
    warning = result.stderr.decode().strip()
    decision = ""
    if stdout:
        decision = json.loads(stdout).get("hookSpecificOutput", {}).get(
            "permissionDecision", ""
        )
    return result.returncode, decision, stdout, warning


def matches(fixture, status, decision, stdout, warning):
    expected = fixture["expected"]
    markers = fixture.get("expected_warning_all")
    if markers is None:
        marker = fixture.get("expected_warning_contains", "")
        markers = [marker] if marker else []
    if expected == "deny":
        return status == 0 and decision == "deny"
    if expected == "warn":
        return (
            status == 0
            and decision == ""
            and stdout == ""
            and warning != ""
            and "\n" not in warning
            and all(marker in warning for marker in markers)
        )
    if expected == "allow":
        return status == 0 and decision == "" and stdout == "" and warning == ""
    raise ValueError(f"unknown expectation: {expected}")


def main():
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failed = 0
    for fixture in fixtures:
        status, decision, stdout, warning = run_fixture(fixture)
        actual = "deny" if decision == "deny" else "warn" if warning else "allow"
        if matches(fixture, status, decision, stdout, warning):
            print(
                f"PASS {fixture['id']} group={fixture['group']} "
                f"expected={fixture['expected']} actual={actual}"
            )
        else:
            failed += 1
            print(
                f"FAIL {fixture['id']} group={fixture['group']} "
                f"expected={fixture['expected']} actual={actual} status={status} "
                f"stdout={stdout!r} warning={warning!r}"
            )
    print(f"SUMMARY PASS={len(fixtures) - failed} FAIL={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
