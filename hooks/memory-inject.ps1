# memory-inject.ps1
# Claude Code SessionStart hook:
#   1. Inject cross-session memory stores into additionalContext
#   2. Extract the previous session's conversation log and ask Claude to summarize/save it
#
# RULE: this file must stay ASCII-only. Japanese literals in hook .ps1 files have
# previously broken parsing (encoding mismatch kills the whole hook). Japanese UI
# strings live in memory-strings-ja.json and are read with explicit UTF-8.

$ErrorActionPreference = "SilentlyContinue"
$claudeDir   = "$env:USERPROFILE\.claude"
$projectsDir = "$claudeDir\projects"
$sessionsDir = "$claudeDir\sessions"

# --- Localized strings (ASCII fallbacks if the JSON is missing) --------------
$strMemoryHeader     = "## Memory (from previous sessions)"
$strSessionLogHeader = "## Previous session log (please summarize and save)"
$strSessionLogIntro  = "Below is the conversation log of the previous session ({SESSION_ID}). At the start of this session, save important decisions, feedback, and learnings to {MEM_DIR}, then briefly report how many memories you updated."
$stringsFile = Join-Path $PSScriptRoot "memory-strings-ja.json"
if (Test-Path $stringsFile) {
    try {
        $js = [System.IO.File]::ReadAllText($stringsFile, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
        if ($js.memoryHeader)     { $strMemoryHeader     = $js.memoryHeader }
        if ($js.sessionLogHeader) { $strSessionLogHeader = $js.sessionLogHeader }
        if ($js.sessionLogIntro)  { $strSessionLogIntro  = $js.sessionLogIntro }
    } catch {}
}

# --- Resolve global memory stores (portable across PCs/usernames) ------------
# The harness auto-memory store for the ~/.claude project has a slug like
# C--Users-<username>--claude. This repo syncs across PCs, so stores created on
# other machines may also exist under projects/ - inject all of them.
$memStores = @(Get-ChildItem $projectsDir -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^[cC]--Users-.+--claude$' -and (Test-Path (Join-Path $_.FullName "memory\MEMORY.md")) })

# The store belonging to THIS machine is the save target for new memories.
$localStore = $memStores |
    Where-Object { $_.Name -match "^[cC]--Users-$([regex]::Escape($env:USERNAME))--claude$" } |
    Select-Object -First 1
if ($localStore) { $localMemDir = Join-Path $localStore.FullName "memory" }
else             { $localMemDir = "$projectsDir\C--Users-$($env:USERNAME)--claude\memory" }

# --- Part 1: inject existing memories ----------------------------------------
$memoryContext = ""
$charLimit  = 6000
$totalChars = 0
$sections   = @()

foreach ($store in $memStores) {
    $memDir       = Join-Path $store.FullName "memory"
    $memIndex     = Join-Path $memDir "MEMORY.md"
    $indexContent = Get-Content $memIndex -Raw -Encoding UTF8 2>$null
    if (-not $indexContent) { continue }

    $links  = [regex]::Matches($indexContent, '\[.*?\]\((.+?\.md)\)')
    $bodies = @()

    foreach ($link in $links) {
        $relPath  = $link.Groups[1].Value
        $fullPath = Join-Path $memDir $relPath
        if (-not (Test-Path $fullPath)) { continue }

        $body = Get-Content $fullPath -Raw -Encoding UTF8 2>$null
        if (-not $body) { continue }

        $body     = ($body -replace '(?s)^---.*?---\s*', '').Trim()
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($relPath)
        $snippet  = "### $fileName`n$body"

        if (($totalChars + $snippet.Length) -gt $charLimit) { break }
        $bodies     += $snippet
        $totalChars += $snippet.Length
    }

    if ($bodies.Count -gt 0) {
        $sections += ($indexContent.Trim() + "`n`n---`n`n" + ($bodies -join "`n`n---`n`n"))
    }
}

if ($sections.Count -gt 0) {
    $memoryContext = $strMemoryHeader + "`n`n" + ($sections -join "`n`n---`n`n")
}

# --- Part 2: extract the previous session's log -------------------------------
$sessionLogContext = ""

$sessionFiles = Get-ChildItem "$sessionsDir\*.json" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending

# The second-newest file is the previous session (newest = this startup).
$prevSessionFile = $sessionFiles | Select-Object -Skip 1 -First 1
if (-not $prevSessionFile) {
    $prevSessionFile = $sessionFiles | Select-Object -First 1
}

if ($prevSessionFile) {
    $prevSession   = Get-Content $prevSessionFile.FullName -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    $prevSessionId = $prevSession.sessionId

    if ($prevSessionId) {
        # Search every project dir for the session id (more reliable than
        # guessing the slug naming convention).
        $jsonlPath = Get-ChildItem $projectsDir -Directory -ErrorAction SilentlyContinue |
                     ForEach-Object { Join-Path $_.FullName "$prevSessionId.jsonl" } |
                     Where-Object { Test-Path $_ } |
                     Select-Object -First 1

        if ($jsonlPath) {
            $lines    = Get-Content $jsonlPath -Encoding UTF8 2>$null
            $allTurns = @()

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

            # Keep only the latest 40 turns (older parts are not needed).
            $turns = $allTurns | Select-Object -Last 40

            if ($turns.Count -gt 0) {
                $turnText = $turns -join "`n"
                $intro = $strSessionLogIntro -replace '\{SESSION_ID\}', $prevSessionId -replace '\{MEM_DIR\}', $localMemDir
                $sessionLogContext = "`n`n---`n`n" + $strSessionLogHeader + "`n`n" + $intro + "`n`n" + $turnText
            }
        }
    }
}

# --- Output -------------------------------------------------------------------
$combined = ($memoryContext + $sessionLogContext).Trim()
if (-not $combined) { exit 0 }

$output = @{
    hookSpecificOutput = @{
        additionalContext = $combined
    }
} | ConvertTo-Json -Compress -Depth 5

# Write UTF-8 bytes straight to the stdout stream. Do NOT use Write-Output here:
# under -File with a redirected/piped stdout, PowerShell encodes pipeline output
# using the system ANSI code page (cp932 on JP Windows), so the Japanese
# additionalContext gets emitted as Shift_JIS and Claude Code (which reads stdout
# as UTF-8) shows mojibake (e.g. user name -> garbled kanji). Byte-level write
# bypasses console/ACP encoding entirely and is deterministic across machines.
$bytes  = [System.Text.Encoding]::UTF8.GetBytes($output)
$stdout = [System.Console]::OpenStandardOutput()
$stdout.Write($bytes, 0, $bytes.Length)
$stdout.Flush()
exit 0
