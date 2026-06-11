# log-commands.ps1
# Claude Code PreToolUse hook: log Bash commands with a timestamp.
# RULE: keep this file ASCII-only (encoding issues have killed hooks before).

$ErrorActionPreference = "SilentlyContinue"

# Read JSON from stdin and extract the command
$json = $input | Out-String
$cmd = ""
try {
    $obj = $json | ConvertFrom-Json
    $cmd = $obj.tool_input.command
    if (-not $cmd) { exit 0 }
} catch {
    exit 0
}

$logFile = "$env:USERPROFILE\.claude\command-log.txt"
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
$logEntry = "$timestamp  $cmd"

Add-Content -Path $logFile -Value $logEntry -Encoding UTF8

exit 0
