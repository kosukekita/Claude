# log-commands.ps1
# Claude Code PreToolUse hook: Bash コマンドをタイムスタンプ付きでログに記録

$ErrorActionPreference = "SilentlyContinue"

# stdin から JSON を読み取り、コマンドを抽出
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
