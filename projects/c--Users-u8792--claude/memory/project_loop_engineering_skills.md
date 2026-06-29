---
name: project_loop_engineering_skills
description: Loop Engineering IEEE論文から3成果物を作成（loop-evaluator/loop-engineering スキル＋loop-reviewer agent）。非自明な判断=agent定義の正しいパス規約とRED語彙からの合理化テーブル
metadata: 
  node_type: memory
  type: project
  originSessionId: f0bd5198-80e9-4600-a3b2-c4a01583f314
---

Loop Engineering IEEE 論文を取り込み、~/.claude を3成果物で強化（2026-06-29完了）。

**成果物（全てpush済）:**
- `skills/loop-evaluator/SKILL.md` — 生成器/評価者の分離規律（自分が自分の出力を採点しそうなとき）。GAN/maker-checker由来。
- `skills/loop-engineering/SKILL.md` — 自走ループ設計（5 moves×6 parts×5 failure shapes×first-loopチェックリスト×4 silent debts）。
- `agents/loop-reviewer.md` — 敵対的評価者サブエージェント（Agent の subagent_type=loop-reviewer）。「壊れている前提」で実行して採点、読むだけで通さない。
- `CLAUDE.md` の「ループ・自走化の規律」節（loop-engineering の前）。

**非自明な判断（再現困難なので記憶):**
1. **agent定義の正しいパスは `~/.claude/agents/<name>.md`**。最初 `~/.claude/.claude/agents/` (二重.claude) に作ったが、これはハーネス内部所有でgitignore対象＝同期されない。`~/.claude/.claude/` には `scheduled_tasks.lock`/`settings.local.json` 等ハーネス所有物があり**削除厳禁**。auto-push.ps1 のホワイトリストに `agents/` を追加して同期対象化（commit済）。→ [[feedback_autosync_hook_divergence_deadlock]]
2. **合理化テーブルは RED ベースライン実測の語彙で作る**。skill-writing の TDD に従い、スキル無しで圧力シナリオ（締切/サンクコスト/「ユーザーがいいと言った」）をサブエージェントに与え、出た合理化を verbatim で表に。想像で書くと刺さらない。loop-evaluator は12行、各行「合理化→なぜ失敗するか」。
3. **CSO: description に workflow 要約を書かない**（WHEN/症状のみ）。要約するとClaudeが本文を読まず description で済ます既知の罠。[[project_skill_consolidation]] と同方針。
4. ループの実体（動く cron/loop）は作っていない。ユーザー要求は「設定の強化」＝スキル＋規律のみ。

**4つの静かな負債（恒久姿勢、CLAUDE.mdに圧縮記載・詳細はスキル本文）:** Verification debt（独立評価者）/Comprehension rot（サンプル必読＋各変更を説明）/Cognitive surrender（人間チェックポイント最低1）/Token blowout（無人稼働前にハード上限）。
