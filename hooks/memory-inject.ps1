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

# Truncate a string to at most $max UTF-16 code units WITHOUT splitting a
# surrogate pair. PowerShell strings are UTF-16; chars >= U+10000 (emoji, some
# CJK like U+20BB7) are a high+low surrogate pair. A naive Substring(0,$max) can
# stop between the two halves, leaving a lone high surrogate. That serializes to
# invalid JSON and the API rejects the whole request:
#   "invalid high surrogate in string". Drop a trailing lone high surrogate.
function Limit-Text([string]$s, [int]$max) {
    if ($null -eq $s -or $s.Length -le $max) { return $s }
    $cut = $s.Substring(0, $max)
    $last = [int][char]$cut[$cut.Length - 1]
    if ($last -ge 0xD800 -and $last -le 0xDBFF) {
        $cut = $cut.Substring(0, $cut.Length - 1)  # trailing high surrogate -> drop it
    }
    return $cut
}

# Strip characters that serialize to invalid JSON / poison the request body.
# Two kinds are removed (both seen in real corrupted transcripts on JP Windows):
#   1. LONE surrogates - a high (U+D800..U+DBFF) not followed by a low, or a low
#      (U+DC00..U+DFFF) not preceded by a high. These come from old CP932-mojibake
#      and from naive truncation. A VALID high+low pair (real emoji/astral char)
#      is kept intact.
#   2. U+8792 - the mojibake kanji produced when the username "u8792" gets
#      Unicode-escape-mangled. It is a valid BMP char but is a known poison marker
#      here, and re-injecting it keeps the corruption loop alive.
# Runs on the final additionalContext string right before output, so it protects
# regardless of which upstream path produced the bad chars.
function Remove-BadChars([string]$s) {
    if ([string]::IsNullOrEmpty($s)) { return $s }
    $sb  = New-Object System.Text.StringBuilder $s.Length
    $len = $s.Length
    for ($i = 0; $i -lt $len; $i++) {
        $cp = [int][char]$s[$i]
        if ($cp -eq 0x8792) { continue }                      # drop mojibake kanji
        if ($cp -ge 0xD800 -and $cp -le 0xDBFF) {             # high surrogate
            if ($i + 1 -lt $len) {
                $next = [int][char]$s[$i + 1]
                if ($next -ge 0xDC00 -and $next -le 0xDFFF) {  # valid pair: keep both
                    [void]$sb.Append($s[$i]); [void]$sb.Append($s[$i + 1]); $i++; continue
                }
            }
            continue                                          # lone high: drop
        }
        if ($cp -ge 0xDC00 -and $cp -le 0xDFFF) { continue }  # lone low: drop
        [void]$sb.Append($s[$i])
    }
    return $sb.ToString()
}

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
                        $t = Limit-Text ($texts -join ' ') 200
                        $allTurns += "User: $t"
                    }
                }
                elseif ($obj.type -eq "assistant") {
                    $texts = @($obj.message.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text })
                    if ($texts) {
                        $t = Limit-Text ($texts -join ' ') 200
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

# Final safety net: strip lone surrogates / mojibake before this string becomes
# additionalContext. Without this, a corrupted transcript (lone U+DCxx etc.) is
# re-injected every SessionStart and the API rejects the whole request with
# "400 ... invalid high surrogate". This protects all projects unconditionally.
$combined = Remove-BadChars $combined

$output = @{
    hookSpecificOutput = @{
        hookEventName     = "SessionStart"
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
