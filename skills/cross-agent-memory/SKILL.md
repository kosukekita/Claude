---
name: cross-agent-memory
description: >
  Claude Code と Codex CLI の間およびセッション間で記憶を継続・管理するスキル。
  ~/.claude/memory/ を共有メモリストアとして扱い、自動フックと連携する。
  Use when user says: "覚えておいて", "memorize", "記憶して", "remember this",
  "記憶を確認", "memory status", "記憶を整理", "memory cleanup",
  "Codexに同期", "sync to Codex", "記憶を保存", "forget", "忘れて".
  Do NOT use for general file editing or coding tasks unrelated to memory management.
---

# Cross-Agent Memory

Claude Code と Codex CLI の間、そしてセッション間で記憶を効率よく継続させるための管理スキル。

## アーキテクチャ概要

```
~/.claude/memory/
├── MEMORY.md        ← インデックス（常にSessionStartで注入される）
├── AGENTS.md        ← Codex向け自動生成ファイル（編集禁止）
├── user_*.md        ← ユーザー情報の記憶
├── feedback_*.md    ← フィードバック・好みの記憶
├── project_*.md     ← プロジェクト情報の記憶
└── reference_*.md   ← 参照情報の記憶
```

**自動フロー（手動操作不要）:**
- `SessionStart` → `memory-inject.ps1`: MEMORY.md をコンテキストに自動注入
- `Stop` → `memory-save.ps1` + `memory-sync-codex.ps1`: 変更をステージング & AGENTS.md を更新
- Codex: `model_instructions_file` で AGENTS.md を SessionStart 時に自動読み込み

---

## アクション: 記憶を保存（save）

**トリガー:** 「〇〇を覚えておいて」「memorize」「remember this」「記憶して」

### 手順

1. **内容を分類する** — 以下の type から最適なものを選ぶ:
   - `user`: ユーザーの役割・好み・スキル
   - `feedback`: 作業スタイル・好まないパターン・検証済みアプローチ
   - `project`: プロジェクト固有の情報・決定・期限
   - `reference`: 外部リソース・ツール・ドキュメントへのポインタ

2. **ファイル名を決める** — `{type}_{kebab-case-slug}.md` 形式

3. **既存ファイルを確認** — 同じトピックのファイルがあれば更新、なければ新規作成

4. **ファイルを書く** — frontmatter フォーマット:
   ```
   ---
   name: kebab-case-slug
   description: 一行の説明（MEMORY.md インデックスに表示される）
   metadata:
     type: user|feedback|project|reference
   ---

   記憶の内容（Markdown）

   **Why:** なぜこれが重要か（feedback/project type の場合）
   **How to apply:** 将来のセッションでどう使うか
   ```

5. **MEMORY.md を更新** — インデックスに追加:
   ```
   - [タイトル](ファイル名.md) — 一行の説明
   ```

6. **Codex に同期** — 以下を実行:
   ```
   powershell -ExecutionPolicy Bypass -File "$HOME/.claude/hooks/memory-sync-codex.ps1"
   ```

---

## アクション: 記憶を確認（status）

**トリガー:** 「記憶を確認」「memory status」「何を覚えてる?」

### 手順

1. `~/.claude/memory/MEMORY.md` を読み込む
2. メモリファイルの一覧を表示（type別にグループ化）
3. `AGENTS.md` の最終更新日時を確認してCodex同期状態を報告:
   ```
   powershell -Command "(Get-Item '$HOME/.claude/memory/AGENTS.md').LastWriteTime"
   ```
4. ファイル数・合計サイズを報告:
   ```
   powershell -Command "Get-ChildItem '$HOME/.claude/memory/*.md' | Measure-Object -Property Length -Sum | Select-Object Count, Sum"
   ```

**出力フォーマット:**
```
## 記憶ステータス

**ファイル数:** X件
**合計サイズ:** Y KB
**Codex同期:** YYYY-MM-DD HH:mm（最終更新）

### user（ユーザー情報）
- [ファイル名] — 説明

### feedback（フィードバック）
- [ファイル名] — 説明

### project（プロジェクト）
- [ファイル名] — 説明

### reference（参照）
- [ファイル名] — 説明
```

---

## アクション: 記憶を整理（cleanup）

**トリガー:** 「記憶を整理」「memory cleanup」「古い記憶を削除」

### 手順

1. `memory/` 配下のすべての `.md` ファイルを読み込む
2. 以下の観点でチェック:
   - **重複**: 同じトピックの記憶が複数存在していないか
   - **陳腐化**: 日付が古い project 記憶（30日以上経過）
   - **フォーマット不整合**: frontmatter が欠けているか不正
   - **MEMORY.md との不一致**: インデックスに載っていないファイルや、存在しないファイルへのリンク
3. 問題点をリストアップしてユーザーに確認を取る
4. 承認された整理を実行（削除・統合・更新）
5. Codex に再同期する

---

## アクション: Codex 同期（sync）

**トリガー:** 「Codexに同期」「sync to Codex」「AGENTS.md を更新」

### 手順

1. 同期スクリプトを実行:
   ```
   powershell -ExecutionPolicy Bypass -File "$HOME/.claude/hooks/memory-sync-codex.ps1"
   ```
2. 生成された `~/.claude/memory/AGENTS.md` の冒頭を確認:
   ```
   powershell -Command "Get-Content '$HOME/.claude/memory/AGENTS.md' -TotalCount 5"
   ```
3. 成功を報告する

---

## アクション: 記憶を削除（forget）

**トリガー:** 「忘れて」「forget」「記憶を削除」

### 手順

1. 削除対象を特定（MEMORY.md を検索）
2. ユーザーに確認を取る
3. ファイルを削除
4. MEMORY.md インデックスから該当行を削除
5. Codex に再同期する

---

## トラブルシューティング

### SessionStart で記憶が注入されない
- `~/.claude/memory/MEMORY.md` が存在するか確認
- settings.json の SessionStart フックに `memory-inject.ps1` が登録されているか確認

### Codex が記憶を認識しない
- `~/.codex/config.toml` に `model_instructions_file` が設定されているか確認:
  ```toml
  model_instructions_file = "C:\\Users\\{username}\\.claude\\memory\\AGENTS.md"
  ```
- `AGENTS.md` が存在するか確認（Stop フック後に生成される）
- 手動で sync アクションを実行する

### AGENTS.md が生成されない
- PowerShell で直接実行してエラーを確認:
  ```
  powershell -ExecutionPolicy Bypass -File "$HOME/.claude/hooks/memory-sync-codex.ps1"
  ```
