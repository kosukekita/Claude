# YAML Frontmatter Reference

SKILL.md の YAML フロントマターの完全リファレンス。

---

## Required Fields

### 最小限のフォーマット

```yaml
---
name: skill-name-in-kebab-case
description: What it does and when to use it. Include specific trigger phrases.
---
```

### name (required)

- **形式:** kebab-case のみ
- **制限:** スペースなし、大文字なし
- **一致:** フォルダ名と一致すべき

```yaml
# 正しい
name: notion-project-setup
name: code-review-helper
name: data-pipeline-builder

# 間違い
name: Notion Project Setup    # スペースと大文字
name: notion_project_setup    # アンダースコア
name: NotionProjectSetup      # PascalCase
```

### description (required)

- **構造:** `[何をするか] + [いつ使うか] + [主な機能]`
- **長さ:** 1024文字以下
- **要件:**
  - WHAT: スキルが何をするか
  - WHEN: いつ使うべきか（トリガー条件）
  - 特定のタスク/フレーズを含める
  - XMLタグ（`<` `>`）禁止

```yaml
# 構造化された良い例
description: >
  Analyzes Figma design files and generates developer handoff documentation.
  Use when user uploads .fig files, asks for "design specs",
  "component documentation", or "design-to-code handoff".

# トリガーフレーズを含む例
description: >
  Manages Linear project workflows including sprint planning, task creation,
  and status tracking. Use when user mentions "sprint", "Linear tasks",
  "project planning", or asks to "create tickets".

# 明確な価値提案の例
description: >
  End-to-end customer onboarding workflow for PayFlow. Handles account creation,
  payment setup, and subscription management. Use when user says "onboard new
  customer", "set up subscription", or "create PayFlow account".
```

---

## Optional Fields

### license

オープンソースでスキルを公開する場合:

```yaml
license: MIT
license: Apache-2.0
```

### compatibility

スキルが動作する環境:

```yaml
compatibility: Claude Code, Claude.ai, API
compatibility: Claude Code only
```

1-500文字。環境要件（対象製品、必要なシステムパッケージ、ネットワークアクセス要件など）を示す。

### metadata

任意のカスタムキー・バリューペア:

```yaml
metadata:
  author: Your Name
  version: 1.0.0
  mcp-server: your-mcp-server
  category: productivity
  tags: [project-management, automation]
  documentation: https://example.com/docs
  support: support@example.com
```

推奨フィールド:
- `author`: 作成者/組織名
- `version`: セマンティックバージョン
- `mcp-server`: MCP連携の場合のサーバー名

### allowed-tools

ツールアクセスを制限（オプション）:

```yaml
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"
```

---

## Complete Example

```yaml
---
name: notion-workspace-setup
description: >
  Creates and configures Notion workspaces for project management. Handles
  database creation, template setup, and team onboarding. Use when user says
  "set up Notion workspace", "create project database", or "initialize Notion
  for [project name]".
license: MIT
compatibility: Claude Code, Claude.ai with Notion MCP
metadata:
  author: ProjectHub Inc.
  version: 2.1.0
  mcp-server: notion
  category: productivity
  tags: [notion, project-management, workspace]
  documentation: https://projecthub.io/skills/notion
---
```

---

## Security Notes

### Allowed

- 任意の標準YAMLタイプ（文字列、数値、ブーリアン、リスト、オブジェクト）
- カスタムmetadataフィールド
- 長い description（最大1024文字）

### Forbidden

- XMLアングルブラケット（`<` `>`）- セキュリティ制限
- YAML内のコード実行（安全なYAMLパースを使用）
- "claude" や "anthropic" プレフィックスを含む name（予約済み）

**理由:** フロントマターはClaudeのシステムプロンプトに表示される。悪意あるコンテンツがインジェクション攻撃を引き起こす可能性がある。

---

## Multi-line Strings

### Folded Scalar (`>`)

改行がスペースに変換される。段落テキストに適している。

```yaml
description: >
  This is a long description
  that spans multiple lines.
  All newlines become spaces.
```

結果: `"This is a long description that spans multiple lines. All newlines become spaces."`

### Literal Scalar (`|`)

改行を保持する。フォーマット済みテキストに適している。

```yaml
description: |
  Line 1
  Line 2
  Line 3
```

結果:
```
Line 1
Line 2
Line 3
```

### Chomping Indicators

- `>-` / `|-`: 末尾の改行を削除
- `>+` / `|+`: 末尾の改行を保持

---

## Common Mistakes

### 1. Missing delimiters

```yaml
# 間違い
name: my-skill
description: Does things

# 正しい
---
name: my-skill
description: Does things
---
```

### 2. Indentation errors

```yaml
# 間違い
metadata:
author: Name
  version: 1.0

# 正しい
metadata:
  author: Name
  version: 1.0
```

### 3. Unquoted special characters

```yaml
# 間違い - コロンがエスケープされていない
description: Note: this has a colon

# 正しい
description: "Note: this has a colon"
```

### 4. Inconsistent quoting

```yaml
# 間違い - 閉じ引用符がない
description: "Does things

# 正しい
description: "Does things"
```

---

## Validation Checklist

- [ ] `---` 区切りがファイル先頭と frontmatter 終端にある
- [ ] `name` が kebab-case でスペース・大文字なし
- [ ] `name` が "claude" や "anthropic" を含まない
- [ ] `description` が WHAT と WHEN を含む
- [ ] `description` が 1024 文字以下
- [ ] XML タグ（`< >`）がどこにもない
- [ ] 特殊文字が適切に引用されている
- [ ] インデントが一貫している（スペース2つ推奨）
