# guard-file-revert.ps1
# Claude Code PreToolUse hook (Write|Edit|MultiEdit|NotebookEdit).
# 目的: ユーザーの手動編集を上書きする revert 事故を防ぐ。
# エージェントが最後に「見た/書いた」内容と、ディスク現物の hash が食い違う場合だけ
# exit 2 でブロックし、再読込＆照合を促す。証拠がある時だけ止める（過剰ブロック回避）。
# 何かあれば必ず exit 0（fail-open。グローバル運用を絶対に壊さない）。

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
    $file = $obj.tool_input.file_path
    if (-not $file) { $file = $obj.tool_input.path }
    if (-not $file) { exit 0 }
    if (-not (Test-Path -LiteralPath $file)) { exit 0 }   # 新規作成は対象外

    $stateDir = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.claude\state\file-snapshots'
    $snap = Join-Path $stateDir ((Get-StateKey $file) + '.json')
    if (-not (Test-Path -LiteralPath $snap)) { exit 0 }   # 未追跡=初回接触は判定不能

    $s = Get-Content -LiteralPath $snap -Raw -ErrorAction Stop | ConvertFrom-Json
    $cur = Get-ContentHash $file
    if ($null -eq $cur) { exit 0 }
    if ($cur -eq $s.last_seen_hash -or $cur -eq $s.last_agent_write_hash) { exit 0 }  # 既知の内容

    $mt = (Get-Item -LiteralPath $file).LastWriteTime.ToString('u')
    [Console]::Error.WriteLine("REVERT GUARD (blocked): '$file' changed on disk since you last read/wrote it (modified $mt) — most likely a manual edit or deletion by the user. Re-READ the file now and reconcile your change with its CURRENT content. Do NOT overwrite it from old context, a backup, a template, or a generator's output. If you intend to discard the user's change, ask them first.")
    exit 2
} catch {
    exit 0
}
