---
name: slide-making
description: >
  1スライド=1HTMLファイル（slide-01.html…）で1920×1080の発表スライドを作成するスキル。
  Codex の Image Gen で参照画像を生成し、Claude Code が HTML を書いて目視で完全一致するまで
  フィードバックループで修正する。CSS/JS全インライン、最大3行テキスト、T-01〜T-12テンプレート。
  Use when user requests HTMLスライド作成, スライドHTML, PowerPoint貼付用スライド,
  1920x1080 slide, スライドメイキング, slide-making, スライドデザイン, 発表スライド HTML, PNG出力.
  複数スライドも可（各スライドを個別HTMLにする場合のみ）。
  Do NOT trigger for: .pptx直接生成（python-pptx等）, 複数スライドを1HTMLにまとめるデッキ（use infographic）,
  academic poster（use make-poster）.
---

# slide-making

## Overview

**役割分担：**

| フェーズ | 担当 | 内容 |
|----------|------|------|
| Phase 1 | Claude Code | 要件確認・テンプレート提案 |
| Phase 2 | Codex | Image Gen で参照画像を生成するだけ |
| Phase 3 | Claude Code | HTML 生成 → Playwright スクリーンショット → 目視確認 → CSS 修正ループ |
| Phase 4 | Claude Code | PPTX 変換・PNG 貼付（オプション） |

**Codex の使用箇所は3か所のみ：**
1. Phase 2 — Image Gen で参照画像を生成
2. Phase 3 Codex フォールバック — 3回連続で改善なしの場合
3. HTML 完成後の `/codex-review` — コード品質チェック

**成果物ディレクトリ構造（例）：**

```
slides/my-deck/
├── reference-01.png   # Codex Image Gen で生成した参照画像
├── slide-01.html      # Claude Code が作成した最終 HTML
├── screenshot-01.png  # Playwright スクリーンショット（確認用）
├── slide-01.pptx      # html2pptx.app 変換後（方法B時）
└── pptx-slide-1.png   # PPTX→PNG 変換済み（方法B検証時）
```

---

## CRITICAL Rules

**以下は絶対ルール。1つでも違反したら出力前に修正する。**

1. **1スライド = 1HTMLファイル** — 複数スライドを1つのHTMLにまとめることは禁止
2. **テキスト最大3行** — 箇条書き・本文を合わせて1スライドあたり3行を超えない
3. **縦罫線禁止** — 表は `border-bottom` のみ使用
4. **1920×1080 固定** — `html, body { width: 1920px; height: 1080px; overflow: hidden; }` を変更しない
5. **CSS/JS 全インライン** — 外部ファイルへの分割禁止（Google Fonts CDN・Chart.js CDN は例外）

---

## Design System

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

**フォント**: `'Noto Sans JP', 'Meiryo', sans-serif`（Google Fonts CDN 使用）

詳細は `references/design-rules.md` を参照。

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
HTMLスニペット: `references/slide-templates.md` を参照。

---

## Workflow

### Phase 1 — 要件確認 & テンプレート提案（Claude Code）

1. スライド枚数・各スライドのタイトルとキーメッセージを確認
2. 出力ディレクトリを決定（例: `~/slides/my-deck/`）
3. T-01〜T-12 から最適テンプレートを選んでユーザーに提案・承認を得る
4. 承認後に Phase 2 へ

**ユーザー確認ポイント：** テンプレート選定後・最終PNG/PPTX完成後の2回。

---

### Phase 2 — Codex で Image Gen（参照画像生成のみ）

**Codex の役割はここだけ。HTML は書かせない。参照画像はレイアウト・雰囲気用であり、最終テキストは HTML 側で正確に再現する。**

```bash
codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  --cd "{出力ディレクトリ}" \
  "/goal 参照デザイン画像を image_gen で生成してください。

## タスク
image_gen ツールを使って以下のプロンプトで画像を生成し、
reference-{スライド番号}.png として {出力ディレクトリ} に保存してください。

プロンプト:
'Professional Japanese business consulting presentation slide,
McKinsey BCG style, white background #F9F9F9, blue accent #0071BC,
{テンプレート種別: 例 4-step process flow / bar chart / comparison table} layout,
minimal clean design, 16:9 widescreen 1920x1080,
bold Noto Sans JP typography, high quality, no watermark,
{コンテンツの補足: 例 Step 1: 現状分析, Step 2: PoC設計...}'

## 完了条件
- reference-{番号}.png が {出力ディレクトリ} に存在すること
- ファイルサイズを報告すること
- HTML は作成しないこと"
```

> ⚠️ `--dangerously-bypass-approvals-and-sandbox` はサンドボックスを完全に無効化する。
> ユーザー由来のコンテンツをプロンプトに含める場合は **信頼できるコンテンツのみ**渡すこと。

---

### Phase 3 — HTML生成 + 視覚的フィードバックループ（Claude Code が全て担当）

**このフェーズは Claude Code が自律的に実行する。Codex は3連続失敗時のフォールバックのみ。**

#### Step 3-1: HTML 初版作成

`assets/slide-base.html` を基に、参照画像のデザイン言語（色・レイアウト・余白・カード構造）を
忠実に再現した HTML を `{出力ディレクトリ}/slide-{番号}.html` として作成する。

#### Step 3-2: Playwright でスクリーンショット取得

```python
# uv run --with playwright python - で実行
import asyncio
from playwright.async_api import async_playwright

async def screenshot(html_path: str, out_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto(f'file:///{html_path}')
        await page.wait_for_timeout(2500)  # Google Fonts 読み込み待ち
        await page.screenshot(path=out_path, full_page=False)
        await browser.close()

asyncio.run(screenshot('{html_path}', '{out_path}'))
```

Windows では `file:///C:/...` 形式でパスを渡すこと。

#### Step 3-3: 視覚的フィードバックループ（全項目 PASS になるまで繰り返す）

**判定は目視のみ。**

スクリーンショットと参照画像を Read ツールで並べて表示し、以下を1項目ずつ確認する：

各ループの終わりに以下の PASS/FAIL 表を必ず記録する。
**1項目でも FAIL があれば次フェーズに進んではならない。**

| 項目 | 判定 | 差異の具体的記述 |
|------|------|-----------------|
| アイコン①種類・形・太さ | PASS/FAIL | |
| アイコン②種類・形・太さ | PASS/FAIL | |
| アイコン③種類・形・太さ | PASS/FAIL | |
| アイコン④種類・形・太さ | PASS/FAIL | |
| テキスト・改行位置 | PASS/FAIL | |
| 番号バッジ | PASS/FAIL | |
| カード幅・高さ・余白 | PASS/FAIL | |
| 矢印形状 | PASS/FAIL | |
| 全体縦位置 | PASS/FAIL | |

**禁止事項：**
- 「ほぼ一致」「十分近い」「雰囲気は合っている」という理由での完了宣言
- チェックリストを記録せずに完了と判断する

**修正サイクル：**
1. PASS/FAIL 表を記録する（全項目）
2. FAIL 項目を1つ選んで修正する
3. Playwright で再スクリーンショット
4. 再度目視確認 → 改善していなければ **必ず revert** して別のアプローチを試みる
5. 全項目 PASS になるまで繰り返す

**目視で一致とみなしてよい差異（許容）：**
- フォント周辺の微細なアンチエイリアス差（Image Gen ラスター vs ブラウザレンダリング）
- Google Fonts のカーニング差による1〜2px程度のテキスト位置ズレ

**注意 — CSS の SVG サイズ上書き罠：**
```css
/* グローバルに svg { width:100%; } を設定するとアイコンサイズが制御不能になる */
.card-icon svg { width: 80px !important; height: 80px !important; }
```

**Codexフォールバック（3修正連続で改善なし時）：**
```
/goal 参照画像（reference-01.png）とスクリーンショット（screenshot-01.png）を見比べて、
HTMLを参照画像に完全一致させてください。
現在の差異: {具体的な差異のリスト}
修正後はPlaywrightでスクリーンショットを撮り、目視で確認してください。
```

#### Step 3-4: アイコンが3回修正しても改善しない場合 — リファレンスPNGクロップ方式

SVGで複雑なアイコンを再現しようとすると形状・太さが必ず乖離する。これは原理的な限界。

**解決策：リファレンスPNGからアイコン領域を直接クロップして base64 埋め込みする。**

詳細手順・コードは `references/png-crop-icon.md` を参照。

要点：
- クロップ座標は PIL で `ref.size` 確認後、目視で推定
- 白余白は `trim_whitespace()` で除去してからbase64化
- HTML は Python f-string で全体再構築（正規表現置換は禁止）
- クロップ画像を確認用に保存してから埋め込む

#### Step 3-5: HTML完成後の codex-review

視覚的フィードバックループで収束したら、生成した HTML のコード品質を `/codex-review` でチェックする。

```bash
# 出力ディレクトリで実行
cd /path/to/output-dir
codex --dangerously-bypass-approvals-and-sandbox review "slide-01.html をレビューしてください：
- インラインSVGアイコンがPPTX変換時に消えるリスクがないか
- CSS変数（--main-color等）の使い方に問題がないか
- 1920×1080固定・overflow:hidden が守られているか
- グローバルな svg { width/height } でアイコンサイズが壊れるリスクがないか
- PPTX変換を想定した場合の改善点
日本語で回答してください。"
```

CRITICAL/WARNING が出た場合は修正してから次フェーズへ進む。

---

### Phase 4 — PPTX 変換（オプション）

#### 方法 A: PNG 貼付（デザイン完全保持）

PNG を PowerPoint に貼付する場合：
1. 「挿入」→「画像」→「このデバイスから」で PNG を選択
2. 「書式」→「サイズ」で幅 `33.87cm`（13.33インチ）に設定
3. 位置を左上 `(0, 0)` に合わせる

#### 方法 B: html2pptx.app で編集可能 .pptx に変換

`HTML2PPTX_API_KEY` は `~/.claude/settings.local.json` の `env` ブロックに設定済み。
Bash ツールからは直接参照できないため、以下で取得すること：

```bash
API_KEY=$(python -c "import json; d=json.load(open('C:/Users/u8792/.claude/settings.local.json')); print(d['env']['HTML2PPTX_API_KEY'])")
uv run --with httpx skills/slide-making/scripts/export_to_pptx.py \
  --input slide-01.html --output slide-01.pptx --api-key "$API_KEY"
```

> ⚠️ export_to_pptx.py の `client.stream()` が 400 エラーになる場合は、
> ジョブが返す `downloadUrl` を `curl -o output.pptx` で直接ダウンロードすること。

詳細は `references/html2pptx-guide.md` を参照。

#### PPTX変換後の必須検証

PPTX → PNG 化して目視で確認する（PowerShell COM）：

```powershell
$pptxPath = "$env:USERPROFILE\path\to\slide-01.pptx"
$outPng   = "$env:USERPROFILE\path\to\pptx-slide-1.png"
$pptApp   = New-Object -ComObject PowerPoint.Application
$pptApp.Visible = 1
$pres = $pptApp.Presentations.Open($pptxPath, 0, 0, 0)
$pres.Slides[1].Export($outPng, "PNG", 1920, 1080)
$pres.Close(); $pptApp.Quit()
```

**目視チェック項目（PNG を HTML と並べて確認）：**
- [ ] 全アイコンが表示されている（インラインSVGは消えることがある）
- [ ] テキストの改行位置が崩れていない
- [ ] カード・矢印・区切り線など全要素が揃っている
- [ ] フォントが正しく表示されている

**問題があった場合 — `/codex-review` で原因特定と修正：**

```bash
cd /path/to/output-dir
codex --dangerously-bypass-approvals-and-sandbox review "slide-01.html で以下のPPTX変換後の問題が発生しました：{問題の詳細}
HTMLのどの部分が原因か特定し、PPTX変換に対応した修正案を提示してください。
特にインラインSVG・フォント埋め込み・外部リソース参照の観点で見てください。
インラインSVGが消える場合は base64 data URI の img タグへの変換方法も示してください。
日本語で回答してください。"
```

レビュー指摘を反映してHTMLを修正し、再度PPTX変換→目視確認を繰り返す。

---

## HTML の基本構造（ベーステンプレート）

`assets/slide-base.html` を出発点として使う。詳細は該当ファイルを参照。

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
    .emp-u   { text-decoration: underline; text-underline-offset: 0.15em; }
    .emp-inv { background: var(--text-color); color: var(--base-color); padding: 0 0.2em; }
    .emp-main   { color: var(--main-color); font-weight: 700; }
    .emp-accent { color: var(--accent-color); font-weight: 700; }
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

### 技術（CRITICAL Rules）
- [ ] `html, body` が `1920px × 1080px; overflow: hidden` 固定
- [ ] CSS/JS が全てインライン（Google Fonts CDN は除く）
- [ ] 表に縦罫線がない（`border-bottom` のみ）
- [ ] 1スライド = 1HTMLファイル

### デザイン
- [ ] 背景 `#F9F9F9`・テキスト `#1A1A1A`・余白 48px 以上
- [ ] フォントサイズ: タイトル 50pt / 見出し 35pt / 本文 25pt
- [ ] メインカラー + アクセントカラーの合計使用率が 5% 以下

### 内容
- [ ] テキストが1スライドあたり最大3行
- [ ] 1スライド1メッセージ・データは図表で視覚化

### 視覚的フィードバックループ
- [ ] PASS/FAIL 表を記録し全項目 PASS を確認した
- [ ] `/codex-review` で CRITICAL/WARNING がないことを確認した

### PPTX変換後（方法Bのみ）
- [ ] PPTX → PNG 化して目視確認した
- [ ] 全アイコン表示・テキスト・フォントが崩れていない
- [ ] 問題があれば `/codex-review` で原因特定・修正した

**Iron Law: 1 slide = 1 HTML file. Never combine.**

---

## Common Mistakes

| ミス | 修正 |
|------|------|
| 視覚的フィードバックループを省略する | 目視で全項目 PASS になるまで必ずループを継続する |
| 修正後に改善していないのに次の修正に進む | 改善していなければ即 Revert して別のアプローチを試みる |
| 3回連続で改善なしでもループを続ける | Codex フォールバックに切り替える |
| Codex に HTML を書かせる | HTML は Claude Code が書く。Codex は Image Gen・フォールバック・レビューのみ |
| `svg { width:100% }` でグローバル設定 | 特定コンテナには `!important` で個別上書きする |
| インラインSVGのままPPTX変換する | base64 data URI の `img` タグに変換する |
| SVGでアイコンを手書きし続ける | 3回失敗したらリファレンスPNGクロップ方式に切り替える（Step 3-4参照） |
| base64 img を正規表現で置換する | Python f-string で HTML 全体を再構築する |
| クロップ画像の白余白をトリミングしない | `trim_whitespace()` で除去してからbase64化する |
| `settings.local.json` の env をシェルから直接参照 | `python -c "import json; ..."` で明示的に取得する |

---

## Prerequisites（依存関係）

| ツール | 用途 | インストール |
|--------|------|-------------|
| Playwright | スクリーンショット取得 | `uv run playwright install chromium` |
| Pillow + numpy | PNG クロップ・比較 | `uv add pillow numpy` |
| PowerPoint（COM） | PPTX → PNG 変換（方法B検証） | Windows 標準 |
| `HTML2PPTX_API_KEY` | html2pptx.app API | `~/.claude/settings.local.json` の `env` に設定済み |

---

## References

- `references/design-rules.md` — 色/フォント/余白/強調の詳細リファレンス
- `references/slide-templates.md` — T-01〜T-12 HTMLスニペット集
- `references/thesvg-usage.md` — アイコン取得・recolor・ライセンス
- `references/png-crop-icon.md` — リファレンスPNGクロップ方式の詳細手順・コード
- `references/html2pptx-guide.md` — HTML→PPTX変換ガイド（インラインSVG非対応の注意事項含む）
- `references/powerpoint-handoff.md` — HTML→PNG→PowerPoint 貼付の完全手順
- `scripts/fetch_icon.py` — theSVG CDN取得＋キャッシュ
- `scripts/render_slide.py` — Playwright経由でPNG化
- `scripts/export_to_pptx.py` — html2pptx.app REST API経由で編集可能 .pptx 出力
- `assets/slide-base.html` — 1920×1080単一スライドHTML雛形
- `assets/template.html` — デザインパターンギャラリー（T-01〜T-12）
- `../codex-review/SKILL.md` — Codex CLI によるコードレビュースキル
