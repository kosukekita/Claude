# html2pptx.app ガイド — HTMLスライドをPowerPointに変換する

html2pptx.app は HTML/CSS を **編集可能な .pptx** に変換する REST API サービス。
Playwright PNG 貼付との使い分け:

| 観点 | html2pptx.app（REST API） | Playwright PNG |
|------|--------------------------|----------------|
| 編集可能性 | テキスト・図形が編集可能 | 画像なので編集不可 |
| 変換精度 | CSS 解釈に依存（ズレあり） | ブラウザ表示と完全一致 |
| 推奨用途 | 後で編集したい資料 | デザイン完全保持が必要な資料 |

---

## 前提条件

- **APIキー**: https://html2pptx.app のダッシュボードで発行（`sk_live_xxxx` 形式）
- **環境変数**: `HTML2PPTX_API_KEY=sk_live_xxxx` を設定するか `--api-key` オプションで渡す
- **Free Previewプラン**: 3 RPM / 100 件/日 / 50 スライド/ジョブ（無料）

---

## スクリプトによる変換

`scripts/export_to_pptx.py` を使う（PEP 723 インラインスクリプト、`uv run` で実行）。

```powershell
# 1枚変換
uv run skills/slide-making/scripts/export_to_pptx.py --input slide-01.html --output slide-01.pptx

# バッチ変換（複数スライドを1つの.pptxに）
uv run skills/slide-making/scripts/export_to_pptx.py --input "slides/*.html" --output deck.pptx

# APIキーを直接指定
uv run skills/slide-making/scripts/export_to_pptx.py --input slide-01.html --output slide-01.pptx --api-key sk_live_xxxx
```

---

## REST API リファレンス

### 認証

```
Authorization: Bearer sk_live_xxxx   （推奨）
または
X-API-Key: sk_live_xxxx
```

### Step 1: ジョブ作成

**POST** `https://html2pptx.app/api/export/jobs`

```json
{
  "fileName": "presentation.pptx",
  "html": "<section class=\"slide\" style=\"width:1920px;height:1080px\">...</section>",
  "css": "",
  "autoEmbedFonts": true,
  "width": 13.333,
  "height": 7.5,
  "responseFormat": "url"
}
```

**重要パラメータ:**
- `html`: `.slide` クラスを持つ `<section>` 要素を含む HTML（必須）
- `width` / `height`: PowerPoint スライドサイズ（インチ）。`13.333 × 7.5` = 16:9 標準
- `autoEmbedFonts`: `true` にすると日本語フォント（Noto Sans JP 等）が埋め込まれる
- `responseFormat`: `"url"`（デフォルト）、`"base64"`、`"both"`

**レスポンス:**
```json
{
  "jobId": "5d934729-a0db-4aa9-bc65-e7a3e7e52b32",
  "status": "queued",
  "slideCount": 1
}
```

### Step 2: ジョブステータス確認

**GET** `https://html2pptx.app/api/export/jobs/{jobId}`

ステータス遷移: `queued` → `processing` → `completed` | `failed`

**完了時のレスポンス:**
```json
{
  "jobId": "...",
  "status": "completed",
  "downloadUrl": "https://storage.example.com/..."
}
```

### Step 3: ファイルダウンロード

`downloadUrl` に GET リクエストを送ると `.pptx` バイナリが返る。

---

## HTMLコントラクト（html2pptxが要求する仕様）

```html
<!-- 各スライドは .slide クラスの <section> で囲む -->
<section class="slide" style="width:1920px; height:1080px;">
  <!-- スライドコンテンツ -->
</section>
```

**対応 CSS**: flexbox, grid, gradient, box-shadow, border-radius, transform
**非対応**: script, iframe, form, a タグ / SVG 外部参照 / 相対パス画像
**画像**: 絶対 URL（`https://...`）または base64 データ URI を使う

> **サイズの扱い**: slide-base.html は `1920×1080px` 固定だが、API の `width=13.333, height=7.5` を指定することで PowerPoint 側のスライドサイズ（インチ）が 16:9 に正規化される。HTML の px 値はそのまま渡してよい。

---

## エラーコード

| コード | 説明 | 対処 |
|------|------|------|
| 401 | APIキー未設定または無効 | `HTML2PPTX_API_KEY` を確認 |
| 422 | スライド数超過 | プランのスライド上限を確認 |
| 429 | レート制限超過 | `Retry-After` ヘッダーの秒数待機 |
| 502/503 | サーバー側エラー | 数秒後にリトライ |
