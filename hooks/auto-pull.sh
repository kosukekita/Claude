#!/usr/bin/env bash
# auto-pull.sh
# Claude Code SessionStart hook (Linux/macOS): pull the latest from GitHub at startup.
# POSIX/bash counterpart of auto-pull.ps1; the PowerShell version runs on Windows.
# Runs at the repo root (~/.claude) so we never create .claude/.claude.
# Always exits 0 so a sync hiccup never blocks session startup.

set +e
claude_dir="$HOME/.claude"
cd "$claude_dir" 2>/dev/null || exit 0

# Confirm this is a git repository
[ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] || exit 0

# Confirm a remote is configured
[ -n "$(git remote 2>/dev/null)" ] || exit 0

# Stash uncommitted local changes before pulling (so --ff-only can't be blocked)
stashed=0
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    git stash push -u -m "auto-pull-stash" >/dev/null 2>&1 && stashed=1
fi

# fetch & fast-forward pull
git fetch origin >/dev/null 2>&1
git pull --ff-only origin main >/dev/null 2>&1

# Restore stashed changes
if [ "$stashed" -eq 1 ]; then
    git stash pop >/dev/null 2>&1
fi

exit 0
