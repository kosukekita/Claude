#!/usr/bin/env bash
# 各PCで一度だけ実行するCodexセットアップ（べき等）。
#   1) Codex CLI を最新化（gpt-5.6-sol は新しいCLIでないと 400 で弾かれる）
#   2) PATH上の「古いcodexの影」を退治（npm prefix 外の孤児インストールは
#      `codex update` が届かないまま PATH 先頭に居座り、tmux/ログインシェルだけ
#      旧版が起動して gpt-5.6-sol が 400 で落ちる。2026-07-17 実機で遭遇）
#   3) ~/.codex/config.toml の既定モデルを gpt-5.6-sol にする（top-level `model`）
#   4) /goal（自走実装）と goals 機能フラグを有効化
# ~/.claude は全PCへGitHub同期されるので、このスクリプトも各PCに配られる。
# 各PCで:  bash ~/.claude/bin/setup-codex-latest-model.sh
# （Windowsは git-bash か WSL で実行。ネイティブなら下の手動手順を参照）
set -eu

MODEL="gpt-5.6-sol"
CFG="$HOME/.codex/config.toml"

echo "[1/6] Codex CLI を最新化..."
if command -v codex >/dev/null 2>&1; then
  codex update || echo "  (codex update 失敗/不要。必要なら手動で 'npm install -g @openai/codex')"
  echo "  version: $(codex --version 2>/dev/null || echo '?')"
else
  echo "  codex コマンドが見つかりません。先に Codex CLI を入れてください。"
fi

echo "[2/6] PATH上の古いcodexを検出して現行版へ貼り替え..."
# npm の global prefix が正本。それ以外の場所に居る codex 実体は
# `codex update` が更新できないので、シンボリックリンクを正本へ向け直す。
NPM_PREFIX="$(npm prefix -g 2>/dev/null || true)"
if [ -n "$NPM_PREFIX" ] && [ -x "$NPM_PREFIX/lib/node_modules/@openai/codex/bin/codex.js" ]; then
  CANON="$NPM_PREFIX/lib/node_modules/@openai/codex/bin/codex.js"
  # ログインシェルのPATHを再現して、実際に何が拾われるかを見る
  for d in $(printf '%s' "$PATH" | tr ':' ' '); do
    [ -e "$d/codex" ] || continue
    real="$(readlink -f "$d/codex" 2>/dev/null || printf '%s' "$d/codex")"
    [ "$real" = "$(readlink -f "$CANON")" ] && continue
    ver="$("$d/codex" --version 2>/dev/null | head -1 || echo '?')"
    echo "  影を発見: $d/codex ($ver) → $CANON へ貼り替え"
    ln -sfn "$CANON" "$d/codex"
  done
  echo "  解決先: $(command -v codex) ($(codex --version 2>/dev/null || echo '?'))"
else
  echo "  (npm global prefix が特定できずスキップ)"
fi

echo "[3/6] $CFG に model = \"$MODEL\" を設定（べき等）..."
mkdir -p "$HOME/.codex"; touch "$CFG"
if grep -qE '^[[:space:]]*model[[:space:]]*=' "$CFG"; then
  # 既存の top-level model 行を書き換え（最初の1件のみ・portable awk）
  awk -v m="$MODEL" '{ if ($0 ~ /^[[:space:]]*model[[:space:]]*=/ && !d) { print "model = \"" m "\""; d=1 } else print }' "$CFG" > "$CFG.tmp"
  mv "$CFG.tmp" "$CFG"
else
  # 先頭に追記（TOMLは最初のテーブルより前なら top-level キー可）
  printf 'model = "%s"\n' "$MODEL" | cat - "$CFG" > "$CFG.tmp" && mv "$CFG.tmp" "$CFG"
fi

echo "[4/6] /goal（goals）機能を有効化..."
codex features enable goals 2>/dev/null || echo "  (既に有効、または features サブコマンド未対応のCLI)"

echo "[5/6] agmsg（Codex↔Claude 相談チャネル）を導入..."
# /goal 自走中の Codex が、元プランを書いた Fable 5 に相談するための経路。
# 導入済みなら --update（scripts だけ入れ替え、DB・チームは温存）、未導入なら新規install。
if command -v git >/dev/null 2>&1; then
  TMPD="$(mktemp -d)"
  if git clone --depth 1 https://github.com/fujibee/agmsg.git "$TMPD/agmsg" >/dev/null 2>&1; then
    if [ -d "$HOME/.agents/skills/agmsg" ]; then
      (cd "$TMPD/agmsg" && ./install.sh --cmd agmsg --update >/dev/null) \
        && echo "  更新: $(bash "$HOME/.agents/skills/agmsg/scripts/version.sh" 2>/dev/null || echo '?')"
    else
      (cd "$TMPD/agmsg" && ./install.sh --cmd agmsg) && echo "  導入完了: ~/.agents/skills/agmsg/"
    fi
  else
    echo "  (clone 失敗。手動: npx agmsg)"
  fi
  rm -rf "$TMPD"
else
  echo "  (git が無いのでスキップ。手動: npx agmsg)"
fi

echo "[6/6] 確認..."
grep -nE '^[[:space:]]*model[[:space:]]*=' "$CFG" || { echo "  ★ model 行が見当たりません"; exit 1; }
codex features list 2>/dev/null | grep -E '^goals' || true
echo "完了。検証: codex exec --sandbox read-only --skip-git-repo-check \"OK\"  で  model: $MODEL  と出れば成功。"
echo "      /goal は codex TUI で '/goal <目標>' と打つと 'Goal active' と出れば成功。"

# --- Windowsネイティブ（git-bash/WSLが無い場合）の手動手順 ---
#   1) codex update
#   2) %USERPROFILE%\.codex\config.toml の先頭付近に次の1行を追加:
#        model = "gpt-5.6-sol"
#   3) codex features enable goals
