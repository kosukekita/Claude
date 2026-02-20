---
name: gemini-review
description: Gemini CLIを使ってコードや文章をGemini（最新モデル）にレビュー・確認してもらう。「Geminiにも確認」「Geminiでチェック」「セカンドオピニオン」などと言われた時に使用。
allowed-tools: Bash, Read, Glob
---

# Gemini Review Skill

Gemini CLI を使って、Gemini の最新モデルにコードや文章のレビューを依頼するスキル。

## 使い方

ユーザーが指定したファイルや内容を Gemini CLI に渡してレビューを取得する。

## 前提条件：Preview Features の有効化

Gemini 3 系モデルを使用するには、Gemini CLI で Preview Features を有効にする必要がある：

1. `gemini` を対話モードで起動
2. `/settings` を実行
3. **Preview Features (e.g., models)** を `true` に切り替え
4. `r` を押して設定を反映し CLI を再起動
5. `/model` で **Auto (Gemini 3)** が選択可能なことを確認

## 手順

1. レビュー対象のファイルまたはコンテンツを特定する
2. 以下のコマンドでGemini CLIにレビューを依頼する：
```bash
# ファイルの場合
cat <ファイルパス> | gemini -p "以下のコードをレビューしてください。バグ、改善点、セキュリティの懸念があれば指摘してください。" -m gemini-3-pro-preview

# テキストの場合
gemini -p "<プロンプト内容>" -m gemini-3-pro-preview
```

3. `-m` オプションで使用するモデルを指定する（**常に最新モデルを使用すること**）：
   - `gemini-3-pro-preview` — 最新・最高性能モデル（**デフォルト**、2026年2月時点、要 Preview Features）
   - `gemini-3.1-pro-preview` — 次世代モデル（コードに定義済み、未デプロイ。利用可能になったらこちらに切替）
   - `gemini-2.5-pro` — 安定版。Preview 無効時 or Gemini 3 容量不足時のフォールバック
   - `gemini-3-flash-preview` — 高速・低コスト版（要 Preview Features）

4. JSON出力が必要な場合は `--output-format json` を追加

## モデル選択ロジック

1. まず `gemini-3-pro-preview` を試行
2. 429（容量不足）エラーの場合 → `gemini-2.5-pro` にフォールバック
3. 404（モデル未発見）エラーの場合 → Preview Features 未有効の可能性。有効化手順を案内

## プロンプトテンプレート

### コードレビュー
```
以下のコードをレビューしてください：
- バグや潜在的な問題
- パフォーマンスの改善点
- セキュリティの懸念
- コードの可読性・保守性
```

### 論文・文章チェック
```
以下の文章を学術的な観点からレビューしてください：
- ロジックの一貫性
- 文法・表現の改善点
- 引用や根拠の妥当性
```

## 注意事項

- Gemini CLI が未インストールの場合、`npm install -g @google/gemini-cli` でインストールを案内する
- 認証エラーの場合、`gemini` を対話モードで実行してログインを案内する
- 機密データを含むファイルの場合はユーザーに確認する
- Gemini の回答を取得後、Claude自身の見解と比較して総合的なフィードバックを提示する
