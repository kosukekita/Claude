#!/usr/bin/env python3
"""Create and consume auditable one-time destructive-guard overrides."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid
from typing import Mapping

from hook_observability import append_hook_event, state_root


# This is not an unforgeable boundary: an agent with shell access can create the
# same state. It intentionally provides friction and auditability, not security.
RULE_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def command_digest(command: str) -> str:
    return hashlib.sha256(command.encode("utf-8")).hexdigest()


def override_directory(environ: Mapping[str, str]) -> Path:
    return state_root(environ) / "claude-hooks" / "guard-overrides"


def override_token_path(
    rule: str, command_hash: str, environ: Mapping[str, str]
) -> Path:
    key = hashlib.sha256(f"{rule}\0{command_hash}".encode()).hexdigest()
    return override_directory(environ) / f"{key}.json"


def requested_by(environ: Mapping[str, str]) -> str:
    return environ.get("USER") or environ.get("USERNAME") or "unknown"


def create_override(
    rule: str,
    command_hash: str,
    reason: str,
    environ: Mapping[str, str] | None = None,
) -> Path:
    active_environ = environ or os.environ
    if not RULE_PATTERN.fullmatch(rule):
        raise ValueError("rule must contain only lowercase letters, digits, and hyphens")
    if not HASH_PATTERN.fullmatch(command_hash):
        raise ValueError("command hash must be 64 lowercase hexadecimal characters")
    if not reason.strip():
        raise ValueError("reason must not be empty")
    destination = override_token_path(rule, command_hash, active_environ)
    destination.parent.mkdir(parents=True, exist_ok=True)
    token = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_by": requested_by(active_environ),
        "rule": rule,
        "command_hash": command_hash,
        "reason": reason.strip(),
    }
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(token, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")
    return destination


def consume_override(
    command: str,
    rule: str,
    environ: Mapping[str, str] | None = None,
) -> dict | None:
    """Atomically consume a matching token and record use before allowing."""
    active_environ = environ or os.environ
    command_hash = command_digest(command)
    source = override_token_path(rule, command_hash, active_environ)
    claim = source.with_name(f".{source.name}.{os.getpid()}.{uuid.uuid4().hex}.consuming")
    try:
        source.rename(claim)
    except OSError:
        return None
    try:
        token = json.loads(claim.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        token = None
    finally:
        try:
            claim.unlink()
        except OSError:
            pass
    if not isinstance(token, dict):
        return None
    if token.get("rule") != rule or token.get("command_hash") != command_hash:
        return None
    recorded = append_hook_event(
        "guard-destructive-and-resolution",
        "override-used",
        "one-time-override-consumed",
        environ=active_environ,
        command=command,
        command_hash=command_hash,
        rule=rule,
        reason=token.get("reason", ""),
        requested_by=token.get("requested_by", "unknown"),
        override_created_at=token.get("created_at"),
    )
    return token if recorded else None


def override_instruction(command: str, rule: str) -> str:
    command_hash = command_digest(command)
    return (
        "OVERRIDE: 一回限り解除（エージェント偽造防止の防壁ではなく、摩擦と監査のみ）: "
        "python3 ~/.claude/hooks/guard_override.py create "
        f"--rule {rule} --command-hash {command_hash} --reason \"<理由>\""
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    create = subparsers.add_parser("create", help="create one one-time override")
    create.add_argument("--rule", required=True)
    create.add_argument("--command-hash", required=True)
    create.add_argument("--reason", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        destination = create_override(args.rule, args.command_hash, args.reason)
    except (OSError, ValueError) as error:
        print(f"OVERRIDE CREATE ERROR: {error}", file=sys.stderr)
        return 2
    print(f"ONE-TIME OVERRIDE CREATED: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
