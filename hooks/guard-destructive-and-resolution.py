#!/usr/bin/env python3
"""Claude Code PreToolUse guard for destructive rm and Higgsfield video settings."""

import json
import os
import sys


SHELL_OPERATORS = {";", "&&", "||", "|", "&", "\n"}
APPROVED_RESOLUTIONS = {"480p", "1080p"}
APPROVED_QUALITIES = {"fast", "high"}
IMAGE_MARKERS = {
    "image",
    "images",
    "image-generate",
    "generate-image",
    "text-to-image",
    "image-to-image",
}


def shell_tokens(command):
    """Return (text, has_unquoted_glob) tokens, preserving command separators."""
    tokens = []
    text = []
    glob = False
    quote = None
    escaped = False
    i = 0

    def emit():
        nonlocal text, glob
        if text:
            tokens.append(("".join(text), glob))
            text = []
            glob = False

    while i < len(command):
        char = command[i]
        if escaped:
            text.append(char)
            escaped = False
        elif quote == "'":
            if char == "'":
                quote = None
            else:
                text.append(char)
        elif quote == '"':
            if char == '"':
                quote = None
            elif char == "\\" and i + 1 < len(command):
                i += 1
                text.append(command[i])
            else:
                text.append(char)
        elif char == "\\":
            escaped = True
        elif char in ("'", '"'):
            quote = char
        elif char.isspace():
            emit()
            if char == "\n":
                tokens.append(("\n", False))
        elif char in ";&|":
            emit()
            if i + 1 < len(command) and command[i + 1] == char and char in "&|":
                tokens.append((char * 2, False))
                i += 1
            else:
                tokens.append((char, False))
        else:
            text.append(char)
            if char in "*?":
                glob = True
            elif char == "[" and "]" in command[i + 1 :]:
                glob = True
        i += 1
    if escaped:
        text.append("\\")
    emit()
    return tokens


def command_segments(tokens):
    segment = []
    for token in tokens:
        if token[0] in SHELL_OPERATORS:
            if segment:
                yield segment
                segment = []
        else:
            segment.append(token)
    if segment:
        yield segment


def is_rm_executable(value):
    return os.path.basename(value).lower() == "rm"


def destructive_rm_reason(segment):
    for index, (value, _) in enumerate(segment):
        if not is_rm_executable(value):
            continue
        recursive = False
        force = False
        operands = []
        options_done = False
        for operand, has_glob in segment[index + 1 :]:
            if not options_done and operand == "--":
                options_done = True
                continue
            if not options_done and operand.startswith("-") and operand != "-":
                option = operand.lstrip("-").lower()
                recursive |= "r" in option or "recursive" in option
                force |= "f" in option or "force" in option
                continue
            options_done = True
            operands.append((operand, has_glob))
        if any(has_glob for _, has_glob in operands):
            return (
                "rm のグロブ削除をブロックしました。対象を明示列挙するか、"
                "グロブ削除を意図するなら該当ファイルを確認してから実行してください。"
            )
        if recursive and force and operands:
            return (
                "rm -rf/-fr によるディレクトリ削除をブロックしました。対象を明示確認し、"
                "必要なら安全な方法で個別に実行してください。"
            )
    return None


def option_value(values, name):
    for index, value in enumerate(values):
        lowered = value.lower()
        if lowered == name and index + 1 < len(values):
            return values[index + 1].lower()
        if lowered.startswith(name + "="):
            return lowered.split("=", 1)[1]
    return None


def higgsfield_reason(segment):
    values = [value for value, _ in segment]
    lowered = [value.lower() for value in values]
    if not any(os.path.basename(value).lower() == "higgsfield" for value in values):
        return None
    # Explicit static-image commands are outside this guard's scope.
    if any(value in IMAGE_MARKERS for value in lowered):
        return None

    resolution = option_value(values, "--resolution")
    quality = option_value(values, "--quality")
    mode = option_value(values, "--mode")
    if resolution is not None and resolution not in APPROVED_RESOLUTIONS:
        return (
            f"Higgsfield 動画の未承認解像度 {resolution!r} をブロックしました。"
            "既定はテスト=480p / 本番=1080p です。意図的に上げる場合は"
            "ユーザー承認を得てから実行してください。"
        )
    if mode == "4k":
        return (
            "Higgsfield 動画の未承認解像度 '4k' をブロックしました。"
            "既定はテスト=480p / 本番=1080p です。意図的に上げる場合は"
            "ユーザー承認を得てから実行してください。"
        )
    if quality is not None and quality not in APPROVED_QUALITIES:
        return (
            f"Higgsfield 動画の未承認品質 {quality!r} をブロックしました。"
            "許可済み品質は fast / high です。ultra 等へ上げる場合は"
            "ユーザー承認を得てから実行してください。"
        )
    return None


def deny(reason):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    command = payload.get("tool_input", {}).get("command")
    if not isinstance(command, str):
        return 0

    segments = list(command_segments(shell_tokens(command)))
    for check in (destructive_rm_reason, higgsfield_reason):
        for segment in segments:
            reason = check(segment)
            if reason:
                deny(reason)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
