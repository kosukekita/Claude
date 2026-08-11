#!/usr/bin/env bash
set -u

hooks_dir="$(cd "$(dirname "$0")/.." && pwd)"
repo_dir="$(cd "$hooks_dir/.." && pwd)"
fixtures="$hooks_dir/tests/destructive-fixtures.json"
guard="$hooks_dir/guard-destructive-and-resolution.py"
passed=0
failed=0

while IFS= read -r fixture; do
  name="$(jq -r '.name' <<<"$fixture")"
  command="$(jq -r '.command' <<<"$fixture")"
  expected="$(jq -r '.expected' <<<"$fixture")"
  expected_reason="$(jq -r '.expected_reason // empty' <<<"$fixture")"
  virtual_env="$(jq -r '.virtual_env // empty' <<<"$fixture")"
  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"
  payload="$(jq -nc --arg command "$command" '{tool_input:{command:$command}}')"
  if [[ -n "$virtual_env" ]]; then
    printf '%s\n' "$payload" | env VIRTUAL_ENV="$virtual_env" python3 "$guard" >"$stdout_file" 2>"$stderr_file"
  else
    printf '%s\n' "$payload" | env -u VIRTUAL_ENV -u CONDA_PREFIX python3 "$guard" >"$stdout_file" 2>"$stderr_file"
  fi
  status=$?
  decision="$(jq -r '.hookSpecificOutput.permissionDecision // empty' "$stdout_file" 2>/dev/null)"
  reason="$(jq -r '.hookSpecificOutput.permissionDecisionReason // empty' "$stdout_file" 2>/dev/null)"
  warning="$(tr '\n' ' ' <"$stderr_file")"

  ok=0
  case "$expected" in
    deny)
      [[ $status -eq 0 && "$decision" == "deny" && \
         ( -z "$expected_reason" || "$reason" == "$expected_reason" ) ]] && ok=1
      ;;
    warn)
      [[ $status -eq 0 && "$decision" != "deny" && "$warning" == *"PIP INSTALL WARNING"* ]] && ok=1
      ;;
    allow)
      [[ $status -eq 0 && "$decision" != "deny" && "$warning" != *"PIP INSTALL WARNING"* ]] && ok=1
      ;;
  esac
  if [[ $ok -eq 1 ]]; then
    printf 'PASS: %s => %s\n' "$name" "$expected"
    passed=$((passed + 1))
  else
    printf 'FAIL: %s expected=%s status=%s decision=%s warning=%s\n' \
      "$name" "$expected" "$status" "$decision" "$warning"
    failed=$((failed + 1))
  fi
done < <(jq -c '.[]' "$fixtures")

if ! rg -q 'dispatch\.js\\" block-dangerous' "$repo_dir/settings.json" && \
   [[ ! -e "$hooks_dir/block-dangerous.ps1" ]] && \
   [[ -e "$hooks_dir/retired/block-dangerous.ps1" ]]; then
  printf 'PASS: block-dangerous registration removed and source archived\n'
  passed=$((passed + 1))
else
  printf 'FAIL: block-dangerous registration/archive state\n'
  failed=$((failed + 1))
fi

printf 'SUMMARY PASS=%s FAIL=%s\n' "$passed" "$failed"
[[ $failed -eq 0 ]]
