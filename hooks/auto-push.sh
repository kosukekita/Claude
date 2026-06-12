#!/usr/bin/env bash
# auto-push.sh
# Claude Code Stop hook (Linux/macOS): auto-commit and push changes under ~/.claude.
# POSIX/bash counterpart of auto-push.ps1; the PowerShell version runs on Windows.
# Targets: shared config/docs/skills/hooks plus every synced memory store.
# Always exits 0 so a sync hiccup never blocks the Stop event.

set +e
claude_dir="$HOME/.claude"
cd "$claude_dir" 2>/dev/null || exit 0

# Confirm this is a git repository
[ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] || exit 0

# Confirm a remote is configured
[ -n "$(git remote 2>/dev/null)" ] || exit 0

# Stage changed files (shared config/docs/skills/hooks + GLOBAL memory stores).
# Only the global ~/.claude memory store is synced; per-project memory stays
# local (it would leak research info to the public repo and can't be cross-read
# across OSes anyway). The global store's slug ends in "--claude": Windows is
# C--Users-<user>--claude, Linux/macOS is -<homepath>--claude. Restrict the glob
# to "*--claude/memory" so project slugs are never staged even if .gitignore
# (the primary backstop) ever permitted them. Resolve dynamically across machines.
add_targets=(".gitignore" ".mcp.json" "CLAUDE.md" "settings.json" "skills" "hooks" "bin")
if [ -d projects ]; then
    for d in projects/*--claude/memory; do
        # glob may not expand if no match; skip the literal pattern
        [ -d "$d" ] && add_targets+=("$d")
    done
fi

for t in "${add_targets[@]}"; do
    [ -e "$t" ] && git add "$t" >/dev/null 2>&1
done

# Anything staged?
staged="$(git diff --cached --name-only 2>/dev/null)"
[ -n "$staged" ] || exit 0

# Build a commit message from the staged files
file_count="$(printf '%s\n' "$staged" | grep -c .)"
first_file="$(printf '%s\n' "$staged" | head -n1 | sed 's#^\.claude/##')"
if [ "$file_count" -eq 1 ]; then
    msg="Auto-update: $first_file"
else
    msg="Auto-update: $first_file and $((file_count - 1)) more file(s)"
fi

git commit -m "$msg" >/dev/null 2>&1
git push >/dev/null 2>&1

exit 0
