# Human-in-the-loop reproduction loop (Windows native PowerShell).
# Linux / Mac / Git Bash / WSL では hitl-loop.template.sh を使うこと。
#
# このファイルをコピーし、下の手順を編集して実行する。
# エージェントがスクリプトを起動し、ユーザーが端末の指示に従う。
#
# 使い方:
#   powershell -NonInteractive:$false -File hitl-loop.template.ps1
#   （対話入力が必要なので NonInteractive では動かない。実ターミナルで実行する）
#
# ヘルパー2つ:
#   Step "<指示>"             → 指示を表示し Enter を待つ
#   Capture -Name VAR "<質問>" → 質問を表示し、回答を $script:VAR に読み込む
#
# 最後に、キャプチャした値が KEY=VALUE 形式で出力される（エージェントが解析する）。

$ErrorActionPreference = 'Stop'

# UTF-8 出力（cp932 文字化け回避）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Step([string]$Instruction) {
    Write-Host "`n>>> $Instruction"
    Read-Host "    [完了したら Enter]" | Out-Null
}

function Capture([string]$Name, [string]$Question) {
    Write-Host "`n>>> $Question"
    $answer = Read-Host "    > "
    Set-Variable -Name $Name -Value $answer -Scope Script
}

# --- ここから編集 -------------------------------------------------------

Step "http://localhost:3000 でアプリを開き、サインインする。"

Capture -Name ERRORED   "'Export' ボタンをクリック。エラーは出たか？ (y/n)"

Capture -Name ERROR_MSG "エラーメッセージを貼り付け（無ければ 'none'）:"

# --- ここまで編集 -------------------------------------------------------

Write-Host "`n--- Captured ---"
Write-Host "ERRORED=$($script:ERRORED)"
Write-Host "ERROR_MSG=$($script:ERROR_MSG)"
