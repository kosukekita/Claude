---
name: cross-agent-memory
description: >
  Claude Code と Codex CLI の間およびセッション間で記憶を継続・管理するスキル。
  ハーネスの auto-memory ストア（~/.claude/projects/<スラグ>/memory/）を共有メモリとして扱い、自動フックと連携する。
  Use when user says: "覚えておいて", "memorize", "記憶して", "remember this",
  "記憶を確認", "memory status", "記憶を整理", "memory cleanup",
  "Codexに同期", "sync to Codex", "記憶を保存", "forget", "忘れて".
  Do NOT use for general file editing or coding tasks unrelated to memory management.
---

# Cross-Agent Memory

Claude Code と Codex CLI の間、そしてセッション間で記憶を効率よく継続させるための管理スキル。

## メモリストアの場所（重要）

グローバル記憶の実体は**ハーネスの auto-memory ディレクトリ**にある。パスはマシンのユーザー名に依存する:

```
~/.claude/projects/[cC]--Users-<ユーザー名>--claude/memory/
```

以下、このパスを `<MEM_DIR>` と表記する。PowerShell での解決方法:

```powershell
$memDir = Get-ChildItem "$env:USERPROFILE\.claude\projects" -Directory |
  Where-Object { $_.Name -match "^[cC]--Users-$([regex]::Escape($env:USERNAME))--claude$" } |
  Select-Object -First 1 | ForEach-Object { Join-Path $_.FullName "memory" }
```

このリポジトリは複数PCでGitHub同期されるため、他PC由来のストア（別ユーザー名のスラグ）が並存することがある。フックは全ストアを注入する。

## アーキテクチャ概要

```
<MEM_DIR>/
├── MEMORY.md        ← インデックス（SessionStartで注入される）
├── user_*.md        ← ユーザー情報の記憶
├── feedback_*.md    ← フィードバック・好みの記憶
├── project_*.md     ← プロジェクト情報の記憶
└── reference_*.md   ← 参照情報の記憶

~/.codex/AGENTS.md   ← Codex向け自動生成ミラー（編集禁止）
```

**自動フロー（手動操作不要）:**
- `SessionStart` → `memory-inject.ps1`: 全ストアの MEMORY.md＋本文をコンテキストに自動注入
- `SessionStart`/`Stop` → `memory-sync-codex.ps1`: `~/.codex/AGENTS.md` を再生成（Codex はこの場所を標準で読むため設定不要）
- `Stop` → `auto-push.ps1`: メモリ変更を含む共有ファイルを自動コミット・プッシュ

---

## アクション: 記憶を保存（save）

**トリガー:** 「〇〇を覚えておいて」「memorize」「remember this」「記憶して」

### 保存ゲート（記録に値するか — 書く前に判定）

mattpocock/skills の `grill-with-docs` の ADR-worthiness 規律を流用。**3条件をすべて満たすものだけ**を記憶として残し、索引の肥大を防ぐ:

1. **不可逆 / 高コスト** — 再発見にコストがかかる（バグの根本原因、環境固有の罠、取得済みライセンス等）。次に同じことをゼロから調べ直す羽目になるか？
2. **文脈なしでは意外** — コード・git 履歴・CLAUDE.md から自明に導けない。「リポを読めば分かる」ものは保存しない。
3. **本物のトレードオフ/判断の産物** — なぜそうしたかの理由がある（feedback/project は `Why:` を必ず書く）。「当たり前のこと」は記録しない。

満たさない例（保存しない）: 一般的な技術知識、コード構造、過去の修正そのもの、この会話だけで完結する事項。ユーザーがそれらを「覚えて」と言ったら、**何が非自明だったか**を1つ聞き出してそれを保存する（CLAUDE.md の方針どおり）。

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

1. `<MEM_DIR>/MEMORY.md` を読み込む
2. メモリファイルの一覧を表示（type別にグループ化）
3. `~/.codex/AGENTS.md` の最終更新日時を確認してCodex同期状態を報告:
   ```
   powershell -Command "(Get-Item \"$env:USERPROFILE/.codex/AGENTS.md\").LastWriteTime"
   ```
4. ファイル数・合計サイズを報告（`<MEM_DIR>/*.md` を Measure-Object で集計）

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

1. `<MEM_DIR>/` 配下のすべての `.md` ファイルを読み込む
2. 以下の観点でチェック:
   - **重複**: 同じトピックの記憶が複数存在していないか。スキル・CLAUDE.md に既に記録済みの内容は削除候補
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
2. 生成された `~/.codex/AGENTS.md` の冒頭を確認:
   ```
   powershell -Command "Get-Content \"$env:USERPROFILE/.codex/AGENTS.md\" -TotalCount 5"
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
5. 他の記憶ファイルから対象への `[[wikilink]]` 参照を grep して更新
6. Codex に再同期する

---

## トラブルシューティング

### SessionStart で記憶が注入されない
- `<MEM_DIR>/MEMORY.md` が存在するか確認
- settings.json の SessionStart フックに `memory-inject.ps1` が登録されているか確認

### Codex が記憶を認識しない
- `~/.codex/AGENTS.md` が存在するか確認（SessionStart/Stop フックが生成する）
- 無ければ手動で sync アクションを実行する（Codex は `~/.codex/AGENTS.md` を標準で読むため config.toml の設定は不要）

### AGENTS.md が生成されない
- PowerShell で直接実行してエラーを確認:
  ```
  powershell -ExecutionPolicy Bypass -File "$HOME/.claude/hooks/memory-sync-codex.ps1"
  ```

### ツールのパスが化ける（このリポジトリ特有）
- パス中の `\u` + 16進4桁（例: ユーザー名 u8792）が Unicode エスケープ解釈される既知問題がある。ツールに渡すパスは常にフォワードスラッシュで書く（詳細はグローバル記憶 `feedback_u8792_path_unicode_escape` を参照）
