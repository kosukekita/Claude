# Video Recording

## 動画キャプチャ

ブラウザ操作の動画を WebM 形式で記録する。

## 基本的な使い方

```shell
# ブラウザを開く
playwright-cli open https://example.com

# 録画開始
playwright-cli video-start

# 操作を実行
playwright-cli goto https://example.com/demo
playwright-cli click e3
playwright-cli fill e5 "test data"
playwright-cli screenshot

# 録画停止（ファイル名を指定）
playwright-cli video-stop recording.webm

# ブラウザを閉じる
playwright-cli close
```

## ヘッドモードでの録画

視覚的な動作を確認しながら録画する場合:

```shell
playwright-cli open https://example.com --headed
playwright-cli video-start
# ... 操作 ...
playwright-cli video-stop demo.webm
playwright-cli close
```

## 用途

- **バグレポート**: 問題の再現手順を動画で記録
- **デモ作成**: 機能のデモンストレーション動画
- **テスト結果の記録**: E2E テストの実行状況を記録
- **ドキュメント**: 操作手順の視覚的な記録
