# block-dangerous.ps1
# Claude Code PreToolUse hook: 危険なコマンドをブロック
# exit 2 でブロック（Claudeへエラーメッセージを返す）、exit 0 で通過

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

$dangerousPatterns = @(
    "rm\s+-rf",
    "rm\s+.*-r",
    "git\s+reset\s+--hard",
    "git\s+push\s+.*--force",
    "git\s+push\s+.*-f\b",
    "git\s+clean\s+-f",
    "git\s+branch\s+-[Dd]\s+main",
    "git\s+branch\s+-[Dd]\s+master",
    "DROP\s+TABLE",
    "DROP\s+DATABASE",
    "TRUNCATE\s+TABLE",
    "curl\s+.*\|\s*(ba)?sh",
    "wget\s+.*\|\s*(ba)?sh",
    "curl\s+.*\|\s*powershell",
    "iex\s*\(",
    "Invoke-Expression"
)

foreach ($pattern in $dangerousPatterns) {
    if ($cmd -match $pattern) {
        Write-Error "Blocked: Command '$cmd' matches dangerous pattern '$pattern'. Propose a safer alternative."
        exit 2
    }
}

# Block global pip install (prefer uv).
# Allow uv-managed installs (uv pip / uv add / uv run --with) and in-venv pip.
$isUvManaged = $cmd -match "\buv\s+(pip|add|run)\b"
$isPipInstall = $cmd -match "(^|\s|;|&&|\|)\s*(sudo\s+)?(python[0-9.]*\s+-m\s+)?pip[0-9.]*\s+install\b"
if ($isPipInstall -and -not $isUvManaged) {
    Write-Error "Blocked: global 'pip install' is forbidden. Use uv instead: 'uv add <pkg>', 'uv pip install <pkg>', or 'uv run --with <pkg>'. For an isolated env, create one with 'uv venv' and run inside it."
    exit 2
}

exit 0
