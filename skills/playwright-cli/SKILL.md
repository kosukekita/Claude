---
name: playwright-cli
description: >
  Playwright MCP を活用したブラウザ自動化・E2Eテスト・ログイン自動化。
  Webページのナビゲーション、フォーム入力、スクリーンショット、データ抽出、
  セッション管理、リクエストモック、トレース、動画録画、汎用ログインフローをカバー。
  Use when user needs browser automation, web testing, form filling,
  screenshots, data extraction, or universal login automation.
  Trigger phrases: "ブラウザ自動化", "E2Eテスト", "スクリーンショット",
  "フォーム入力", "Webスクレイピング", "playwright", "ブラウザ操作",
  "ログインテスト", "画面キャプチャ", "ログイン自動化", "SSO", "MFA",
  "browser automation", "web testing", "login automation", "auth flow".
allowed-tools: Bash(playwright-cli:*)
---

# Browser Automation with playwright-cli

## Workflow

ブラウザ自動化タスクを受けたら、以下のステップで進める:

### Step 1: タスク分類

| タスク種別 | 内容 | 主要コマンド |
|-----------|------|-------------|
| **ページ確認** | スクリーンショット、要素確認 | `open`, `goto`, `snapshot`, `screenshot` |
| **フォーム操作** | 入力、クリック、送信 | `fill`, `click`, `type`, `select` |
| **認証テスト** | ログイン状態の保存・復元 | `state-save`, `state-load` |
| **データ抽出** | ページ内容の取得 | `eval`, `snapshot` |
| **デバッグ** | コンソール、ネットワーク監視 | `console`, `network`, `tracing-start` |

### Step 2: ブラウザセッション開始

```shell
# 基本的な開始
playwright-cli open https://example.com

# 特定ブラウザを指定
playwright-cli open --browser=chrome https://example.com

# 永続プロファイル（Cookie保持）
playwright-cli open --persistent https://example.com
```

### Step 3: 操作実行

1. `snapshot` でページ構造を確認（要素の ref を取得）
2. ref を使って操作（`click e3`, `fill e5 "value"`）
3. 必要に応じて `screenshot` で結果を確認

### Step 4: 終了処理

```shell
# 状態を保存する場合
playwright-cli state-save auth.json
playwright-cli close

# 単純に終了
playwright-cli close
```

---

## Quick Start

```shell
# ブラウザを開く
playwright-cli open

# ページに移動
playwright-cli goto https://playwright.dev

# スナップショットで要素を確認（ref番号を取得）
playwright-cli snapshot

# ref を使って操作
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter

# スクリーンショット
playwright-cli screenshot

# 終了
playwright-cli close
```

---

## Commands

### Core

```shell
playwright-cli open
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
playwright-cli fill e5 "user@example.com"
playwright-cli drag e2 e8
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
playwright-cli snapshot --filename=after-click.yaml
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
playwright-cli close
```

### Navigation

```shell
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### Keyboard

```shell
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### Mouse

```shell
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
```

### Save as

```shell
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli pdf --filename=page.pdf
```

### Tabs

```shell
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

### Storage

```shell
# 状態の保存・復元
playwright-cli state-save
playwright-cli state-save auth.json
playwright-cli state-load auth.json

# Cookies
playwright-cli cookie-list
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

# LocalStorage
playwright-cli localstorage-list
playwright-cli localstorage-get theme
playwright-cli localstorage-set theme dark
playwright-cli localstorage-delete theme
playwright-cli localstorage-clear

# SessionStorage
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get step
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-delete step
playwright-cli sessionstorage-clear
```

### Network

```shell
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

### DevTools

```shell
playwright-cli console
playwright-cli console warning
playwright-cli network
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli video-start
playwright-cli video-stop video.webm
```

### Install

```shell
playwright-cli install --skills
playwright-cli install-browser
```

### Configuration

```shell
# ブラウザ指定
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --browser=msedge

# 拡張機能経由
playwright-cli open --extension

# 永続プロファイル
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile

# 設定ファイル
playwright-cli open --config=my-config.json

# 終了・データ削除
playwright-cli close
playwright-cli delete-data
```

### Browser Sessions

```shell
# 名前付きセッション
playwright-cli -s=mysession open example.com --persistent
playwright-cli -s=mysession open example.com --profile=/path/to/profile
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close
playwright-cli -s=mysession delete-data

# セッション管理
playwright-cli list
playwright-cli close-all
playwright-cli kill-all
```

---

## Examples

### フォーム送信

```shell
playwright-cli open https://example.com/form
playwright-cli snapshot

playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

### マルチタブワークフロー

```shell
playwright-cli open https://example.com
playwright-cli tab-new https://example.com/other
playwright-cli tab-list
playwright-cli tab-select 0
playwright-cli snapshot
playwright-cli close
```

### DevTools でデバッグ

```shell
playwright-cli open https://example.com
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli network
playwright-cli close
```

### トレース記録

```shell
playwright-cli open https://example.com
playwright-cli tracing-start
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli tracing-stop
playwright-cli close
```

---

## Troubleshooting

### ブラウザが起動しない

```shell
# ブラウザをインストール
playwright-cli install-browser

# 既存プロセスを強制終了
playwright-cli kill-all
```

### 要素が見つからない（ref が無効）

1. `snapshot` を再実行して最新の ref を取得
2. ページの読み込み完了を待つ
3. 要素が iframe 内にある場合は別途対応

### Cookie が保持されない

```shell
# 永続プロファイルを使用
playwright-cli open --persistent https://example.com

# または状態を明示的に保存・復元
playwright-cli state-save auth.json
playwright-cli close
playwright-cli open https://example.com
playwright-cli state-load auth.json
```

### ネットワークエラー

```shell
# ネットワークログを確認
playwright-cli network

# タイムアウト設定がある場合は長めに設定
```

---

## Universal Login Flow

> Source: [login-machine](https://github.com/RichardHruby/login-machine)

任意のWebサイトにログインするための汎用パターン。サイト固有のスクリプトを書く代わりに、ビジョン分析で画面を認識してログインフローを自動化。

### ログインエージェントループ

```
1. ログインページに移動
2. スクリーンショット + HTML を取得
3. 画面タイプを分類
4. ユーザー入力を要求 or 自動処理
5. ブラウザ DOM に入力を送信
6. ログイン完了まで繰り返し
```

### 画面タイプ分類

| タイプ | 内容 | 処理方法 |
|--------|------|----------|
| `credential_login_form` | メール/パスワード/OTP | フォーム表示 → ユーザー入力 → DOM に送信 |
| `choice_screen` | アカウント選択、SSO | ボタン表示 → ユーザー選択 → クリック |
| `magic_login_link` | 「メールを確認」画面 | URL 入力 → ユーザーがリンク貼付 → 移動 |
| `loading_screen` | スピナー、リダイレクト | 自動待機 → 再分析（最大12回） |
| `blocked_screen` | Cookie バナー、ポップアップ | 自動解除 → 再分析 |
| `logged_in_screen` | ダッシュボード、ホーム | 完了状態 |

### ログインフロー実装例

```shell
# 1. ログインページを開く
playwright-cli open https://example.com/login

# 2. スナップショットで画面を分析
playwright-cli snapshot

# 3. 画面タイプに応じて操作
# credential_login_form の場合:
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3  # Submit ボタン

# 4. 結果を確認
playwright-cli snapshot

# 5. ログイン状態を保存
playwright-cli state-save auth.json
playwright-cli close
```

### SSO / MFA 対応

```shell
# SSO ログイン（Google, Microsoft等）
playwright-cli open https://app.example.com/login
playwright-cli snapshot  # → choice_screen: "Continue with Google"
playwright-cli click e5  # Google ボタン
playwright-cli snapshot  # → Google ログインページ
playwright-cli fill e1 "user@gmail.com"
playwright-cli click e2
playwright-cli snapshot  # → パスワード画面
playwright-cli fill e3 "password"
playwright-cli click e4
playwright-cli snapshot  # → 2FA or リダイレクト

# MFA/2FA 対応
playwright-cli snapshot  # → OTP フィールド
playwright-cli fill e5 "123456"
playwright-cli click e6

# Magic Link 対応
playwright-cli snapshot  # → "Check your email"
playwright-cli goto "https://example.com/verify?token=abc123"
playwright-cli snapshot  # → logged_in_screen
```

### セキュリティ原則

1. **認証情報の分離**: LLM はフィールド構造のみ分析。認証情報は直接 DOM に送信
2. **ロケーター検証**: 生成セレクタは使用前に DOM 検証。無効時は再試行（最大3回）
3. **観察ベース**: アクション後は必ず再分析。次の画面を推測しない

---

## References

詳細は以下を参照:
- `references/request-mocking.md` — リクエストモック
- `references/running-code.md` — Playwright コード実行
- `references/session-management.md` — セッション管理
- `references/storage-state.md` — ストレージ状態（Cookie, localStorage）
- `references/test-generation.md` — テスト生成
- `references/tracing.md` — トレース
- `references/video-recording.md` — 動画録画
