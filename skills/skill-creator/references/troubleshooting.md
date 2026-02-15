# Troubleshooting Guide

スキル開発でよくある問題と解決策。

---

## Skill won't upload

### Error: "Could not find SKILL.md in uploaded folder"

**原因:** ファイル名が正確に SKILL.md ではない

**解決策:**
1. SKILL.md にリネーム（大文字・小文字厳密）
2. `ls -la` で確認（SKILL.md と表示されるべき）

### Error: "Invalid frontmatter"

**原因:** YAMLフォーマットの問題

**よくある間違い:**

```yaml
# 間違い - 区切りがない
name: my-skill
description: Does things

# 間違い - 閉じ引用符がない
name: my-skill
description: "Does things

# 正しい
---
name: my-skill
description: Does things
---
```

### Error: "Invalid skill name"

**原因:** name にスペースや大文字がある

```yaml
# 間違い
name: My Cool Skill

# 正しい
name: my-cool-skill
```

---

## Skill doesn't trigger

**症状:** スキルが自動的にロードされない

### 修正方法

description フィールドを見直す。

**チェックリスト:**
- 曖昧すぎないか?（"Helps with projects" は機能しない）
- ユーザーが実際に言うトリガーフレーズを含むか?
- 該当するファイルタイプを言及しているか?

**デバッグ方法:**
Claudeに聞く: "When would you use the [skill name] skill?"
Claudeは description を引用して返答する。何が足りないか判断できる。

### 良い description の例

```yaml
# 具体的でアクション可能
description: >
  Analyzes Figma design files and generates developer handoff documentation.
  Use when user uploads .fig files, asks for "design specs",
  "component documentation", or "design-to-code handoff".

# トリガーフレーズを含む
description: >
  Manages Linear project workflows including sprint planning, task creation,
  and status tracking. Use when user mentions "sprint", "Linear tasks",
  "project planning", or asks to "create tickets".
```

---

## Skill triggers too often

**症状:** 無関係なクエリでスキルがロードされる

### 解決策

#### 1. ネガティブトリガーを追加

```yaml
description: >
  Advanced data analysis for CSV files. Use for statistical modeling,
  regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
```

#### 2. より具体的に

```yaml
# 広すぎる
description: Processes documents

# 適切な範囲
description: Processes PDF legal documents for contract review
```

#### 3. スコープを明確化

```yaml
description: >
  PayFlow payment processing for e-commerce. Use specifically for
  online payment workflows, not for general financial queries.
```

---

## Instructions not followed

**症状:** スキルはロードされるがClaudeが指示に従わない

### 原因と対策

#### 1. 指示が冗長すぎる

**対策:**
- 簡潔に保つ
- 箇条書きや番号リストを使用
- 詳細なドキュメントは `references/` に移動

#### 2. 重要な指示が埋もれている

**対策:**
- 重要な指示を先頭に配置
- `## Important` や `## Critical` ヘッダーを使用
- 必要なら繰り返す

#### 3. 曖昧な言語

```markdown
# 悪い例
Make sure to validate things properly

# 良い例
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

#### 4. モデルの「怠惰」

明示的な励ましを追加:

```markdown
## Performance Notes
- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
```

---

## MCP connection issues

**症状:** スキルはロードされるがMCP呼び出しが失敗

### チェックリスト

#### 1. MCP サーバーが接続されているか確認
- Claude.ai: Settings > Extensions > [Your Service]
- "Connected" ステータスが表示されるべき

#### 2. 認証を確認
- APIキーが有効で期限切れでないか
- 適切な権限/スコープが付与されているか
- OAuthトークンがリフレッシュされているか

#### 3. MCPを単独でテスト
スキルなしでMCPを直接呼び出してみる:
"Use [Service] MCP to fetch my projects"
これが失敗すればMCPの問題であり、スキルの問題ではない

#### 4. ツール名を確認
- スキルが正しいMCPツール名を参照しているか
- MCPサーバーのドキュメントを確認
- ツール名は大文字・小文字を区別

---

## Large context issues

**症状:** スキルが遅い、または応答品質が低下

### 原因
- スキルコンテンツが大きすぎる
- 同時に有効なスキルが多すぎる
- Progressive disclosure ではなくすべてをロード

### 解決策

#### 1. SKILL.md サイズを最適化
- 詳細ドキュメントを `references/` に移動
- インラインではなく参照へのリンク
- SKILL.md を 5,000 ワード以下に保つ

#### 2. 有効なスキルを減らす
- 同時に 20-50 以上のスキルが有効なら評価
- 選択的な有効化を推奨
- 関連機能は「パック」にまとめることを検討

---

## Common YAML mistakes

### 1. インデントエラー

```yaml
# 間違い - インデント不一致
metadata:
author: Name
  version: 1.0

# 正しい
metadata:
  author: Name
  version: 1.0
```

### 2. 特殊文字のエスケープ

```yaml
# 間違い - コロンがエスケープされていない
description: Note: this needs quotes

# 正しい
description: "Note: this needs quotes"
# または
description: >
  Note: this needs quotes
```

### 3. マルチライン文字列

```yaml
# 折り返しスカラー（改行がスペースに）
description: >
  This is a long description
  that spans multiple lines.

# リテラルスカラー（改行を保持）
description: |
  Line 1
  Line 2
```

---

## Quick Debug Checklist

1. [ ] SKILL.md が正確にそのスペルか?
2. [ ] YAML フロントマターに `---` 区切りがあるか?
3. [ ] name が kebab-case でスペース・大文字なしか?
4. [ ] description に WHAT と WHEN があるか?
5. [ ] XML タグ（`< >`）がどこにもないか?
6. [ ] MCP サーバーが接続されているか（必要な場合）?
7. [ ] 正しいツール名を使用しているか?
