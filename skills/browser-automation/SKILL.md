---
name: browser-automation
description: >
  ブラウザ自動化の統合スキル。2つのモードを提供:
  (1) Playwright モード — 新規ブラウザを起動してE2Eテスト・スクレイピング・フォーム操作、
  (2) Chrome CDP モード — ライブChromeセッションに接続してデバッグ・既存ログイン活用。
  Use when user needs browser automation, web testing, form filling, screenshots,
  data extraction, login automation, live Chrome debugging, or page inspection.
  Trigger phrases: ブラウザ自動化, E2Eテスト, スクリーンショット, フォーム入力,
  Webスクレイピング, playwright, ブラウザ操作, ログインテスト, 画面キャプチャ,
  ログイン自動化, SSO, MFA, browser automation, web testing, login automation,
  Chrome操作, ライブブラウザ, CDP, DevTools, 開いているページ, タブ操作,
  live Chrome, inspect page, debug page.
allowed-tools: Bash(browser-automation:*)
---

# Browser Automation

## モード選択ガイド

| 観点 | Playwright モード | Chrome CDP モード |
|------|------------------|------------------|
| **用途** | E2Eテスト、スクレイピング、自動化 | ライブブラウザ操作、デバッグ |
| **ブラウザ** | 新規インスタンス起動 | 既に開いているChromeに接続 |
| **ログイン** | state-save/load で管理 | 既存セッションをそのまま利用 |
| **コマンド** | `playwright-cli ...` | `node scripts/cdp.mjs ...` |
| **Node.js 22+** | 不要 | 必要 |

**Playwright モードを選ぶとき**: クリーンな状態から自動化したい、CI/CD での E2E テスト、ブラウザ複数同時操作
**CDP モードを選ぶとき**: 既にログイン済みのページを操作したい、開いているタブを直接検査・操作したい、既存セッションを利用したい

---

## Playwright モード

### Workflow

ブラウザ自動化タスクを受けたら、以下のステップで進める:

| タスク種別 | 内容 | 主要コマンド |
|-----------|------|-------------|
| **ページ確認** | スクリーンショット、要素確認 | `open`, `goto`, `snapshot`, `screenshot` |
| **フォーム操作** | 入力、クリック、送信 | `fill`, `click`, `type`, `select` |
| **認証テスト** | ログイン状態の保存・復元 | `state-save`, `state-load` |
| **データ抽出** | ページ内容の取得 | `eval`, `snapshot` |
| **デバッグ** | コンソール、ネットワーク監視 | `console`, `network`, `tracing-start` |

### Quick Start

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

### Commands

#### Core

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

#### Navigation

```shell
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

#### Keyboard

```shell
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

#### Mouse

```shell
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
```

#### Save as

```shell
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli pdf --filename=page.pdf
```

#### Tabs

```shell
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

#### Storage

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

#### Network

```shell
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

#### DevTools

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

#### Browser Sessions

```shell
# 名前付きセッション
playwright-cli -s=mysession open example.com --persistent
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close

# セッション管理
playwright-cli list
playwright-cli close-all
playwright-cli kill-all
```

#### Configuration

```shell
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile
playwright-cli open --config=my-config.json
playwright-cli delete-data
```

### Universal Login Flow

> Source: [login-machine](https://github.com/RichardHruby/login-machine)

| タイプ | 内容 | 処理方法 |
|--------|------|----------|
| `credential_login_form` | メール/パスワード/OTP | フォーム表示 → ユーザー入力 → DOM に送信 |
| `choice_screen` | アカウント選択、SSO | ボタン表示 → ユーザー選択 → クリック |
| `magic_login_link` | 「メールを確認」画面 | URL 入力 → ユーザーがリンク貼付 → 移動 |
| `loading_screen` | スピナー、リダイレクト | 自動待機 → 再分析（最大12回） |
| `blocked_screen` | Cookie バナー、ポップアップ | 自動解除 → 再分析 |
| `logged_in_screen` | ダッシュボード、ホーム | 完了状態 |

```shell
# ログインフロー例
playwright-cli open https://example.com/login
playwright-cli snapshot                        # credential_login_form
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot                        # ログイン後の状態確認
playwright-cli state-save auth.json
playwright-cli close
```

---

## Chrome CDP モード

### Prerequisites

1. Chrome でリモートデバッグを有効化: `chrome://inspect/#remote-debugging` → スイッチをオン
2. Node.js 22+ がインストール済みであること
3. スクリプトパス: `~/.claude/skills/browser-automation/scripts/cdp.mjs`

### Quick Start

```bash
# 開いているページを一覧表示
node ~/.claude/skills/browser-automation/scripts/cdp.mjs list

# 出力例:
# 6BE827FA  https://example.com  Example Domain
# A3F2910B  https://github.com   GitHub

# スクリーンショット（<target> は list で確認した一意プレフィックス）
node ~/.claude/skills/browser-automation/scripts/cdp.mjs shot 6BE827FA

# アクセシビリティツリー確認
node ~/.claude/skills/browser-automation/scripts/cdp.mjs snap 6BE827FA --compact

# JavaScript 評価
node ~/.claude/skills/browser-automation/scripts/cdp.mjs eval 6BE827FA "document.title"
```

### Commands

```bash
scripts/cdp.mjs list                           # 開いているページ一覧
scripts/cdp.mjs shot <target> [file]           # スクリーンショット
scripts/cdp.mjs snap <target> [--compact]      # アクセシビリティツリー
scripts/cdp.mjs eval <target> <expr>           # JavaScript 評価
scripts/cdp.mjs html <target> [selector]       # HTML 取得
scripts/cdp.mjs nav  <target> <url>            # ナビゲーション
scripts/cdp.mjs net  <target>                  # リソースタイミング
scripts/cdp.mjs click   <target> <selector>    # CSS セレクタでクリック
scripts/cdp.mjs clickxy <target> <x> <y>       # 座標クリック（CSS px）
scripts/cdp.mjs type    <target> <text>        # テキスト入力（クロスオリジン対応）
scripts/cdp.mjs loadall <target> <sel> [ms]    # 「もっと読む」繰り返しクリック
scripts/cdp.mjs evalraw <target> <method> [json] # 生 CDP コマンド
scripts/cdp.mjs open [url]                     # 新しいタブを開く
scripts/cdp.mjs stop [target]                  # デーモン停止
```

### Coordinates

`shot` はネイティブ解像度で保存: **画像px = CSS px × DPR**

`clickxy` は **CSS ピクセル** で指定:
```
CSS px = スクリーンショット画像px ÷ DPR
```

`shot` 実行時に DPR が出力される。Retina (DPR=2) の場合は座標を 2 で割る。

### Tips

- ページ構造の確認: `snap --compact` を優先（`html` より高速）
- クロスオリジン iframe: `click`/`clickxy` でフォーカス後 `type`（`eval` 経由の入力は不可）
- フォールド下: `eval` でスクロール後に `shot`
- デーモンは 20 分間のアイドル後に自動終了

---

## Examples

### Playwright: フォーム送信

```shell
playwright-cli open https://example.com/form
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

### Playwright: ログイン状態の保存・再利用

```shell
# ログインして保存
playwright-cli open https://example.com/login --persistent
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password"
playwright-cli click e3
playwright-cli state-save auth.json
playwright-cli close

# 後で再利用
playwright-cli open https://example.com
playwright-cli state-load auth.json
playwright-cli goto https://example.com/dashboard
```

### CDP: 開いているページのスクリーンショット

```bash
node scripts/cdp.mjs list
# → A3F2910B  https://github.com   GitHub

node scripts/cdp.mjs shot A3F2910B github.png
```

### CDP: フォームに入力して送信

```bash
node scripts/cdp.mjs list
# → 6BE827FA  https://example.com/form  Form Page

node scripts/cdp.mjs snap 6BE827FA --compact
node scripts/cdp.mjs click  6BE827FA "input[name='email']"
node scripts/cdp.mjs type   6BE827FA "user@example.com"
node scripts/cdp.mjs click  6BE827FA "button[type='submit']"
node scripts/cdp.mjs shot   6BE827FA result.png
```

---

## Troubleshooting

### Playwright: ブラウザが起動しない

```shell
playwright-cli install-browser
playwright-cli kill-all
```

### Playwright: 要素が見つからない

1. `snapshot` を再実行して最新の ref を取得
2. ページの読み込み完了を待つ
3. iframe 内の要素は別途対応

### CDP: Chrome に接続できない

1. `chrome://inspect/#remote-debugging` でリモートデバッグが有効か確認
2. `node scripts/cdp.mjs list` でページが表示されるか確認
3. `DevToolsActivePort` が非標準パスの場合: `CDP_PORT_FILE=/path/to/DevToolsActivePort node scripts/cdp.mjs list`

### CDP: 「デバッグを許可」モーダルが表示される

初回接続時のみ表示される。手動で「許可」をクリックすると、以降はデーモンが接続を維持するため再表示されない。

---

## References

- `references/chrome-cdp.md` — CDP モード詳細リファレンス
- `references/request-mocking.md` — リクエストモック
- `references/running-code.md` — Playwright コード実行
- `references/session-management.md` — セッション管理
- `references/storage-state.md` — ストレージ状態（Cookie, localStorage）
- `references/test-generation.md` — テスト生成
- `references/tracing.md` — トレース
- `references/video-recording.md` — 動画録画
