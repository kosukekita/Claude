# Browser Session Management

## セッションの基本

各ワークスペースに独自のデーモンプロセスが割り当てられ、クロスプロジェクト干渉を防止する。

## デフォルトセッション

```shell
# ブラウザを起動（インメモリプロファイル）
playwright-cli open https://example.com

# 操作
playwright-cli click e3
playwright-cli screenshot

# ブラウザを閉じる
playwright-cli close
```

## 名前付きセッション

```shell
# セッション "auth" を作成（永続プロファイル付き）
playwright-cli -s=auth open https://example.com --persistent

# セッション "auth" で操作
playwright-cli -s=auth goto https://example.com/dashboard
playwright-cli -s=auth screenshot

# セッション "scraper" を別途作成
playwright-cli -s=scraper open https://other.com

# セッション一覧
playwright-cli list

# 特定セッションを閉じる
playwright-cli -s=auth close

# 全セッションを閉じる
playwright-cli close-all
```

## ブラウザ選択

```shell
playwright-cli open --browser=chrome    # Google Chrome
playwright-cli open --browser=firefox   # Firefox
playwright-cli open --browser=webkit    # WebKit (Safari)
playwright-cli open --browser=msedge    # Microsoft Edge
```

## プロファイル管理

```shell
# インメモリ（デフォルト: クリーンな状態で毎回開始）
playwright-cli open

# 永続プロファイル（Cookie やログイン状態を保持）
playwright-cli open --persistent

# カスタムプロファイルディレクトリ
playwright-cli open --profile=C:\Users\u8792\browser-profiles\myprofile

# プロファイルデータの削除
playwright-cli delete-data
playwright-cli -s=mysession delete-data
```

## 設定ファイル

```shell
# JSON 設定ファイルを指定して起動
playwright-cli open --config=my-config.json
```

## トラブルシューティング

```shell
# 全ブラウザプロセスを強制終了
playwright-cli kill-all
```
