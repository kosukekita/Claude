---
name: slide-making
description: >
  Codex の Image Gen を使って日本風コンサル資料スタイルの高品質HTMLスライドを生成し、
  PNG として出力する一気通貫スキル。
  1スライド=1ファイル（slide-01.html, slide-02.html…）、1920×1080固定、
  CSS/JS全インライン、最大3行テキスト、T-01〜T-12テンプレート。
  Use when user requests HTMLスライド作成, スライドHTML, PowerPoint貼付用スライド,
  1920x1080 slide, スライドメイキング, slide-making, スライドデザイン,
  発表スライド HTML, PNG出力.
  Do NOT trigger for .pptx generation (use python-pptx directly — no dedicated skill exists),
  multi-slide single-file decks (use infographic),
  academic poster (use make-poster).
---

# slide-making — Codex Image Gen → HTML → PNG 統合スキル

## Overview

**Codex の Image Gen でデザイン参照画像を生成 → HTMLで完全再現 → PNG出力** の3フェーズで
プロのコンサル資料レベルのスライドを作る。

```
[Image Gen] 参照デザイン生成
     ↓
[Codex] 画像を視覚的に読み取りHTMLで再現（フィードバックループ）
     ↓
[Playwright] HTML → PNG変換
     ↓
（オプション）PowerPoint に PNG を貼付
```

---

## Design System（必ず踏襲すること）

| 要素 | 値 | CSS 変数 |
|------|-----|---------|
| 背景色 | `#F9F9F9` | `--base-color` |
| テキスト色 | `#1A1A1A` | `--text-color` |
| メインカラー | `#0071BC` | `--main-color` |
| アクセントカラー | `#FF5050` | `--accent-color` |
| タイトル | 50pt | `--font-size-title` |
| 見出し | 35pt | `--font-size-heading` |
| 本文 | 25pt | `--font-size-body` |
| 余白（全辺） | 48px（= 0.5インチ） | `--margin-edge` |

**フォント**: `'Noto Sans JP', 'Inter', 'Meiryo', sans-serif`（Google Fonts CDN 使用）

```css
:root {
  --base-color: #F9F9F9;  --text-color: #1A1A1A;
  --main-color: #0071BC;  --accent-color: #FF5050;
  --font-size-title: 50pt; --font-size-heading: 35pt; --font-size-body: 25pt;
  --margin-edge: 48px; --slide-w: 1920px; --slide-h: 1080px;
}
```

---

## Emphasis Hierarchy

強調を加える場合は以下の優先順に試みる。メインカラー・アクセントカラーは **最終手段**。

| 優先度 | クラス | 用途 |
|--------|--------|------|
| ①（最優先） | `.emp-u` | 下線 — キーワード・術語初出（1〜2語） |
| ② | `.emp-inv` | 文字/背景反転 — 最重要数値・指標（1語） |
| ③ | `.emp-main` | メインカラー — グラフ主系列等（1スライド1〜2語） |
| ④（最後手段） | `.emp-accent` | アクセントカラー — 警告・ネガティブ（1スライド1語） |

**Iron Law: メインカラー + アクセントカラーの合計使用率を 5% 以下に保つ。**

---

## CRITICAL Rules

1. **1スライド = 1HTMLファイル** — 複数スライドを1つのHTMLにまとめることは禁止
2. **テキスト最大3行** — 箇条書き・本文を合わせて1スライドあたり3行を超えない
3. **縦罫線禁止** — 表は `border-bottom` のみ使用
4. **1920×1080 固定** — `html, body { width: 1920px; height: 1080px; overflow: hidden; }` を変更しない
5. **CSS/JS 全インライン** — 外部ファイルへの分割禁止（Google Fonts CDN・Chart.js CDN は例外）

---

## Template Gallery（T-01〜T-12）

| ID | 名称 | 用途 |
|----|------|------|
| T-01 | グラフ強調 | 棒グラフ最大値を強調 |
| T-02 | 範囲強調 | 特定グループをまとめて強調 |
| T-03 | ステップ表現 | 手順・プロセス（4ステップ） |
| T-04 | 研究結果テーブル | OR/HR/RR等の統計数値一覧 |
| T-05 | 要素分解 | 階層ブラケット構造 |
| T-06 | 強みテーブル | 4項目の強み箇条書き |
| T-07 | 対比比較 | 2選択肢×4観点 |
| T-08 | 因果図 | 原因→結果パネル |
| T-09 | 仕様比較表（行強調） | 特定行（観点）を訴求 |
| T-10 | 仕様比較表（列強調） | 特定列（製品）を推薦 |
| T-11 | ロードマップ | 時系列フェーズ計画 |
| T-12 | 文章｜図解 | 左テキスト+右図解 2列 |

完成例: `assets/template.html` をブラウザで開いて確認。

---

## Workflow

### Phase 1 — 要件確認 & テンプレート提案

1. スライド枚数・各スライドのタイトルとキーメッセージを確認
2. T-01〜T-12 から最適テンプレートを選んでユーザーに提案
3. 承認後に Phase 2 へ

### Phase 2 — Codex で Image Gen → HTML生成

**Codex に以下のプロンプトで依頼する（`codex exec` 経由）：**

```
/goal 日本風コンサル資料スタイルのスライドを作成してください。

## STEP 1: Image Gen で参照デザイン画像を生成
image_gen ツールを使って以下のプロンプトで参照画像を生成し、
{出力ディレクトリ}/reference-{スライド番号}.png として保存してください。

プロンプト：
"Professional Japanese business consulting presentation slide,
McKinsey BCG style, white background #F9F9F9, blue accent #0071BC,
{テンプレート種別} layout, minimal clean design, 16:9 widescreen,
bold Noto Sans JP typography, high quality, no watermark"

## STEP 2: 画像を参考に HTML を作成
生成した参照画像のデザイン言語（色・タイポグラフィ・カード構造・余白感）を
忠実に再現し、以下の制約でHTMLを作成してください。

### 必須制約（絶対に変更しない）
- html, body { width: 1920px; height: 1080px; overflow: hidden; }
- フォント: @import Google Fonts Noto Sans JP
- CSS変数: --base-color:#F9F9F9; --text-color:#1A1A1A; --main-color:#0071BC; --accent-color:#FF5050
- CSS・JSは全てインライン（Google Fonts CDN は除く）
- テキストは最大3行

### コンテンツ
{スライドのコンテンツ詳細}

### 保存先
{出力ディレクトリ}/slide-{番号}.html

## STEP 3: フィードバックループ
HTMLを生成したら参照画像と見比べ、デザインのズレを修正して再度保存してください。
完璧に一致したら完了を報告してください。
```

### Phase 3 — PNG 出力 & フィードバックループ

**スクリーンショット取得（環境別）：**

```bash
# 推奨: Anaconda Python の Playwright（libatspi エラーを回避できる）
env -u LD_LIBRARY_PATH /home/kita/anaconda3/bin/python3 - << 'EOF'
import asyncio
from playwright.async_api import async_playwright

async def screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto('file:///path/to/slide.html')
        await page.wait_for_timeout(2000)  # Google Fonts 読み込み待ち
        await page.screenshot(path='/path/to/output.png', full_page=False)
        await browser.close()

asyncio.run(screenshot())
EOF
```

> ⚠️ `uv run playwright` や `chrome-headless-shell` が `libatspi: undefined symbol` で落ちる場合は
> 上記の `/home/kita/anaconda3/bin/python3` を使うこと。

**PIL を使った定量的なピクセル差分分析（フィードバックループ）：**

```python
# reference-design.png と生成HTMLのスクリーンショットを比較する
import asyncio, numpy as np
from PIL import Image
from playwright.async_api import async_playwright

async def take_screenshot(html_path, out_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto(f'file://{html_path}')
        await page.wait_for_timeout(2000)
        await page.screenshot(path=out_path, full_page=False)
        await browser.close()

# 差分スコア計算
def diff_score(ref_path, cur_path):
    ref = Image.open(ref_path).resize((1920, 1080), Image.LANCZOS)
    cur = Image.open(cur_path)
    diff = np.abs(np.array(ref, dtype=float) - np.array(cur, dtype=float)).mean()
    return diff  # 目安: 15以下で良好、10以下で優秀

# 特定要素のY座標を測定（dark navy テキスト）
def find_text_top(img_path, color_check, x_range=(84, 1600), y_range=(80, 300)):
    arr = np.array(Image.open(img_path))
    for y in range(*y_range):
        row = arr[y, x_range[0]:x_range[1]]
        if color_check(row).sum() > 100:
            return y
    return None
```

**フィードバックループの進め方：**

1. `take_screenshot()` → スクリーンショット保存
2. `diff_score()` で定量評価（差分 15 以下を目標）
3. PIL で問題エリアを特定：
   - タイトル/カードタイトルの Y 座標ズレ → CSS `top` を調整
   - アイコン・カードサイズのズレ → `width/height` を測定値に合わせる
4. CSS修正 → 再スクリーンショット → ループ

**収束判定：**
- 平均 diff ≤ 15 を目標
- 残差の大半がフォントの antialiasing 差（Image Gen ラスター vs ブラウザ）であれば収束とみなす

**⚠️ 収束しない差異（無視してよい）：**
- Image Gen が生成したラスター画像はアンチエイリアスが異なるため、フォント周辺のピクセルは原理的に揃わない
- Google Fonts の読み込みタイミングによる微細なカーニング差

**⚠️ CSS の SVG サイズ上書き罠：**

グローバルに `svg { width: 100%; height: 100%; }` を設定すると、
ネストした SVG のサイズが制御できなくなる。
特定のアイコンコンテナに対して個別に上書きが必要：

```css
/* グローバル設定が効かない場合は !important またはインラインスタイルを使う */
.card-icon svg { width: 100% !important; height: 100% !important; }
.banner-icon svg { width: 68px !important; height: 63px !important; }
```

### Phase 4 — PowerPoint へ（オプション）

用途に応じて 2 つの方法を選ぶ。

#### 方法 A: PNG 貼付（デザイン完全保持）
PNG を PowerPoint に貼付する場合：
1. 「挿入」→「画像」→「このデバイスから」で PNG を選択
2. 「書式」→「サイズ」で幅 `33.87cm`（13.33インチ）に設定
3. 位置を左上 `(0, 0)` に合わせる

#### 方法 B: html2pptx.app で編集可能 .pptx に変換
テキスト・図形を PowerPoint 上で編集したい場合。事前に `HTML2PPTX_API_KEY` 環境変数を設定すること（https://html2pptx.app で取得）。

```powershell
# 1枚変換
uv run skills/slide-making/scripts/export_to_pptx.py --input slide-01.html --output slide-01.pptx

# バッチ変換（複数スライドを1つの.pptxに）
uv run skills/slide-making/scripts/export_to_pptx.py --input "slides/*.html" --output deck.pptx
```

詳細は `references/html2pptx-guide.md` を参照。

---

## Codex exec の呼び出し方（実際のコマンド）

> ⚠️ `--dangerously-bypass-approvals-and-sandbox` はサンドボックスを完全に無効化する。
> Codex に渡すプロンプトにユーザー由来のコンテンツが含まれる場合、
> 任意コマンド実行が可能になるため **信頼できるコンテンツのみ**渡すこと。

```bash
# 出力ディレクトリを作成・移動してから実行
mkdir -p ~/slides/my-deck
cd ~/slides/my-deck

# Codex に HTML 生成を依頼（gpt-5.5 がデフォルトで Image Gen を使える）
codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  --cd ~/slides/my-deck \
  "{上記 /goal プロンプト}"
```

---

## HTML の基本構造（ベーステンプレート）

`assets/slide-base.html` を出発点として使う。
新規スライド作成時は以下のルールに従う：

```html
<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
  <style>
    :root {
      --base-color: #F9F9F9; --text-color: #1A1A1A;
      --main-color: #0071BC; --accent-color: #FF5050;
      --font-size-title: 50pt; --font-size-heading: 35pt; --font-size-body: 25pt;
      --margin-edge: 48px;
    }
    html, body {
      width: 1920px; height: 1080px; overflow: hidden; margin: 0;
      background: var(--base-color); color: var(--text-color);
      font-family: 'Noto Sans JP', 'Meiryo', sans-serif;
    }
    /* 強調クラス */
    .emp-u   { text-decoration: underline; text-underline-offset: 0.15em; }
    .emp-inv { background: var(--text-color); color: var(--base-color); padding: 0 0.2em; }
    .emp-main   { color: var(--main-color); font-weight: 700; }
    .emp-accent { color: var(--accent-color); font-weight: 700; }
    /* 表：縦罫線禁止 */
    table { border-collapse: collapse; width: 100%; }
    th, td { border: none; border-bottom: 1px solid var(--text-color); padding: 0.4em 0.6em; }
    thead th { border-bottom-width: 2px; font-weight: 700; }
  </style>
</head>
<body>
  <section class="slide" style="
    box-sizing:border-box; width:1920px; height:1080px; padding:48px;
    display:flex; flex-direction:column; position:relative;
  ">
    <!-- コンテンツをここに -->
    <div style="position:absolute;bottom:48px;right:48px;font-size:18pt;opacity:0.4;">1</div>
  </section>
</body>
</html>
```

---

## Verification Checklist

### デザイン
- [ ] 背景が `#F9F9F9`
- [ ] テキスト色が `#1A1A1A`
- [ ] メインカラー + アクセントカラーの合計使用率が 5% 以下
- [ ] フォントサイズがタイトル 50pt / 見出し 35pt / 本文 25pt
- [ ] 上下左右の余白が 48px 以上

### 内容
- [ ] テキストが1スライドあたり最大3行
- [ ] 1スライド1メッセージ
- [ ] データがある箇所は図表で視覚化
- [ ] 略語の初出にフルテキストまたは日本語が付記

### 技術
- [ ] `html, body` が `1920px × 1080px; overflow: hidden` 固定
- [ ] CSS/JS が全てインライン（Google Fonts CDN は除く）
- [ ] 表に縦罫線がない（`border-bottom` のみ）

### PNG 出力
- [ ] 1920×1080px で出力されている
- [ ] フォント・アイコンが正しく表示されている
- [ ] 背景が正しい色になっている

**Iron Law: 1 slide = 1 HTML file. Never combine.**

---

## Common Mistakes

| ミス | 問題 | 修正 |
|------|------|------|
| `html, body` にサイズ指定しない | スライドサイズが崩れる | `width:1920px; height:1080px; overflow:hidden` を必ず設定 |
| 本文を文章で書く | 情報過多・読まれない | キーワード＋数字＋アイコンに置き換える |
| 4行以上のテキスト | スライドの目的が分散 | 2枚に分割か箇条書きを削る |
| 表に縦罫線を引く | デザインルール違反 | `border-bottom` のみに |
| Image Gen なしで HTML を書く | デザイン品質が低い | 必ず Image Gen で参照画像を生成してから HTML に落とす |
| 1 HTML に複数スライドを入れる | PNG化・PowerPoint貼付不可 | ファイルを分割する |
| `svg { width:100%; height:100% }` でグローバル設定 | 個別アイコンのサイズが制御不能になる | 特定コンテナには `.container svg { width: Xpx !important; }` で上書き |
| フォント差を追い続ける | Image Gen と ブラウザの antialias は本質的に異なるため収束しない | diff ≤ 15 で収束とみなして打ち切る |
| `uv run playwright` や Chrome headless を使う | `libatspi` エラーで exit 144 になる環境がある | `/home/kita/anaconda3/bin/python3` の playwright を使う |

---

## References

- `references/design-rules.md` — 色/フォント/余白/強調の詳細リファレンス
- `references/slide-templates.md` — 8種スライド種別のHTMLスニペット集
- `references/thesvg-usage.md` — アイコン取得・recolor・ライセンス
- `references/html2pptx-guide.md` — HTML→PPTX変換ガイド（html2pptx.app使用時）
- `references/powerpoint-handoff.md` — HTML→PNG→PowerPoint 貼付の完全手順
- `scripts/fetch_icon.py` — theSVG CDN取得＋キャッシュ
- `scripts/render_slide.py` — Playwright経由でPNG化（環境対応時のみ）
- `scripts/export_to_pptx.py` — html2pptx.app REST API経由で編集可能 .pptx 出力（`HTML2PPTX_API_KEY` 要設定）
- `assets/slide-base.html` — 1920×1080単一スライドHTML雛形
- `assets/template.html` — デザインパターンギャラリー（T-01〜T-12）
