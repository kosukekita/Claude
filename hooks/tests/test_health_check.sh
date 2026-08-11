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

output="$(node "$hooks_dir/hook-health-check.mjs" 2>&1)"
status=$?

if [[ $status -eq 0 && "$output" == *"[HOOK HEALTH]"* && \
      "$output" != *"block-dangerous:unresolved"* && \
      "$output" == *"guard-file-revert:unresolved"* && \
      "$output" == *"record-file-snapshot:unresolved"* ]]; then
  printf 'PASS: SessionStart health check exposes the remaining unresolved hooks\n'
  exit 0
fi

printf 'FAIL: SessionStart health check output=%s status=%s\n' "$output" "$status"
exit 1
