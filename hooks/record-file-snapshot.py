#!/usr/bin/env python3
"""PostToolUse hook: record agent-observed and agent-written file hashes."""

import json
import sys

from file_snapshot_common import record_event


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0
    try:
        record_event(payload)
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
