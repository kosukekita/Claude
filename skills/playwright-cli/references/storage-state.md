# Storage State Management

## ストレージ状態の保存と復元

Cookie、localStorage、sessionStorage を含むブラウザ状態を JSON ファイルに保存・復元できる。

```shell
# 現在の状態を保存
playwright-cli state-save
playwright-cli state-save auth.json

# 保存した状態を復元（ログイン状態の再利用等）
playwright-cli state-load auth.json
```

## Cookie 管理

```shell
# 全 Cookie を一覧
playwright-cli cookie-list

# 特定ドメインの Cookie のみ
playwright-cli cookie-list --domain=example.com

# 特定の Cookie を取得
playwright-cli cookie-get session_id

# Cookie を設定
playwright-cli cookie-set session_id abc123
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure

# Cookie を削除
playwright-cli cookie-delete session_id

# 全 Cookie をクリア
playwright-cli cookie-clear
```

## localStorage 管理

```shell
# 全項目を一覧
playwright-cli localstorage-list

# 値を取得
playwright-cli localstorage-get theme

# 値を設定
playwright-cli localstorage-set theme dark

# 値を削除
playwright-cli localstorage-delete theme

# 全てクリア
playwright-cli localstorage-clear
```

## sessionStorage 管理

```shell
# 全項目を一覧
playwright-cli sessionstorage-list

# 値を取得
playwright-cli sessionstorage-get step

# 値を設定
playwright-cli sessionstorage-set step 3

# 値を削除
playwright-cli sessionstorage-delete step

# 全てクリア
playwright-cli sessionstorage-clear
```

## 典型的なワークフロー: ログイン状態の保存と再利用

```shell
# 1. ログイン
playwright-cli open https://example.com/login --persistent
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3

# 2. 認証状態を保存
playwright-cli state-save auth.json
playwright-cli close

# 3. 後で認証状態を復元して使用
playwright-cli open https://example.com
playwright-cli state-load auth.json
playwright-cli goto https://example.com/dashboard
```
