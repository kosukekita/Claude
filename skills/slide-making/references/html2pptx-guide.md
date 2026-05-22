# html2pptx ガイド — HTMLスライドをPowerPointに変換する

**⚠️ 注意: `html2pptx` は PyPI パッケージとして存在しない。**  
ブラウザ経由の Webサービス（html2pptx.app）のみ利用可能。

---

## 利用方法（Webサービス）

https://html2pptx.app でブラウザから変換できる（無料・要ログイン不要）。

1. ブラウザで HTML ファイルを開く
2. html2pptx.app にアクセス
3. HTML をアップロードまたはURLを貼り付けて変換

> **推奨**: Playwright PNG → PowerPoint への PNG 貼付の方が
> デザインの完全保持という観点では確実。
> html2pptx.app はテキスト編集可能な .pptx が欲しい場合に使う。

---

## html2pptx.app vs Playwright PNG 比較

| 観点 | html2pptx.app（Webサービス） | Playwright PNG |
|------|---------------------------|---------------|
| 編集可能性 | テキスト・図形が編集可能 | 画像なので編集不可 |
| 変換精度 | CSS解釈に依存（ズレあり） | ブラウザ表示と完全一致 |
| 推奨用途 | 後で編集したい資料 | デザイン完全保持が必要な資料 |
| 環境依存 | ブラウザのみ（インストール不要） | playwright + chromium が必要 |
