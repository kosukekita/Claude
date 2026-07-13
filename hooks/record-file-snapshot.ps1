# record-file-snapshot.ps1
# Claude Code PostToolUse hook (Read|Write|Edit|MultiEdit|NotebookEdit).
# エージェントがファイルを「見た/書いた」後に、その現物 hash をスナップショット保存する。
# Read -> last_seen_hash を更新（＝最後に見た内容）。
# Write/Edit -> last_seen_hash と last_agent_write_hash の両方を更新（＝自分が書いた内容）。
# guard-file-revert.ps1 がこの記録と現物を比較して外部変更を検知する。
# 何かあれば必ず exit 0（fail-open）。

$ErrorActionPreference = "SilentlyContinue"

function Get-StateKey($p) {
    $n = $p.Replace('\','/').TrimEnd('/').ToLowerInvariant()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($n)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    (($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '').Substring(0,40)
}
function Get-ContentHash($p) {
    try {
        $fi = Get-Item -LiteralPath $p -ErrorAction Stop
        if ($fi.Length -gt 52428800) { return "sz:$($fi.Length):mt:$($fi.LastWriteTimeUtc.Ticks)" }
        return (Get-FileHash -LiteralPath $p -Algorithm SHA256 -ErrorAction Stop).Hash
    } catch { return $null }
}

try {
    $json = $input | Out-String
    $obj = $json | ConvertFrom-Json
    $tool = "$($obj.tool_name)"
    $file = $obj.tool_input.file_path
    if (-not $file) { $file = $obj.tool_input.path }
    if (-not $file) { $file = $obj.tool_input.notebook_path }
    if (-not $file) { exit 0 }
    if (-not (Test-Path -LiteralPath $file)) { exit 0 }

    $cur = Get-ContentHash $file
    if ($null -eq $cur) { exit 0 }

    $stateDir = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.claude\state\file-snapshots'
    if (-not (Test-Path -LiteralPath $stateDir)) { New-Item -ItemType Directory -Force -Path $stateDir | Out-Null }
    $snap = Join-Path $stateDir ((Get-StateKey $file) + '.json')

    $data = @{}
    if (Test-Path -LiteralPath $snap) {
        try { $existing = Get-Content -LiteralPath $snap -Raw | ConvertFrom-Json
              $existing.PSObject.Properties | ForEach-Object { $data[$_.Name] = $_.Value } } catch {}
    }
    $now = (Get-Date).ToString('u')
    $data['path'] = $file.Replace('\','/')
    $data['last_seen_hash'] = $cur
    $data['last_seen_at'] = $now
    $data['last_seen_by'] = $tool
    if ($tool -match '^(Write|Edit|MultiEdit|NotebookEdit)$') {
        $data['last_agent_write_hash'] = $cur
        $data['last_agent_write_at'] = $now
    }
    ($data | ConvertTo-Json -Compress) | Set-Content -LiteralPath $snap -Encoding UTF8
    exit 0
} catch {
    exit 0
}
