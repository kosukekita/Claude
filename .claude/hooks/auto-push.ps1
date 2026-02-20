# auto-push.ps1
# Claude Code Stop hook: .claude/ 配下の変更を自動コミット・プッシュ
# 対象: CLAUDE.md, skills/, hooks/ の変更のみ

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

    # 変更されたファイルをステージング（.claude/ 配下のみ）
    # git add は新規ファイル（untracked）も含めてステージする
    git add CLAUDE.md skills/ hooks/ 2>$null

    # ステージされた変更があるか確認
    $staged = git diff --cached --name-only
    if (-not $staged) { exit 0 }

    # 変更内容からコミットメッセージを生成
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
