---
name: codex-review
description: >
  Codex CLI (`codex review`) を使ってコードをレビューするスキル。
  通常レビュー・敵対的レビュー・セキュリティ監査・アーキテクチャレビュー・PR前確認・構造化出力に対応。
  「Codexでレビュー」「codex review」「敵対的レビュー」「adversarial」などと言われた時に使用。
allowed-tools: Bash, Read, Glob
---

# Codex Review Skill

`codex review` CLI を使って、Codex（GPT-4o / o3 等）にコードレビューを依頼するスキル。

## Instructions

### Step 1: レビュー種別とターゲットを特定

ユーザーの指示から以下を判断する：

**レビュー種別**（デフォルト: `standard`）
- `standard` — バグ・パフォーマンス・可読性の総合レビュー
- `adversarial` — 設計批判・障害モード・暗黙の前提を徹底的に問う
- `security` — 認証・インジェクション・機密情報漏洩を重点チェック
- `arch` / `architecture` — 設計パターン・依存関係・スケーラビリティを評価
- `pr` — PR前の最終確認（マージ可否の判断）
- `structured` — JSON形式で結果を出力（CI/自動処理向け）

**レビュー範囲**（デフォルト: `--uncommitted`）
- 未コミット変更: `--uncommitted`
- ブランチ差分: `--base <branch>`（例: `--base main`）
- 特定コミット: `--commit <SHA>`

### Step 2: プロンプトを選択して `codex review` を実行

種別に応じたプロンプトを `references/prompt-templates.md` から選択し、実行する：

```bash
# standard（デフォルト）
codex review --uncommitted "以下のコードをレビューしてください：\n- バグや潜在的な問題\n- パフォーマンスの改善点\n- セキュリティの懸念\n- コードの可読性・保守性\n日本語で回答してください。"

# adversarial
codex review --uncommitted "1. この設計判断は本当に最適か？代替案とそのトレードオフを具体的に示せ\n2. この実装が壊れるシナリオは何か？障害モードを列挙せよ\n3. 暗黙の前提条件は何か？それが崩れた場合どうなるか\n4. スケーラビリティ・保守性・セキュリティで見落としている懸念はないか\n5. このアプローチに対する最も強い反論は何か\n日本語で回答してください。"

# security
codex review --uncommitted "以下のコードをセキュリティの観点から監査してください：\n- 認証・認可の問題\n- インジェクション攻撃（SQLi, XSS等）への脆弱性\n- 機密情報の取り扱い\n- 依存ライブラリのリスク\n日本語で回答してください。"

# arch / architecture
codex review --uncommitted "以下のコードのアーキテクチャをレビューしてください：\n- 設計パターンの適切さ\n- モジュール間の依存関係\n- スケーラビリティの懸念\n- テスタビリティ\n日本語で回答してください。"

# pr
codex review --base main "このPR前の変更について総合的にレビューしてください。\nマージしても問題ないか、懸念点があれば日本語で教えてください。"

# structured
codex review --uncommitted "以下の変更をレビューし、結果を以下のJSON形式で返してください：\n{\n  \"verdict\": \"approve | needs-attention\",\n  \"summary\": \"総合所見（1-2文）\",\n  \"findings\": [\n    {\n      \"severity\": \"critical | warning | suggestion\",\n      \"title\": \"問題の短いタイトル\",\n      \"body\": \"詳細説明\",\n      \"file\": \"ファイルパス（不明な場合は null）\",\n      \"line\": \"行番号または範囲（不明な場合は null）\",\n      \"confidence\": \"high | medium | low\",\n      \"recommendation\": \"推奨する修正方法\"\n    }\n  ],\n  \"next_steps\": [\"次にすべきアクション1\", \"アクション2\"]\n}\nJSONのみを返してください。説明文は不要です。"
```

ユーザーが `--base <branch>` や `--commit <SHA>` を指定した場合は `--uncommitted` を差し替える。

### Step 3: 結果を提示

- Codex の出力をそのまま表示する
- `structured` の場合は JSON をパースして整形して見せる
- 必要に応じて Claude 自身の補足コメントを追記する

## Examples

### Example 1: 通常のコードレビュー
User: "Codexでレビューして"

Actions:
1. 種別: `standard`、範囲: `--uncommitted` と判断
2. `codex review --uncommitted "..."` を実行
3. 結果を表示

### Example 2: 敵対的レビュー
User: "adversarial reviewして" / "敵対的レビューを実行して"

Actions:
1. 種別: `adversarial`、範囲: `--uncommitted` と判断
2. `codex review --uncommitted "1. この設計判断は..."` を実行
3. 結果を表示

### Example 3: mainブランチとの差分をセキュリティレビュー
User: "mainとの差分をセキュリティレビューして"

Actions:
1. 種別: `security`、範囲: `--base main` と判断
2. `codex review --base main "セキュリティの観点から..."` を実行
3. 結果を表示

### Example 4: 構造化出力
User: "JSON形式でレビュー結果を出して"

Actions:
1. 種別: `structured`、範囲: `--uncommitted` と判断
2. `codex review --uncommitted "...JSON形式で..."` を実行
3. JSON をパースして整形表示

## Troubleshooting

### Error: codex not found
**Cause:** Codex CLI が未インストール
**Solution:** `npm install -g @openai/codex` を実行

### Error: 認証エラー
**Cause:** OpenAI API キーが未設定
**Solution:** `codex login` を実行してログイン

### Error: No changes to review
**Cause:** レビュー対象の変更がない（`--uncommitted` 時）
**Solution:** `--base <branch>` や `--commit <SHA>` で範囲を指定する

## References

- `references/prompt-templates.md` — 各種レビュープロンプトのテンプレート集
