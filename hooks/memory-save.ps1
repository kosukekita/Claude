# memory-save.ps1
# Claude Code Stop hook: セッション終了時に memory/ 配下の変更を git にステージングする

$ErrorActionPreference = "SilentlyContinue"
$claudeDir = "$env:USERPROFILE\.claude"

Push-Location $claudeDir

try {
    $gitCheck = git rev-parse --is-inside-work-tree 2>&1
    if ($gitCheck -ne "true") { exit 0 }

    # memory/ 配下の変更をステージング
    git add memory/ 2>$null
} finally {
    Pop-Location
}

exit 0
