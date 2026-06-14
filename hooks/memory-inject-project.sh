#!/usr/bin/env bash
# memory-inject-project.sh
# Claude Code SessionStart hook (cross-OS): inject PROJECT-specific memory that
# lives inside the project folder itself, at <cwd>/.claude-memory/, as
# additionalContext. This complements the global memory-inject hook (which only
# reads ~/.claude/projects/<slug>/memory/ and is cwd-blind).
#
# WHY a hook, not a CLAUDE.md rule: a CLAUDE.md sentence is a soft prompt and is
# not even loaded when cwd is a pCloud project (only that project's own CLAUDE.md
# loads). A SessionStart hook runs deterministically and its output is injected
# into context before the first turn, so project memory is loaded reliably and
# independent of the OS-dependent ~/.claude auto-memory slug.
#
# Cross-PC rationale: project folders live on pCloud and sync as real files, so
# <project>/.claude-memory/ is the same on every machine regardless of the slug.
#
# Always exits 0; prints nothing (so no context) when there is no project memory.

set +e

# --- Read the SessionStart stdin JSON and extract cwd ------------------------
# Prefer cwd from stdin (canonical project dir); fall back to CLAUDE_PROJECT_DIR.
payload="$(cat 2>/dev/null)"
cwd=""
if [ -n "$payload" ]; then
    if command -v jq >/dev/null 2>&1; then
        cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"
    elif command -v python3 >/dev/null 2>&1; then
        cwd="$(printf '%s' "$payload" | python3 -c 'import sys,json;
try:
    print(json.load(sys.stdin).get("cwd",""))
except Exception:
    pass' 2>/dev/null)"
    fi
fi
[ -n "$cwd" ] || cwd="$CLAUDE_PROJECT_DIR"
[ -n "$cwd" ] || exit 0

mem_dir="$cwd/.claude-memory"
index="$mem_dir/MEMORY.md"
[ -f "$index" ] || exit 0

# Do NOT double-inject the global store: if cwd is ~/.claude itself, the global
# memory-inject hook already handles its memory. (~/.claude has no .claude-memory
# anyway, but guard explicitly in case someone creates one.)
case "$cwd" in
    "$HOME/.claude"|"$HOME/.claude/") exit 0 ;;
esac

# --- Build the injected context ----------------------------------------------
# Mirror memory-inject.ps1: emit the MEMORY.md index, then each linked body with
# its YAML frontmatter stripped. Cap total size to stay friendly to context.
# Project memories can be large (deploy logs etc.), so allow more than the global
# store and ALWAYS include at least the first body even if it alone exceeds the
# cap (otherwise a single big first file would inject nothing).
char_limit=12000
emitted=0
bodies=""

index_content="$(cat "$index" 2>/dev/null)"
[ -n "$index_content" ] || exit 0

# Extract relative .md paths from markdown links: [..](path.md)
links="$(printf '%s\n' "$index_content" | grep -oE '\]\(([^)]+\.md)\)' | sed -E 's/^\]\(//; s/\)$//')"

while IFS= read -r rel; do
    [ -n "$rel" ] || continue
    full="$mem_dir/$rel"
    [ -f "$full" ] || continue
    body="$(cat "$full" 2>/dev/null)"
    [ -n "$body" ] || continue
    # Strip a leading YAML frontmatter block (--- ... ---) if present.
    body="$(printf '%s\n' "$body" | awk '
        NR==1 && $0=="---" { infm=1; next }
        infm && $0=="---"  { infm=0; next }
        !infm { print }
    ')"
    name="$(basename "$rel" .md)"
    snippet="### $name
$body"
    # Append first, THEN check the cap, so at least one body always lands even
    # if it alone exceeds char_limit. Stop adding more once we're over budget.
    bodies="$bodies

---

$snippet"
    emitted=$((emitted + ${#snippet}))
    [ "$emitted" -gt "$char_limit" ] && break
done <<EOF
$links
EOF

# Nothing usable beyond the index -> still inject the index alone is low value;
# only emit when we have at least one body.
[ -n "$bodies" ] || exit 0

context="## Project memory (from <project>/.claude-memory/, synced via pCloud)

$index_content
$bodies"

# --- Output as SessionStart additionalContext --------------------------------
# CRITICAL: sanitize before output. On Windows the bash/awk/grep/sed text pipeline
# above can split multibyte UTF-8 under a non-UTF-8 locale, producing LONE
# surrogates (and the mojibake kanji U+8792). If those reach additionalContext,
# Claude Code's request body becomes invalid JSON and EVERY turn fails with
# "400 ... invalid high surrogate". So we ALWAYS route the final context through
# python3, which both JSON-encodes it AND strips lone surrogates / U+8792.
# A valid surrogate PAIR (real emoji/astral char) is preserved.
# jq is intentionally NOT used for output anymore: it cannot strip lone surrogates.
if command -v python3 >/dev/null 2>&1; then
    python3 -c '
import sys, json
ctx = sys.stdin.buffer.read().decode("utf-8", "surrogatepass")
out = []
i, n = 0, len(ctx)
while i < n:
    cp = ord(ctx[i])
    if cp == 0x8792:               # mojibake kanji -> drop
        i += 1; continue
    if 0xD800 <= cp <= 0xDBFF:     # high surrogate
        if i + 1 < n and 0xDC00 <= ord(ctx[i+1]) <= 0xDFFF:
            out.append(ctx[i]); out.append(ctx[i+1]); i += 2; continue
        i += 1; continue            # lone high -> drop
    if 0xDC00 <= cp <= 0xDFFF:     # lone low -> drop
        i += 1; continue
    out.append(ctx[i]); i += 1
clean = "".join(out)
sys.stdout.write(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":clean}}))
' <<PYEOF
$context
PYEOF
else
    # No python3: fall back to plain stdout. Cannot strip surrogates here, but a
    # non-UTF-8 bash without python3 is unlikely; this keeps the hook functional.
    printf '%s\n' "$context"
fi

exit 0
