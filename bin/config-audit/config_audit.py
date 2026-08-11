#!/usr/bin/env python3
"""Deterministic, read-only checks for the Claude configuration repository."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class Finding:
    """One stable, evidence-backed audit finding."""

    kind: str
    target: str
    location: str
    summary: str
    evidence: dict[str, Any] = field(default_factory=dict)
    value: int | float | str | None = None

    @property
    def finding_id(self) -> str:
        return f"{self.kind}:{self.target}"


@dataclass(frozen=True)
class ReportItem:
    status: str
    finding: Finding


@dataclass(frozen=True)
class AuditDelta:
    new_or_changed: list[ReportItem]
    resolved: list[Finding]
    next_state: dict[str, Any]

    @property
    def should_notify(self) -> bool:
        return bool(self.new_or_changed or self.resolved)


@dataclass(frozen=True)
class AuditRun:
    report: str
    report_path: Path
    delta: AuditDelta
    email_sent: bool


def _line_number(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return number
    return 1


def _source_lines(path: Path) -> Iterable[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    return enumerate(text.splitlines(), start=1)


def _resolve_reference(raw: str, source: Path, claude_dir: Path) -> Path:
    home_dir = claude_dir.parent
    if raw == "~" or raw == "$HOME":
        return home_dir
    if raw.startswith("~/"):
        return home_dir / raw.removeprefix("~/")
    if raw.startswith("$HOME/"):
        return home_dir / raw.removeprefix("$HOME/")
    if raw.startswith(("agents/", "bin/", "hooks/", "improvements/", "projects/")):
        return claude_dir / raw
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    local = source.parent / raw.removeprefix("./")
    if local.exists() or "/skills/" not in str(source):
        return local
    cross_skill = [
        path
        for path in (claude_dir / "skills").glob(f"*/{raw}")
        if path.exists()
    ]
    return cross_skill[0] if len(cross_skill) == 1 else local


def _is_file_reference(raw: str, source: Path) -> bool:
    if any(marker in raw for marker in ("...", "*", "%", "[", "]", "(", ")")):
        return False
    if raw.startswith(("--", "/api/", "/v1/", "/health", "/rpc")):
        return False
    if raw.startswith("./") and "/skills/" in str(source):
        return False
    if raw.startswith("/") and not raw.startswith("/home/"):
        return Path(raw).suffix in {
            ".cjs",
            ".js",
            ".json",
            ".jsonl",
            ".md",
            ".mjs",
            ".ps1",
            ".py",
            ".service",
            ".sh",
            ".timer",
            ".toml",
            ".yaml",
            ".yml",
        }
    if raw.startswith(("~", "$HOME/", "/home/", "./", "../")):
        return True
    if source.name in {"CLAUDE.md", "settings.json"}:
        return "/" in raw or bool(Path(raw).suffix)
    allowed_skill_prefixes = (
        "agents/",
        "assets/",
        "bin/",
        "docs/",
        "hooks/",
        "reference/",
        "references/",
        "scripts/",
        "templates/",
    )
    return raw.startswith(allowed_skill_prefixes)


def find_dead_refs(
    sources: Iterable[Path],
    claude_dir: Path,
    *,
    platform_name: str | None = None,
) -> list[Finding]:
    """Find nonexistent file references written inside Markdown code spans."""

    platform_name = platform_name or sys.platform
    findings: list[Finding] = []
    path_pattern = re.compile(r"`([^`\n]+)`")
    for source in sources:
        for line_number, line in _source_lines(source):
            if re.search(
                r"生成される|無ければ|if you prefer|optional", line, re.IGNORECASE
            ):
                continue
            for raw in path_pattern.findall(line):
                raw = raw.strip().strip('"\'')
                if platform_name != "win32" and re.search(
                    r"\bWindows\b|\bwin32\b", line, re.IGNORECASE
                ):
                    continue
                if platform_name != "win32" and raw.lower().endswith((".exe", ".ps1")):
                    continue
                if (
                    "://" in raw
                    or any(char in raw for char in "*{}<>")
                    or " " in raw
                    or not _is_file_reference(raw, source)
                ):
                    continue
                resolved = _resolve_reference(raw, source, claude_dir)
                if resolved.exists():
                    continue
                findings.append(
                    Finding(
                        kind="dead-ref",
                        target=raw,
                        location=f"{source}:{line_number}",
                        summary=f"参照先が存在しません: {raw}",
                        evidence={
                            "line_text": line.strip(),
                            "resolved_target": str(resolved),
                            "exists": False,
                            "check": "Path.exists() == False",
                        },
                    )
                )
    return findings


def find_dead_skill_refs(
    sources: Iterable[Path], available_skills: set[str]
) -> list[Finding]:
    """Find emphasized skill names that do not resolve to an active skill."""

    findings: list[Finding] = []
    emphasized_pattern = re.compile(
        r"\*\*([A-Za-z][A-Za-z0-9:_-]*)\*\*\s*スキル"
    )
    plain_pattern = re.compile(
        r"(?<![A-Za-z0-9_&])([A-Za-z][A-Za-z0-9_]*[-:][A-Za-z0-9:_-]+)"
        r"\s+スキル"
    )
    call_pattern = re.compile(r"Skill\(([^)]+)\)")
    for source in sources:
        for line_number, line in _source_lines(source):
            referenced = set(emphasized_pattern.findall(line))
            referenced.update(plain_pattern.findall(line))
            for raw_call in call_pattern.findall(line):
                cleaned = raw_call.removeprefix("skill=").strip().strip('"\'')
                cleaned = cleaned.removesuffix(":*")
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9:_-]*", cleaned):
                    referenced.add(cleaned)
            for skill_name in sorted(referenced - available_skills):
                findings.append(
                    Finding(
                        kind="dead-ref",
                        target=f"skill:{skill_name}",
                        location=f"{source}:{line_number}",
                        summary=f"参照スキル名が存在しません: {skill_name}",
                        evidence={
                            "line_text": line.strip(),
                            "resolved_name": skill_name,
                            "exists": False,
                            "check": "name not present in active SKILL.md frontmatter",
                        },
                    )
                )
    return findings


def find_dead_memlinks(memory_dir: Path) -> list[Finding]:
    """Find wiki links whose corresponding memory Markdown file is absent."""

    findings: list[Finding] = []
    pattern = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    for source in sorted(memory_dir.glob("*.md")):
        for line_number, line in _source_lines(source):
            for raw_target in pattern.findall(line):
                filename = raw_target if raw_target.endswith(".md") else f"{raw_target}.md"
                resolved = memory_dir / filename
                if resolved.exists():
                    continue
                findings.append(
                    Finding(
                        kind="dead-memlink",
                        target=raw_target,
                        location=f"{source}:{line_number}",
                        summary=f"記憶リンク先が存在しません: {raw_target}",
                        evidence={
                            "line_text": line.strip(),
                            "resolved_target": str(resolved),
                            "exists": False,
                            "check": "Path.exists() == False",
                        },
                    )
                )
    return findings


def find_memory_index_orphans(memory_dir: Path) -> list[Finding]:
    """Find index entries without files and memory files absent from the index."""

    index = memory_dir / "MEMORY.md"
    text = index.read_text(encoding="utf-8")
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")
    indexed: dict[str, int] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        for target in link_pattern.findall(line):
            indexed.setdefault(target, line_number)

    findings: list[Finding] = []
    for target, line_number in indexed.items():
        resolved = memory_dir / target
        if not resolved.exists():
            findings.append(
                Finding(
                    kind="mem-index",
                    target=target,
                    location=f"{index}:{line_number}",
                    summary=f"索引にある記憶ファイルが存在しません: {target}",
                    evidence={
                        "resolved_target": str(resolved),
                        "exists": False,
                        "check": "Path.exists() == False",
                    },
                )
            )

    for memory_file in sorted(memory_dir.glob("*.md")):
        if memory_file.name == "MEMORY.md" or memory_file.name in indexed:
            continue
        findings.append(
            Finding(
                kind="mem-index",
                target=memory_file.name,
                location=f"{memory_file}:1",
                summary=f"実ファイルが MEMORY.md の索引にありません: {memory_file.name}",
                evidence={
                    "index": str(index),
                    "exists": True,
                    "check": "filename not present in parsed MEMORY.md links",
                },
            )
        )
    return findings


def _iter_hook_commands(settings: dict[str, Any]) -> Iterable[str]:
    for groups in settings.get("hooks", {}).values():
        for group in groups:
            for hook in group.get("hooks", []):
                command = hook.get("command")
                if isinstance(command, str):
                    yield command


def find_hook_noops(
    claude_dir: Path,
    *,
    platform_name: str | None = None,
    command_exists: Callable[[str], bool] | None = None,
) -> list[Finding]:
    """Reproduce dispatch.js resolution and report hooks with no runnable target."""

    platform_name = platform_name or sys.platform
    command_exists = command_exists or (lambda command: shutil.which(command) is not None)
    settings_path = claude_dir / "settings.json"
    settings_text = settings_path.read_text(encoding="utf-8")
    settings = json.loads(settings_text)
    hooks_dir = claude_dir / "hooks"
    findings: list[Finding] = []

    for command in _iter_hook_commands(settings):
        match = re.search(r"dispatch\.js[\"']?\s+([A-Za-z0-9_.-]+)", command)
        if not match:
            continue
        target = match.group(1)
        base = Path(target).stem
        if platform_name == "win32":
            extensions = [".mjs", ".cjs", ".js", ".ps1", ".py", ".sh"]
        else:
            extensions = [".mjs", ".cjs", ".js", ".sh", ".py", ".ps1"]
        candidates = [f"{base}{extension}" for extension in extensions]
        available = [name for name in candidates if (hooks_dir / name).exists()]

        runnable = False
        for name in available:
            extension = Path(name).suffix
            if extension == ".ps1" and platform_name != "win32":
                runnable = command_exists("pwsh") or command_exists("powershell")
            elif extension == ".sh" and platform_name == "win32":
                runnable = command_exists("bash")
            else:
                runnable = True
            if runnable:
                break
        if runnable:
            continue

        missing_commands: list[str] = []
        if any(name.endswith(".ps1") for name in available) and platform_name != "win32":
            missing_commands = [
                command_name
                for command_name in ("pwsh", "powershell")
                if not command_exists(command_name)
            ]
        findings.append(
            Finding(
                kind="hook-noop",
                target=base,
                location=f"{settings_path}:{_line_number(settings_text, base)}",
                summary=f"このOSで実行可能なフック実体がありません: {base}",
                evidence={
                    "candidates": candidates,
                    "available_files": available,
                    "missing_commands": missing_commands,
                    "platform": platform_name,
                    "check": "dispatch.js extension priority reproduced",
                },
            )
        )
    return findings


def find_size(claude_md: Path, previous_value: int | None = None) -> Finding:
    """Measure CLAUDE.md with an explicit, deterministic token approximation."""

    byte_count = len(claude_md.read_bytes())
    approximate_tokens = math.ceil(byte_count / 4)
    delta = None if previous_value is None else approximate_tokens - previous_value
    return Finding(
        kind="size",
        target=str(claude_md),
        location=str(claude_md),
        summary=(
            f"CLAUDE.md は約 {approximate_tokens:,} tokens "
            "（推奨 1,000 未満）"
        ),
        value=approximate_tokens,
        evidence={
            "absolute_path": str(claude_md.resolve()),
            "measured_value": approximate_tokens,
            "previous_value": previous_value,
            "delta": delta,
            "measurement_method": "approx: ceil(UTF-8 byte count / 4)",
        },
    )


def _walk_json(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _explicit_skill_calls(log_file: Path) -> Iterable[str]:
    for line in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        for item in _walk_json(record):
            if item.get("name") != "Skill":
                continue
            arguments = item.get("input")
            if isinstance(arguments, dict) and isinstance(arguments.get("skill"), str):
                yield arguments["skill"]


def _skill_name(skill_file: Path) -> str:
    for line in skill_file.read_text(encoding="utf-8").splitlines():
        match = re.match(r"name:\s*(.+?)\s*$", line)
        if match:
            return match.group(1).strip('"\'')
    return skill_file.parent.name


def find_unused_skills(skills_dir: Path, logs_dir: Path) -> list[Finding]:
    """Report skills with zero explicit Skill tool calls in available logs."""

    skill_files = _active_skill_files(skills_dir)
    log_files = sorted(logs_dir.rglob("*.jsonl"))
    used_skill_names: set[str] = set()
    for log_file in log_files:
        for skill_name in _explicit_skill_calls(log_file):
            used_skill_names.add(skill_name)

    findings: list[Finding] = []
    for skill_file in skill_files:
        skill_name = _skill_name(skill_file)
        if skill_name in used_skill_names:
            continue
        findings.append(
            Finding(
                kind="skill-unused",
                target=skill_name,
                location=f"{skill_file}:1",
                summary=f"呼び出し実績ゼロ（要人間判断）: {skill_name}",
                value=0,
                evidence={
                    "skill_name": skill_name,
                    "log_files_scanned": len(log_files),
                    "explicit_call_count": 0,
                    "glob": "**/*.jsonl",
                },
            )
        )
    return findings


def _journal_timestamp(entry: dict[str, Any]) -> str:
    raw = str(entry.get("__REALTIME_TIMESTAMP", ""))
    try:
        timestamp = int(raw) / 1_000_000
    except ValueError:
        return raw or "unknown"
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def find_systemd_user_unit_failures(
    entries: Iterable[dict[str, Any]],
) -> list[Finding]:
    """Find systemd user-unit failures while preserving the original journal line."""

    failure_pattern = re.compile(
        r"\b(failed|failure|exit-code|status=[1-9][0-9]*)\b", re.IGNORECASE
    )
    by_unit: dict[str, Finding] = {}
    for entry in entries:
        if entry.get("_COMM") != "systemd" and entry.get("SYSLOG_IDENTIFIER") != "systemd":
            continue
        unit = entry.get("_SYSTEMD_USER_UNIT")
        message = entry.get("MESSAGE")
        if not isinstance(unit, str) or not isinstance(message, str):
            continue
        if not failure_pattern.search(message):
            continue
        named_unit = re.search(
            r"Failed to (?:start|stop) ([^\s]+\.(?:service|timer))", message
        )
        if named_unit:
            unit = named_unit.group(1)
        if not unit.endswith((".service", ".timer")):
            continue
        failure_time = _journal_timestamp(entry)
        by_unit[unit] = Finding(
            kind="hook-fail",
            target=unit,
            location=f"journalctl:{failure_time}",
            summary=f"直近7日の journal に失敗記録があります: {unit}",
            evidence={
                "unit": unit,
                "failure_time": failure_time,
                "journal_message": message,
            },
        )
    return sorted(by_unit.values(), key=lambda finding: finding.target)


def _parse_incident_date(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_mtime(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def find_unreflected_incidents(
    incidents_path: Path, claude_md: Path, hooks_dir: Path
) -> list[Finding]:
    """Find incidents newer than both rule and hook updates."""

    claude_mtime = claude_md.stat().st_mtime
    hook_files = [path for path in hooks_dir.iterdir() if path.is_file()]
    hooks_latest_mtime = max(path.stat().st_mtime for path in hook_files)
    findings: list[Finding] = []
    for line_number, line in _source_lines(incidents_path):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        raw_date = record.get("ts") or record.get("date")
        if not isinstance(raw_date, str):
            continue
        incident_time = _parse_incident_date(raw_date).timestamp()
        if claude_mtime > incident_time or hooks_latest_mtime > incident_time:
            continue
        target = f"line-{line_number}:{raw_date}"
        findings.append(
            Finding(
                kind="incident-unreflected",
                target=target,
                location=f"{incidents_path}:{line_number}",
                summary=f"設定への反映が確認できない事故記録: {raw_date}",
                evidence={
                    "incident_date": raw_date,
                    "claude_mtime": _format_mtime(claude_mtime),
                    "hooks_latest_mtime": _format_mtime(hooks_latest_mtime),
                },
            )
        )
    return findings


def _finding_to_record(finding: Finding) -> dict[str, Any]:
    return {
        "kind": finding.kind,
        "target": finding.target,
        "location": finding.location,
        "summary": finding.summary,
        "evidence": finding.evidence,
        "value": finding.value,
    }


def _finding_from_record(record: dict[str, Any]) -> Finding:
    return Finding(
        kind=str(record["kind"]),
        target=str(record["target"]),
        location=str(record["location"]),
        summary=str(record["summary"]),
        evidence=dict(record.get("evidence", {})),
        value=record.get("value"),
    )


def validate_finding_evidence(finding: Finding) -> None:
    """Reject any finding that cannot be verified from its rendered evidence."""

    required_by_kind = {
        "dead-memlink": {"line_text", "resolved_target", "exists", "check"},
        "hook-noop": {
            "candidates",
            "available_files",
            "missing_commands",
            "platform",
            "check",
        },
        "mem-index": {"check"},
        "size": {
            "absolute_path",
            "measured_value",
            "previous_value",
            "delta",
            "measurement_method",
        },
        "skill-unused": {
            "skill_name",
            "log_files_scanned",
            "explicit_call_count",
            "glob",
        },
        "hook-fail": {"unit", "failure_time", "journal_message"},
        "incident-unreflected": {
            "incident_date",
            "claude_mtime",
            "hooks_latest_mtime",
        },
    }
    if not finding.location:
        raise ValueError(f"finding has no evidence location: {finding.finding_id}")
    if finding.kind == "dead-ref":
        common = {"line_text", "exists", "check"}
        missing = common - finding.evidence.keys()
        if not ({"resolved_target", "resolved_name"} & finding.evidence.keys()):
            missing.add("resolved_target|resolved_name")
    else:
        required = required_by_kind.get(finding.kind)
        if required is None:
            raise ValueError(f"unknown finding kind: {finding.kind}")
        missing = required - finding.evidence.keys()
    if missing:
        raise ValueError(
            f"finding evidence incomplete ({finding.finding_id}): "
            + ", ".join(sorted(missing))
        )


def compare_with_state(
    current_findings: Iterable[Finding],
    previous_state: dict[str, Any],
    *,
    size_change_threshold: int,
) -> AuditDelta:
    """Compare current findings with persisted state using stable finding IDs."""

    previous = previous_state.get("findings", {})
    if not isinstance(previous, dict):
        raise ValueError("state.findings must be an object")
    current = {finding.finding_id: finding for finding in current_findings}
    new_or_changed: list[ReportItem] = []
    for finding_id, finding in sorted(current.items()):
        old_record = previous.get(finding_id)
        if old_record is None:
            new_or_changed.append(ReportItem(status="new", finding=finding))
            continue
        if finding.kind != "size":
            continue
        old_value = old_record.get("value")
        if not isinstance(old_value, (int, float)) or not isinstance(
            finding.value, (int, float)
        ):
            continue
        if abs(finding.value - old_value) >= size_change_threshold:
            new_or_changed.append(ReportItem(status="changed", finding=finding))

    resolved = [
        _finding_from_record(record)
        for finding_id, record in sorted(previous.items())
        if finding_id not in current
    ]
    next_state = {
        "version": 1,
        "findings": {
            finding_id: _finding_to_record(finding)
            for finding_id, finding in sorted(current.items())
        },
    }
    return AuditDelta(
        new_or_changed=new_or_changed,
        resolved=resolved,
        next_state=next_state,
    )


def read_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {"version": 1, "findings": {}}
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("version") != 1 or not isinstance(state.get("findings"), dict):
        raise ValueError(f"unsupported or invalid state: {state_path}")
    return state


def write_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_name(f".{state_path.name}.tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(state_path)


def render_report(delta: AuditDelta) -> str:
    """Render only newly changed and resolved findings with their evidence."""

    lines = [
        "Claude config-audit 週次レポート",
        "",
        (
            f"新規・変更: {len(delta.new_or_changed)} / "
            f"解消: {len(delta.resolved)}"
        ),
    ]
    for item in delta.new_or_changed:
        finding = item.finding
        label = "NEW" if item.status == "new" else "CHANGED"
        lines.extend(
            [
                "",
                f"[{label}] {finding.kind}: {finding.summary}",
                f"  ID: {finding.finding_id}",
                f"  location: {finding.location}",
                f"  target: {finding.target}",
                "  evidence:",
            ]
        )
        for key, value in finding.evidence.items():
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
            lines.append(f"    {key}: {rendered}")

    for finding in delta.resolved:
        lines.append(
            f"\n[RESOLVED] {finding.kind}: {finding.target} "
            f"(previous: {finding.location})"
        )

    if any(
        item.finding.kind == "skill-unused" for item in delta.new_or_changed
    ):
        lines.extend(
            [
                "",
                "skill-unused の読み方:",
                "- 明示的な Skill ツール呼び出ししか数えていません。",
                "- Windows機の使用実績は不可視です。",
                "- 他スキルからの依存・ルーティング先として使われている場合は、"
                "0回でも必要です。",
            ]
        )

    lines.extend(
        [
            "",
            "通知: " + ("送信対象です" if delta.should_notify else "送信しません"),
        ]
    )
    return "\n".join(lines) + "\n"


def _active_skill_files(skills_dir: Path) -> list[Path]:
    return sorted(
        path / "SKILL.md"
        for path in skills_dir.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def _memory_dir(claude_dir: Path) -> Path:
    preferred = claude_dir / "projects" / "-home-kita--claude" / "memory"
    if preferred.is_dir():
        return preferred
    candidates = sorted(
        path.parent
        for path in (claude_dir / "projects").glob("*/memory/MEMORY.md")
    )
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError(
        "cannot uniquely resolve global memory directory under "
        f"{claude_dir / 'projects'}"
    )


def read_journal_entries() -> list[dict[str, Any]]:
    completed = subprocess.run(
        [
            "journalctl",
            "--user",
            "--since",
            "7 days ago",
            "--no-pager",
            "-o",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"journalctl failed ({completed.returncode}): {completed.stderr.strip()}"
        )
    entries: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid journal JSON: {error}") from error
        if isinstance(value, dict):
            entries.append(value)
    return entries


def send_report_email(report_path: Path) -> None:
    mailer = Path(__file__).with_name("send_mail.mjs")
    completed = subprocess.run(
        ["/usr/bin/node", str(mailer), str(report_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"mail sender failed ({completed.returncode}): {completed.stderr.strip()}"
        )


def _previous_size_value(
    state: dict[str, Any], claude_md: Path
) -> int | None:
    record = state.get("findings", {}).get(f"size:{claude_md}")
    if not isinstance(record, dict):
        return None
    value = record.get("value")
    return value if isinstance(value, int) else None


def run_audit(
    *,
    claude_dir: Path,
    output_dir: Path,
    size_change_threshold: int,
    dry_run: bool,
    journal_entries: Iterable[dict[str, Any]] | None = None,
    mailer: Callable[[Path], None] = send_report_email,
) -> AuditRun:
    """Run all checks, persist state/report, and optionally send one email."""

    if size_change_threshold < 1:
        raise ValueError("size_change_threshold must be at least 1")
    required = [
        claude_dir / "CLAUDE.md",
        claude_dir / "settings.json",
        claude_dir / "hooks",
        claude_dir / "skills",
        claude_dir / "projects",
        claude_dir / "improvements" / "incidents.jsonl",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("required audit inputs missing: " + ", ".join(missing))

    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / "state.json"
    state = read_state(state_path)
    claude_md = claude_dir / "CLAUDE.md"
    settings = claude_dir / "settings.json"
    skills_dir = claude_dir / "skills"
    projects_dir = claude_dir / "projects"
    memory_dir = _memory_dir(claude_dir)
    incidents = claude_dir / "improvements" / "incidents.jsonl"
    hooks_dir = claude_dir / "hooks"
    skill_files = _active_skill_files(skills_dir)
    sources = [claude_md, settings, *skill_files]
    skill_names = {_skill_name(skill_file) for skill_file in skill_files}

    findings: list[Finding] = [
        find_size(claude_md, _previous_size_value(state, claude_md)),
        *find_dead_refs(sources, claude_dir),
        *find_dead_skill_refs(sources, skill_names),
        *find_dead_memlinks(memory_dir),
        *find_memory_index_orphans(memory_dir),
        *find_hook_noops(claude_dir),
        *find_unused_skills(skills_dir, projects_dir),
        *find_unreflected_incidents(incidents, claude_md, hooks_dir),
    ]
    if journal_entries is None:
        journal_entries = read_journal_entries()
    findings.extend(find_systemd_user_unit_failures(journal_entries))
    for finding in findings:
        validate_finding_evidence(finding)

    delta = compare_with_state(
        findings,
        state,
        size_change_threshold=size_change_threshold,
    )
    report = render_report(delta)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    report_path = output_dir / f"report-{timestamp}.txt"
    report_path.write_text(report, encoding="utf-8")
    write_state(state_path, delta.next_state)

    email_sent = False
    if delta.should_notify and not dry_run:
        mailer(report_path)
        email_sent = True
    return AuditRun(
        report=report,
        report_path=report_path,
        delta=delta,
        email_sent=email_sent,
    )


def _load_config(config_path: Path) -> dict[str, Any]:
    value = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"config must be an object: {config_path}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--claude-dir", type=Path, default=Path.home() / ".claude")
    parser.add_argument(
        "--output-dir", type=Path, default=Path.home() / "media-out/config-audit"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("config.json"),
    )
    parser.add_argument("--size-change-threshold", type=int)
    arguments = parser.parse_args(argv)
    try:
        config = _load_config(arguments.config)
        threshold = arguments.size_change_threshold
        if threshold is None:
            threshold = int(config["size_change_threshold"])
        result = run_audit(
            claude_dir=arguments.claude_dir.expanduser().resolve(),
            output_dir=arguments.output_dir.expanduser().resolve(),
            size_change_threshold=threshold,
            dry_run=arguments.dry_run,
        )
        if arguments.dry_run:
            sys.stdout.write(result.report)
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
