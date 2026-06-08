---
name: browser-automation
description: >
  Playwright を使ったブラウザ自動化スキル。新規ブラウザを起動して
  E2Eテスト・スクレイピング・フォーム操作・ログイン状態の保存/再利用を行う。
  ネットワークモック・トレース・動画録画にも対応。
  Use when user needs to AUTOMATE a browser from a clean state:
  E2E testing, scraping with a launched browser, multi-step form automation,
  saving/restoring login state, network mocking, tracing, or video recording.
  単に公開URLの本文を読むだけなら標準の WebFetch/WebSearch を使う（このスキルは不要）。
  既に開いているログイン済み Chrome を操作・検査するだけなら chrome-devtools-mcp を使う。
  Trigger phrases: ブラウザ自動化, E2Eテスト, スクレイピング, フォーム入力自動化,
  Webスクレイピング, playwright, ログインテスト, ログイン状態の保存,
  ネットワークモック, トレース, 動画録画, browser automation, web testing,
  login automation, scraping, e2e, playwright-cli.
allowed-tools: Bash(browser-automation:*)
---

# Browser Automation (Playwright)

新規ブラウザインスタンスをクリーンな状態から起動して自動化する。`playwright-cli` で操作する。

## いつこのスキルを使うか

| やりたいこと | 使うもの |
|------|---------|
| 公開ページの本文を読むだけ | **WebFetch / WebSearch（標準）** — このスキル不要 |
| 取得がブロックされる公開ページ | `https://r.jina.ai/<URL>`（CLAUDE.md のフォールバック） |
| 既に開いているログイン済み Chrome を操作・検査 | **chrome-devtools-mcp** — このスキル不要 |
| クリーン起動して E2E テスト・自動化 | **このスキル（Playwright）** |
| ログイン状態を保存して再利用 | **このスキル（state-save / state-load）** |
| ネットワークモック・トレース・動画録画 | **このスキル** |

**このスキルを選ぶとき**: クリーンな状態から自動化したい、CI/CD での E2E テスト、ブラウザ複数同時操作、Firefox/WebKit を含むクロスブラウザ、ログイン状態のファイル保存・再利用。

---

## Workflow

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

### Browser Sessions

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

### Configuration

```shell
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile
playwright-cli open --config=my-config.json
playwright-cli delete-data
```

## Universal Login Flow

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

### ログイン状態の保存・再利用

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

---

## Troubleshooting

### ブラウザが起動しない

```shell
playwright-cli install-browser
playwright-cli kill-all
```

### 要素が見つからない

1. `snapshot` を再実行して最新の ref を取得
2. ページの読み込み完了を待つ
3. iframe 内の要素は別途対応

---

## References

- `references/request-mocking.md` — リクエストモック
- `references/running-code.md` — Playwright コード実行
- `references/session-management.md` — セッション管理
- `references/storage-state.md` — ストレージ状態（Cookie, localStorage）
- `references/test-generation.md` — テスト生成
- `references/tracing.md` — トレース
- `references/video-recording.md` — 動画録画
