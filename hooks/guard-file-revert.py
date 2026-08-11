#!/usr/bin/env python3
"""PreToolUse hook: audit or block writes based on stale file contents."""

import json
import sys

from file_snapshot_common import guard_event
from hook_observability import json_error_detail, record_fail_open


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except UnicodeDecodeError as error:
        record_fail_open("guard-file-revert", "invalid-encoding", error)
        return 0
    except json.JSONDecodeError as error:
        record_fail_open("guard-file-revert", json_error_detail(error), error)
        return 0
    if not isinstance(payload, dict):
        record_fail_open("guard-file-revert", "non-object-payload")
        return 0
    try:
        result = guard_event(payload)
    except OSError as error:
        record_fail_open("guard-file-revert", "state-read-write-error", error)
        return 0
    except Exception as error:
        record_fail_open("guard-file-revert", "unexpected-error", error)
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
