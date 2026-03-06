---
name: google-workspace-cli
description: "Google Workspace 公式 CLI (gws) を活用した Google Workspace 操作。Gmail、Calendar、Drive、Docs、Sheets、Chat、Tasks など全 Google Workspace API をターミナルから操作。MCP サーバー対応、AIエージェントスキル内蔵。Use when user manages Google Workspace services via CLI: email, calendar, documents, spreadsheets, file management, or task automation. Trigger phrases: Gmail, Google Calendar, Google Drive, Google Docs, Google Sheets, メール送信, 予定確認, ドライブ, スプレッドシート, gws, Google Workspace, カレンダー予定, メール検索."
---

# Google Workspace CLI (gws)

> One CLI for all of Google Workspace — built for humans and AI agents.
> 公式リポジトリ: https://github.com/googleworkspace/cli

## Workflow

Google Workspace 操作タスクを受けたら、以下のステップで進める:

### Step 1: タスク分類

| タスク種別 | サービス | コマンド例 |
|-----------|----------|-----------|
| **メール** | Gmail | `gws gmail users messages list` |
| **予定管理** | Calendar | `gws calendar events list` |
| **ファイル** | Drive | `gws drive files list` |
| **文書** | Docs | `gws docs documents get` |
| **表計算** | Sheets | `gws sheets spreadsheets values get` |
| **チャット** | Chat | `gws chat spaces messages create` |
| **タスク** | Tasks | `gws tasks tasks list` |
| **連絡先** | People | `gws people people connections list` |
| **グループ** | Groups | `gws cloudidentity groups list` |
| **管理** | Admin | `gws admin directory users list` |

### Step 2: アカウント確認

```bash
# 設定済みアカウント一覧
gws auth list

# デフォルトアカウント設定
gws auth default work@corp.com

# コマンドごとに指定
gws --account personal@gmail.com drive files list
```

### Step 3: コマンド実行

すべての出力は構造化 JSON。`--dry-run` で実行前プレビュー可能:
```bash
gws drive files list --params '{"pageSize": 5}'
gws drive files list --params '{"pageSize": 5}' --dry-run
```

### Step 4: 結果処理

JSON 出力を `jq` で加工:
```bash
gws drive files list --params '{"pageSize": 100}' --page-all | jq -r '.files[].name'
```

---

## インストール

```bash
# npm（推奨 — プリビルドバイナリ含む）
npm install -g @googleworkspace/cli

# ソースからビルド（Rust ツールチェーン必要）
cargo install --git https://github.com/googleworkspace/cli --locked

# Nix
nix run github:googleworkspace/cli
```

---

## 認証セットアップ

### インタラクティブ OAuth（推奨）

```bash
# ガイド付きセットアップ（Cloud プロジェクト設定）
gws auth setup

# ログイン（全スコープ）
gws auth login

# 特定サービスのみ（テスト用アプリはスコープ上限25）
gws auth login -s drive,gmail,sheets
```

### Manual OAuth 設定

1. [Google Cloud Console](https://console.cloud.google.com/) → OAuth consent screen 設定（External / Testing）
2. **テストユーザーとして自分のアカウントを追加**（必須）
3. OAuth client ID 作成（Desktop app タイプ）
4. JSON ダウンロード → `~/.config/gws/client_secret.json` に保存

### マルチアカウント

```bash
gws auth login --account work@corp.com
gws auth login --account personal@gmail.com
gws auth list
gws auth default work@corp.com
```

### ヘッドレス / CI 環境

```bash
# ブラウザ環境でエクスポート
gws auth export --unmasked > credentials.json

# ヘッドレス環境で設定
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/credentials.json
gws drive files list
```

### 環境変数

| 変数 | 説明 |
|------|------|
| `GOOGLE_WORKSPACE_CLI_TOKEN` | 事前取得の OAuth2 トークン |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | OAuth / サービスアカウント JSON |
| `GOOGLE_WORKSPACE_CLI_ACCOUNT` | デフォルトアカウントメール |
| `GOOGLE_WORKSPACE_CLI_IMPERSONATED_USER` | Domain-Wide 委任用メール |
| `GOOGLE_WORKSPACE_CLI_CLIENT_ID` | OAuth クライアント ID |
| `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` | OAuth クライアントシークレット |
| `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` | 設定ディレクトリ（デフォルト: `~/.config/gws`） |

---

## コマンド体系

gws は Discovery Service から動的にコマンドを構築する。基本構文:

```
gws <service> <resource> <method> [--params JSON] [--json JSON] [flags]
```

スキーマ確認:
```bash
gws schema drive.files.list
```

### 共通フラグ

| フラグ | 説明 |
|--------|------|
| `--dry-run` | リクエストをプレビュー（実行しない） |
| `--page-all` | 全ページ取得（NDJSON） |
| `--page-limit <N>` | 最大ページ数（デフォルト: 10） |
| `--page-delay <MS>` | ページ間遅延（デフォルト: 100ms） |
| `--account <email>` | 使用アカウント指定 |

---

## Gmail

```bash
# メッセージ一覧
gws gmail users messages list --params '{"userId": "me", "maxResults": 10}'

# 未読メッセージ
gws gmail users messages list --params '{"userId": "me", "q": "is:unread"}'

# 特定送信者
gws gmail users messages list --params '{"userId": "me", "q": "from:example@gmail.com"}'

# メッセージ取得
gws gmail users messages get --params '{"userId": "me", "id": "<message-id>"}'

# メール送信（RFC 2822 base64url エンコード）
gws gmail users messages send --params '{"userId": "me"}' \
  --json '{"raw": "<base64url-encoded-message>"}'

# ラベル一覧
gws gmail users labels list --params '{"userId": "me"}'

# 下書き一覧
gws gmail users drafts list --params '{"userId": "me"}'
```

---

## Calendar

```bash
# 予定一覧
gws calendar events list --params '{"calendarId": "primary", "maxResults": 10, "timeMin": "2026-03-06T00:00:00Z"}'

# 予定作成
gws calendar events insert --params '{"calendarId": "primary"}' \
  --json '{"summary": "会議", "start": {"dateTime": "2026-03-07T14:00:00+09:00"}, "end": {"dateTime": "2026-03-07T15:00:00+09:00"}}'

# 終日イベント
gws calendar events insert --params '{"calendarId": "primary"}' \
  --json '{"summary": "休暇", "start": {"date": "2026-03-20"}, "end": {"date": "2026-03-21"}}'

# 予定削除
gws calendar events delete --params '{"calendarId": "primary", "eventId": "<event-id>"}'

# カレンダー一覧
gws calendar calendarList list
```

---

## Drive

```bash
# ファイル一覧
gws drive files list --params '{"pageSize": 10}'

# フォルダ内のファイル
gws drive files list --params '{"q": "\"<folder-id>\" in parents", "pageSize": 20}'

# ファイル検索
gws drive files list --params '{"q": "name contains \"レポート\""}'

# ファイルアップロード（マルチパート）
gws drive files create --json '{"name": "report.pdf"}' --upload ./report.pdf

# フォルダ作成
gws drive files create --json '{"name": "新規フォルダ", "mimeType": "application/vnd.google-apps.folder"}'

# ファイル削除
gws drive files delete --params '{"fileId": "<file-id>"}'

# 全ページ取得
gws drive files list --params '{"pageSize": 100}' --page-all | jq -r '.files[].name'
```

---

## Sheets

```bash
# スプレッドシート作成
gws sheets spreadsheets create --json '{"properties": {"title": "Q1 Budget"}}'

# セル読み取り（!はシングルクォートで囲む）
gws sheets spreadsheets values get \
  --params '{"spreadsheetId": "<id>", "range": "Sheet1!A1:C10"}'

# データ書き込み
gws sheets spreadsheets values update \
  --params '{"spreadsheetId": "<id>", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["Name", "Score"], ["Alice", 95]]}'

# 行追加
gws sheets spreadsheets values append \
  --params '{"spreadsheetId": "<id>", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["Name", "Score"], ["Alice", 95]]}'
```

> **注意**: Sheets 範囲の `!` は bash の履歴展開と競合するため、**単一引用符で囲む**こと。

---

## Docs

```bash
# ドキュメント取得
gws docs documents get --params '{"documentId": "<doc-id>"}'

# ドキュメント作成
gws docs documents create --json '{"title": "新規ドキュメント"}'
```

---

## Chat

```bash
# スペース一覧
gws chat spaces list

# メッセージ送信
gws chat spaces messages create \
  --params '{"parent": "spaces/<space-id>"}' \
  --json '{"text": "メッセージ内容"}'

# ドライラン
gws chat spaces messages create \
  --params '{"parent": "spaces/<space-id>"}' \
  --json '{"text": "Deploy complete."}' \
  --dry-run
```

---

## Tasks

```bash
# タスクリスト一覧
gws tasks tasklists list

# タスク一覧
gws tasks tasks list --params '{"tasklist": "<tasklist-id>"}'

# タスク作成
gws tasks tasks insert --params '{"tasklist": "<tasklist-id>"}' \
  --json '{"title": "タスク名", "due": "2026-03-15T00:00:00Z"}'
```

---

## MCP サーバー

gws は MCP (Model Context Protocol) サーバーとしても動作する:

```bash
# 特定サービスのツールを公開
gws mcp -s drive,gmail,calendar

# 全サービス（ツール数が多いので注意）
gws mcp -s all
```

### Claude Desktop 設定例

```json
{
  "mcpServers": {
    "gws": {
      "command": "gws",
      "args": ["mcp", "-s", "drive,gmail,calendar"]
    }
  }
}
```

> 各サービスは約10～80ツールを追加。クライアントのツール上限（通常50～100）を考慮して選択。

---

## Model Armor（セキュリティ）

Google Cloud Model Armor 統合でプロンプトインジェクション検査:

```bash
gws gmail users messages get --params '...' \
  --sanitize "projects/P/locations/L/templates/T"
```

環境変数:
- `GOOGLE_WORKSPACE_CLI_SANITIZE_TEMPLATE`: デフォルトテンプレート
- `GOOGLE_WORKSPACE_CLI_SANITIZE_MODE`: `warn`（デフォルト）または `block`

---

## Troubleshooting

### "Access blocked" または 403 エラー

OAuth アプリがテストモードで、アカウントがテストユーザーリストに未登録。

**対処**: Google Cloud Console → OAuth consent screen → Test users → アカウント追加。

### "Google hasn't verified this app"

テストモードの標準警告。"Continue" をクリックして続行。

### スコープ不足

**症状**: `insufficient permission`

**対処**: 必要なサービスを指定して再ログイン:
```bash
gws auth login -s drive,gmail,sheets,calendar
```

### API quota exceeded

**症状**: `429 Too Many Requests`

**対処**: リクエスト間隔を空ける / `--page-delay` を増やす / Cloud Console で quota 確認。

---

## References

- [Google Workspace CLI (gws)](https://github.com/googleworkspace/cli) — 公式リポジトリ
- [Google Workspace APIs](https://developers.google.com/workspace) — API リファレンス
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app) — 認証ガイド
