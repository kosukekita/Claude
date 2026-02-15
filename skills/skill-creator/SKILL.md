---
name: skill-creator
description: >
  Claude用スキルの設計・構築・テスト・改善を支援するワークフロー自動化スキル。
  ユースケース定義からYAMLフロントマター生成、インストラクション作成、
  トリガーテスト、イテレーション改善まで一貫してガイド。
  Use when user wants to create, build, design, or improve Claude skills.
  Trigger phrases: "スキルを作成", "スキル構築", "skill作成", "新しいスキル",
  "SKILL.md", "スキルを設計", "スキルを改善", "create skill", "build skill",
  "design skill", "improve skill", "/skill-creator".
---

# Skill Creator

Claude用スキルを設計・構築・改善するためのインタラクティブガイド。

## What is a Skill?

スキルは、特定のタスクやワークフローをClaudeに教えるための命令セットをフォルダとしてパッケージ化したもの。

### スキルの構成要素

```
your-skill-name/
├── SKILL.md              # 必須: YAML フロントマター + Markdown 本文
├── scripts/              # オプション: 実行可能コード
├── references/           # オプション: 詳細ドキュメント
└── assets/               # オプション: テンプレート、フォント等
```

### 3レベルの Progressive Disclosure

1. **第1レベル（YAMLフロントマター）**: 常にシステムプロンプトにロード。スキルを使うべきかの判断に使用
2. **第2レベル（SKILL.md本文）**: スキルが関連すると判断された時にロード。完全な指示を含む
3. **第3レベル（リンクファイル）**: 必要に応じてナビゲート・参照する追加ファイル

---

## Workflow

スキル作成リクエストを受けたら、以下のステップで進める:

### Step 1: ユースケース定義

ユーザーと対話して以下を明確化:

```
Use Case: [タスク名]
Trigger: [ユーザーがどう言うか]
Steps:
1. [ステップ1]
2. [ステップ2]
...
Result: [期待される成果]
```

**質問リスト:**
- ユーザーは何を達成したいのか?
- このタスクにはどんなマルチステップワークフローが必要か?
- どのツールが必要か（ビルトイン or MCP）?
- どんなドメイン知識やベストプラクティスを埋め込むべきか?

### Step 2: カテゴリ特定

3つのカテゴリからスキルの種類を特定:

| カテゴリ | 用途 | 主な技法 |
|---------|------|----------|
| **Document & Asset Creation** | 一貫した高品質出力（ドキュメント、プレゼン、コード等） | スタイルガイド埋め込み、テンプレート、品質チェックリスト |
| **Workflow Automation** | 一貫した方法論が有益なマルチステッププロセス | ステップバイステップのバリデーションゲート、イテレーティブな改善ループ |
| **MCP Enhancement** | MCPサーバーのツールアクセスを強化 | 複数MCP呼び出しの連携、ドメイン専門知識、エラーハンドリング |

### Step 3: YAML フロントマター作成

#### 必須フィールド

```yaml
---
name: your-skill-name
description: What it does and when to use it (trigger conditions).
---
```

#### 命名規則（厳格）

- **SKILL.md**: 必ず `SKILL.md`（大文字・小文字厳密）
- **フォルダ名**: kebab-case のみ
  - 良い例: `notion-project-setup`
  - 悪い例: `Notion Project Setup`, `notion_project_setup`, `NotionProjectSetup`
- **nameフィールド**: kebab-case、スペースなし、大文字なし

#### description フィールドの書き方

**構造**: `[何をするか] + [いつ使うか] + [主な機能]`

**良い例:**
```yaml
description: >
  Figmaデザインファイルを分析し、開発者向けハンドオフドキュメントを生成。
  Use when user uploads .fig files, asks for "design specs",
  "component documentation", or "design-to-code handoff".
```

**悪い例:**
```yaml
# 曖昧すぎる
description: Helps with projects.

# トリガーなし
description: Creates sophisticated multi-page documentation systems.

# 技術的すぎてユーザートリガーなし
description: Implements the Project entity model with hierarchical relationships.
```

#### オプションフィールド

```yaml
license: MIT  # オープンソースの場合
compatibility: Claude Code, Claude.ai, API  # 動作環境
metadata:
  author: Your Name
  version: 1.0.0
  mcp-server: your-mcp-server  # MCP連携の場合
```

#### セキュリティ制限

**禁止事項:**
- XMLアングルブラケット（`<` `>`）
- "claude" や "anthropic" を含む name

### Step 4: メイン指示の作成

#### 推奨構造

```markdown
# Your Skill Name

## Instructions

### Step 1: [最初の主要ステップ]
何が起こるかの明確な説明。

### Step 2: [次のステップ]
...

## Examples

### Example 1: [一般的なシナリオ]
User says: "[ユーザー入力例]"

Actions:
1. [アクション1]
2. [アクション2]

Result: [期待される結果]

## Troubleshooting

### Error: [よくあるエラーメッセージ]
**Cause:** [なぜ発生するか]
**Solution:** [修正方法]
```

#### ベストプラクティス

**具体的でアクション可能に:**
```markdown
# 良い例
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)

# 悪い例
Validate the data before proceeding.
```

**エラーハンドリングを含める:**
```markdown
## Common Issues

### MCP Connection Failed
If you see "Connection refused":
1. Verify MCP server is running: Check Settings > Extensions
2. Confirm API key is valid
3. Try reconnecting: Settings > Extensions > [Your Service] > Reconnect
```

**Progressive Disclosure を活用:**
- SKILL.md はコア指示に集中
- 詳細ドキュメントは `references/` に移動してリンク

### Step 5: テスト計画作成

#### トリガーテスト

```
Should trigger:
- "[スキルを使うべき明確なリクエスト1]"
- "[言い換えたリクエスト]"
- "[関連するリクエスト]"

Should NOT trigger:
- "[無関係なリクエスト1]"
- "[一般的な質問]"
- "[別のスキルが処理すべきリクエスト]"
```

#### 機能テスト

- 有効な出力が生成されるか
- API呼び出しが成功するか
- エラーハンドリングが機能するか
- エッジケースがカバーされているか

### Step 6: イテレーション改善

#### アンダートリガーの兆候と対策

**兆候:**
- スキルが使われるべき時にロードされない
- ユーザーが手動で有効化している
- "いつ使えばいい？"という質問がある

**対策:** descriptionにより詳細とニュアンスを追加（特にキーワード）

#### オーバートリガーの兆候と対策

**兆候:**
- 無関係なクエリでスキルがロードされる
- ユーザーがスキルを無効化する
- 目的についての混乱

**対策:** ネガティブトリガーを追加してより具体的に

```yaml
description: >
  Advanced data analysis for CSV files. Use for statistical modeling,
  regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
```

#### 指示が守られない場合

**原因と対策:**
1. **冗長すぎる** → 簡潔に。箇条書きや番号リストを使用
2. **重要指示が埋もれている** → 重要な指示を先頭に。`## Important` や `## Critical` ヘッダーを使用
3. **曖昧な言語** → 具体的に

```markdown
# 悪い例
Make sure to validate things properly

# 良い例
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

---

## Patterns

詳細は `references/patterns.md` を参照。

### Pattern 1: Sequential Workflow Orchestration
マルチステッププロセスを特定の順序で実行する必要がある場合に使用。

### Pattern 2: Multi-MCP Coordination
ワークフローが複数のサービスにまたがる場合に使用。

### Pattern 3: Iterative Refinement
出力品質がイテレーションで改善される場合に使用。

### Pattern 4: Context-aware Tool Selection
同じ成果を異なるツールで達成する場合に使用。

### Pattern 5: Domain-specific Intelligence
スキルがツールアクセス以上の専門知識を追加する場合に使用。

---

## Output Format

スキル作成時は以下の形式で出力:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL: [Skill Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Category: [Document & Asset / Workflow Automation / MCP Enhancement]
Use Case: [1-2文でユースケースを説明]

YAML Frontmatter:
---
name: [skill-name]
description: [完全なdescription]
---

Suggested Triggers:
- "[トリガーフレーズ1]"
- "[トリガーフレーズ2]"

File Structure:
[フォルダ構造を表示]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quick Checklist

### 開始前
- [ ] 2-3の具体的なユースケースを特定
- [ ] 必要なツールを特定（ビルトイン or MCP）
- [ ] フォルダ構造を計画

### 開発中
- [ ] フォルダ名が kebab-case
- [ ] SKILL.md が存在（正確なスペル）
- [ ] YAML フロントマターに `---` 区切り
- [ ] name フィールドが kebab-case、スペースなし、大文字なし
- [ ] description に WHAT と WHEN を含む
- [ ] XML タグ（`< >`）がどこにもない
- [ ] 指示が明確でアクション可能
- [ ] エラーハンドリングを含む
- [ ] 例を提供
- [ ] 参照を明確にリンク

### アップロード前
- [ ] 明確なタスクでトリガーテスト
- [ ] 言い換えリクエストでトリガーテスト
- [ ] 無関係なトピックでトリガーしないことを確認
- [ ] 機能テストがパス
- [ ] .zip ファイルとして圧縮

### アップロード後
- [ ] 実際の会話でテスト
- [ ] アンダー/オーバートリガーを監視
- [ ] ユーザーフィードバックを収集
- [ ] description と指示をイテレーション

---

## References

詳細は以下を参照:
- `references/patterns.md` — 5つのスキルパターンの詳細例
- `references/troubleshooting.md` — よくある問題と解決策
- `references/yaml-reference.md` — YAMLフロントマターの完全リファレンス
