---
name: background-waiter-design
description: バックグラウンド監視でプロセス名の文字列マッチ(pgrep/pkill -f)を使うと自爆・デッドロックする。PID待ちか完了マーカーファイル方式を使う
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-10T09:45:55.524Z
---

★2026-08-10 に同種事故が1日3回発生（実測）:
1. `pkill -f "turbo_bench"` が自分のコマンド行に一致して自シェルを SIGTERM（exit 144）
2. `pgrep -f "agy --print"` の見張りが自分の eval 文字列に一致して永久ループ
3. 2つの発射台スクリプトが互いのコマンド行内の `agy -c -p` を「実行中」と誤検出し、
   **本体の agy が一度も起動しないまま約1時間デッドロック**（ユーザーの「何待ち？」で発覚）

**Why**: Bash ツールのラッパーは実行コマンド全文を自プロセスの引数に含むため、`-f`（full
cmdline マッチ）は監視対象の名前を書いた瞬間、監視スクリプト自身と兄弟スクリプトに一致する。
`[a]gy` 形式の自己免疫パターンは**自分には効くが兄弟には効かない**（兄弟のコマンド行には
プレーンな文字列が残るため）。

**How to apply**（バックグラウンドの長時間ジョブを待つとき）:
- **第一選択: 完了マーカーファイル**。ジョブ末尾で `echo DONE >> log` し、見張りは
  `until grep -q DONE log; do sleep 60; done`（プロセス表を一切見ない）
- 同一シェル内なら **PID 直接待ち**（`cmd & pid=$!; wait $pid`）
- どうしても pgrep するなら `-x`（コマンド名完全一致・agy 等の実行体名）を使い、`-f` は使わない
- kill も同様: 文字列 pkill でなく PID を特定してから kill
