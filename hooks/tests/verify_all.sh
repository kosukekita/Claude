#!/usr/bin/env bash
set -u

hooks_dir="$(cd "$(dirname "$0")/.." && pwd)"
repo_dir="$(cd "$hooks_dir/.." && pwd)"
manifest="$hooks_dir/manifest.json"
temp_home="$(mktemp -d)"
mkdir -p "$temp_home/.claude" "$temp_home/.codex" "$temp_home/.state"

passed=0
pending=0
skipped=0
failed=0

printf '%s\n' '=== Static registration and resolution checks ==='
if node "$hooks_dir/tests/verify_all.js"; then
  passed=$((passed + 1))
else
  failed=$((failed + 1))
fi

mapfile -t targets < <(node - "$repo_dir/settings.json" "$manifest" "$hooks_dir/dispatch.js" <<'NODE'
const fs = require('fs');
const settings = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const manifest = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const dispatch = require(process.argv[4]);
const targets = dispatch.registeredTargets(settings);
for (const target of [...targets].sort()) {
  const metadata = manifest.targets[target];
  console.log(`${target}\t${metadata ? metadata.platform : 'missing'}\t${metadata?.implementation_status || 'active'}`);
}
NODE
)

printf '%s\n' '=== Linux functional invocation of every registered target ==='
for row in "${targets[@]}"; do
  IFS=$'\t' read -r target platform implementation_status <<<"$row"
  if [[ "$platform" == "windows" ]]; then
    printf 'SKIP %s (platform=windows)\n' "$target"
    skipped=$((skipped + 1))
    continue
  fi

  payload='{"tool_name":"Read","tool_input":{}}'
  if [[ "$target" == "guard-destructive-and-resolution" || "$target" == "block-dangerous" ]]; then
    payload='{"tool_input":{"command":"ls -la"}}'
  fi
  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"
  printf '%s\n' "$payload" | env \
    HOME="$temp_home" \
    CLAUDE_HOME="$temp_home/.claude" \
    CODEX_HOME="$temp_home/.codex" \
    XDG_STATE_HOME="$temp_home/.state" \
    CLAUDE_HOOK_MANIFEST="$manifest" \
    node "$hooks_dir/dispatch.js" "$target" >"$stdout_file" 2>"$stderr_file"
  status=$?
  stderr_text="$(tr '\n' ' ' <"$stderr_file")"
  if [[ "$implementation_status" == "pending" && $status -eq 0 && \
        "$stderr_text" == *"HOOK DISPATCH WARNING"* ]]; then
    printf 'PENDING %s (unresolved implementation is visible)\n' "$target"
    pending=$((pending + 1))
  elif [[ "$implementation_status" == "pending" ]]; then
    printf 'FAIL %s pending state was not reported status=%s stderr=%s\n' \
      "$target" "$status" "$stderr_text"
    failed=$((failed + 1))
  elif [[ $status -eq 0 && "$stderr_text" != *"HOOK DISPATCH WARNING"* ]]; then
    printf 'PASS %s\n' "$target"
    passed=$((passed + 1))
  else
    printf 'FAIL %s status=%s stderr=%s\n' "$target" "$status" "$stderr_text"
    failed=$((failed + 1))
  fi
done

printf 'SUMMARY PASS=%s PENDING=%s SKIP=%s FAIL=%s\n' \
  "$passed" "$pending" "$skipped" "$failed"
[[ $failed -eq 0 ]]
