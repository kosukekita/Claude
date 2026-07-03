#!/usr/bin/env bash
# auto-push.sh
# Claude Code Stop hook (Linux/macOS): auto-commit and push changes under ~/.claude.
# POSIX/bash counterpart of auto-push.ps1; keep the two in lockstep. The synced
# machines are Windows (.ps1) and Linux (.sh), so a fix in one must land in both.
# Targets: shared config/docs/skills/hooks/agents/bin plus every synced memory store.
# Always exits 0 so a sync hiccup never blocks the Stop event.

set +e
claude_dir="$HOME/.claude"
cd "$claude_dir" 2>/dev/null || exit 0

# Confirm this is a git repository
[ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] || exit 0

# Confirm a remote is configured
[ -n "$(git remote 2>/dev/null)" ] || exit 0

# Never commit onto a detached HEAD (see auto-push.ps1 for the full rationale):
# the commit would attach to no branch, publish nothing, and float forever while
# origin/main stalls. Reattach to main, fast-forwarding main up to the detached
# commit only when main is an ANCESTOR of HEAD (no main-only history discarded);
# otherwise check out main and leave the detached commits safe in the reflog.
if [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "HEAD" ]; then
    detached="$(git rev-parse HEAD 2>/dev/null)"
    if git merge-base --is-ancestor main HEAD 2>/dev/null; then
        git branch --force main "$detached" >/dev/null 2>&1
    fi
    git checkout main >/dev/null 2>&1
fi

# Stage changed files (shared config/docs/skills/hooks/agents/bin + GLOBAL memory
# stores). Only the global ~/.claude memory store is synced; per-project memory
# stays local (it would leak research info to the public repo and can't be
# cross-read across OSes anyway). The global store's slug ends in "--claude":
# Windows is C--Users-<user>--claude, Linux/macOS is -<homepath>--claude. Restrict
# the glob to "*--claude/memory" so project slugs are never staged even if
# .gitignore (the primary backstop) ever permitted them. Resolve dynamically.
add_targets=(".gitignore" ".mcp.json" "CLAUDE.md" "settings.json" "skills" "hooks" "agents" "bin")
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

# First push attempt. If rejected because the remote moved ahead (another
# machine/session pushed), rebase our new commit onto the fresh origin/main and
# retry ONCE. Without this the rejected push is swallowed, leaving the commit
# local forever (ahead grows, auto-pull can never catch up -> divergence
# deadlock). Never force; if the rebase conflicts we abort cleanly and leave the
# commit local to retry next time.
git push >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
    git fetch origin >/dev/null 2>&1
    git -c core.editor=true rebase --no-autostash --no-rerere-autoupdate origin/main >/dev/null 2>&1
    if [ -d "$claude_dir/.git/rebase-merge" ]; then
        git rebase --abort >/dev/null 2>&1
    elif [ -d "$claude_dir/.git/rebase-apply" ]; then
        git rebase --abort >/dev/null 2>&1
    else
        git push >/dev/null 2>&1
    fi
fi

exit 0
