#!/usr/bin/env python3
"""PreToolUse hook: audit or block writes based on stale file contents."""

import json
import sys

from file_snapshot_common import guard_event


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0
    try:
        result = guard_event(payload)
    except OSError:
        return 0
    if result["decision"] == "deny":
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "REVERT GUARD: the file changed on disk since the last "
                            "Read/Write/Edit. Re-read the current file and reconcile "
                            "the change before editing."
                        ),
                    }
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
