---
name: slide-making
description: >
  ドラフト（Markdown等のテキスト）を 1920×1080 の発表スライドに変換するスキル。
  出力は2系統: HTMLパス（1スライド=1HTML→PNG/PDF 派生）と PPTXパス（python-pptx でネイティブ直接生成、HTML不経由）。
  どちらが欲しいか未指定なら、着手前に必ず確認する。
  アイコン・図版は Codex の GPT Image（image_gen）でパーツのみ生成し、テキストは常に HTML/python-pptx 側で正確に組む（画像に焼き込まない）。
  Use when user turns a draft/markdown into presentation slides, or requests
  スライド作成, HTMLスライド, PPTX/PowerPointスライド, .pptx, 発表スライド, slide deck, 1920x1080 slide, PNG/PDF スライド.
  Do NOT trigger for: 複数の図を1HTMLにまとめるデッキ（use infographic）, academic poster（use make-poster）.
---

# slide-making

ドラフトテキストを発表スライドにする。1920×1080 固定。**GPT Image はパーツ（アイコン・図版）だけ**を作り、
テキストは HTML か python-pptx 側で正確に組む。

## STEP 0 — 出力形式を必ず確認（最重要）

**ユーザーが「HTML」か「PPTX」かを明示していなければ、作業を一切始める前に AskUserQuestion で確認する。**
PNG・PDF は HTML パスの派生物。両方欲しいと言われた場合のみ両パスを実行する。

| 入力 | 選択 | 主成果物 | 派生 |
|------|------|----------|------|
| ドラフトテキスト | **HTMLパス** | `slide-NN.html` | PNG（`render_slide.py`）/ PDF（`--pdf`） |
| ドラフトテキスト | **PPTXパス** | `deck.pptx`（python-pptx ネイティブ） | （必要なら PNG 目視用） |

> **PPTX は HTML を経由しない。** HTML→画像→pptx 貼り付けや外部変換 API は使わない。
> `scripts/build_pptx.py` で直接 `.pptx` を生成する。

## 共通の絶対ルール

1. **1920×1080 固定**（= 13.333in × 7.5in）。余白 48px（0.5in）。
2. **テキストは最大3行/スライド・1スライド1メッセージ**（3行は上限。原則は文を使わず視覚化 →「コンテンツ設計」）。
3. **表は横罫線のみ**（縦罫線禁止）。
4. **GPT Image はパーツのみ。** スライド全体を画像化しない／テキスト・数字を画像に焼き込まない
   （日本語が崩れ・誤り・編集不能になる）。文字は必ず HTML/python-pptx の実テキストで組む。
5. HTMLパス: 1スライド=1HTML、CSS/JS 全インライン（Google Fonts/Chart.js CDN は例外）。
   PPTXパス: python-pptx で shape/textbox を直接配置。

## コンテンツ設計（視覚優先・脱文章）

スライドは**読む文書ではなく見る図**。文章を貼らず、**要点だけ**を視覚化する。**STEP 0 の直後・執筆前に**ドラフトをこの原則で要素分解してから組む。

1. **要点のみ抽出。** 説明文・修飾・前置き・冗長表現は描かない。1スライド1メッセージ。
2. **文章を使わず視覚化する。** アイコン・ピクトグラム・図形・矢印・数字で示し、ラベルは**単語か数字のみ**。
3. **3行は上限であって目標ではない**（共通ルール#2）。狙いは「文を減らす」こと。理想は0〜数語のラベル。
4. **どうしても文が要るときだけ1行**に収める（**改行禁止・原則適用/例外許容**）。内容が要求する場合に限り1行の文を許す。
5. **数値・固有名詞・専門用語は改変しない**（長すぎる語のみ短縮可）。
6. **初出の略語**はフルスペル併記か短い説明。ただし**文章化せず**単語・短句（数語以内）で。収まらなければ略語のままにし、その旨を残す。
7. **描かないもの（既定）**: ページ番号・発表者セリフ・学会/セッション名・「ご清聴ありがとうございました」・指定外のテキスト/ロゴ/装飾。同内容の重複も禁止。**ユーザーが明示した時だけ**例外。
8. **パーツは意味で置く。** アイコンは語の意味と対応させて配置（隅に機械的に置かない）。配色・線・余白は既存デザインシステムに準拠。

> 悪例:「自律的に作業 — コードの調査・編集・テスト実行まで多段階で自走」（説明文）
> 良例: ［調査］→［編集］→［テスト］（各ラベルに `parts/` のアイコン＋矢印、単語のみ）

## デザインシステム

| 要素 | 値 | px→inch/pt（PPTX用） |
|------|-----|----------------------|
| 背景 `--base-color` | `#F9F9F9`（約70%） | スライド全面 |
| テキスト `--text-color` | `#1A1A1A`（約25%） | 本文・表罫線 |
| メイン `--main-color` | `#0071BC`（<4%） | 重要強調 |
| アクセント `--accent-color` | `#FF5050`（<1%） | 警告・ネガティブ |
| タイトル / 見出し / 本文 | 50 / 35 / 25pt | 同左 |
| 余白 | 48px | 0.5in |

フォント: `'Noto Sans JP', 'Meiryo', sans-serif`。**Iron Law: メイン+アクセントの合計 5% 以下。**
強調は優先順に `.emp-u`（下線）→ `.emp-inv`（反転）→ `.emp-main` → `.emp-accent`。詳細 `references/design-rules.md`。

## パーツ生成（GPT Image / theSVG・両パス共通）

アイコン・図版は作業ディレクトリの `parts/` に用意してから埋め込む。**テキストは含めない。**

- **GPT Image（既定）**: Codex 組み込み `image_gen` ツール（`OPENAI_API_KEY` 不要）。
  透過アイコンはクロマキー背景で生成 → `remove_chroma_key.py` で除去。手順は `references/codex-imagegen-workflow.md`。
- **theSVG（ベクター）**: ブランド/汎用アイコンは `uv run scripts/fetch_icon.py --slug <name>`。詳細 `references/thesvg-usage.md`。

HTMLパスでは `<img src="parts/icon.png">`、PPTXパスでは spec の `images[].path` に相対パスで渡す。

## パス A — HTML

1. `assets/slide-base.html` を起点に 1スライド=1HTML を執筆（デザインシステムはインライン済み）。テンプレは `references/slide-templates.md`（T-01〜T-12）。
2. `parts/` のアイコン・図版を `<img>`/CSS で埋め込む。
3. PNG 化: `uv run scripts/render_slide.py --input slide-01.html --output slide-01.png`
   （複数は `--input "slides/*.html" --output-dir ./png`）。
4. PDF 化: `uv run scripts/render_slide.py --input slide-01.html --pdf slide-01.pdf`
   （複数入力は 1つの結合PDFになる）。
5. **視覚チェック**: スクショと意図（参照画像があれば併置）を Read で見比べ、改行位置・アイコン・余白・全体縦位置を確認。
   「ほぼ一致」で完了宣言しない。アイコンサイズが暴れたら `.card-icon svg { width:80px!important }` のように個別指定
   （グローバルな `svg{width}` 上書きは禁止）。
6. PowerPoint へ貼るなら: PNG を挿入 → 幅 33.87cm（13.33in）→ 位置 (0,0)。

## パス B — PPTX（ネイティブ・HTML不経由）

1. ドラフトを **JSON spec** に構造化（title/subtitle/bullets/body/images/table/emphasis）。スキーマと完全例は `references/pptx-guide.md`。
2. パーツ（アイコン・図）を `parts/*.png` に生成（上記）。
3. 生成: `uv run --with python-pptx scripts/build_pptx.py --spec deck.json --out deck.pptx`
4. **検証**: PowerPoint で開くか、PNG 化して目視（`env -u LD_LIBRARY_PATH soffice --headless --convert-to png --outdir . deck.pptx`）。
   特に**テーブルが横罫線のみ**・背景色・強調色・パーツ位置を確認。

## よくある失敗

| 失敗 | 対策 |
|------|------|
| HTML か PPTX か聞かずに勝手に決める | STEP 0 で必ず確認 |
| PPTX を HTML 経由で作る（変換API・スクショ貼付） | `build_pptx.py` でネイティブ生成 |
| スライド全体を画像生成／テキストを画像に焼く | GPT Image はパーツのみ。文字は実テキスト |
| 古い `gpt-5.5` 参照・`OPENAI_API_KEY` 前提 | 組み込み `image_gen`（key不要）。`references/codex-imagegen-workflow.md` |
| 表に縦罫線が出る | HTML: `border-bottom` のみ。PPTX: `build_pptx.py` が自動で横罫線のみ |
| グローバル `svg{width}` でアイコン暴走 | 個別に `width/height` 指定 |
| 「ほぼ一致」で完了 | 視覚チェックを記録し全項目一致まで継続 |

## 前提ツール

- Playwright（PNG/PDF）: 初回 `uv run playwright install chromium`
- python-pptx（PPTX）: `uv run --with python-pptx` で自動導入
- Codex CLI 0.132.0（GPT Image、組み込み `image_gen`）
- LibreOffice（任意・PPTX目視用）: `env -u LD_LIBRARY_PATH soffice ...`

## ファイル

- `scripts/render_slide.py` — HTML→PNG / `--pdf` で PDF（Playwright, `uv run`, cross-OS）
- `scripts/build_pptx.py` — JSON spec → ネイティブ `.pptx`（python-pptx）
- `scripts/fetch_icon.py` — theSVG アイコン取得
- `assets/slide-base.html` — HTML 起点テンプレ / `assets/template.html` — T-01〜T-12 完成例ギャラリー
- `references/design-rules.md` — デザインシステム / `slide-templates.md` — HTMLスニペット / `thesvg-usage.md` — アイコン
- `references/codex-imagegen-workflow.md` — GPT Image パーツ生成 / `pptx-guide.md` — PPTX spec とガイド
