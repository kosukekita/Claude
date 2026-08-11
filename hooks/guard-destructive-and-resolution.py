#!/usr/bin/env python3
"""Claude Code PreToolUse guard for destructive rm and Higgsfield video settings."""

import json
import os
import re
import sys


SHELL_OPERATORS = {";", "&&", "||", "|", "&", "\n"}
PIPELINE_BOUNDARIES = {";", "&&", "||", "&", "\n"}
PIPELINE_PRODUCERS = {"curl", "wget"}
PIPELINE_CONSUMERS = {
    "sh",
    "bash",
    "zsh",
    "dash",
    "powershell",
    "pwsh",
    "python",
    "python3",
    "node",
    "perl",
    "ruby",
}
GIT_GLOBAL_OPTIONS_WITH_VALUE = {
    "-c",
    "-C",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--super-prefix",
    "--config-env",
}
SQL_CLIENTS = {"psql", "mysql"}
APPROVED_RESOLUTIONS = {"480p", "1080p"}
APPROVED_QUALITIES = {"fast", "high"}
# Refresh this list from the TYPE=image rows of: higgsfield model list --image
IMAGE_JOB_TYPES = {
    "nano_banana_pro",
    "nano_banana_flash",
    "nano_banana_2_lite",
    "seedream_v5_pro",
    "seedream_v5_lite",
    "seedream_v4_5",
    "gpt_image_2",
    "flux_2",
    "flux_kontext",
    "z_image",
    "grok_image",
    "recraft_v4_1",
    "text2image_soul_v2",
    "soul_location",
    "soul_cinematic",
    "soul_cast",
    "kling_omni_image",
    "openai_hazel",
    "image_auto",
    "outpaint",
    "topaz_image",
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
        elif char == "&" and text and text[-1] in {">", "<"}:
            text.append(char)
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


def command_tokens(segment):
    """Strip common shell wrappers while preserving token metadata."""
    remaining = list(segment)
    while remaining:
        value = remaining[0][0]
        executable = os.path.basename(value).lower()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", value):
            remaining.pop(0)
            continue
        if executable == "sudo":
            remaining.pop(0)
            while remaining and remaining[0][0].startswith("-"):
                option = remaining.pop(0)[0]
                if option in {"-u", "-g", "-h", "-p", "-c", "-t"} and remaining:
                    remaining.pop(0)
            continue
        if executable == "env":
            remaining.pop(0)
            while remaining and (
                remaining[0][0].startswith("-")
                or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", remaining[0][0])
            ):
                remaining.pop(0)
            continue
        if executable == "command":
            remaining.pop(0)
            while remaining and remaining[0][0].startswith("-"):
                remaining.pop(0)
            continue
        break
    return remaining


def destructive_rm_reason(segment):
    segment = command_tokens(segment)
    if not segment or not is_rm_executable(segment[0][0]):
        return None
    recursive = False
    force = False
    operands = []
    options_done = False
    for operand, has_glob in segment[1:]:
        if not options_done and operand == "--":
            options_done = True
            continue
        if not options_done and operand.startswith("--"):
            option = operand[2:].split("=", 1)[0].lower()
            recursive |= option == "recursive"
            force |= option == "force"
            continue
        if not options_done and operand.startswith("-") and operand != "-":
            flags = operand[1:]
            recursive |= "r" in flags.lower()
            force |= "f" in flags.lower()
            continue
        options_done = True
        operands.append((operand, has_glob))
    if any(has_glob for _, has_glob in operands):
        return (
            "rm のグロブ削除をブロックしました。対象を明示列挙するか、"
            "グロブ削除を意図するなら該当ファイルを確認してから実行してください。"
        )
    if recursive and operands:
        if force:
            return (
                "rm -rf/-fr によるディレクトリ削除をブロックしました。対象を明示確認し、"
                "必要なら安全な方法で個別に実行してください。"
            )
        return (
            "rm の再帰削除をブロックしました。対象を明示確認し、"
            "必要なら安全な方法で個別に実行してください。"
        )
    return None


def executable_name(segment):
    unwrapped = command_tokens(segment)
    if not unwrapped:
        return ""
    return os.path.basename(unwrapped[0][0]).lower()


def option_has_short_flag(value, flag):
    return value.startswith("-") and not value.startswith("--") and flag in value[1:]


def git_subcommand_args(unwrapped):
    """Return a Git subcommand and its argv after global options."""
    args = [value for value, _ in unwrapped[1:]]
    index = 0
    while index < len(args):
        value = args[index]
        lowered = value.lower()
        if value == "--":
            index += 1
            break
        if value in GIT_GLOBAL_OPTIONS_WITH_VALUE:
            index += 2
            continue
        if any(
            lowered.startswith(option.lower() + "=")
            for option in GIT_GLOBAL_OPTIONS_WITH_VALUE
            if option.startswith("--")
        ):
            index += 1
            continue
        if (value.startswith("-C") and value != "-C") or (
            value.startswith("-c") and value != "-c"
        ):
            index += 1
            continue
        if value.startswith("-"):
            index += 1
            continue
        return lowered, args[index + 1 :]
    if index < len(args):
        return args[index].lower(), args[index + 1 :]
    return "", []


def git_reason(segment):
    unwrapped = command_tokens(segment)
    if executable_name(unwrapped) != "git":
        return None
    subcommand, args = git_subcommand_args(unwrapped)
    lowered = [value.lower() for value in args]
    if subcommand == "reset" and "--hard" in lowered:
        return "git reset --hard をブロックしました。履歴を破壊しない方法を使ってください。"
    if subcommand == "push":
        force = any(
            value == "--force"
            or value.startswith("--force=")
            or option_has_short_flag(value, "f")
            for value in lowered
        )
        forced_refspec = any(value.startswith("+") for value in args)
        if force or forced_refspec:
            return "git push の force オプションをブロックしました。通常の push を使ってください。"
    if subcommand == "clean":
        force = any(
            value == "--force" or option_has_short_flag(value, "f")
            for value in lowered
        )
        if force:
            return "git clean -f をブロックしました。対象を列挙して回収可能な方法を使ってください。"
    if subcommand == "branch":
        deletes = any(value in {"-d", "--delete"} for value in lowered)
        protected = any(value in {"main", "master"} for value in lowered)
        if deletes and protected:
            return "main/master ブランチの削除をブロックしました。"
    return None


def git_warning_reason(segment):
    unwrapped = command_tokens(segment)
    if executable_name(unwrapped) != "git":
        return None
    subcommand, args = git_subcommand_args(unwrapped)
    if subcommand != "push":
        return None
    lowered = [value.lower() for value in args]
    if any(
        value == "--force-with-lease" or value.startswith("--force-with-lease=")
        for value in lowered
    ):
        return (
            "GIT PUSH WARNING: --force-with-lease はリモート更新を検査しますが、"
            "対象ブランチを取り違えると自分のコミットを失えます。push 先ブランチ名を確認してください。"
        )
    return None


def sql_warning_reason(segments):
    for segment in segments:
        unwrapped = command_tokens(segment)
        if executable_name(unwrapped) not in SQL_CLIENTS:
            continue
        text = " ".join(value for value, _ in unwrapped[1:])
        if re.search(
            r"\b(?:DROP\s+(?:TABLE|DATABASE)|TRUNCATE\s+TABLE)\b",
            text,
            flags=re.IGNORECASE,
        ):
            return (
                "SQL DESTRUCTIVE WARNING: このDDLは対象データを失う操作です。"
                "接続先と対象を確認し、実行前にバックアップを取得してください。"
            )
    return None


def powershell_expression_warning_reason(segments):
    for segment in segments:
        unwrapped = command_tokens(segment)
        if not unwrapped:
            continue
        executable = executable_name(unwrapped)
        text = " ".join(value for value, _ in unwrapped)
        is_powershell_command = executable in {"powershell", "pwsh"}
        is_direct_expression = bool(
            re.fullmatch(r"iex\s*\(.*", unwrapped[0][0], flags=re.IGNORECASE)
            or executable == "invoke-expression"
        )
        if (is_powershell_command or is_direct_expression) and re.search(
            r"\biex\s*\(|\bInvoke-Expression\b", text, flags=re.IGNORECASE
        ):
            return (
                "POWERSHELL EVAL WARNING: 動的実行は入力を任意のコードとして実行します。"
                "内容をファイルへ保存・確認し、明示的なコマンドとして実行してください。"
            )
    return None


def pipeline_chains(tokens):
    """Yield command-stage lists for each control-flow-delimited pipeline."""
    stages = [[]]
    for token in tokens:
        operator = token[0]
        if operator == "|":
            if stages[-1]:
                stages.append([])
        elif operator in PIPELINE_BOUNDARIES:
            completed = [stage for stage in stages if stage]
            if completed:
                yield completed
            stages = [[]]
        else:
            stages[-1].append(token)
    completed = [stage for stage in stages if stage]
    if completed:
        yield completed


def pipeline_reason(tokens):
    for stages in pipeline_chains(tokens):
        executables = [executable_name(stage) for stage in stages]
        for producer_index, producer in enumerate(executables):
            if producer not in PIPELINE_PRODUCERS:
                continue
            for consumer in executables[producer_index + 1 :]:
                if consumer in PIPELINE_CONSUMERS:
                    return (
                        f"{producer} から {consumer} へのパイプ実行をブロックしました。"
                        "取得内容をファイルへ保存・確認してから実行してください。"
                    )
    return None


def pip_install_segment(segment):
    unwrapped = command_tokens(segment)
    if not unwrapped:
        return False
    values = [value for value, _ in unwrapped]
    executable = executable_name(unwrapped)
    if executable == "uv":
        return False
    if re.fullmatch(r"pip(?:\d+(?:\.\d+)*)?", executable):
        return len(values) > 1 and values[1].lower() == "install"
    if re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", executable):
        lowered = [value.lower() for value in values[1:]]
        return len(lowered) > 2 and lowered[0] == "-m" and re.fullmatch(
            r"pip(?:\d+(?:\.\d+)*)?", lowered[1]
        ) is not None and lowered[2] == "install"
    return False


def pip_warning_needed(segments, environ):
    if environ.get("VIRTUAL_ENV") or environ.get("CONDA_PREFIX"):
        return False
    return any(pip_install_segment(segment) for segment in segments)


def option_value(values, name):
    for index, value in enumerate(values):
        lowered = value.lower()
        if lowered == name and index + 1 < len(values):
            return values[index + 1].lower()
        if lowered.startswith(name + "="):
            return lowered.split("=", 1)[1]
    return None


def higgsfield_command(values):
    """Return argv following the Higgsfield executable, or None."""
    for index, value in enumerate(values):
        if os.path.basename(value).lower() == "higgsfield":
            return [item.lower() for item in values[index + 1 :]]
    return None


def higgsfield_job_type(command):
    """Return the job_type from `generate create/cost JOB_TYPE`, if present."""
    if (
        command is not None
        and len(command) >= 3
        and command[0] == "generate"
        and command[1] in {"create", "cost"}
    ):
        return command[2]
    return None


def is_static_image_command(command):
    """Recognize `higgsfield image ...` by its subcommand position."""
    return command is not None and len(command) >= 1 and command[0] == "image"


def higgsfield_reason(segment):
    values = [value for value, _ in segment]
    command = higgsfield_command(values)
    if command is None:
        return None
    if is_static_image_command(command):
        return None
    if higgsfield_job_type(command) in IMAGE_JOB_TYPES:
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

    tokens = shell_tokens(command)
    segments = list(command_segments(tokens))
    for check in (destructive_rm_reason, git_reason, higgsfield_reason):
        for segment in segments:
            reason = check(segment)
            if reason:
                deny(reason)
                return 0
    reason = pipeline_reason(tokens)
    if reason:
        deny(reason)
        return 0
    for segment in segments:
        reason = git_warning_reason(segment)
        if reason:
            print(reason, file=sys.stderr)
    for check in (sql_warning_reason, powershell_expression_warning_reason):
        reason = check(segments)
        if reason:
            print(reason, file=sys.stderr)
    if pip_warning_needed(segments, os.environ):
        print(
            "PIP INSTALL WARNING: global pip install can pollute the interpreter. "
            "Prefer uv add, uv pip install, or an activated virtual environment.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
