#!/usr/bin/env bash
# auto-pull.sh
# Claude Code SessionStart hook (Linux/macOS): pull the latest from GitHub at startup.
# POSIX/bash counterpart of auto-pull.ps1; keep the two in lockstep. The synced
# machines are Windows (.ps1) and Linux (.sh), so a fix in one must land in both.
# Runs at the repo root (~/.claude) so we never create .claude/.claude.
# Always exits 0 so a sync hiccup never blocks session startup.

set +e
claude_dir="$HOME/.claude"
cd "$claude_dir" 2>/dev/null || exit 0

# Confirm this is a git repository
[ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] || exit 0

# Confirm a remote is configured
[ -n "$(git remote 2>/dev/null)" ] || exit 0

# Recover from a detached HEAD before anything else (see auto-pull.ps1 for the
# full rationale). A detached HEAD is the divergence trap: auto-push commits onto
# no branch, the push publishes nothing, and the commit floats while origin/main
# stalls. Only fast-forward main up to the detached commit when main is an
# ANCESTOR of HEAD (detached commits sit on top of main, no history discarded);
# otherwise just check out main and let the rebase below reconcile, leaving the
# detached commits safe in the reflog.
if [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "HEAD" ]; then
    detached="$(git rev-parse HEAD 2>/dev/null)"
    if git merge-base --is-ancestor main HEAD 2>/dev/null; then
        git branch --force main "$detached" >/dev/null 2>&1
    fi
    git checkout main >/dev/null 2>&1
fi

# Stash dirty TRACKED files before rebasing. Exclude untracked files: an
# untracked-only dirty state (chrome/, paste-cache/, etc.) must not set
# stashed=1, or the apply below would pop a pre-existing unrelated stash.
stashed=0
if [ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]; then
    git stash push -m "auto-pull-stash" >/dev/null 2>&1 && stashed=1
fi

# fetch, then rebase local commits on top of origin/main. Rebase (not --ff-only)
# self-heals divergence: --ff-only no-ops forever once a local commit exists and
# lets 'behind' grow unbounded. core.editor=true prevents any interactive prompt.
# If the rebase hits a conflict it would pause forever inside the hook, so detect
# an in-progress rebase and abort cleanly, leaving the tree exactly as it was.
# No --force: rebasing only un-pushed local commits never rewrites pushed history.
git fetch origin >/dev/null 2>&1
git -c core.editor=true rebase --no-autostash --no-rerere-autoupdate origin/main >/dev/null 2>&1
[ -d "$claude_dir/.git/rebase-merge" ] && git rebase --abort >/dev/null 2>&1
[ -d "$claude_dir/.git/rebase-apply" ] && git rebase --abort >/dev/null 2>&1

# Restore stashed changes with apply+drop (not pop): if apply conflicts, the
# stash stays intact so nothing is lost and it can be resolved manually. Only
# drop when apply succeeded cleanly.
if [ "$stashed" -eq 1 ]; then
    git stash apply >/dev/null 2>&1 && git stash drop >/dev/null 2>&1
fi

exit 0
