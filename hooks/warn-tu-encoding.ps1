# warn-tu-encoding.ps1
# Claude Code PreToolUse hook (Bash): warn-only, never blocks.
# ToolUniverse CLI (`tu` / `tooluniverse`) on Windows corrupts output under cp932.
# It must run with PYTHONIOENCODING=utf-8. This hook warns when that env var is
# missing from a tu command so the user/Claude can re-run it correctly.
# exit 0 always (warning is advisory, not a block).

$ErrorActionPreference = "SilentlyContinue"

$json = $input | Out-String
$cmd = ""
try {
    $obj = $json | ConvertFrom-Json
    $cmd = $obj.tool_input.command
    if (-not $cmd) { exit 0 }
} catch {
    exit 0
}

# Match an invocation of the tu CLI:
#  - "tu " as a standalone command word (start, or after ; && | etc.)
#  - or the longer "tooluniverse" form (e.g. uvx --from tooluniverse tu ...)
$isTu = ($cmd -match "(^|\s|;|&&|\|)tu\s") -or ($cmd -match "tooluniverse")
$hasEncoding = $cmd -match "PYTHONIOENCODING\s*=\s*utf-8"

if ($isTu -and -not $hasEncoding) {
    # Write to stderr directly; Write-Error is suppressed by SilentlyContinue above.
    [Console]::Error.WriteLine("Warning (not blocked): ToolUniverse CLI on Windows needs 'PYTHONIOENCODING=utf-8' to avoid cp932 mojibake. Prefer: PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu <COMMAND>. Re-run with the prefix if output looks garbled.")
}

exit 0
