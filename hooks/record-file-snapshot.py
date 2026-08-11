#!/usr/bin/env python3
"""PostToolUse hook: record agent-observed and agent-written file hashes."""

import json
import sys

from file_snapshot_common import record_event as record_snapshot_event
from hook_observability import json_error_detail, record_fail_open


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except UnicodeDecodeError as error:
        record_fail_open("record-file-snapshot", "invalid-encoding", error)
        return 0
    except json.JSONDecodeError as error:
        record_fail_open("record-file-snapshot", json_error_detail(error), error)
        return 0
    if not isinstance(payload, dict):
        record_fail_open("record-file-snapshot", "non-object-payload")
        return 0
    try:
        record_snapshot_event(payload)
    except OSError as error:
        record_fail_open("record-file-snapshot", "state-write-error", error)
        return 0
    except Exception as error:
        record_fail_open("record-file-snapshot", "unexpected-error", error)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
