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

    # Never commit onto a detached HEAD: the commit would attach to no branch,
    # the push would publish nothing, and it would float forever while origin/main
    # stalls (the exact divergence trap auto-pull also guards). Reattach to main,
    # fast-forwarding main up to the detached commit only when main is an ANCESTOR
    # of HEAD (so no main-only history is discarded); otherwise check out main and
    # leave the detached commits safe in the reflog.
    $branch = (git rev-parse --abbrev-ref HEAD 2>&1)
    if ($branch -eq "HEAD") {
        $detached = (git rev-parse HEAD 2>&1)
        git merge-base --is-ancestor main HEAD 2>$null
        if ($LASTEXITCODE -eq 0) { git branch --force main $detached 2>$null }
        git checkout main 2>$null
    }

    # Stage changed files (shared config/docs/skills/hooks + memory stores).
    # git add also stages new (untracked) files. Memory stores live at
    # projects/<slug>--claude/memory and are un-ignored by .gitignore; the slug
    # contains the machine's username, so resolve it dynamically instead of
    # hardcoding one machine's path. Only add paths that exist (git errors on
    # missing pathspecs).
    $memTargets = @(Get-ChildItem "projects" -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^[cC]--Users-.+--claude$' } |
        ForEach-Object { "projects/$($_.Name)/memory" })
    $addTargets = @(".gitignore", ".mcp.json", "CLAUDE.md", "settings.json", "skills/", "hooks/", "agents/", "bin/") + $memTargets
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

    # First push attempt. If rejected because the remote moved ahead (another
    # machine/session pushed), rebase our new commit onto the fresh origin/main
    # and retry ONCE. Without this the rejected push was swallowed, leaving the
    # commit local forever (ahead grew, then auto-pull's --ff-only could never
    # catch up -> the divergence deadlock). Never force; if the rebase conflicts
    # we abort cleanly and leave the commit local to retry next time.
    git push 2>$null
    if ($LASTEXITCODE -ne 0) {
        git fetch origin 2>$null
        git -c core.editor=true rebase --no-autostash --no-rerere-autoupdate origin/main 2>$null
        if (Test-Path (Join-Path $claudeDir ".git\rebase-merge")) { git rebase --abort 2>$null }
        elseif (Test-Path (Join-Path $claudeDir ".git\rebase-apply")) { git rebase --abort 2>$null }
        else { git push 2>$null }
    }
} finally {
    Pop-Location
}

exit 0
