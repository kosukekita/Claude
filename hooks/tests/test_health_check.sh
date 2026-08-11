#!/usr/bin/env bash
set -u

hooks_dir="$(cd "$(dirname "$0")/.." && pwd)"
repo_dir="$(cd "$hooks_dir/.." && pwd)"
configured="$(node -e '
const s = require(process.argv[1]);
for (const group of s.hooks.SessionStart || []) {
  for (const hook of group.hooks || []) {
    if ((hook.command || "").includes("hook-health-check")) {
      process.stdout.write(hook.command);
      process.exit(0);
    }
  }
}
process.exit(1);
' "$repo_dir/settings.json")"
if [[ "$configured" != 'node "$HOME/.claude/hooks/hook-health-check.mjs"' ]]; then
  printf 'FAIL: SessionStart health check must avoid nested Node dispatch: %s\n' "$configured"
  exit 1
fi

pending_output="$(node "$hooks_dir/hook-health-check.mjs" 2>&1)"
pending_status=$?
broken_output="$(
  CLAUDE_HOOK_MANIFEST="$hooks_dir/tests/manifest-empty.json" \
    node "$hooks_dir/hook-health-check.mjs" 2>&1
)"
broken_status=$?

if [[ $pending_status -eq 0 && "$pending_output" == *"protect-files:pending"* && \
      "$pending_output" == *"warn-bash-overwrite:pending"* && \
      "$pending_output" == *"memory-inject:pending"* && \
      "$pending_output" != *"warn-tu-encoding"* && \
      "$pending_output" != *"pixel-agents-shim"* && \
      "$(printf '%s\n' "$pending_output" | wc -l)" -eq 1 && \
      $broken_status -eq 0 && "$broken_output" == *"[HOOK HEALTH]"* && \
      "$broken_output" == *"missing-manifest"* ]]; then
  printf 'PASS: SessionStart distinguishes pending cross-platform hooks from Windows-only skips\n'
  exit 0
fi

printf 'FAIL: pending=(%s/%s) broken=(%s/%s)\n' \
  "$pending_status" "$pending_output" "$broken_status" "$broken_output"
exit 1
