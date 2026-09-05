#!/usr/bin/env bash
set -u

hooks_dir="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$hooks_dir/memory-sync-codex.sh"
passed=0
failed=0

work_dir="$(mktemp -d)"
cleanup() { rm -rf "$work_dir"; }
trap cleanup EXIT

run_hook() {
  local claude_home="$1"
  local codex_home="$2"
  CLAUDE_HOME="$claude_home" CODEX_HOME="$codex_home" bash "$HOOK"
}

# --- Case 1-4: marker handling on a realistic CLAUDE.md fixture ---------
markers_claude_home="$work_dir/markers/.claude"
markers_codex_home="$work_dir/markers/.codex"
mkdir -p "$markers_claude_home/projects"

cat >"$markers_claude_home/CLAUDE.md" <<'EOF'
# Global Rules

Shared line visible to both.

<!-- codex-only
## Role split (Codex view)
You are the implementer here.
-->
<!-- claude-only -->
## Role split (Claude view)
Claude is the designer and verifier, not the implementer.
<!-- /claude-only -->
## Memory

This memory section header is followed by a separately marked block below.
<!-- claude-only -->
## Tool-call leak bug
count/court/call leak details.
<!-- /claude-only -->

## Always do

Common closing line.
EOF

run_hook "$markers_claude_home" "$markers_codex_home" >/dev/null 2>&1
agents_out="$markers_codex_home/AGENTS.md"

if [[ -f "$agents_out" ]]; then
  content="$(cat "$agents_out")"
else
  content=""
fi

check() {
  local expectation="$1" label="$2" pattern="$3"
  if [[ "$expectation" == present && "$content" == *"$pattern"* ]] ||
     [[ "$expectation" == absent && "$content" != *"$pattern"* ]]; then
    printf 'PASS: %s\n' "$label"
    passed=$((passed + 1))
  else
    printf 'FAIL: %s (expectation=%s pattern=%q)\n' "$label" "$expectation" "$pattern"
    failed=$((failed + 1))
  fi
}

check absent  "1 no literal claude-only/codex-only marker text leaks" "claude-only"
check absent  "1b no literal codex-only marker text leaks" "codex-only"
check absent  "2 claude-only section body is dropped" "Tool-call leak bug"
check present "3 codex-only body is expanded without markers" "Role split (Codex view)"
check absent  "4 claude-only body content does not appear" "Claude is the designer and verifier"
check present "sanity: shared content survives" "Shared line visible to both"
check present "sanity: closing section survives" "Common closing line"

# --- Case 5: marker-free CLAUDE.md must round-trip byte-identical -------
plain_claude_home="$work_dir/plain/.claude"
plain_codex_home="$work_dir/plain/.codex"
mkdir -p "$plain_claude_home/projects"
cat >"$plain_claude_home/CLAUDE.md" <<'EOF'
# Global Rules

No markers here at all.

## Section A

Body text.

## Section B

More body text.
EOF

run_hook "$plain_claude_home" "$plain_codex_home" >/dev/null 2>&1
plain_out="$plain_codex_home/AGENTS.md"

if [[ -f "$plain_out" ]]; then
  global_section="$(awk '
    /^## Global Instructions$/ { capture = 1; next }
    /^---$/ && capture { exit }
    capture { print }
  ' "$plain_out")"
  # Trim exactly one leading and one trailing blank line inserted by the
  # heredoc around $global_rules, so we compare the CLAUDE.md body itself.
  expected="$(cat "$plain_claude_home/CLAUDE.md")"
  actual="$(printf '%s' "$global_section" | sed -e '1{/^$/d}' -e '${/^$/d}')"
  if [[ "$actual" == "$expected" ]]; then
    printf 'PASS: 5 marker-free input round-trips byte-identical\n'
    passed=$((passed + 1))
  else
    printf 'FAIL: 5 marker-free input round-trips byte-identical\n'
    printf -- '--- expected ---\n%s\n--- actual ---\n%s\n' "$expected" "$actual"
    failed=$((failed + 1))
  fi
else
  printf 'FAIL: 5 marker-free input round-trips byte-identical (no AGENTS.md written)\n'
  failed=$((failed + 1))
fi

# --- Case 6: unclosed marker is fail-open (exit 0, no crash/corruption) -
broken_claude_home="$work_dir/broken/.claude"
broken_codex_home="$work_dir/broken/.codex"
mkdir -p "$broken_claude_home/projects" "$broken_codex_home"
cat >"$broken_claude_home/CLAUDE.md" <<'EOF'
# Global Rules

Before the broken block.

<!-- claude-only -->
This claude-only block is never closed.

## Trailing heading that should not resurface
EOF
# Seed an existing AGENTS.md to confirm the hook does not leave a corrupt
# partial file behind even though the input is malformed.
printf 'previous good content\n' >"$broken_codex_home/AGENTS.md"

run_hook "$broken_claude_home" "$broken_codex_home" >/dev/null 2>&1
broken_status=$?

if [[ $broken_status -eq 0 && -s "$broken_codex_home/AGENTS.md" ]]; then
  printf 'PASS: 6 unclosed marker input is fail-open (exit 0, AGENTS.md intact)\n'
  passed=$((passed + 1))
else
  printf 'FAIL: 6 unclosed marker input is fail-open (status=%s)\n' "$broken_status"
  failed=$((failed + 1))
fi

printf '\nResult: %s passed, %s failed\n' "$passed" "$failed"
[[ $failed -eq 0 ]]
