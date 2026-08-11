#!/usr/bin/env python3
"""Shared state and classification logic for file snapshot/revert hooks."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


MAX_HASH_BYTES = 50 * 1024 * 1024
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
SHELL_SEPARATORS = {"|", "||", "&", "&&", ";"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_root(environ: Mapping[str, str]) -> Path:
    override = environ.get("CLAUDE_HOOK_STATE_DIR")
    if override:
        return Path(override)
    xdg_state = environ.get("XDG_STATE_HOME")
    if xdg_state:
        return Path(xdg_state) / "claude-hooks" / "file-revert"
    if os.name == "nt" and environ.get("LOCALAPPDATA"):
        return Path(environ["LOCALAPPDATA"]) / "claude-hooks" / "file-revert"
    return Path.home() / ".local" / "state" / "claude-hooks" / "file-revert"


def config_path(environ: Mapping[str, str]) -> Path:
    override = environ.get("CLAUDE_FILE_REVERT_CONFIG")
    if override:
        return Path(override)
    return Path(__file__).with_name("file-revert-config.json")


def configured_mode(environ: Mapping[str, str]) -> str:
    try:
        value = json.loads(config_path(environ).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "audit"
    return "block" if value.get("mode") == "block" else "audit"


def normalized_path(value: str | os.PathLike[str], cwd: str | None = None) -> Path:
    path_value = Path(value).expanduser()
    if not path_value.is_absolute():
        path_value = Path(cwd or os.getcwd()) / path_value
    normalized = os.path.normpath(os.path.abspath(path_value))
    if os.name == "nt":
        normalized = os.path.normcase(normalized)
    return Path(normalized)


def state_key(value: str | os.PathLike[str], cwd: str | None = None) -> str:
    normalized = str(normalized_path(value, cwd)).replace("\\", "/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:40]


def snapshot_path(
    value: str | os.PathLike[str],
    environ: Mapping[str, str],
    cwd: str | None = None,
) -> Path:
    return state_root(environ) / "snapshots" / f"{state_key(value, cwd)}.json"


def audit_log_path(environ: Mapping[str, str]) -> Path:
    return state_root(environ) / "audit.jsonl"


def session_marker_path(session_id: str, environ: Mapping[str, str]) -> Path:
    key = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:40]
    return state_root(environ) / "sessions" / f"{key}.json"


def content_hash(path_value: Path) -> str | None:
    try:
        stat = path_value.stat()
        if not path_value.is_file():
            return None
        if stat.st_size > MAX_HASH_BYTES:
            return f"sz:{stat.st_size}:mt:{stat.st_mtime_ns}"
        digest = hashlib.sha256()
        with path_value.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except (FileNotFoundError, IsADirectoryError, OSError):
        return None


def read_json(path_value: Path) -> dict:
    try:
        value = json.loads(path_value.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def atomic_write_json(path_value: Path, value: dict) -> None:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path_value.parent,
        prefix=f".{path_value.name}.",
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")
        os.replace(temporary_name, path_value)
    except OSError:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def payload_file(payload: dict) -> str | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    for field in ("file_path", "path", "notebook_path"):
        value = tool_input.get(field)
        if isinstance(value, str) and value:
            return value
    return None


def session_id(payload: dict) -> str:
    value = payload.get("session_id")
    return value if isinstance(value, str) and value else "unknown-session"


def shell_segments(tokens: list[str]) -> list[list[str]]:
    segments = []
    current = []
    for token in tokens:
        if token in SHELL_SEPARATORS:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def shell_tokens(command: str) -> list[str]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="|&;<>")
        lexer.whitespace_split = True
        lexer.commenters = ""
        return list(lexer)
    except ValueError:
        return []


def bash_write_targets(command: str, cwd: str | None = None) -> list[Path]:
    """Return only high-confidence shell write targets; unknown forms stay unknown."""
    tokens = shell_tokens(command)
    raw_targets = []
    for index, token in enumerate(tokens[:-1]):
        if token in {">", ">>"}:
            candidate = tokens[index + 1]
            if candidate not in SHELL_SEPARATORS and not candidate.startswith("&"):
                raw_targets.append(candidate)

    for segment in shell_segments(tokens):
        if not segment:
            continue
        executable = os.path.basename(segment[0]).lower()
        args = segment[1:]
        if executable == "tee":
            targets = [value for value in args if not value.startswith("-")]
            if len(targets) == 1:
                raw_targets.append(targets[0])
        elif executable == "sed" and any(
            value == "-i" or value.startswith("-i") for value in args
        ):
            candidates = [value for value in args if not value.startswith("-")]
            if len(candidates) >= 2:
                raw_targets.append(candidates[-1])
        elif executable in {"cp", "mv"}:
            candidates = [value for value in args if not value.startswith("-")]
            if len(candidates) >= 2:
                raw_targets.append(candidates[-1])

    resolved = []
    seen = set()
    for value in raw_targets:
        if value in {"/dev/null", "NUL"}:
            continue
        target = normalized_path(value, cwd)
        key = str(target)
        if key not in seen:
            seen.add(key)
            resolved.append(target)
    return resolved


def update_snapshot(
    path_value: Path,
    tool_name: str,
    environ: Mapping[str, str],
    agent_write: bool,
) -> None:
    current_hash = content_hash(path_value)
    if current_hash is None:
        return
    destination = snapshot_path(path_value, environ)
    state = read_json(destination)
    now = utc_now()
    state.update(
        {
            "path": str(path_value).replace("\\", "/"),
            "last_seen_hash": current_hash,
            "last_seen_at": now,
            "last_seen_by": tool_name,
        }
    )
    if agent_write:
        state["last_agent_write_hash"] = current_hash
        state["last_agent_write_at"] = now
    atomic_write_json(destination, state)


def record_bash(payload: dict, environ: Mapping[str, str]) -> dict:
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        command = ""
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else None
    targets = bash_write_targets(command, cwd)
    for target in targets:
        update_snapshot(target, "Bash", environ, agent_write=True)
    marker = {
        "timestamp": utc_now(),
        "targets": [str(target).replace("\\", "/") for target in targets],
        "high_confidence": bool(targets),
    }
    atomic_write_json(session_marker_path(session_id(payload), environ), marker)
    return marker


def clear_bash_marker(payload: dict, environ: Mapping[str, str]) -> None:
    try:
        session_marker_path(session_id(payload), environ).unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def record_event(payload: dict, environ: Mapping[str, str] | None = None) -> dict:
    active_environ = environ or os.environ
    tool_name = payload.get("tool_name")
    if tool_name == "Bash":
        return record_bash(payload, active_environ)

    clear_bash_marker(payload, active_environ)
    file_value = payload_file(payload)
    if not isinstance(tool_name, str) or not file_value:
        return {"recorded": False}
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else None
    path_value = normalized_path(file_value, cwd)
    update_snapshot(
        path_value,
        tool_name,
        active_environ,
        agent_write=tool_name in WRITE_TOOLS,
    )
    return {"recorded": path_value.exists(), "path": str(path_value)}


def append_audit_event(event: dict, environ: Mapping[str, str]) -> None:
    destination = audit_log_path(environ)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")


def guard_event(payload: dict, environ: Mapping[str, str] | None = None) -> dict:
    active_environ = environ or os.environ
    file_value = payload_file(payload)
    if not file_value:
        return {"decision": "allow", "classification": None}
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else None
    path_value = normalized_path(file_value, cwd)
    current_hash = content_hash(path_value)
    if current_hash is None:
        return {"decision": "allow", "classification": None}
    state = read_json(snapshot_path(path_value, active_environ))
    if not state:
        return {"decision": "allow", "classification": None}

    classification = None
    if current_hash == state.get("last_agent_write_hash"):
        classification = "agent-write"
    elif current_hash != state.get("last_seen_hash"):
        marker = read_json(session_marker_path(session_id(payload), active_environ))
        classification = "ambiguous" if marker else "user-edit"

    mode = configured_mode(active_environ)
    decision = "deny" if classification == "user-edit" and mode == "block" else "allow"
    if classification is not None:
        append_audit_event(
            {
                "timestamp": utc_now(),
                "session_id": session_id(payload),
                "path": str(path_value).replace("\\", "/"),
                "classification": classification,
                "mode": mode,
                "decision": decision,
            },
            active_environ,
        )
    return {"decision": decision, "classification": classification}
