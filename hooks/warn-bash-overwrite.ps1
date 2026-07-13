# warn-bash-overwrite.ps1
# Claude Code PreToolUse hook (Bash): warn-only, never blocks (exit 0 always).
# Bash が起動するサブプロセスの書き込み(shutil.copyfile / write_text / > file / 生成スクリプト
# 再実行 等)は Write/Edit フックを通らないので、ここでコマンド文字列を見て「既存ファイルを
# 上書き/再生成しうる」パターンだけに助言を出す。ブロックはしない(誤検知が多いため)。

$ErrorActionPreference = "SilentlyContinue"

try {
    $json = $input | Out-String
    $obj = $json | ConvertFrom-Json
    $cmd = $obj.tool_input.command
    if (-not $cmd) { exit 0 }

    # 既存ファイルを丸ごと作り直す/上書きする典型パターン
    $risky = @(
        'shutil\.copyfile', 'shutil\.copy2?\(', 'copyfile\(', 'copytree\(',
        '\.write_text\(', '\.write_bytes\(', 'Path\([^)]*\)\.write',
        "open\([^)]*,\s*['""][wa]", 'Set-Content', 'Out-File', 'Copy-Item',
        'build_\w+\.py', 'generate\w*\.py', 'make_\w+\.py',
        '>\s*[^>\s|]+\.(docx|md|txt|json|ya?ml|html?|csv|xlsx|pptx|tex|bib)'
    )
    $hit = $false
    foreach ($p in $risky) { if ($cmd -match $p) { $hit = $true; break } }

    if ($hit) {
        [Console]::Error.WriteLine("REVERT-RISK REMINDER (not blocked): this command may overwrite or regenerate existing files outside the Write/Edit guard. Before it runs: if the user manually edited or deleted any target since you last generated it, re-read that file and fold their changes into the source first. Prefer editing the live file over rebuilding it from a backup/template. Never resurrect content the user deleted.")
    }
    exit 0
} catch {
    exit 0
}
