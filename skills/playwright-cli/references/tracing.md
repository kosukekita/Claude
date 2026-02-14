# Tracing

## トレースの記録

トレースは実行の詳細データ（ネットワークリクエスト、DOM スナップショット、コンソール出力等）をキャプチャする。デバッグや問題分析に有用。

## 基本的な使い方

```shell
# ブラウザを開く
playwright-cli open https://example.com

# トレース開始
playwright-cli tracing-start

# 操作を実行
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli click e10

# トレース停止（ファイルが保存される）
playwright-cli tracing-stop

# ブラウザを閉じる
playwright-cli close
```

## トレースファイルの閲覧

トレースファイル（`.zip`）は Playwright Trace Viewer で閲覧可能:

```shell
npx playwright show-trace trace.zip
```

## トレース vs ビデオ

| 特性 | トレース | ビデオ |
|------|---------|--------|
| **情報量** | 詳細（DOM, ネットワーク, コンソール） | 画面のみ |
| **ファイルサイズ** | 大きい | 中程度 |
| **デバッグ向き** | 高い | 低い |
| **共有しやすさ** | Trace Viewer 必要 | 動画プレイヤーで再生可 |
| **用途** | 問題の根本原因分析 | 視覚的な動作確認 |

## ベストプラクティス

- 問題が再現しにくい場合、トレースを有効にして操作を記録
- トレースファイルは大きくなるため、必要な操作のみ記録する
- CI/CD でのテスト失敗時にトレースを自動保存すると便利
