---
name: slide-making
description: >
  ドラフト（Markdown等のテキスト）を 1920×1080 の発表スライドに変換するスキル。
  出力は2系統: HTMLパス（1スライド=1HTML→PNG/PDF 派生）と PPTXパス（python-pptx でネイティブ直接生成、HTML不経由）。
  どちらが欲しいか未指定なら、着手前に必ず確認する。
  アイコン・図版はまず theSVG から取得し、無ければ Codex の GPT Image（image_gen）でパーツのみ生成する。テキストは常に HTML/python-pptx 側で正確に組む（画像に焼き込まない）。
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
> **両方欲しい時も「HTMLを変換」しない。** HTML と PPTX は表現単位が違う（CSS相対配置 vs 絶対座標）ので機械変換できない。
> HTML でデザインを詰めてよいが、PPTX は**同じ意図から spec を直接書いて**ネイティブ生成する（並行制作）。

## STEP 1 — クリエイティブディレクション＋設計図（実装の前に必ず）

**いきなりスライドを作らない。** あなたは情報設計・編集・視覚表現・プレゼンテーション設計を統合する
**AIクリエイティブディレクター**として、観客の「理解」と「認識」がページごとに変化する体験を設計する
（プロンプト正本は `references/creative-direction.md` — 既定フロー・ユーザー確定 2026-07-21）。
そのうえで **Markdown「設計図」を起こし AskUserQuestion で合意してから** HTML/PPTX 実装に入る（`references/design-planning.md`）。

1. **ブリーフ7項目ゲート**: `テーマ / 目的 / 対象者 / 想定枚数 / 発表時間 / 観客の変化(開始前→終了後) / 利用媒体` の
   **未指定項目は着手前に必ず質問**（判定と聞き方は `creative-direction.md §1`）。数字スライドを作るなら「手元の数字」も確認。
   省略できるのはユーザーが「任せる」と明示した項目のみ（仮定を明記）。読み手で粒度を変える（経営層=結論・効果先出し／実務者=手順・根拠厚め）。
2. **フェーズ1〜6 を既定で実行**: 曖昧さの発見 → 中心概念 → 構成案（9部の物語構造） → 視覚設計 → 3方向デザイン案 → 反対監査
   （各フェーズの中身は `creative-direction.md §2`、既存フローへの割付は同 `§3`）。
3. **設計図 Markdown を起こす**: フェーズ3 の構成を、1スライド=1ブロックで `# 言い切りタイトル(15字以内) / > GOAL: / 構造型 / 軸 / 図種＋数字の種類 / 配置 / → だから(So What)` に落とす。
   `GOAL` か `So What` が書けないスライドは作らない。
4. **構造型を1つ当てる**: 構造6型（順番／対比／仕分け／問題打ち手効果／因果／結論先出し）から**1枚1つ**。詰める軸は2つまで（2つ言いたければ2枚に分割）。
5. **数字のあるスライドはグラフを逆算で決める**: `主張→必要な数字→図種` の順。**選んだ図種が出力パスで実装可能か確認**
   （ファネル・サンキー・ヒートマップ・モザイク等の Chart.js 標準外と PPTX の全グラフは `parts/*.png` に画像化）。
6. **AskUserQuestion で合意**: 質問は束ねて最小往復（R0 出力形式＋ブリーフ7項目 → R1 中心概念＋全体構成 → R2 3案選択＋各スライドの構造/図種 → R3 反対監査の結果＋設計図の最終承認）。
   **承認前に HTML/PPTX 実装を始めない。**

> 設計図フェーズで決めるのは「何を・どの順で・どの型で・どの図で」＋中心概念とデザイン方向。
> 個別の配色・余白・強調の実装値は既存「コンテンツ設計」「デザインシステム」が正
> （3案がシステム外を提案する場合の扱いは `creative-direction.md §3` フェーズ5 行）。

## 共通の絶対ルール

1. **1920×1080 固定**（= 13.333in × 7.5in）。余白 48px（0.5in）。
2. **テキストは最大3行/スライド・1スライド1メッセージ**（3行は上限。原則は文を使わず視覚化 →「コンテンツ設計」）。
3. **表は横罫線のみ**（縦罫線禁止）。
4. **GPT Image はパーツのみ。** スライド全体を画像化しない／テキスト・数字を画像に焼き込まない
   （日本語が崩れ・誤り・編集不能になる）。文字は必ず HTML/python-pptx の実テキストで組む。
5. HTMLパス: 1スライド=1HTML、CSS/JS 全インライン（Google Fonts/Chart.js CDN は例外）。
   PPTXパス: python-pptx で shape/textbox を直接配置。

## コンテンツ設計（視覚優先・脱文章）

スライドは**読む文書ではなく見る図**。文章を貼らず、**要点だけ**を視覚化する。**STEP 1（設計図）合意後・執筆前に**ドラフトをこの原則で要素分解してから組む。設計図フェーズの「言い切り見出し・So What・脱文章」は `references/design-planning.md §6` と本節が対になる。

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

## パーツ生成（theSVG → GPT Image の自動チェーン・両パス共通）

アイコンが必要と判断したら、**確認を待たず次の順に自動で取りに行く**（パーツのみ・**テキストは含めない**）。
作業ディレクトリの `parts/` に集めてから埋め込む。

1. **まず theSVG を試す（既定の第一候補）**: `uv run scripts/fetch_icon.py --slug <name> --variant <v>`。
   ブランド/技術ロゴ・汎用装飾アイコン（矢印・チェック・DB 等）はほぼここで揃う。slug 推定は `references/thesvg-usage.md` の「よく使う slug」と manifest（`icons.json`）を当てる。
2. **theSVG に無ければ GPT Image で作る（フォールバック）**: `fetch_icon.py` が **HTTP 404 → 非ゼロ終了**したら（＝そのアイコンが theSVG に無い）、
   Codex 組み込み `image_gen` でその場で生成する（`OPENAI_API_KEY` 不要）。手順・透過処理は `references/codex-imagegen-workflow.md`。

> **判定基準**: theSVG はブランドアイコン主体。会社/技術ロゴ→theSVG が高確率で在る。独自イラスト・抽象概念のピクトグラム→無いことが多く GPT Image 行き。
> **安全弁**: GPT 生成は `--dangerously-bypass-approvals-and-sandbox` を伴う。プロンプトに含めるのは**信頼できる内容のみ**。ライセンス改変禁止（AWS Architecture=CC BY-ND 等）は theSVG 側の注意に従う。

HTMLパスでは `<img src="parts/icon.png">`（theSVG は `.svg` も可）、PPTXパスでは spec の `images[].path` に相対パスで渡す（SVG は PNG 化してから）。

## パス A — HTML

1. `assets/slide-base.html` を起点に 1スライド=1HTML を執筆（デザインシステムはインライン済み）。テンプレは `assets/template.html`（T-01〜T-12 完成例ギャラリー）と `references/slide-templates.md`（§1〜§8 コピー用スニペット）の二段で参照。
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

1. ドラフトを **JSON spec** に構造化（title/subtitle/bullets/body/images/table/**cards**/emphasis）。スキーマと完全例は `references/pptx-guide.md`。
   - **アイコン＋ラベルを概念ごとにまとめる構造化レイアウト（3カラム等）は必ず `cards` を使う**（`bullets`+`images` の個別配置はアイコンと文字が分離して対応が読めない）。`cards` がカード枠・縦スタック・等間隔を自動化する。
2. パーツ（アイコン・図）を `parts/*.png` に生成（上記）。
3. 生成: `uv run --with python-pptx scripts/build_pptx.py --spec deck.json --out deck.pptx`
4. **検証**: PowerPoint で開くか、PNG 化して目視（`env -u LD_LIBRARY_PATH soffice --headless --convert-to png --outdir . deck.pptx`）。
   特に**テーブルが横罫線のみ**・背景色・強調色・パーツ位置を確認。

## よくある失敗

| 失敗 | 対策 |
|------|------|
| HTML か PPTX か聞かずに勝手に決める | STEP 0 で必ず確認 |
| 設計図を作らずいきなりスライドを実装する | STEP 1 で Markdown 設計図を起こし AskUserQuestion で承認を得てから実装 |
| ブリーフ7項目の未指定分を聞かず着手（「スキルに要求がない」「急ぎ」「ドラフトで自明」） | 未指定項目は R0 で必ず質問（`creative-direction.md §1`）。削れるのは「任せる」と明示された項目のみ。急ぎ対応は往復の圧縮で行い項目は削らない |
| 中心概念・3案比較・反対監査を飛ばして設計図承認に進む | フェーズ2/5/6 は既定工程（`creative-direction.md §3`）。反対監査は R3 直前に必須 |
| 観客の変化を「終了後」だけで定義する（GOAL/So What で代用） | 開始前の認識・不安・誤解も必須。変化＝開始前→終了後の差分 |
| GOAL・So What を書かずに作図する | 各スライドに `GOAL` と `→ だから` を必須。書けないスライドは作らない |
| 1枚に構造型・軸を2つ詰める | 構造型は1枚1つ・軸は2つまで。2つ言いたければ2枚に分割 |
| グラフを先に決めて主張を後付け | `主張→数字→図種` の逆算順序。グラフは証拠であって主役でない |
| 描けない図種（ファネル/サンキー等）を選ぶ | 設計図で実装可能性を確認。Chart.js 標準外・PPTX グラフは `parts/*.png` に画像化 |
| 箇条書きが長い文（説明文）になる | 要点のみ抽出し単語・数字・アイコンで視覚化（「コンテンツ設計」） |
| アイコンを意味なく隅に置く | 語の意味と対応させて配置。ページ番号/セリフ/「ご清聴」は既定で描かない |
| PPTX を HTML 経由で作る（変換API・スクショ貼付） | `build_pptx.py` でネイティブ生成 |
| スライド全体を画像生成／テキストを画像に焼く | GPT Image はパーツのみ。文字は実テキスト |
| theSVG を試さずいきなり GPT 生成 | まず `fetch_icon.py`。404（非ゼロ終了）で初めて GPT Image にフォールバック |
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
- `references/creative-direction.md` — **STEP 1 クリエイティブディレクション**（ブリーフ7項目ゲート・プロンプト正本・フェーズ1〜6の統合マップ）
- `references/design-planning.md` — **STEP 1 設計図フェーズ**（入力ゲート・設計図スキーマ・構造6型/グラフ12選の選定表・見出し言い切り）
- `references/design-rules.md` — デザインシステム / `slide-templates.md` — HTMLスニペット（§1〜§8）/ `thesvg-usage.md` — アイコン
- `references/codex-imagegen-workflow.md` — GPT Image パーツ生成 / `pptx-guide.md` — PPTX spec とガイド
