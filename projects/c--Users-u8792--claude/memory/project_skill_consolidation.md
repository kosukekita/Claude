---
name: project_skill_consolidation
description: ~/.claude/skills のリファクタリング結果。2026-05-31/06-08に実施。現36スキル。code-reviewer/codex-review/gemini-review削除、skill-creator統合、codex-consult新設。標準コマンド重複は削除可、同一ツール×同一成果物のみ統合可
metadata:
  type: project
---

# レビュースキル整理 + codex-consult新設（2026-06-08 第2回の続き）

37→**36スキル**。ユーザーが「codex-review は会話文脈を理解してClaude補完する役割のはず」と指摘したのが発端。検証(4エージェントWorkflow)の結論:

- **codex-review 削除**: `codex review` CLIサブコマンドは**コード差分のワンショットレビュー専用**。会話履歴を渡す口がCLIに無い（resume/session-id無し）。会話文脈補完は構造上担えない。コードレビューは標準/code-reviewかBash直叩きで代替。
- **gemini-review 削除**: `cat file | gemini -p ...` の薄いラッパー。論文セカンドオピニオンもBash直叩き（gemini CLI 0.36.0稼働中）で完全代替。ユーザーは論文レビュー知識の退避も不要と判断。
- **重大な発見**: `codex:rescue`（codexプラグイン）**も会話文脈を渡していない**。thin forwarding wrapperでタスク文字列1本＋cwdのみ転送。`buildTurnInput`が`[{type:text,text:prompt}]`しか組まない。→ **「会話文脈を理解したCodex補完」を自動でやる機構は存在しない**。
- **codex-consult 新設**: 「会話文脈をClaudeが構造化テンプレ（議論/目標/試したこと/詰まり/対象/求めること）に要約 → `/codex:rescue`に渡す」プロトコルをスキル化。rescue/second-opinion/handoffの3用途。`/codex:rescue`は$ARGUMENTSをそのままcodexに転送するので、Claudeが文脈を埋めれば届く。**運搬役(rescue)は完成済み、足りないのは文脈要約というClaudeの振る舞いだった**。
- slide-making の codex-review 参照は `codex review` CLI直叩きに統一（元々CLI直叩きしていた）。

**重要教訓**: PowerShellの`Get-Content`表示はcp932で日本語が化けて見えるが、Writeツールは正しくUTF-8保存している。検証はRead(harness)かmojibake(U+FFFD)チェックで行う。`Get-Content`の表示化けに騙されない。

---

# スキル統合 第2回（2026-06-08 実施）

39→**37スキル**。3つのWorkflow（Hook監査・description監査・統合プラン）を経てユーザー承認の上で実施。

## 実施内容
- **削除**: `code-reviewer` → 標準スラッシュコマンド `/code-review`（in-Claude差分レビュー、ultraでクラウド多エージェント）と裏ツール（Read/Grep/Glob）も成果物も完全一致のため。**教訓: 標準コマンドと完全重複する自作スキルは削除してよい**。
- **統合**: `skill-creator` → **`writing-skills`**。両者とも外部ツールゼロ・成果物が同じSKILL.mdで真に重複。skill-creator固有資産（6ステップ手順・3カテゴリ分類・トリガー診断表）を writing-skills の「Authoring Walkthrough」節に移植、patterns.md を writing-skills/skill-patterns.md にコピー、writing-skills description に日本語トリガー語追加。**矛盾点**: skill-creator は「description=WHAT+WHEN」だが writing-skills は「description=WHENのみ（テスト由来の知見）」→ writing-skills を正とした。
- **境界明示追加（descriptionのみ）**: zotero（検索系research-toolkit/alphaxivと区別）, academic-writing↔ai-prediction-model（TRIPOD: 執筆 vs 解析実装を相互にDo NOT trigger）。
- **付随修正**: codex-review/gemini-review/test-plan.md の「code-reviewerを使う」案内を「/code-reviewを使う」に変更。CLAUDE.md にスキル推薦ルール追加（タスク開始時に該当スキルを一言提案）。

## 重要な発見
- 8重複クラスタ27スキルを精査した結果、**ほとんどが「見た目の重複」で実体は別物**だった。安易に統合していたら「Codexでレビュー」等が壊れていた。
- `requesting-code-review`/`subagent-driven-development` の `superpowers:code-reviewer` 参照は**実在しないエージェント型への願望的記述**（superpowers プラグイン前提）。同梱 code-reviewer.md テンプレートは実在。code-reviewer**スキル**削除とは無関係なので触らない。

---

# スキル統合 第1回（2026-05-31 実施）

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
