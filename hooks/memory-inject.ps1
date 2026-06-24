# memory-inject.ps1
# Claude Code SessionStart hook:
#   Inject cross-session memory stores (summarized memory only) into
#   additionalContext.
#
# DESIGN (changed 2026-06): this hook used to ALSO extract the previous
# session's RAW conversation log and inject it under a "previous session log"
# header so Claude would summarize it. That was the root cause of a serious bug:
# the raw log contained tool-call syntax fragments that a past assistant turn had
# leaked into its text (antml:invoke / antml:parameter tags, raw <div ...> HTML,
# etc.). Re-injecting that text burned it into the new session's context and
# corrupted the model's tool-call generation on the very first turn (raw
# call/invoke syntax leaking into the reply, Bash 'command' param dropped). It was
# also self-perpetuating: the corrupted turn got saved and re-injected every
# start. We now inject ONLY the summarized memory stores (MEMORY.md + linked
# bodies under memory/), which are curated prose and never contain tool-call
# syntax. The "auto-summarize last session" flow is intentionally removed.
#
# RULE: this file must stay ASCII-only. Japanese literals in hook .ps1 files have
# previously broken parsing (encoding mismatch kills the whole hook). Japanese UI
# strings live in memory-strings-ja.json and are read with explicit UTF-8.

$ErrorActionPreference = "SilentlyContinue"
$claudeDir   = "$env:USERPROFILE\.claude"
$projectsDir = "$claudeDir\projects"

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

# Safety net against SEMANTIC poison (distinct from Remove-BadChars, which only
# guards byte/JSON validity). Even though summarized memory is curated prose and
# should never contain tool-call syntax, a memory file could in theory capture a
# code snippet that LOOKS like a tool call or raw HTML. If such a fragment lands
# in additionalContext it can derail the model's own tool-call generation on the
# first turn. So we neutralize anything resembling:
#   - assistant tool-call XML: <invoke ...>, <parameter ...>,
#     <invoke name=...>, <parameter name=...> and their closing tags
#   - raw HTML tags (<div ...>, <span ...>, </div>, etc.)
# Neutralization replaces the angle brackets with fullwidth look-alikes so the
# information is preserved (a human/model can still read it) but it is no longer
# parsed as a real tag. This is deliberately conservative: it only touches things
# that open like a tag, leaving normal prose, code fences, and math untouched.
function Remove-ToolCallSyntax([string]$s) {
    if ([string]::IsNullOrEmpty($s)) { return $s }
    # 1) Explicit assistant tool-call markers (with or without the antml: prefix),
    #    opening or closing, are the most dangerous - defang them by name.
    $s = [regex]::Replace($s,
        '</?\s*(?:antml:)?(?:invoke|parameter|function_calls)\b[^>]*>',
        { param($m) "[[sanitized-toolcall:" + ($m.Value -replace '[<>]', '') + "]]" })
    # 1b) BARE markers with no angle brackets: real corrupted logs often leak only
    #     a fragment of a tag (e.g. the literal text "antml:invoke" with the < >
    #     already stripped upstream). The antml: prefix is a reliable tool-call
    #     fingerprint that never appears in legitimate prose, so defang it even
    #     without brackets. We insert a zero-width-free marker so the token can no
    #     longer be matched as tool-call syntax by the model.
    $s = [regex]::Replace($s,
        '\bantml:(invoke|parameter|function_calls)\b',
        { param($m) "[[sanitized-toolcall:antml-" + $m.Groups[1].Value + "]]" })
    # 2) Any remaining raw HTML-ish tag: replace the < > delimiters with fullwidth
    #    look-alikes so it cannot be parsed as a tag while staying human-readable.
    $s = [regex]::Replace($s,
        '<(/?[a-zA-Z][^>]*)>',
        { param($m) [char]0xFF1C + $m.Groups[1].Value + [char]0xFF1E })
    return $s
}

# --- Localized strings (ASCII fallback if the JSON is missing) ----------------
$strMemoryHeader = "## Memory (from previous sessions)"
$stringsFile = Join-Path $PSScriptRoot "memory-strings-ja.json"
if (Test-Path $stringsFile) {
    try {
        $js = [System.IO.File]::ReadAllText($stringsFile, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
        if ($js.memoryHeader) { $strMemoryHeader = $js.memoryHeader }
    } catch {}
}

# --- Resolve global memory stores (portable across PCs/usernames) ------------
# The harness auto-memory store for the ~/.claude project has a slug like
# C--Users-<username>--claude. This repo syncs across PCs, so stores created on
# other machines may also exist under projects/ - inject all of them.
$memStores = @(Get-ChildItem $projectsDir -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^[cC]--Users-.+--claude$' -and (Test-Path (Join-Path $_.FullName "memory\MEMORY.md")) })

# --- Inject existing (summarized) memories -----------------------------------
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

# --- Output -------------------------------------------------------------------
$combined = $memoryContext.Trim()
if (-not $combined) { exit 0 }

# Two-stage sanitize before this string becomes additionalContext:
#   1. Remove-ToolCallSyntax - defang semantic poison (tool-call syntax / raw HTML)
#      so it cannot derail the model's first-turn tool-call generation.
#   2. Remove-BadChars       - strip lone surrogates / mojibake so the request
#      body stays valid JSON (otherwise "400 ... invalid high surrogate").
# Order matters: defang tags first (it inserts only safe BMP chars), then the
# byte-level pass guarantees JSON validity of the final string.
$combined = Remove-ToolCallSyntax $combined
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
