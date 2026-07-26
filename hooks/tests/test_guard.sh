#!/usr/bin/env bash
set -u

HOOK="${HOME}/.claude/hooks/guard-destructive-and-resolution.py"
SETTINGS="${HOME}/.claude/settings.json"
passed=0
failed=0

run_case() {
  local expectation="$1"
  local label="$2"
  local command="$3"
  local output status decision
  output="$(python3 -c 'import json,sys; print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "$command" | "$HOOK")"
  status=$?
  decision="$(printf '%s' "$output" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null)"
  if { [[ "$expectation" == deny ]] && { [[ $status -ne 0 ]] || [[ "$decision" == deny ]]; }; } ||
     { [[ "$expectation" == allow ]] && [[ $status -eq 0 ]] && [[ "$decision" != deny ]]; }; then
    printf 'PASS: %s\n' "$label"
    passed=$((passed + 1))
  else
    printf 'FAIL: %s (status=%s decision=%s output=%s)\n' "$label" "$status" "$decision" "$output"
    failed=$((failed + 1))
  fi
}

run_case deny  "1 rm glob is denied" \
  'rm -f /tmp/x/*.png'
run_case allow "2 explicit rm paths are allowed" \
  'rm -f /tmp/x/a.png /tmp/x/b.png'
run_case deny  "3 Higgsfield 720p is denied" \
  'higgsfield generate create seedance_2_0 --resolution 720p --prompt demo'
run_case deny  "4a Higgsfield ultra is denied" \
  'higgsfield generate create veo3_1 --quality ultra --prompt demo'
run_case deny  "4b Higgsfield 4k is denied" \
  'higgsfield generate create veo3_1 --resolution=4k --prompt demo'
run_case allow "4c Higgsfield 480p is allowed" \
  'higgsfield generate create seedance_2_0 --resolution 480p'
run_case allow "4d Higgsfield 1080p/high is allowed" \
  'higgsfield generate create veo3_1 --resolution=1080p --quality high'
run_case deny  "4e Higgsfield Kling --mode 4k is denied" \
  'higgsfield generate create kling3_0 --mode 4k'
run_case allow "4f Higgsfield Kling --mode std is allowed" \
  'higgsfield generate create kling3_0 --mode std'
run_case allow "5a ls is allowed" 'ls -la'
run_case allow "5b ffmpeg is allowed" 'ffmpeg -i in.mp4 out.mp4'
run_case allow "5c git status is allowed" 'git status'
run_case allow "5d quoted rm glob is literal and allowed" \
  "rm -f '/tmp/x/*.png'"
run_case allow "5e explicit static-image generation is allowed" \
  'higgsfield image generate --resolution 4k --quality ultra'
run_case deny "5f rm -rf directory is denied" 'rm -rf /tmp/x'

if jq -e '
  .hooks.PreToolUse
  | any(
      .matcher == "Bash"
      and any(.hooks[];
        .type == "command"
        and .command == "$HOME/.claude/hooks/guard-destructive-and-resolution.py"
      )
    )
' "$SETTINGS" >/dev/null &&
   python3 -m json.tool "$SETTINGS" >/dev/null; then
  printf 'PASS: 6 settings registration and JSON syntax\n'
  passed=$((passed + 1))
else
  printf 'FAIL: 6 settings registration and JSON syntax\n'
  failed=$((failed + 1))
fi

printf '\nResult: %s passed, %s failed\n' "$passed" "$failed"
[[ $failed -eq 0 ]]
