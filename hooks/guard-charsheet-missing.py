#!/usr/bin/env python3
"""Claude Code PreToolUse guard for missing character sheets in Higgsfield video generation."""

import json
import os
import re
import sys

try:
    from hook_observability import json_error_detail, record_fail_open
except ImportError:
    def record_fail_open(*args, **kwargs):
        pass
    def json_error_detail(error):
        return "invalid-json"


DENY_MESSAGE = """キャラクターシートの同梱漏れをブロックしました。

このコマンドのプロンプトには人物を示す語が含まれていますが、
--image-references に character_sheet/ のシートが指定されていません。

同梱すべきシート:
  泥棒が写る → 01_analysis/character_sheet/burglar_sheet_v1.png
  家族が写る → 01_analysis/character_sheet/family_sheet_v4.png

人物が写らないカットなら、プロンプトに NO PERSON / NO CHILD を明記してください。

（この違反は2026-08-13/15/16 に3回発生したため機械ブロック化されました）"""

TARGET_COMMAND_PATTERN = re.compile(r"\bhiggsfield\s+generate\s+create\b", re.IGNORECASE)

ENGLISH_PERSON_WORDS = [
    "person", "people", "man", "woman", "adult", "child", "children", "kid",
    "boy", "girl", "father", "mother", "dad", "mom", "family", "burglar",
    "hand", "hands", "arm", "arms", "leg", "legs", "foot", "feet",
    "finger", "shoulder", "face"
]
ENGLISH_PERSON_PATTERN = re.compile(
    r"\b(?:" + "|".join(ENGLISH_PERSON_WORDS) + r")\b",
    re.IGNORECASE
)

JAPANESE_PERSON_WORDS = [
    "人物", "家族", "父", "母", "子ども", "子供", "兄弟", "泥棒",
    "手", "腕", "脚", "足", "指"
]
JAPANESE_PERSON_PATTERN = re.compile(
    "|".join(map(re.escape, JAPANESE_PERSON_WORDS))
)

NEGATION_PATTERN = re.compile(
    r"\b(?:no\s+person|no\s+child|no\s+people|nobody)\b",
    re.IGNORECASE
)

CHARACTER_SHEET_REF_PATTERN = re.compile(
    r"--(?:image-references|image)(?:=|\s+)[\"']?[^\"'\s]*character_sheet\/",
    re.IGNORECASE
)


def is_target_command(command: str) -> bool:
    """Check if the command contains 'higgsfield generate create'."""
    return bool(TARGET_COMMAND_PATTERN.search(command))


def has_person_word(text: str) -> bool:
    """Check if text mentions a person in English or Japanese."""
    return bool(ENGLISH_PERSON_PATTERN.search(text) or JAPANESE_PERSON_PATTERN.search(text))


def has_negation(text: str) -> bool:
    """Check if text contains explicit person negation (e.g. NO PERSON)."""
    return bool(NEGATION_PATTERN.search(text))


def has_character_sheet_reference(command: str) -> bool:
    """Check if --image-references or --image specifies a character_sheet/ path."""
    return bool(CHARACTER_SHEET_REF_PATTERN.search(command))


def should_block(command: str) -> bool:
    """Return True if command violates the character sheet policy."""
    if not is_target_command(command):
        return False

    if has_negation(command):
        return False

    if not has_person_word(command):
        return False

    if has_character_sheet_reference(command):
        return False

    return True


def deny(reason: str) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


def main() -> int:
    try:
        try:
            payload = json.load(sys.stdin)
        except UnicodeDecodeError as error:
            record_fail_open("guard-charsheet-missing", "invalid-encoding", error)
            return 0
        except json.JSONDecodeError as error:
            record_fail_open("guard-charsheet-missing", json_error_detail(error), error)
            return 0

        if not isinstance(payload, dict):
            record_fail_open("guard-charsheet-missing", "non-object-payload")
            return 0

        tool_input = payload.get("tool_input")
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str):
            record_fail_open("guard-charsheet-missing", "non-string-command")
            return 0

        if should_block(command):
            deny(DENY_MESSAGE)
            return 0

    except Exception as error:
        record_fail_open("guard-charsheet-missing", "unexpected-error", error)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
