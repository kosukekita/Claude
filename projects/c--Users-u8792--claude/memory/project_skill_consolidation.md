---
name: project_skill_consolidation
description: ~/.claude/skills のリファクタリング結果。achievement+career→cv-profileに統合。重複reference 2件を解消。他はトリガー修正のみで据え置き
metadata:
  type: project
---

# スキル統合（2026-05-31 実施）

`~/.claude/skills`（40スキル）のリファクタリング。13エージェント並列分析＋敵対的検証の結論に基づき実施。

## 実施内容
- **マージ**: `achievement`（業績）+ `career`（経歴）→ **`cv-profile`**。両 reference を verbatim 移植。CV/履歴書/科研費は経歴＋業績を1ドキュメントに統合するため。旧フォルダ削除済み。
- **重複reference解消**: `debugging-wizard/references/systematic-debugging.md`（standalone `systematic-debugging` のクローン）を削除。`code-reviewer/references/receiving-feedback.md`（standalone `receiving-code-review` の複製）を8行スタブ化。
- **トリガー衝突修正（description編集のみ）**: debugging-wizard（ツール scope化）, executing-plans / subagent-driven-development（別session vs 現session を先頭明示）, dispatching-parallel-agents, infographic（スライド語をデッキscope化）, codex-review / gemini-review（外部ツール明示必須化）, code-reviewer（in-Claudeデフォルト化）, research-toolkit（arXiv→alphaxiv deflection）。

## 据え置きの判断（重要）
一見重複でも別ジョブのものは**マージしない**方針を採用:
- `codex-review` / `gemini-review` は**異なる外部CLI**（codex vs gemini）→ マージ不可
- `infographic` / `slide-making` / `make-poster` / `ui-ux-design` は別アーティファクト×別ツールチェーン
- `debugging-wizard`（ツール）/ `systematic-debugging`（プロセス）は役割が違う
- `alphaxiv` / `research-toolkit` / `zotero` は別バックエンド

**Why:** 安易なマージは capability loss を招く。重複は「同一ジョブ・同一ツール」のものだけに限定。
**How to apply:** 今後スキルを追加・整理する際、外部ツールが違う/アーティファクトが違うものは統合せず description のトリガー語で衝突回避する。関連: [[feedback_slide_icon_approach]]
