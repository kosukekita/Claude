#!/usr/bin/env python3
"""Comprehensive test suite for guard-charsheet-missing hook."""

import json
import subprocess
import sys
from pathlib import Path

HOOK_PY = Path(__file__).resolve().parent.parent / "guard-charsheet-missing.py"
DISPATCH_JS = Path(__file__).resolve().parent.parent / "dispatch.js"


def run_hook_direct(command: str) -> dict:
    """Run guard-charsheet-missing.py directly via python3 with payload."""
    payload = json.dumps({"tool_input": {"command": command}}).encode("utf-8")
    proc = subprocess.run(
        [sys.executable, str(HOOK_PY)],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    decision = None
    output = proc.stdout.decode("utf-8").strip()
    if output:
        try:
            data = json.loads(output)
            decision = data.get("hookSpecificOutput", {}).get("permissionDecision")
        except json.JSONDecodeError:
            pass
    return {"exit_code": proc.returncode, "decision": decision, "stdout": output, "stderr": proc.stderr.decode("utf-8")}


def run_hook_via_dispatch(command: str) -> dict:
    """Run guard-charsheet-missing via dispatch.js."""
    payload = json.dumps({"tool_input": {"command": command}}).encode("utf-8")
    proc = subprocess.run(
        ["node", str(DISPATCH_JS), "guard-charsheet-missing"],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    decision = None
    output = proc.stdout.decode("utf-8").strip()
    if output:
        try:
            data = json.loads(output)
            decision = data.get("hookSpecificOutput", {}).get("permissionDecision")
        except json.JSONDecodeError:
            pass
    return {"exit_code": proc.returncode, "decision": decision, "stdout": output, "stderr": proc.stderr.decode("utf-8")}


def main():
    passed = 0
    failed = 0

    def assert_case(label: str, command: str, expected_decision: str | None):
        nonlocal passed, failed
        res_direct = run_hook_direct(command)
        res_dispatch = run_hook_via_dispatch(command)

        ok_direct = (res_direct["exit_code"] == 0 and res_direct["decision"] == expected_decision)
        ok_dispatch = (res_dispatch["exit_code"] == 0 and res_dispatch["decision"] == expected_decision)

        if ok_direct and ok_dispatch:
            print(f"PASS: [{label}] decision={expected_decision}")
            passed += 1
        else:
            print(f"FAIL: [{label}] expected={expected_decision}, direct={res_direct}, dispatch={res_dispatch}")
            failed += 1

    print("=== Criteria 1: higgsfield generate create with person words and without sheet -> DENY ===")
    english_words = [
        "person", "people", "man", "woman", "adult", "child", "children", "kid",
        "boy", "girl", "father", "mother", "dad", "mom", "family", "burglar",
        "hand", "hands", "arm", "arms", "leg", "legs", "foot", "feet",
        "finger", "shoulder", "face"
    ]
    for word in english_words:
        cmd = f'higgsfield generate create seedance_2_0 --prompt "A scene showing a {word} in the room"'
        assert_case(f"En person word: {word}", cmd, "deny")

    japanese_words = [
        "人物", "家族", "父", "母", "子ども", "子供", "兄弟", "泥棒",
        "手", "腕", "脚", "足", "指"
    ]
    for word in japanese_words:
        cmd = f'higgsfield generate create seedance_2_0 --prompt "{word}が部屋にいるシーン"'
        assert_case(f"Ja person word: {word}", cmd, "deny")

    print("\n=== Criteria 2: With character_sheet/ reference -> ALLOW ===")
    assert_case(
        "character_sheet space separated",
        'higgsfield generate create seedance_2_0 --prompt "A burglar enters" --image-references 01_analysis/character_sheet/burglar_sheet_v1.png',
        None
    )
    assert_case(
        "character_sheet equals separated",
        'higgsfield generate create seedance_2_0 --prompt "Family dinner" --image-references="01_analysis/character_sheet/family_sheet_v4.png"',
        None
    )
    assert_case(
        "character_sheet single quotes",
        "higgsfield generate create seedance_2_0 --prompt 'A father and son' --image-references '01_analysis/character_sheet/family_sheet_v4.png'",
        None
    )
    assert_case(
        "character_sheet via --image",
        'higgsfield generate create seedance_2_0 --prompt "A woman smiling" --image 01_analysis/character_sheet/family_sheet_v4.png',
        None
    )
    assert_case(
        "character_sheet via --image=",
        'higgsfield generate create seedance_2_0 --prompt "A boy running" --image="character_sheet/boy.png"',
        None
    )

    print("\n=== Criteria 3: NO PERSON / negation -> ALLOW ===")
    assert_case(
        "NO PERSON uppercase",
        'higgsfield generate create seedance_2_0 --prompt "An empty landscape, NO PERSON in sight"',
        None
    )
    assert_case(
        "no person lowercase",
        'higgsfield generate create seedance_2_0 --prompt "an empty street, no person walking"',
        None
    )
    assert_case(
        "NO CHILD",
        'higgsfield generate create seedance_2_0 --prompt "A playground at night with NO CHILD"',
        None
    )
    assert_case(
        "no people",
        'higgsfield generate create seedance_2_0 --prompt "A futuristic city with no people around"',
        None
    )
    assert_case(
        "NOBODY",
        'higgsfield generate create seedance_2_0 --prompt "A dark room, NOBODY inside"',
        None
    )

    print("\n=== Criteria 4: Non-higgsfield commands and other commands -> ALLOW ===")
    assert_case("ls -la", "ls -la", None)
    assert_case("ffmpeg command", "ffmpeg -i in.mp4 -vf scale=1280:720 out.mp4", None)
    assert_case("git status", "git status", None)
    assert_case("python script", "python3 -c 'print(\"hello man\")'", None)
    assert_case("higgsfield generate cost", 'higgsfield generate cost veo3_1 --prompt "A man walking"', None)
    assert_case("higgsfield image generate", 'higgsfield image generate --prompt "A portrait of a woman"', None)
    assert_case("higgsfield without person words", 'higgsfield generate create seedance_2_0 --prompt "A red car driving on an empty highway"', None)

    print(f"\n==========================================")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"==========================================")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
