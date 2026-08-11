#!/usr/bin/env python3
"""Fail-open JSONL observability shared by Python hooks."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Mapping


def state_root(environ: Mapping[str, str]) -> Path:
    if environ.get("XDG_STATE_HOME"):
        return Path(environ["XDG_STATE_HOME"])
    if os.name == "nt" and environ.get("LOCALAPPDATA"):
        return Path(environ["LOCALAPPDATA"])
    return Path.home() / ".local" / "state"


def event_log_path(environ: Mapping[str, str] | None = None) -> Path:
    active_environ = environ or os.environ
    return state_root(active_environ) / "claude-hooks" / "dispatch-events.jsonl"


def json_error_detail(error: json.JSONDecodeError) -> str:
    """Distinguish surrogate-escaped input bytes from ordinary malformed JSON."""
    if any(0xD800 <= ord(character) <= 0xDFFF for character in error.doc):
        return "invalid-encoding"
    return "invalid-json"


def append_hook_event(
    target: str,
    kind: str,
    detail: str,
    environ: Mapping[str, str] | None = None,
    **fields,
) -> bool:
    """Append one event; observability failure must never block the hook."""
    active_environ = environ or os.environ
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "platform": "windows" if os.name == "nt" else sys.platform,
        "kind": kind,
        "detail": detail,
        **fields,
    }
    try:
        destination = event_log_path(active_environ)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
        return True
    except (OSError, UnicodeError, TypeError, ValueError):
        return False


def record_fail_open(
    target: str,
    detail: str,
    error: Exception | None = None,
    environ: Mapping[str, str] | None = None,
) -> bool:
    fields = {}
    if error is not None:
        fields = {"error_type": type(error).__name__, "error": str(error)}
    return append_hook_event(
        target,
        "fail-open",
        detail,
        environ=environ,
        **fields,
    )
