---
name: codex-review
description: >
  Codex CLI を使ってコードや文章を OpenAI モデルにレビュー・確認してもらう。
  git diff レビュー（未コミット変更・ブランチ差分・特定コミット）とファイル単体レビューに対応。
  「Codexにも確認」「Codexでレビュー」「Codexにセカンドオピニオン」「コミット前にCodexに確認」などと言われた時に使用。
allowed-tools: Bash, Read, Glob
---

# Codex Review Skill

Codex CLI（ChatGPT サブスクリプション認証済み）を使って、OpenAI の最新モデルにコードや文章のレビューを依頼するスキル。

## Instructions

### Step 1: レビュー対象を特定

ユーザーの指示から以下のどのケースかを判断する：

| ケース | 判断基準 | 使用コマンド |
|--------|----------|-------------|
| **git diff レビュー** | 「未コミットの変更」「今の変更」「このPR」「このブランチ」 | `codex review` |
| **特定コミットのレビュー** | コミットSHA・「このコミット」 | `codex review --commit` |
| **ファイル単体レビュー** | 特定ファイルパスを指定 | `cat file | codex exec` |
| **テキストレビュー** | コードや文章をその場で貼り付け | `echo | codex exec` |

### Step 2: Codex CLI でレビューを実行

モデルは `~/.codex/config.toml` の設定に従い、常に最新モデルを使用（`-m` 指定不要）。
現在の設定: `model = "gpt-5.4"`, `model_reasoning_effort = "high"`

**ケース A: 未コミット変更のレビュー（最頻出）**
```bash
codex review --uncommitted "日本語でレビューしてください。バグ・改善点・セキュリティの懸念を指摘してください。"
```

**ケース B: ブランチ差分のレビュー**
```bash
codex review --base main "日本語でレビューしてください"
```

**ケース C: 特定コミットのレビュー**
```bash
codex review --commit {SHA} "日本語でレビューしてください"
```

**ケース D: ファイル単体レビュー**
```bash
cat {ファイルパス} | codex exec "以下のコードをレビューしてください。バグ・改善点・セキュリティの懸念を指摘してください。"
```

### Step 3: 結果を統合してフィードバック

Codex の回答取得後、Claude 自身の見解と比較して総合的なフィードバックを提示する。

## モデル設定

`~/.codex/config.toml` でモデルを一元管理。スキル内では `-m` を指定しない（config の値を使用）。

```toml
model = "gpt-5.4"           # 現在の最新モデル
model_reasoning_effort = "high"  # 高精度レビューのため high を推奨
```

新モデルへの切り替えは `config.toml` の `model` を更新するだけでよい。

## Examples

### Example 1: 未コミット変更のレビュー
User says: "今の変更をCodexにもレビューしてもらって"

Actions:
1. `codex review --uncommitted "日本語でレビューしてください"` を実行
2. Codex の回答を取得
3. Claude の見解と比較して総合フィードバックを提示

Result: Codex と Claude 両方の視点を統合したコードレビュー結果

### Example 2: ファイル単体レビュー
User says: "このファイルをCodexにレビューしてもらって"

Actions:
1. 対象ファイルを Read ツールで確認
2. `cat {ファイルパス} | codex exec "コードをレビューしてください"` を実行
3. Codex の回答を取得
4. Claude の分析と合わせて提示

Result: Codex と Claude 両方の視点を統合したファイルレビュー結果

### Example 3: ブランチ差分のレビュー（PR前確認）
User says: "mainとの差分をCodexに確認してもらって"

Actions:
1. `codex review --base main "バグ・設計の懸念点を日本語で指摘してください"` を実行
2. 結果を Claude の分析と統合して提示

Result: マージ前の品質チェック結果

## Troubleshooting

### Error: Not logged in / 認証エラー
**Cause:** Codex が ChatGPT にログインしていない
**Solution:** `codex login` を実行してブラウザで ChatGPT にログインする

### Error: command not found: codex
**Cause:** Codex CLI が未インストール
**Solution:** `npm install -g @openai/codex` を実行してインストール

### Error: no git repository found
**Cause:** `codex review` は git リポジトリ内でのみ動作する
**Solution:** git リポジトリ外の場合はファイル単体レビュー（`cat file | codex exec`）を使用する

### レビュー結果が英語で返ってくる
**Cause:** デフォルトの応答言語が英語
**Solution:** プロンプトに「日本語でレビューしてください」を明示する

## 注意事項

- 機密データ・認証情報を含むファイルは外部送信前にユーザーへ確認する
- `codex review` は git diff を自動取得するため、大規模な差分は時間がかかる場合がある
- ChatGPT サブスクリプションの利用制限に達した場合は時間をおいて再試行

## References

- `references/prompt-templates.md` — コードレビュー・論文チェック等のプロンプトテンプレート
- `references/setup-guide.md` — Codex CLI のインストールとログイン手順
- `references/test-plan.md` — トリガーテスト・機能テスト一覧
