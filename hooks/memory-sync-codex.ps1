# memory-sync-codex.ps1
# Claude Code Stop hook: ~/.claude/memory/ の内容を Codex 向け AGENTS.md に変換・同期する
# Codex は model_instructions_file = "...AGENTS.md" でこのファイルを起動時に自動読み込みする

$ErrorActionPreference = "SilentlyContinue"
$memDir   = "$env:USERPROFILE\.claude\memory"
$memIndex = "$memDir\MEMORY.md"
$agentsOut = "$memDir\AGENTS.md"

if (-not (Test-Path $memIndex)) { exit 0 }

$indexContent = Get-Content $memIndex -Raw -Encoding UTF8 2>$null
if (-not $indexContent) { exit 0 }

# インデックスからリンクされたファイルを展開
$links   = [regex]::Matches($indexContent, '\[.*?\]\((.+?\.md)\)')
$bodies  = @()
$charLimit = 6000
$totalChars = 0

foreach ($link in $links) {
    $relPath  = $link.Groups[1].Value
    $fullPath = Join-Path $memDir $relPath

    # AGENTS.md 自身は除外（循環防止）
    if ($relPath -eq "AGENTS.md") { continue }
    if (-not (Test-Path $fullPath)) { continue }

    $body = Get-Content $fullPath -Raw -Encoding UTF8 2>$null
    if (-not $body) { continue }

    # frontmatter 除去
    $body = $body -replace '(?s)^---.*?---\s*', ''
    $body = $body.Trim()

    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($relPath)
    $snippet  = "### $fileName`n$body"

    if (($totalChars + $snippet.Length) -gt $charLimit) { break }
    $bodies    += $snippet
    $totalChars += $snippet.Length
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

$agentsContent = @"
# Cross-Agent Memory (Claude Code -> Codex)
# 自動生成: $timestamp
# このファイルは memory-sync-codex.ps1 が自動生成します。直接編集しないでください。

このファイルは Claude Code の ~/.claude/memory/ から自動同期された記憶です。
セッションをまたいで一貫したコンテキストを保つために使用してください。

## Memory Index

$indexContent

---

## Memory Contents

$($bodies -join "`n`n---`n`n")
"@

Set-Content -Path $agentsOut -Value $agentsContent -Encoding UTF8
exit 0
