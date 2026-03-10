# auto-pull.ps1
# Claude Code SessionStart hook: 起動時に GitHub 最新版を pull
# .claude/.claude にならないよう、リポジトリルート (~/.claude) で実行

$ErrorActionPreference = "SilentlyContinue"
$claudeDir = "$env:USERPROFILE\.claude"

Push-Location $claudeDir

try {
    # git リポジトリか確認
    $gitCheck = git rev-parse --is-inside-work-tree 2>&1
    if ($gitCheck -ne "true") { exit 0 }

    # リモートが設定されているか確認
    $remote = git remote 2>&1
    if (-not $remote) { exit 0 }

    # ローカルに未コミットの変更がある場合は stash
    $status = git status --porcelain 2>&1
    $stashed = $false
    if ($status) {
        git stash push -m "auto-pull-stash" 2>$null
        $stashed = $true
    }

    # fetch & pull
    git fetch origin 2>$null
    git pull --ff-only origin main 2>$null

    # stash していた場合は復元
    if ($stashed) {
        git stash pop 2>$null
    }
} finally {
    Pop-Location
}

exit 0
