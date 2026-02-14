# Test Generation

## ブラウザ操作からテストコードを生成

playwright-cli で実行したブラウザ操作を元に、Playwright テストコードを生成できる。

## 基本フロー

```shell
# 1. ブラウザを開いてページに移動
playwright-cli open https://example.com/form

# 2. スナップショットで要素の ref を確認
playwright-cli snapshot

# 3. 操作を実行
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3

# 4. 結果を確認
playwright-cli snapshot
playwright-cli screenshot --filename=result.png
playwright-cli close
```

## セマンティックロケータ

`snapshot` コマンドで取得した ref（e1, e2 等）は、ページのアクセシビリティツリーに基づくセマンティックロケータ。これにより:
- CSS セレクタよりも安定
- ページ構造の変更に強い
- 可読性が高い

## スナップショットの活用

```shell
# デフォルトのスナップショット（標準出力に表示）
playwright-cli snapshot

# ファイルに保存
playwright-cli snapshot --filename=before.yaml

# 操作後に再度スナップショット
playwright-cli click e3
playwright-cli snapshot --filename=after.yaml
```

## テスト作成のベストプラクティス

1. **操作前にスナップショット** — 要素の ref を確認
2. **操作後にスナップショット** — 状態変化を確認
3. **スクリーンショットで視覚確認** — UI の見た目を検証
4. **セッション管理を活用** — 認証状態の再利用
