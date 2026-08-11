#!/usr/bin/env bash
set -u

hooks_dir="$(cd "$(dirname "$0")/.." && pwd)"
repo_dir="$(cd "$hooks_dir/.." && pwd)"
manifest="$hooks_dir/manifest.json"
temp_home="$(mktemp -d)"
mkdir -p "$temp_home/.claude" "$temp_home/.codex" "$temp_home/.state"

passed=0
skipped=0
failed=0

printf '%s\n' '=== Static registration and resolution checks ==='
if node "$hooks_dir/tests/verify_all.js"; then
  passed=$((passed + 1))
else
  failed=$((failed + 1))
fi

mapfile -t targets < <(node - "$repo_dir/settings.json" "$manifest" <<'NODE'
const fs = require('fs');
const settings = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const manifest = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const targets = new Set();
for (const groups of Object.values(settings.hooks || {})) {
  for (const group of groups) for (const hook of group.hooks || []) {
    const command = hook.command || '';
    const dispatch = command.match(/dispatch\.js\"?\s+([A-Za-z0-9._-]+)/);
    const direct = command.match(/hooks\/([A-Za-z0-9._-]+)\.(?:mjs|cjs|js|sh|py|ps1)/);
    if (dispatch) targets.add(dispatch[1].replace(/\.(?:ps1|sh|py|mjs|js|cjs)$/, ''));
    else if (direct) targets.add(direct[1]);
  }
}
for (const target of [...targets].sort()) {
  const metadata = manifest.targets[target];
  console.log(`${target}\t${metadata ? metadata.platform : 'missing'}`);
}
NODE
)

printf '%s\n' '=== Linux functional invocation of every registered target ==='
for row in "${targets[@]}"; do
  target="${row%%$'\t'*}"
  platform="${row#*$'\t'}"
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
  if [[ $status -eq 0 && "$stderr_text" != *"HOOK DISPATCH WARNING"* ]]; then
    printf 'PASS %s\n' "$target"
    passed=$((passed + 1))
  else
    printf 'FAIL %s status=%s stderr=%s\n' "$target" "$status" "$stderr_text"
    failed=$((failed + 1))
  fi
done

printf 'SUMMARY PASS=%s SKIP=%s FAIL=%s\n' "$passed" "$skipped" "$failed"
[[ $failed -eq 0 ]]
