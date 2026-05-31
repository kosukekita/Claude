# memory-inject.ps1
# Claude Code SessionStart hook: 記憶ファイルをコンテキストに注入する
# ~/.claude/memory/MEMORY.md とメモリファイル群を読み込み、additionalContext で渡す

$ErrorActionPreference = "SilentlyContinue"
$memDir = "$env:USERPROFILE\.claude\memory"
$memIndex = "$memDir\MEMORY.md"

if (-not (Test-Path $memIndex)) { exit 0 }

# MEMORY.md（インデックス）を読み込む
$indexContent = Get-Content $memIndex -Raw -Encoding UTF8 2>$null
if (-not $indexContent) { exit 0 }

# インデックスからリンクされたファイルを展開（合計8000文字を上限に制限）
$links = [regex]::Matches($indexContent, '\[.*?\]\((.+?\.md)\)')
$bodies = @()
$charLimit = 8000
$totalChars = 0

foreach ($link in $links) {
    $relPath = $link.Groups[1].Value
    $fullPath = Join-Path $memDir $relPath
    if (-not (Test-Path $fullPath)) { continue }

    $body = Get-Content $fullPath -Raw -Encoding UTF8 2>$null
    if (-not $body) { continue }

    # frontmatter を除去（--- で囲まれた部分）
    $body = $body -replace '(?s)^---.*?---\s*', ''
    $body = $body.Trim()

    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($relPath)
    $snippet = "### $fileName`n$body"

    if (($totalChars + $snippet.Length) -gt $charLimit) { break }
    $bodies += $snippet
    $totalChars += $snippet.Length
}

if ($bodies.Count -eq 0) { exit 0 }

$context = @"
## 記憶（前回までのセッションから）

$indexContent

---

$($bodies -join "`n`n---`n`n")
"@

# hookSpecificOutput.additionalContext として JSON 出力
$output = @{
    hookSpecificOutput = @{
        additionalContext = $context
    }
} | ConvertTo-Json -Compress -Depth 5

Write-Output $output
exit 0
