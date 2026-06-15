#!/usr/bin/env bash
# Human-in-the-loop reproduction loop (Linux / Mac / Git Bash / WSL).
# Windows ネイティブ PowerShell では hitl-loop.template.ps1 を使うこと。
#
# このファイルをコピーし、下の手順を編集して実行する。
# エージェントがスクリプトを起動し、ユーザーが端末の指示に従う。
#
# 使い方:
#   bash hitl-loop.template.sh
#
# ヘルパー2つ:
#   step "<指示>"            → 指示を表示し Enter を待つ
#   capture VAR "<質問>"     → 質問を表示し、回答を VAR に読み込む
#
# 最後に、キャプチャした値が KEY=VALUE 形式で出力される（エージェントが解析する）。

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [完了したら Enter] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- ここから編集 -------------------------------------------------------

step "http://localhost:3000 でアプリを開き、サインインする。"

capture ERRORED "'Export' ボタンをクリック。エラーは出たか？ (y/n)"

capture ERROR_MSG "エラーメッセージを貼り付け（無ければ 'none'）:"

# --- ここまで編集 -------------------------------------------------------

printf '\n--- Captured ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
