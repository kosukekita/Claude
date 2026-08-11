# log-commands.ps1
# Retired: this hook recorded raw commands indefinitely and could retain secrets.
# Kept for audit history only; it is not registered in settings.json.
# RULE: keep this file ASCII-only (encoding issues have killed hooks before).

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

$logFile = "$env:USERPROFILE\.claude\command-log.txt"
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
$logEntry = "$timestamp  $cmd"

Add-Content -Path $logFile -Value $logEntry -Encoding UTF8

exit 0
