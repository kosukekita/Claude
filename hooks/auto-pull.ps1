# auto-pull.ps1
# Claude Code SessionStart hook: pull the latest from GitHub at startup.
# Runs at the repo root (~/.claude) so we never create .claude/.claude.
# RULE: keep this file ASCII-only (encoding issues have killed hooks before).

$ErrorActionPreference = "SilentlyContinue"
$claudeDir = "$env:USERPROFILE\.claude"

Push-Location $claudeDir

try {
    # Confirm this is a git repository
    $gitCheck = git rev-parse --is-inside-work-tree 2>&1
    if ($gitCheck -ne "true") { exit 0 }

    # Confirm a remote is configured
    $remote = git remote 2>&1
    if (-not $remote) { exit 0 }

    # Stash dirty TRACKED files before rebasing. We must exclude untracked
    # files: 'git stash push' does not stash untracked by default, so an
    # untracked-only dirty state (e.g. chrome/ or paste-cache/) would set
    # $stashed=$true without actually stashing, and the pop below would then
    # pop someone else's pre-existing stash. --untracked-files=no fixes that.
    $status = git status --porcelain --untracked-files=no 2>&1
    $stashed = $false
    if ($status) {
        git stash push -m "auto-pull-stash" 2>$null
        if ($LASTEXITCODE -eq 0) { $stashed = $true }
    }

    # fetch, then rebase local commits on top of origin/main.
    # --ff-only used to no-op forever once a local commit existed, letting
    # 'behind' grow unbounded. Rebase self-heals that. Non-interactive:
    # core.editor=true prevents any prompt. If the rebase hits a conflict it
    # would otherwise pause forever inside the 30s hook, so we detect a still-
    # in-progress rebase and abort cleanly, leaving the tree exactly as it was
    # (no partial state, no markers). No --force: rebasing only un-pushed local
    # commits never rewrites pushed history.
    git fetch origin 2>$null
    git -c core.editor=true rebase --no-autostash --no-rerere-autoupdate origin/main 2>$null
    if (Test-Path (Join-Path $claudeDir ".git\rebase-merge")) { git rebase --abort 2>$null }
    if (Test-Path (Join-Path $claudeDir ".git\rebase-apply")) { git rebase --abort 2>$null }

    # Restore stashed changes
    if ($stashed) {
        git stash pop 2>$null
    }
} finally {
    Pop-Location
}

exit 0
