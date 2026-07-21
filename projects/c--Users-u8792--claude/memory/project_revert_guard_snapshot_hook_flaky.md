---
name: revert-guard-snapshot-hook-flaky
description: Windowsでrecord-file-snapshot.ps1(PostToolUse)が間欠的に発火せず、guard-file-revert.ps1が自分の直前Editまで誤ブロックする既知バグ（2026-07-21実測・未修正）
metadata: 
  node_type: memory
  type: project
  originSessionId: ebaa69e7-513b-42e6-b8dd-3f06de095786
---

Windows機で `~/.claude/hooks/record-file-snapshot.ps1`（PostToolUse: Read|Write|Edit|MultiEdit|NotebookEdit）が**間欠的に実行されない**。その結果 `~/.claude/state/file-snapshots/*.json` の hash が古いまま残り、`guard-file-revert.ps1`（PreToolUse）が**自分自身の直前の正常な Edit の結果**を「外部変更」と誤検知して連続ブロックする。

**実測（2026-07-21, slide-making スキル編集セッション）:**
- 症状パターン: Read → Edit 1回目成功 → 2回目以降ブロック（成功した Edit の PostToolUse 記録が snapshot に反映されない）。
- 証拠: SKILL.md の snapshot が `last_agent_write_at: 09:57:16` で停止したまま、その後 10:15 までの複数の成功 Edit・Read が未記録。settings.json の matcher 配線は正常。スクリプトのロジックも正常（単体では動く）。
- 真因は未特定（PowerShell 起動の間欠失敗か、ハーネス側の PostToolUse 実行スキップ）。**要修正**: fail-open 設計なので記録失敗が無言で蓄積する。

**運用（修正までの正攻法）:** ガードにブロックされたら、ガード自身の指示どおり対象ファイルを Read で再読込・現物照合してから同じ Edit を再実行する（これで snapshot の last_seen が更新され通る。1 Edit ごとに必要な場合あり）。

**やってはいけない:** `file-snapshots/*.json` を手動で書き換えて通す方法は保護機構の迂回にあたり、auto-mode 分類器も正しくブロックする（[[feedback_protect_files_hook_secrets_path_block]] と同じ原理）。修正するならフック本体を直す。

関連: [[file-revert-prevention-playbook]]（ガード設計の出典）、[[feedback_autosync_hook_divergence_deadlock]]（同じ hooks 群の既知問題）
