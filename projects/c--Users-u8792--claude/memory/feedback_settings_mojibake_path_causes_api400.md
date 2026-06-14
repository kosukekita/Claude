---
name: feedback_settings_mojibake_path_causes_api400
description: 特定プロジェクトでだけ起動直後に API 400 invalid high surrogate が出て /clear で直らない時の真因と切り分け。最有力は SessionStart フックが .claude-memory を非UTF-8 bash で処理して孤立サロゲートを注入していること
metadata:
  node_type: memory
  type: feedback
---

「特定プロジェクト（特に P:/ = pCloud 配下）で Claude Code を起動し、こんにちは等の簡単な入力を送るだけで毎ターン `API Error: 400 The request body is not valid JSON: invalid high surrogate in string: line 1 column N`（N は起動ごと変動）が出て、`/clear` でも直らない」時の確定した真因と直し方。

**真因（2026-06-14 Osteoporosis で特定・実機解決済み）:** SessionStart フック `memory-inject-project.sh` が、プロジェクト直下の `.claude-memory/` を **WSL bash（壊れたディストリ＝非UTF-8ロケール）** で `cat`/`awk`/`grep`/`sed` のテキストパイプライン処理する際にマルチバイト UTF-8 を分断し、**孤立サロゲート（孤立 LOW = U+DCxx を多数）を生成**。それが SessionStart の `additionalContext` として送信ボディに入り、Claude Code 本体の直列化を経て API に拒否されていた。`.claude-memory/` のファイル自体は健全（壊すのはフックの処理過程）。`.claude-memory/` は pCloud プロジェクトにしか無く `~/.claude` には無いため **そのプロジェクトでだけ発生**し、`~/.claude` では出ない。プロジェクトの `.claude/` を外すと「プロジェクト認識」が変わりフック挙動が変わって消える＝「犯人は .claude/ の中身ではなくディレクトリ存在」という観測の正体。

**切り分けの決定打（これを最初にやる）:** `cd <該当プロジェクト>; "test" | claude -p --debug-file C:/Users/u8792/.claude/work/dbg.log` を実行し、dbg.log の中の各 SessionStart フック出力行（`additionalContext": "...`）を **JSONパースして値の中**の孤立サロゲートを数える（ファイルレベルでは健全に見える＝`\uDCxx` エスケープとして値に埋まっているため、必ず JSON パース後の値を見る）。`Hook SessionStart (...) provided additionalContext (N chars)` 行でどのフックが何文字注入したかも分かる。送信ボディに入るフック出力こそが犯人。

**修正（実施済み・全プロジェクトに恒久的に効く）:**
1. `memory-inject-project.sh`: 出力を必ず python3 経由で JSON 化し、その段で孤立サロゲート(ペアでない high/low)と U+8792 を除去（正しいサロゲートペア=絵文字は保持）。jq 出力は廃止（jq は孤立サロゲートを除去できない）。
2. `memory-inject.ps1`: 出力直前に同等のサニタイズ関数 Remove-BadChars を追加。bash版・PowerShell版の両フックを防御。
3. 既存の汚染 transcript（`~/.claude/projects/p--Code-Research-Osteoporosis/*.jsonl` 27件、孤立LOW計2366個）も除去済み（バックアップ `~/.claude/work/transcript_backup`）。本体が transcript を直接読む経路の保険。

**How to apply（再発時）:**
- まず上の `--debug-file` 切り分けで犯人フックを特定する。推測で個別ファイルを潰すと長時間迷走する（2026-06-14 はファイル/設定/MCP/.git を延々と潰して空振りした）。
- 検出・サニタイズ用スクリプトは `~/.claude/work/` に常設: `scan_jsonl_values.py`(JSON値内の孤立サロゲート), `scan_all_bad.py`(ファイルレベル), `clean_transcripts.py`(transcript除去)。生文字は会話に出さず数値(U+XXXX)で報告する。
- 関連: [[feedback_powershell_hook_utf8_stdout]]（同じ文字化けファミリーの PowerShell 版。今回は bash 版）、[[feedback_u8792_path_unicode_escape]]（U+8792 の出どころ）、[[feedback_surrogate_in_grep_pollutes_api_body]]（会話コンテキスト汚染版＝こちらは /clear で復旧。本件は永続フック汚染で /clear では直らずフック修正が必要）。
- 残課題: WSL bash が壊れている（/bin/bash 起動不可）。Claude Code は `command -v bash` で WSL bash を拾うため、フックが非UTF-8で動く。settings.json のフック起動を git bash 優先にすれば文字化け自体を防げる（サニタイズは入れたので 400 は出ないが、日本語が一部欠損しうる）。
