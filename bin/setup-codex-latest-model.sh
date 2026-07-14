#!/usr/bin/env bash
# 各PCで一度だけ実行するCodexセットアップ（べき等）。
#   1) Codex CLI を最新化（gpt-5.6-sol は新しいCLIでないと 400 で弾かれる）
#   2) ~/.codex/config.toml の既定モデルを gpt-5.6-sol にする（top-level `model`）
# ~/.claude は全PCへGitHub同期されるので、このスクリプトも各PCに配られる。
# 各PCで:  bash ~/.claude/bin/setup-codex-latest-model.sh
# （Windowsは git-bash か WSL で実行。ネイティブなら下の手動2手順を参照）
set -eu

MODEL="gpt-5.6-sol"
CFG="$HOME/.codex/config.toml"

echo "[1/3] Codex CLI を最新化..."
if command -v codex >/dev/null 2>&1; then
  codex update || echo "  (codex update 失敗/不要。必要なら手動で 'npm install -g @openai/codex')"
  echo "  version: $(codex --version 2>/dev/null || echo '?')"
else
  echo "  codex コマンドが見つかりません。先に Codex CLI を入れてください。"
fi

echo "[2/3] $CFG に model = \"$MODEL\" を設定（べき等）..."
mkdir -p "$HOME/.codex"; touch "$CFG"
if grep -qE '^[[:space:]]*model[[:space:]]*=' "$CFG"; then
  # 既存の top-level model 行を書き換え（最初の1件のみ・portable awk）
  awk -v m="$MODEL" '{ if ($0 ~ /^[[:space:]]*model[[:space:]]*=/ && !d) { print "model = \"" m "\""; d=1 } else print }' "$CFG" > "$CFG.tmp"
  mv "$CFG.tmp" "$CFG"
else
  # 先頭に追記（TOMLは最初のテーブルより前なら top-level キー可）
  printf 'model = "%s"\n' "$MODEL" | cat - "$CFG" > "$CFG.tmp" && mv "$CFG.tmp" "$CFG"
fi

echo "[3/3] 確認..."
grep -nE '^[[:space:]]*model[[:space:]]*=' "$CFG" || { echo "  ★ model 行が見当たりません"; exit 1; }
echo "完了。検証: codex exec --sandbox read-only --skip-git-repo-check \"OK\"  で  model: $MODEL  と出れば成功。"

# --- Windowsネイティブ（git-bash/WSLが無い場合）の手動2手順 ---
#   1) codex update
#   2) %USERPROFILE%\.codex\config.toml の先頭付近に次の1行を追加:
#        model = "gpt-5.6-sol"
