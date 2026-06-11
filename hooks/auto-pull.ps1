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

    # Stash uncommitted local changes before pulling
    $status = git status --porcelain 2>&1
    $stashed = $false
    if ($status) {
        git stash push -m "auto-pull-stash" 2>$null
        $stashed = $true
    }

    # fetch & pull
    git fetch origin 2>$null
    git pull --ff-only origin main 2>$null

    # Restore stashed changes
    if ($stashed) {
        git stash pop 2>$null
    }
} finally {
    Pop-Location
}

exit 0
