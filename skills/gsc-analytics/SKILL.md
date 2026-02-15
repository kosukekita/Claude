---
name: gsc-analytics
description: >
  Google Search Console MCP を活用した検索パフォーマンス分析・インデックス管理。
  検索アナリティクス、URL検査、サイトマップ管理、期間比較、モバイル/デスクトップ分析。
  Use when user analyzes search performance, checks indexing status, manages sitemaps,
  or investigates SEO issues using Google Search Console data.
  Trigger phrases: "Search Console", "GSC", "検索パフォーマンス", "インデックス状況",
  "クエリ分析", "サイトマップ", "検索順位", "CTR", "インプレッション",
  "URL検査", "クロール", "モバイル検索", "デスクトップ検索".
---

# Google Search Console Analytics

> Google Search Console MCP を使用した検索パフォーマンス分析・SEO診断スキル。

## Workflow

GSC 分析タスクを受けたら、以下のステップで進める:

### Step 1: タスク分類

| タスク種別 | 内容 | 主要ツール |
|-----------|------|-----------|
| **パフォーマンス概要** | サイト全体の検索状況確認 | `get_performance_overview` |
| **クエリ分析** | 検索クエリの詳細分析 | `get_search_analytics`, `get_advanced_search_analytics` |
| **ページ分析** | 特定ページのトラフィック源分析 | `get_search_by_page_query` |
| **期間比較** | 前月比・前年比などの比較 | `compare_search_periods` |
| **インデックス診断** | URL のインデックス状況確認 | `inspect_url_enhanced`, `batch_url_inspection` |
| **サイトマップ管理** | サイトマップの確認・送信 | `list_sitemaps_enhanced`, `submit_sitemap` |

### Step 2: プロパティ確認

まずアクセス可能なプロパティを確認:
```
list_properties → 利用可能なサイト一覧を取得
```

### Step 3: データ取得・分析

タスクに応じて適切なツールを選択してデータを取得。

### Step 4: 洞察・提案

取得データを分析し:
- 主要な発見を要約
- 問題点と改善提案を提示
- 次のアクションを推奨

---

## 利用可能なツール（19種）

### プロパティ管理

| ツール | 説明 |
|-------|------|
| `list_properties` | GSC に登録された全プロパティを一覧表示 |
| `get_site_details` | 特定サイトの詳細情報を取得 |
| `add_site` | 新しいプロパティを追加 |
| `delete_site` | プロパティを削除 |

### 検索アナリティクス

| ツール | 説明 | ユースケース |
|-------|------|-------------|
| `get_search_analytics` | 上位クエリ・ページとメトリクス取得 | 基本的なパフォーマンス確認 |
| `get_performance_overview` | サイト全体のパフォーマンス要約 | 定期レポート作成 |
| `get_advanced_search_analytics` | 詳細なクエリパフォーマンス分析 | 深堀り分析 |
| `compare_search_periods` | 期間間のパフォーマンス比較 | 前月比・前年比分析 |
| `get_search_by_page_query` | 特定ページのトラフィック源分析 | ページ別最適化 |

### URL・インデックス管理

| ツール | 説明 | ユースケース |
|-------|------|-------------|
| `check_indexing_issues` | インデックス問題のあるページを特定 | インデックス診断 |
| `inspect_url_enhanced` | 詳細な URL 検査 | 個別ページの問題調査 |
| `batch_url_inspection` | 複数 URL を一括検査 | サイト全体のインデックス確認 |

### サイトマップ

| ツール | 説明 |
|-------|------|
| `get_sitemaps` | サイトマップ一覧を取得 |
| `list_sitemaps_enhanced` | 詳細なサイトマップ情報 |
| `submit_sitemap` | 新しいサイトマップを送信 |
| `get_sitemap_details` | サイトマップのステータスと警告を確認 |

---

## 分析パターン

### パフォーマンス概要レポート

```
1. get_performance_overview
   → クリック数、インプレッション、CTR、平均順位の概要

2. get_search_analytics (dimensions: query, device)
   → 上位クエリとデバイス別パフォーマンス

3. 結果をまとめてレポート作成
```

### 順位改善の機会発見

```
1. get_advanced_search_analytics
   → 11-20位のクエリ（改善余地が大きい）
   → 高インプレッション・低CTR のクエリ

2. 分析ポイント:
   - 11-20位 → タイトル/メタ最適化で10位以内を狙う
   - 高インプレッション・低CTR → タイトル改善の余地
```

### モバイル vs デスクトップ比較

```
1. get_search_analytics (dimensions: device)
   → デバイス別のパフォーマンス

2. 分析ポイント:
   - モバイルの順位がデスクトップより低い → モバイル最適化が必要
   - モバイルの CTR が低い → タップしやすいタイトルに改善
```

### 期間比較分析

```
1. compare_search_periods
   → 今月 vs 先月、今四半期 vs 前四半期

2. 分析ポイント:
   - 急落したクエリ → 競合の台頭、アルゴリズム変更の影響
   - 急上昇したクエリ → 成功要因を他ページに横展開
```

### インデックス問題の診断

```
1. check_indexing_issues
   → インデックスされていないページを特定

2. batch_url_inspection
   → 重要ページのインデックス状況を一括確認

3. 問題別対応:
   - "Crawled - currently not indexed" → コンテンツ品質改善
   - "Discovered - currently not indexed" → 内部リンク追加
   - "Blocked by robots.txt" → robots.txt 修正
```

---

## レポート出力フォーマット

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GSC PERFORMANCE REPORT: [サイト名]
期間: [開始日] 〜 [終了日]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY:
  クリック数: [数値] ([前期比 +/-%)
  インプレッション: [数値] ([前期比 +/-%)
  平均CTR: [数値]%
  平均順位: [数値]

TOP QUERIES:
  1. [クエリ] — クリック: [数値], 順位: [数値]
  2. ...

OPPORTUNITIES (改善余地):
  - [クエリ]: 順位 [数値] → タイトル最適化で10位以内を狙える
  - [クエリ]: CTR [数値]% → 業界平均より低い、タイトル改善推奨

ISSUES:
  - [問題の説明と対応策]

NEXT ACTIONS:
  1. [推奨アクション]
  2. ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## セットアップ

### 前提条件

- Python 3.11+
- Claude Desktop または Claude Code
- Google Cloud Console でプロジェクト作成済み

### 認証方法

#### OAuth（推奨 - 個人利用）

1. Google Cloud Console で OAuth 2.0 クライアント ID を作成
2. `client_secrets.json` をダウンロード
3. 環境変数を設定:
   ```bash
   export GSC_OAUTH_CLIENT_SECRETS_FILE=/path/to/client_secrets.json
   ```

#### サービスアカウント（自動化・チーム利用）

1. Google Cloud Console でサービスアカウントを作成
2. JSON キーファイルをダウンロード
3. Search Console でサービスアカウントにプロパティへのアクセス権を付与
4. 環境変数を設定:
   ```bash
   export GSC_CREDENTIALS_PATH=/path/to/service-account.json
   export GSC_SKIP_OAUTH=true
   ```

### インストール

```bash
git clone https://github.com/AminForou/mcp-gsc.git
cd mcp-gsc
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Claude Code への登録

```bash
claude mcp add gsc --scope user -- \
  /path/to/mcp-gsc/.venv/bin/python /path/to/mcp-gsc/gsc_server.py
```

環境変数付き:
```bash
claude mcp add gsc --scope user \
  --env GSC_OAUTH_CLIENT_SECRETS_FILE=/path/to/client_secrets.json \
  -- /path/to/mcp-gsc/.venv/bin/python /path/to/mcp-gsc/gsc_server.py
```

---

## Troubleshooting

### 認証エラー

**症状**: `Authentication failed` または `Invalid credentials`

**対応**:
1. 環境変数のパスが正しいか確認
2. OAuth の場合: `client_secrets.json` が有効か確認
3. サービスアカウントの場合: Search Console でアクセス権が付与されているか確認
4. トークンをリフレッシュ（OAuth の場合、既存のトークンファイルを削除して再認証）

### プロパティが表示されない

**症状**: `list_properties` が空の結果を返す

**対応**:
1. Google Search Console で該当アカウントにプロパティが登録されているか確認
2. サービスアカウントの場合: Search Console の「設定」→「ユーザーと権限」でサービスアカウントのメールが追加されているか確認

### データが取得できない

**症状**: `get_search_analytics` がエラーまたは空の結果

**対応**:
1. 指定した期間にデータが存在するか確認（新規サイトは数日かかる）
2. 日付フォーマットが正しいか確認（YYYY-MM-DD）
3. プロパティ URL の形式を確認（`sc-domain:example.com` または `https://example.com/`）

### MCP サーバーが起動しない

**症状**: Claude Code で GSC ツールが表示されない

**対応**:
```bash
# 登録状況を確認
claude mcp list

# 設定詳細を確認
claude mcp get gsc

# 手動で起動テスト
/path/to/mcp-gsc/.venv/bin/python /path/to/mcp-gsc/gsc_server.py
```

---

## References

- [mcp-gsc GitHub](https://github.com/AminForou/mcp-gsc) — MCP サーバーのソースコード
- [Google Search Console API](https://developers.google.com/webmaster-tools/v1/api_reference_index) — API リファレンス
- [Search Console ヘルプ](https://support.google.com/webmasters/) — 公式ドキュメント
