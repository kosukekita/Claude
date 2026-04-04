# protect-files.ps1
# Claude Code PreToolUse hook: 機密ファイルへの編集をブロック
# exit 2 でブロック（Claudeへエラーメッセージを返す）、exit 0 で通過

$ErrorActionPreference = "SilentlyContinue"

# stdin から JSON を読み取り、ファイルパスを抽出
$json = $input | Out-String
$filePath = ""
try {
    $obj = $json | ConvertFrom-Json
    $filePath = $obj.tool_input.file_path
    if (-not $filePath) {
        $filePath = $obj.tool_input.path
    }
    if (-not $filePath) { exit 0 }
} catch {
    exit 0
}

# パスを正規化（バックスラッシュをスラッシュに統一）
$normalizedPath = $filePath -replace '\\', '/'

$protectedPatterns = @(
    "\.env$",
    "\.env\.",
    "\.pem$",
    "\.key$",
    "\.p12$",
    "\.pfx$",
    "credentials\.json$",
    "secrets/",
    "secret/",
    "\.ssh/",
    "id_rsa",
    "id_ed25519"
)

foreach ($pattern in $protectedPatterns) {
    if ($normalizedPath -match $pattern) {
        Write-Error "Blocked: '$filePath' is a protected file. Explain why this edit is necessary before proceeding."
        exit 2
    }
}

exit 0
