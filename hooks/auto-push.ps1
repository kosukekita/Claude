# auto-push.ps1
# Claude Code Stop hook: auto-commit and push changes under ~/.claude.
# Targets: shared config/docs/skills/hooks plus every synced memory store.
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

    # Stage changed files (shared config/docs/skills/hooks + memory stores).
    # git add also stages new (untracked) files. Memory stores live at
    # projects/<slug>--claude/memory and are un-ignored by .gitignore; the slug
    # contains the machine's username, so resolve it dynamically instead of
    # hardcoding one machine's path. Only add paths that exist (git errors on
    # missing pathspecs).
    $memTargets = @(Get-ChildItem "projects" -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^[cC]--Users-.+--claude$' } |
        ForEach-Object { "projects/$($_.Name)/memory" })
    $addTargets = @(".gitignore", ".mcp.json", "CLAUDE.md", "settings.json", "skills/", "hooks/") + $memTargets
    foreach ($t in $addTargets) {
        if (Test-Path $t) { git add $t 2>$null }
    }

    # Anything staged?
    $staged = git diff --cached --name-only
    if (-not $staged) { exit 0 }

    # Build a commit message from the staged files
    $files = @($staged -split "`n" | Where-Object { $_ })
    $fileCount = $files.Count
    $firstFile = $files[0] -replace '^\.claude/', ''
    if ($fileCount -eq 1) {
        $msg = "Auto-update: $firstFile"
    } else {
        $msg = "Auto-update: $firstFile and $($fileCount - 1) more file(s)"
    }

    git commit -m $msg 2>$null
    git push 2>$null
} finally {
    Pop-Location
}

exit 0
