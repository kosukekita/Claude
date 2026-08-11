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
  if { [[ "$expectation" == deny ]] && [[ $status -eq 0 ]] && [[ "$decision" == deny ]]; } ||
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

image_job_types=(
  nano_banana_pro nano_banana_flash nano_banana_2_lite
  seedream_v5_pro seedream_v5_lite seedream_v4_5
  gpt_image_2 flux_2 flux_kontext z_image grok_image recraft_v4_1
  text2image_soul_v2 soul_location soul_cinematic soul_cast
  kling_omni_image openai_hazel image_auto outpaint topaz_image
)
for job_type in "${image_job_types[@]}"; do
  for resolution in 1k 2k 4k; do
    run_case allow "image ${job_type} allows ${resolution}" \
      "higgsfield generate create ${job_type} --resolution ${resolution} --prompt demo"
  done
done

for job_type in seedance_2_0 veo3_1 kling3_0; do
  run_case deny "video ${job_type} denies --resolution 4k" \
    "higgsfield generate create ${job_type} --resolution 4k --prompt demo"
  run_case deny "video ${job_type} denies --mode 4k" \
    "higgsfield generate create ${job_type} --mode 4k --prompt demo"
  run_case deny "video ${job_type} denies --quality ultra" \
    "higgsfield generate create ${job_type} --quality ultra --prompt demo"
  run_case allow "video ${job_type} allows --quality high" \
    "higgsfield generate create ${job_type} --quality high --prompt demo"
  run_case allow "video ${job_type} allows --resolution 1080p" \
    "higgsfield generate create ${job_type} --resolution 1080p --prompt demo"
  run_case allow "video ${job_type} allows --resolution 480p" \
    "higgsfield generate create ${job_type} --resolution 480p --prompt demo"
done

run_case deny "unknown job_type fails closed for --resolution 4k" \
  'higgsfield generate create future_unknown_model --resolution 4k --prompt demo'

for job_type in nano_banana_pro seedream_v5_pro soul_location; do
  for resolution in 1k 2k 4k; do
    run_case allow "image cost ${job_type} allows ${resolution}" \
      "higgsfield generate cost ${job_type} --resolution ${resolution}"
  done
done

for job_type in seedance_2_0 veo3_1; do
  run_case deny "video cost ${job_type} denies --resolution 4k" \
    "higgsfield generate cost ${job_type} --resolution 4k"
  run_case deny "video cost ${job_type} denies --mode 4k" \
    "higgsfield generate cost ${job_type} --mode 4k"
  run_case deny "video cost ${job_type} denies --quality ultra" \
    "higgsfield generate cost ${job_type} --quality ultra"
  run_case allow "video cost ${job_type} allows --quality high" \
    "higgsfield generate cost ${job_type} --quality high"
  run_case allow "video cost ${job_type} allows --resolution 1080p" \
    "higgsfield generate cost ${job_type} --resolution 1080p"
done

run_case deny "image option value cannot bypass video resolution guard" \
  'higgsfield generate create seedance_2_0 --prompt x --image image --resolution 4k'
run_case deny "images option value cannot bypass video resolution guard" \
  'higgsfield generate create seedance_2_0 --prompt x --image images --resolution 4k'
run_case deny "text-to-image option value cannot bypass video quality guard" \
  'higgsfield generate create seedance_2_0 --prompt x --start-image text-to-image --quality ultra'
run_case deny "bare image token cannot bypass unresolved-command guard" \
  'higgsfield workflow reframe demo --source image --resolution 4k'

# Use an empty PATH for the hook process to prove it does not invoke higgsfield or
# wait on the network. Python drives the hook directly and enforces the 1s limit.
if HOOK_PATH="$HOOK" python3 - <<'PY'
import json
import os
import subprocess
import sys

payload = json.dumps({
    "tool_input": {
        "command": "higgsfield generate create future_unknown_model --resolution 4k"
    }
}).encode()
try:
    result = subprocess.run(
        [sys.executable, os.environ["HOOK_PATH"]],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PATH": ""},
        timeout=1,
        check=False,
    )
except subprocess.TimeoutExpired:
    raise SystemExit(1)
decision = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]
raise SystemExit(0 if result.returncode == 0 and decision == "deny" else 1)
PY
then
  printf 'PASS: offline/missing-CLI decision returns within 1 second\n'
  passed=$((passed + 1))
else
  printf 'FAIL: offline/missing-CLI decision did not return within 1 second\n'
  failed=$((failed + 1))
fi

if jq -e '
  .hooks.PreToolUse
  | any(
      .matcher == "Bash"
      and any(.hooks[];
        .type == "command"
        and .command == "node \"$HOME/.claude/hooks/dispatch.js\" guard-destructive-and-resolution"
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
