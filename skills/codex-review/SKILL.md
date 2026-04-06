---
name: codex-review
description: >
  Codex CLI + codex-plugin-cc を使ってコードや文章を OpenAI モデルにレビュー・確認してもらう。
  git diff レビュー（未コミット変更・ブランチ差分・特定コミット）、ファイル単体レビュー、
  敵対的レビュー、構造化 JSON 出力、バックグラウンドジョブに対応。
  「Codexにも確認」「Codexでレビュー」「Codexにセカンドオピニオン」「コミット前にCodexに確認」
  「Codexに反論してもらって」「設計の妥当性をCodexに疑ってもらって」「敵対的レビュー」
  「Codexにタスクを委譲」「構造化出力でCodexにレビュー」などと言われた時に使用。
allowed-tools: Bash, Read, Glob
---

# Codex Review Skill

Codex CLI（ChatGPT サブスクリプション認証済み）+ codex-plugin-cc を使って、OpenAI の最新モデルにコードや文章のレビューを依頼するスキル。

## Instructions

### Step 1: レビュー対象とモードを特定

ユーザーの指示から以下のどのケースかを判断する：

| ケース | 判断基準 | CLI コマンド | プラグインコマンド |
|--------|----------|-------------|-----------------|
| **git diff レビュー** | 「未コミットの変更」「今の変更」「このPR」 | `codex review --uncommitted` | `/codex:review --scope working-tree` |
| **ブランチ差分** | 「このブランチ」「mainとの差分」 | `codex review --base main` | `/codex:review --scope branch` |
| **特定コミット** | コミットSHA・「このコミット」 | `codex review --commit {SHA}` | — |
| **ファイル単体** | 特定ファイルパスを指定 | `cat file \| codex exec` | — |
| **敵対的レビュー** | 「反論」「妥当性を疑って」「adversarial」 | `codex review` + 敵対的プロンプト | `/codex:adversarial-review` |
| **構造化出力** | 「構造化」「JSON で」「findings形式で」 | `codex review` + JSON プロンプト | `/codex:review` （JSON 出力） |
| **タスク委譲** | 「Codexに任せて」「rescue」「修正もやって」 | — | `/codex:rescue` |
| **バックグラウンド** | 「バックグラウンドで」「非同期で」 | — | `/codex:review --background` |

### Step 2: Codex CLI またはプラグインコマンドでレビューを実行

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

**ケース E: 敵対的レビュー（設計の妥当性を疑う）**
```bash
codex review --uncommitted "以下の変更について敵対的レビューを行ってください：
1. この設計判断は本当に最適か？代替案とそのトレードオフを示せ
2. この実装が壊れるシナリオは何か？障害モードを列挙せよ
3. 暗黙の前提条件は何か？それが崩れた場合どうなるか
4. スケーラビリティ・保守性・セキュリティで見落としている懸念はないか
日本語で回答してください。"
```
または `/codex:adversarial-review` コマンドを使用（プラグイン必要）。

**ケース F: 構造化出力レビュー**
```bash
codex review --uncommitted "以下の変更をレビューし、結果を以下のJSON形式で返してください：
{
  \"verdict\": \"approve | needs-attention\",
  \"summary\": \"総合所見（1-2文）\",
  \"findings\": [
    {
      \"severity\": \"critical | warning | suggestion\",
      \"title\": \"問題の短いタイトル\",
      \"body\": \"詳細説明\",
      \"file\": \"ファイルパス\",
      \"line\": \"行番号または範囲\",
      \"recommendation\": \"推奨する修正方法\"
    }
  ],
  \"next_steps\": [\"次にすべきアクション\"]
}
日本語で回答してください。"
```

### Step 3: 結果を統合してフィードバック

Codex の回答取得後、Claude 自身の見解と比較して総合的なフィードバックを提示する。

- **通常レビュー**: Claude の見解と Codex の見解を統合してフィードバック
- **敵対的レビュー**: Claude 自身の見解と対比させて「合意点」「相違点」を明示
- **構造化出力**: JSON をパースし、severity 別（critical → warning → suggestion）に整理して提示

---

## プラグインコマンド リファレンス（codex-plugin-cc）

codex-plugin-cc インストール済みの場合、以下のスラッシュコマンドが利用可能：

| コマンド | 説明 |
|---------|------|
| `/codex:review` | 通常レビュー。`--scope working-tree\|branch\|auto`、`--background` 対応 |
| `/codex:adversarial-review` | 敵対的レビュー。設計判断・障害モード・前提を疑う |
| `/codex:rescue` | タスク委譲。バグ修正・調査などを Codex に任せる |
| `/codex:status` | 実行中・完了済みジョブ一覧 |
| `/codex:result` | ジョブ結果の表示 |
| `/codex:cancel` | 実行中ジョブのキャンセル |
| `/codex:setup` | セットアップ確認・Review Gate の有効化/無効化 |

### Review Gate（オプション）
`/codex:setup --enable-review-gate` で有効化すると、Claude の応答完了前に自動的に Codex レビューが走り、問題があれば完了をブロックする。使用量を大量消費するため、必要時のみ有効化。

---

## モデル設定

`~/.codex/config.toml` でモデルを一元管理。スキル内では `-m` を指定しない（config の値を使用）。

```toml
personality = "pragmatic"
model = "gpt-5.4"                   # 現在の最新モデル
model_reasoning_effort = "high"     # 高精度レビューのため high を推奨
```

新モデルへの切り替えは `config.toml` の `model` を更新するだけでよい。

---

## Examples

### Example 1: 未コミット変更のレビュー
User says: "今の変更をCodexにもレビューしてもらって"

Actions:
1. `codex review --uncommitted "日本語でレビューしてください"` を実行
2. Codex の回答を取得
3. Claude の見解と比較して総合フィードバックを提示

### Example 2: 敵対的レビュー
User says: "Codexに反論してもらって"

Actions:
1. `/codex:adversarial-review` を実行（またはケース E の CLI コマンド）
2. 設計疑義・障害モード・前提の問題点を取得
3. Claude 自身の見解と対比して「合意点」「相違点」を整理

### Example 3: 構造化出力レビュー
User says: "構造化出力でCodexにレビューして"

Actions:
1. ケース F のプロンプトで `codex review --uncommitted` を実行
2. JSON をパースして severity 別に整理（critical → warning → suggestion）
3. verdict と next_steps を強調して提示

### Example 4: タスク委譲
User says: "Codexにバグ修正も任せて"

Actions:
1. `/codex:rescue` コマンドを実行
2. バックグラウンドで Codex が調査・修正
3. `/codex:status` で進捗確認、`/codex:result` で結果確認

---

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

### プラグインコマンドが認識されない
**Cause:** codex-plugin-cc が未インストール、またはリロード未実施
**Solution:** `claude plugin list` で確認。未インストールなら `references/setup-guide.md` の手順に従う。インストール済みなら `/reload-plugins` を実行。

### レビュー結果が英語で返ってくる
**Cause:** デフォルトの応答言語が英語
**Solution:** プロンプトに「日本語でレビューしてください」を明示する

---

## 注意事項

- 機密データ・認証情報を含むファイルは外部送信前にユーザーへ確認する
- `codex review` は git diff を自動取得するため、大規模な差分は時間がかかる場合がある
- ChatGPT サブスクリプションの利用制限に達した場合は時間をおいて再試行
- Review Gate は使用量を大量消費するため、`/codex:setup --enable-review-gate` で有効化する場合は注意

## References

- `references/prompt-templates.md` — コードレビュー・論文チェック・敵対的レビュー・構造化出力等のプロンプトテンプレート
- `references/setup-guide.md` — Codex CLI のインストール・ログイン・プラグイン設定手順
- `references/test-plan.md` — トリガーテスト・機能テスト一覧
