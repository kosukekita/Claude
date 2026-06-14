# GSC セットアップ・トラブルシューティング

## 利用可能なツール（19種）

### プロパティ管理
`list_properties`, `get_site_details`, `add_site`, `delete_site`

### 検索アナリティクス
`get_search_analytics`, `get_performance_overview`, `get_advanced_search_analytics`, `compare_search_periods`, `get_search_by_page_query`

### URL・インデックス管理
`check_indexing_issues`, `inspect_url_enhanced`, `batch_url_inspection`

### サイトマップ
`get_sitemaps`, `list_sitemaps_enhanced`, `submit_sitemap`, `get_sitemap_details`

---

## 認証方法

### OAuth（推奨 - 個人利用）
1. Google Cloud Console で OAuth 2.0 クライアント ID を作成
2. `client_secrets.json` をダウンロード
3. `export GSC_OAUTH_CLIENT_SECRETS_FILE=/path/to/client_secrets.json`

### サービスアカウント（自動化・チーム利用）
1. サービスアカウント作成 → JSON キーダウンロード
2. Search Console でアクセス権付与
3. `export GSC_CREDENTIALS_PATH=/path/to/service-account.json` + `export GSC_SKIP_OAUTH=true`

### Claude Code への登録
```bash
claude mcp add gsc --scope user -- \
  /path/to/mcp-gsc/.venv/bin/python /path/to/mcp-gsc/gsc_server.py
```

---

## Troubleshooting

- **認証エラー**: 環境変数パス確認、トークンリフレッシュ
- **プロパティ非表示**: GSC でアカウントにプロパティ登録確認、サービスアカウントのアクセス権確認
- **データ取得失敗**: 期間にデータ存在するか、日付フォーマット（YYYY-MM-DD）、プロパティURL形式確認
- **MCP 起動失敗**: `claude mcp list` で確認、手動起動テスト

## References
- [mcp-gsc GitHub](https://github.com/AminForou/mcp-gsc)
- [Google Search Console API](https://developers.google.com/webmaster-tools/v1/api_reference_index)
- [Search Console ヘルプ](https://support.google.com/webmasters/)
