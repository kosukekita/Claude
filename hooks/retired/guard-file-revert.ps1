# guard-file-revert.ps1
# Retired after the cross-platform Python snapshot pair replaced it.

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
    if (-not (Test-Path -LiteralPath $file)) { exit 0 }

    $stateDir = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.claude\state\file-snapshots'
    $snap = Join-Path $stateDir ((Get-StateKey $file) + '.json')
    if (-not (Test-Path -LiteralPath $snap)) { exit 0 }

    $s = Get-Content -LiteralPath $snap -Raw -ErrorAction Stop | ConvertFrom-Json
    $cur = Get-ContentHash $file
    if ($null -eq $cur) { exit 0 }
    if ($cur -eq $s.last_seen_hash -or $cur -eq $s.last_agent_write_hash) { exit 0 }

    $mt = (Get-Item -LiteralPath $file).LastWriteTime.ToString('u')
    [Console]::Error.WriteLine("REVERT GUARD (blocked): '$file' changed on disk since you last read/wrote it (modified $mt). Re-read the file and reconcile the current content.")
    exit 2
} catch {
    exit 0
}
