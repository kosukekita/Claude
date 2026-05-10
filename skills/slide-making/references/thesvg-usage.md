# theSVG Icon Usage — slide-making

theSVG（5,600+ ブランドアイコン）の取得・キャッシュ・recolor レシピ。

---

## CDN URL パターン

```
https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/{slug}/{variant}.svg
```

| 変数 | 説明 | 例 |
|------|------|----|
| `{slug}` | アイコン識別名（ハイフン区切り小文字） | `github`, `openai`, `aws-s3` |
| `{variant}` | バリアント種別 | `default`, `mono`, `light`, `dark`, `wordmark` |

manifest（全アイコン一覧）:  
`https://cdn.jsdelivr.net/gh/glincker/thesvg@main/src/data/icons.json`

---

## recolor 可否マトリクス

| カテゴリ | 代表 slug | recolor | 理由 |
|----------|-----------|---------|------|
| 汎用装飾アイコン | `arrow-right`, `check-circle` | ✅ 可 | 商標なし、mono バリアント推奨 |
| OSS ロゴ / 言語 | `python`, `javascript` | ❌ 否推奨 | ブランドガイドライン |
| プラットフォーム | `github`, `slack` | ❌ 否 | ブランドガイドライン |
| クラウドベンダー | `aws`, `azure` | ❌ 否 | ブランドガイドライン |
| AWS Architecture | `aws-architecture-*` | 🚫 禁止 | CC BY-ND（改変禁止） |

---

## `fetch_icon.py` 引数早見

```bash
# ブランドアイコン（原色）
uv run scripts/fetch_icon.py --slug github --variant default

# 汎用装飾アイコン（recolor）
uv run scripts/fetch_icon.py --slug arrow-right --variant mono --recolor

# 出力先を指定
uv run scripts/fetch_icon.py --slug openai --variant default --output ./openai.svg
```

---

## HTML への埋め込み

### パターン A — img タグ（ブランドアイコン・原色保持）

```html
<img src="../cache/icons/github/default.svg" alt="GitHub" class="icon icon-brand">
```

### パターン B — img タグ（テーマカラー適用、mono バリアント）

```html
<img src="../cache/icons/arrow-right/mono.svg" alt="" class="icon icon-theme">
```

### パターン C — SVG インライン（完全な色制御）

```bash
uv run scripts/fetch_icon.py --slug arrow-right --variant mono --recolor --output ./arrow-themed.svg
```

生成した SVG を `<svg>` タグごとペーストし、CSS `color` で色を制御。

---

## よく使う slug

### 汎用装飾（recolor 推奨 / mono バリアント）

| 用途 | slug |
|------|------|
| 右矢印 | `arrow-right` |
| チェック | `check-circle` |
| 警告 | `alert-triangle` |
| 情報 | `info-circle` |
| 禁止 | `x-circle` |
| ユーザー | `user` |
| データ/DB | `database` |
| グラフ | `chart-bar` |
| ドキュメント | `file-text` |

### ブランド / 技術（原色 / default バリアント）

| ブランド | slug |
|---------|------|
| GitHub | `github` |
| Python | `python` |
| OpenAI | `openai` |
| AWS | `aws` |
| Docker | `docker` |
| Slack | `slack` |

---

## ライセンス注意

| 種別 | ライセンス | 注意 |
|------|-----------|------|
| コードベース | MIT | 商用利用可 |
| ブランドアイコン | 各社商標 | ブランドガイドラインに従う |
| AWS Architecture | CC BY-ND 2.0 | **改変禁止** — recolor は ND 違反 |
