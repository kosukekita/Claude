---
name: claude-md-refactor-2026-09-markers
description: 2026-09-05 CLAUDE.md 刷新(18.5KB→11KB)の判断基準と、AGENTS.md 同期用 claude-only/codex-only マーカー規約。ベースライン計測のパイプ罠つき
metadata: 
  node_type: memory
  type: project
  originSessionId: 72965189-542c-5a7e-9e50-abe3b3e81324
  modified: 2026-09-05T02:35:48.995Z
---

# CLAUDE.md 刷新 2026-09-05（ユーザー指示「当たり前の部分を消す」）

**Why:** CLAUDE.md がハーネスのシステムプロンプトと同じ指示・MEMORY.md と同じ内容・事故の物語で膨らみ、毎セッション二重三重に注入されていた。ユーザーは特に「自分でターミナル/ブラウザ操作できるのに人間に頼む」件を重視。

**削った基準（今後も同じ基準で足さない）:**
- ハーネスが既定で持つ指示（自律・再試行・範囲を狭めない・上書き前に読む・記憶の書き方・「tests pass は主張」）は本文に書かない。**ユーザー固有の差分だけ**（人間に頼んでよい (a)〜(d) の4分類、試した経路一覧の義務、診断→自力→Codex の3段）を残す
- MEMORY.md と二重の項目は **CLAUDE.md は1行＋[[記憶]]ポインタ、経緯・実例は記憶**（訂正OS節にもこの規則を明文化）
- 「正本は skill」と書いている手順（校正パス・officecli）は本文から手順を消し、規則だけ残す
- 違反日付つきの項目は「当たり前」に見えても削除せず圧縮

**AGENTS.md 同期のマーカー規約（hooks/memory-sync-codex.sh が解釈）:**
- `<!-- claude-only -->` … `<!-- /claude-only -->` : Codex 向け出力から丸ごと除去（記憶の節・ツールコール漏洩バグ・Claude視点の役割分担）
- 行頭単独の `<!-- codex-only` … `-->` : 中身だけ Codex 向けに展開（Codex 視点の役割分担「あなたが実装者・プランは .agent-plan*.md」）。Claude は HTML コメントとして無視
- 閉じ忘れは fail-open（以降を出さず exit 0）。テストは hooks/tests/test_memory_sync_codex.sh（9件・CLAUDE_HOME/CODEX_HOME を一時ディレクトリに向ける）

**How to apply:** CLAUDE.md に Claude 固有の節を足すときは claude-only で包む。Codex にだけ違う言い方をしたい節は codex-only コメントを併記する。

**罠（自分の計測ミス）:** `bash run_all.sh | tail -5; echo $?` は **tail の終了コード**を見ている。「全 PASS・exit 0」と誤記録した（実際は test_phase1 と test_guard の2件が赤）。パイプ越しの終了コードは `${PIPESTATUS[0]}` で取る。[[verify-with-hashes-not-impressions]] と同型。

関連: [[claude-config-overhaul-2026-08]] [[hook-test-baseline-red-720p-gap]] [[codex-unavailable-sonnet5-fallback]]（本件も Codex 利用上限で Sonnet 5 に委譲。TUI の 400「newer version」は上限の誤表示だった）
