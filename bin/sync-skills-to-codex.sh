#!/usr/bin/env bash
# sync-skills-to-codex.sh — ~/.claude/skills のスキルを Codex の ~/.agents/skills へシンボリックリンクで共有する
#
# 使い方:
#   bash ~/.claude/bin/sync-skills-to-codex.sh            # 同期実行
#   bash ~/.claude/bin/sync-skills-to-codex.sh --dry-run  # 何が起きるか表示のみ
#
# 仕様:
#   - リンク方式なので ~/.claude を git pull すれば Codex 側も自動で最新になる（再実行不要）
#   - ただし「新規スキルの追加」と「スキルの削除」はリンクの張り直しが必要 → pull 後に再実行を推奨
#   - Codex 専用に実体インストールされたスキル（agmsg 等、リンクでない実体ディレクトリ）は絶対に触らない
#   - ソース側で削除されたスキルのぶら下がりリンクは自動削除する
#   - 冪等（何度実行しても安全）
#
# テスト用: SKILLS_SRC / SKILLS_DST 環境変数で対象ディレクトリを差し替え可能
set -euo pipefail

SRC="${SKILLS_SRC:-$HOME/.claude/skills}"
DST="${SKILLS_DST:-$HOME/.agents/skills}"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

if [ ! -d "$SRC" ]; then
  echo "ERROR: ソースが見つかりません: $SRC" >&2
  exit 1
fi
mkdir -p "$DST"

run() { if [ "$DRY" = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

linked=0 retargeted=0 kept=0 protected=0 cleaned=0

# 1) ソース側で消えたスキルの、ぶら下がりリンクを掃除（SRC配下を指すリンクのみ対象）
for l in "$DST"/*; do
  [ -L "$l" ] || continue
  tgt=$(readlink "$l")
  case "$tgt" in
    "$SRC"/*)
      if [ ! -e "$l" ]; then
        echo "clean : $(basename "$l") (ソース削除済み)"
        run rm "$l"
        cleaned=$((cleaned + 1))
      fi
      ;;
  esac
done

# 2) 各スキルをリンク
shopt -s nullglob
for d in "$SRC"/*/; do
  d="${d%/}"
  name=$(basename "$d")
  t="$DST/$name"
  if [ -L "$t" ]; then
    if [ "$(readlink "$t")" = "$d" ]; then
      kept=$((kept + 1))
    else
      echo "retarget: $name"
      run ln -sfn "$d" "$t"
      retargeted=$((retargeted + 1))
    fi
  elif [ -e "$t" ]; then
    # 実体ディレクトリ/ファイル（Codex専用インストール等）は保護
    echo "protect: $name (実体が存在するためスキップ)"
    protected=$((protected + 1))
  else
    echo "link  : $name"
    run ln -s "$d" "$t"
    linked=$((linked + 1))
  fi
done

echo "----"
echo "新規リンク: $linked / 既存維持: $kept / 張り直し: $retargeted / 実体保護: $protected / 掃除: $cleaned"
echo "Codex スキル置き場: $DST"
