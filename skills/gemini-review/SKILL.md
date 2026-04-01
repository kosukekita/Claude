---
name: gemini-review
description: >
  Gemini CLIを使ってコードや文章をGeminiにレビュー・確認してもらう。
  コードレビュー、論文チェック、モデル自動フォールバックに対応。
  「Geminiにも確認」「Geminiでチェック」「セカンドオピニオン」などと言われた時に使用。
allowed-tools: Bash, Read, Glob
---

# Gemini Review Skill

Gemini CLI を使って、Gemini の最新モデルにコードや文章のレビューを依頼するスキル。

## Instructions

### Step 1: レビュー対象を特定

ユーザーが指定したファイルまたはテキストを確認する。

### Step 2: Gemini CLI でレビューを実行

```bash
# ファイルの場合
cat {ファイルパス} | gemini -p "以下のコードをレビューしてください。バグ、改善点、セキュリティの懸念があれば指摘してください。" -m gemini-3-pro-preview

# テキストを直接渡す場合
gemini -p "{プロンプト内容}" -m gemini-3-pro-preview
```

モデルは常に最新を使用する（詳細は「モデル選択ロジック」参照）：
- `gemini-3-pro-preview` — デフォルト（要 Preview Features）
- `gemini-2.5-pro` — フォールバック（安定版）
- `gemini-3-flash-preview` — 高速・低コスト版

### Step 3: 結果を統合してフィードバック

Gemini の回答を取得後、Claude 自身の見解と比較して総合的なフィードバックを提示する。

## モデル選択ロジック

1. まず `gemini-3-pro-preview` を試行
2. 429（容量不足）エラーの場合 → `gemini-2.5-pro` にフォールバック
3. 404（モデル未発見）エラーの場合 → Preview Features 未有効の可能性。`references/setup-guide.md` の手順を案内

## Examples

### Example 1: コードレビュー依頼
User says: "このファイルをGeminiにもレビューしてもらって"

Actions:
1. 対象ファイルを Read ツールで確認
2. `cat {ファイルパス} | gemini -p "コードをレビューしてください" -m gemini-3-pro-preview` を実行
3. Gemini の回答を取得
4. Claude の見解と比較して総合フィードバックを提示

Result: Gemini と Claude 両方の視点を統合したコードレビュー結果

### Example 2: 論文・文章のセカンドオピニオン
User says: "この文章、Geminiにセカンドオピニオンをもらって"

Actions:
1. 対象ファイルまたはテキストを確認
2. `gemini -p "以下の文章を学術的な観点からレビューしてください: ..." -m gemini-3-pro-preview` を実行
3. 論理一貫性・表現・根拠の妥当性についてフィードバックを取得
4. Claude の分析と合わせて提示

Result: 複数の AI 視点による文章レビュー

## Troubleshooting

### Error: 429 Too Many Requests
**Cause:** `gemini-3-pro-preview` のレート制限に到達
**Solution:** `gemini-2.5-pro` にモデルを切り替えて再実行する

### Error: 404 Not Found（モデル未発見）
**Cause:** Preview Features が未有効化
**Solution:** `references/setup-guide.md` の手順で Preview Features を有効にしてから再試行

### Error: command not found: gemini
**Cause:** Gemini CLI が未インストール
**Solution:** `npm install -g @google/gemini-cli` を実行してインストール

### Error: 認証エラー / Authentication failed
**Cause:** Google アカウントへの未ログイン
**Solution:** `gemini`（引数なし）で対話モードを起動し、ログインを完了してから再実行

## 注意事項

- 機密データを含むファイルは外部送信前にユーザーへ確認する
- JSON 出力が必要な場合は `--output-format json` を追加

## References

- `references/prompt-templates.md` — コードレビュー・論文チェック等のプロンプトテンプレート
- `references/setup-guide.md` — Preview Features の有効化手順
- `references/test-plan.md` — トリガーテスト・機能テスト一覧
