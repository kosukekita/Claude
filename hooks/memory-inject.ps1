# memory-inject.ps1
# Claude Code SessionStart hook:
#   1. ~/.claude/memory/ の記憶ファイルを additionalContext に注入
#   2. 直前セッションの会話ログを抽出して要約・保存を依頼

$ErrorActionPreference = "SilentlyContinue"
$memDir      = "$env:USERPROFILE\.claude\memory"
$memIndex    = "$memDir\MEMORY.md"
$sessionsDir = "$env:USERPROFILE\.claude\sessions"
$projectsDir = "$env:USERPROFILE\.claude\projects"

# ── パート1: 既存メモリ注入 ──────────────────────────────────────────────────

$memoryContext = ""

if (Test-Path $memIndex) {
    $indexContent = Get-Content $memIndex -Raw -Encoding UTF8 2>$null

    if ($indexContent) {
        $links      = [regex]::Matches($indexContent, '\[.*?\]\((.+?\.md)\)')
        $bodies     = @()
        $charLimit  = 6000
        $totalChars = 0

        foreach ($link in $links) {
            $relPath  = $link.Groups[1].Value
            $fullPath = Join-Path $memDir $relPath
            if (-not (Test-Path $fullPath)) { continue }

            $body = Get-Content $fullPath -Raw -Encoding UTF8 2>$null
            if (-not $body) { continue }

            $body     = $body -replace '(?s)^---.*?---\s*', ''
            $body     = $body.Trim()
            $fileName = [System.IO.Path]::GetFileNameWithoutExtension($relPath)
            $snippet  = "### $fileName`n$body"

            if (($totalChars + $snippet.Length) -gt $charLimit) { break }
            $bodies     += $snippet
            $totalChars += $snippet.Length
        }

        if ($bodies.Count -gt 0) {
            $memoryContext = @"
## 記憶（前回までのセッションから）

$indexContent

---

$($bodies -join "`n`n---`n`n")
"@
        }
    }
}

# ── パート2: 直前セッションのログ抽出 ────────────────────────────────────────

$sessionLogContext = ""

$sessionFiles = Get-ChildItem "$sessionsDir\*.json" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending

# 2番目に新しいファイルが直前セッション（最新=今回起動分）
$prevSessionFile = $sessionFiles | Select-Object -Skip 1 -First 1
if (-not $prevSessionFile) {
    $prevSessionFile = $sessionFiles | Select-Object -First 1
}

if ($prevSessionFile) {
    $prevSession   = Get-Content $prevSessionFile.FullName -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    $prevSessionId = $prevSession.sessionId

    if ($prevSessionId) {
        # セッションIDで全プロジェクトを検索（命名規則の推測より確実）
        $jsonlPath = Get-ChildItem $projectsDir -Directory -ErrorAction SilentlyContinue |
                     ForEach-Object { Join-Path $_.FullName "$prevSessionId.jsonl" } |
                     Where-Object { Test-Path $_ } |
                     Select-Object -First 1

        if ($jsonlPath) {
            $lines     = Get-Content $jsonlPath -Encoding UTF8 2>$null
            $allTurns  = @()

            foreach ($line in $lines) {
                try { $obj = $line | ConvertFrom-Json -ErrorAction Stop } catch { continue }

                if ($obj.type -eq "user") {
                    $texts = @($obj.message.content |
                               Where-Object { $_.type -eq "text" } |
                               ForEach-Object { ($_.text -replace '(?s)<[^>]+>.*?</[^>]+>', '').Trim() } |
                               Where-Object { $_ })
                    if ($texts) {
                        $t = ($texts -join ' ').Substring(0, [Math]::Min(200, ($texts -join ' ').Length))
                        $allTurns += "User: $t"
                    }
                }
                elseif ($obj.type -eq "assistant") {
                    $texts = @($obj.message.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text })
                    if ($texts) {
                        $t = ($texts -join ' ').Substring(0, [Math]::Min(200, ($texts -join ' ').Length))
                        $allTurns += "Assistant: $t"
                    }
                }
            }

            # 最新40ターンのみ取得（古い部分は要約には不要）
            $turns = $allTurns | Select-Object -Last 40

            if ($turns.Count -gt 0) {
                $turnText = $turns -join "`n"
                $sessionLogContext = @"

---

## 直前セッションのログ（要約・保存をお願いします）

以下は直前のセッション（$prevSessionId）の会話ログです。
このセッション開始時に、重要な情報・決定・学び・フィードバックを ~/.claude/memory/ に保存してください。
保存後「記憶を更新しました（N件）」と一言報告してください。

$turnText
"@
            }
        }
    }
}

# ── 出力 ──────────────────────────────────────────────────────────────────────

$combined = ($memoryContext + $sessionLogContext).Trim()
if (-not $combined) { exit 0 }

$output = @{
    hookSpecificOutput = @{
        additionalContext = $combined
    }
} | ConvertTo-Json -Compress -Depth 5

Write-Output $output
exit 0
