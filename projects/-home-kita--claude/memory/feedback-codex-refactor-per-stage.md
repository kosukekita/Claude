---
name: feedback-codex-refactor-per-stage
description: 段階/タスクの区切りごとに Codex に独立レビューを依頼してリファクタリングする運用ルール（ユーザー恒久指示）
metadata:
  type: feedback
---

多段階の実装・開発タスクでは、**各段階（または各タスク）が一区切りついたら、Codex に独立レビューを依頼してリファクタリングする**こと。ユーザーの恒久運用ルール（2026-06-29 / igapi フェーズ3 実装中に明文化）。

**Why:**
- 自分（生成器）が自分のコードを採点すると Verification debt が溜まる（loop-engineering の「No と言える独立評価者」）。Codex を独立評価者に使うと、自分では気づかない**命名の嘘・未実装リンクの露出・実コードのセキュリティ穴**まで出てくる（実例: igapi で leading-dot candidate_id の穴を Codex 切り出し作業中に発見）。
- これまで「各段階でリファクタ」をユーザーが毎回指示しないと忘れていた。属人化していたので恒久ルール化した。

**How to apply:**
1. 安全性レビューとリファクタレビューは**別物**として扱う。安全性を直したあとも、別途「純リファクタ観点（重複/責務分離/命名/YAGNI/可読性）だけ」で Codex に再レビューを依頼する。
2. 依頼は `codex:codex-rescue` サブエージェント（`Agent` ツール, subagent_type: "codex:codex-rescue"）に、会話文脈を要約したプロンプトを渡す（[[codex-consult]] スキルの手順）。**重い依頼（--effort high / レビュー / 実装委譲）は最初から `--background`**（foreground は親 Bash の 120 秒で切れる）。
3. Codex の提案は鵜呑みにせず、**安全側に倒れる・テストで担保できる・churn が少ないものから**適用する。Codex が「YAGNI でやるな」と言ったもの（例: 状態機械の汎用基底クラス化）は従う。挙動を変える項目（リネーム等）はテストも一緒に更新し、各バッチごとに全テスト緑を確認してからコミット。
4. リファクタはコミットを分ける（安全性修正コミットと混ぜない）。

関連: [[feedback-codex-rescue-hang-causes]]（委譲がハングする真因）, [[feedback-codex-review-output-via-session-jsonl]]（no output でも本文を回収する方法）。
