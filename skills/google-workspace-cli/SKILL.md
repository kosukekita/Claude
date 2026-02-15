---
name: google-workspace-cli
description: >
  gogcli を活用した Google Workspace CLI 操作。Gmail、Calendar、Drive、Docs、
  Sheets、Chat、Tasks、Contacts など 15+ サービスをターミナルから操作。
  Use when user manages Google Workspace services via CLI: email, calendar,
  documents, spreadsheets, file management, or task automation.
  Trigger phrases: "Gmail", "Google Calendar", "Google Drive", "Google Docs",
  "Google Sheets", "メール送信", "予定確認", "ドライブ", "スプレッドシート",
  "gogcli", "Google Workspace", "gog", "カレンダー予定", "メール検索".
---

# Google Workspace CLI (gogcli)

> Google Workspace サービスをターミナルから操作する CLI ツール。

## Workflow

Google Workspace 操作タスクを受けたら、以下のステップで進める:

### Step 1: タスク分類

| タスク種別 | サービス | 主要コマンド |
|-----------|----------|-------------|
| **メール** | Gmail | `gog gmail` |
| **予定管理** | Calendar | `gog calendar` |
| **ファイル** | Drive | `gog drive` |
| **文書** | Docs | `gog docs` |
| **表計算** | Sheets | `gog sheets` |
| **チャット** | Chat | `gog chat` |
| **タスク** | Tasks | `gog tasks` |
| **連絡先** | Contacts/People | `gog contacts`, `gog people` |
| **フォーム** | Forms | `gog forms` |
| **グループ** | Groups | `gog groups` |
| **メモ** | Keep | `gog keep` |

### Step 2: アカウント確認

```bash
# 設定済みアカウント一覧
gog auth list

# 使用するアカウントを指定
export GOG_ACCOUNT=you@gmail.com
```

### Step 3: コマンド実行

JSON 出力でスクリプティング向け:
```bash
gog gmail messages list --json
```

### Step 4: 結果処理

JSON 出力を `jq` で加工、または `--plain` でタブ区切り出力。

---

## インストール

```bash
# Homebrew (macOS/Linux)
brew install steipete/tap/gogcli

# Arch Linux
yay -S gogcli

# ソースからビルド
git clone https://github.com/steipete/gogcli.git
cd gogcli && make
```

---

## 認証セットアップ

### Step 1: OAuth クライアント作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. `APIs & Services` → `Credentials` → `+ CREATE CREDENTIALS`
3. `OAuth client ID` → Application type: **Desktop app**
4. JSON ファイルをダウンロード

### Step 2: 認証情報を登録

```bash
# 認証情報を保存
gog auth credentials ~/Downloads/client_secret_*.json

# アカウント追加（ブラウザ認証）
gog auth add you@gmail.com

# ヘッドレス環境の場合
gog auth add you@gmail.com --manual
```

### Step 3: 確認

```bash
# アカウント一覧
gog auth list

# テスト
export GOG_ACCOUNT=you@gmail.com
gog gmail labels list
```

---

## Gmail

### メッセージ操作

```bash
# 受信トレイのメッセージ一覧
gog gmail messages list

# 未読メッセージ
gog gmail messages list --query "is:unread"

# 特定の送信者から
gog gmail messages list --query "from:example@gmail.com"

# メッセージ詳細
gog gmail messages get <message-id>

# メール送信
gog gmail messages send --to recipient@example.com --subject "件名" --body "本文"

# 添付ファイル付き
gog gmail messages send --to recipient@example.com --subject "件名" --body "本文" --attach file.pdf
```

### ラベル操作

```bash
# ラベル一覧
gog gmail labels list

# ラベル作成
gog gmail labels create "重要/プロジェクトA"

# メッセージにラベル追加
gog gmail messages modify <message-id> --add-labels "重要"
```

### 下書き

```bash
# 下書き一覧
gog gmail drafts list

# 下書き作成
gog gmail drafts create --to recipient@example.com --subject "件名" --body "本文"
```

---

## Calendar

### 予定操作

```bash
# 今日の予定
gog calendar events list

# 特定期間の予定
gog calendar events list --from "2025-01-01" --to "2025-01-31"

# 予定作成
gog calendar events create --title "会議" --start "2025-01-15 14:00" --end "2025-01-15 15:00"

# 終日イベント
gog calendar events create --title "休暇" --start "2025-01-20" --all-day

# 予定削除
gog calendar events delete <event-id>
```

### カレンダー管理

```bash
# カレンダー一覧
gog calendar calendars list

# 特定カレンダーの予定
gog calendar events list --calendar "work@group.calendar.google.com"
```

---

## Drive

### ファイル操作

```bash
# ファイル一覧（ルート）
gog drive files list

# フォルダ内のファイル
gog drive files list --parent <folder-id>

# ファイル検索
gog drive files list --query "name contains 'レポート'"

# ファイルアップロード
gog drive files upload local-file.pdf

# 特定フォルダにアップロード
gog drive files upload local-file.pdf --parent <folder-id>

# ファイルダウンロード
gog drive files download <file-id> --output local-file.pdf

# ファイル削除
gog drive files delete <file-id>
```

### フォルダ操作

```bash
# フォルダ作成
gog drive files create --name "新規フォルダ" --type folder

# ファイル移動
gog drive files move <file-id> --parent <new-folder-id>
```

---

## Sheets

```bash
# スプレッドシート一覧
gog sheets list

# シートのデータ読み取り
gog sheets get <spreadsheet-id> --range "Sheet1!A1:D10"

# データ書き込み
gog sheets update <spreadsheet-id> --range "Sheet1!A1" --values '[["A1", "B1"], ["A2", "B2"]]'

# 行追加
gog sheets append <spreadsheet-id> --range "Sheet1" --values '[["新しい行"]]'
```

---

## Docs

```bash
# ドキュメント一覧
gog docs list

# ドキュメント内容取得
gog docs get <document-id>

# ドキュメント作成
gog docs create --title "新規ドキュメント"
```

---

## Tasks

```bash
# タスクリスト一覧
gog tasks lists list

# タスク一覧
gog tasks list --list <list-id>

# タスク作成
gog tasks create --list <list-id> --title "タスク名" --due "2025-01-15"

# タスク完了
gog tasks complete --list <list-id> --task <task-id>
```

---

## Chat

```bash
# スペース一覧
gog chat spaces list

# メッセージ送信
gog chat messages send --space <space-id> --text "メッセージ"
```

---

## 出力フォーマット

```bash
# デフォルト: 人間向けテーブル
gog gmail messages list

# JSON: スクリプティング向け
gog gmail messages list --json

# プレーン: タブ区切り（パイプ処理向け）
gog gmail messages list --plain
```

---

## 複数アカウント管理

```bash
# アカウント追加
gog auth add personal@gmail.com
gog auth add work@company.com

# エイリアス設定
gog auth alias personal personal@gmail.com
gog auth alias work work@company.com

# アカウント切り替え
export GOG_ACCOUNT=work
gog gmail messages list

# コマンドごとに指定
gog --account personal gmail messages list
```

---

## 自動化例

### 未読メールを JSON で取得して処理

```bash
gog gmail messages list --query "is:unread" --json | jq '.[] | {id, subject: .payload.headers[] | select(.name=="Subject") | .value}'
```

### 今日の予定を Slack に投稿

```bash
TODAY=$(gog calendar events list --json | jq -r '.[].summary' | tr '\n' ', ')
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"今日の予定: $TODAY\"}" \
  https://hooks.slack.com/services/xxx
```

### Drive のファイルを定期バックアップ

```bash
# バックアップスクリプト
gog drive files list --query "modifiedTime > '$(date -d '1 day ago' +%Y-%m-%dT%H:%M:%S)'" --json | \
  jq -r '.[].id' | \
  xargs -I {} gog drive files download {} --output backup/{}
```

---

## Troubleshooting

### 認証エラー

**症状**: `token expired` または `invalid_grant`

**対応**:
```bash
# トークンをリフレッシュ
gog auth refresh you@gmail.com

# 再認証
gog auth add you@gmail.com --force
```

### API quota exceeded

**症状**: `429 Too Many Requests`

**対応**:
- リクエスト間隔を空ける
- バッチ処理を検討
- Google Cloud Console で quota を確認

### アカウントが見つからない

**症状**: `account not found`

**対応**:
```bash
# 環境変数を確認
echo $GOG_ACCOUNT

# アカウント一覧を確認
gog auth list

# 正しいアカウントを設定
export GOG_ACCOUNT=you@gmail.com
```

### スコープ不足

**症状**: `insufficient permission`

**対応**:
```bash
# 必要なスコープで再認証
gog auth add you@gmail.com --scopes "gmail.modify,calendar.events"
```

---

## References

- [gogcli GitHub](https://github.com/steipete/gogcli) — ソースコード・ドキュメント
- [Google Workspace APIs](https://developers.google.com/workspace) — API リファレンス
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app) — 認証ガイド
