---
name: slide-making
description: >
  PowerPoint に1枚ずつ貼り付けるための単一 HTML スライドを生成する。
  1スライド=1ファイル（slide-01.html, slide-02.html…）、CSS/JS 全インライン、
  1920×1080、最大3行テキスト、theSVG アイコン+CDN キャッシュ、横線のみ表、
  強調4階層（下線→反転→メインカラー→アクセントカラー）、余白0.5インチ厳守。
  Use when user requests HTMLスライド作成, スライドHTML, PowerPoint貼付用スライド,
  1920x1080 slide, 単一HTMLスライド, スライドメイキング, slide-making,
  ブラウザで見るスライド, presentation HTML slide, スライドデザイン, 発表スライド HTML.
  Do NOT trigger for .pptx generation (use powerpoint skill),
  multi-slide single-file decks (use infographic),
  academic poster (use make-poster).
---

# slide-making

## Overview

**1スライド = 1HTMLファイル**。CSS/JS は全てインライン。PowerPoint に画像として貼り付けるための 1920×1080 スライドを生成する。テキストは1スライドあたり最大3行。グラフ・図・アイコンでビジュアルに伝え、文章では説明しない。

---

## When to Use

**Should trigger:**
- 「HTMLスライド作って」「PowerPointに貼るスライドのHTMLを生成して」
- 「1920×1080のスライドを1枚作成して」「スライドHTMLを1枚ずつ」
- 「slide-making でタイトルスライドを作って」
- 「発表用スライドをHTMLで」「表紙スライドのHTMLが欲しい」

**Should NOT trigger:**
- 「.pptx ファイルを作って」→ `powerpoint` スキルを使う
- 「Marpでスライドを作って」→ `powerpoint` スキルを使う
- 「インフォグラフィックを作って」→ `infographic` スキルを使う
- 「学術ポスターを作って」→ `make-poster` スキルを使う

---

## CRITICAL Rules

**CRITICAL: 以下は絶対ルール。1つでも違反したら修正してから出力する。**

1. **1スライド = 1HTMLファイル** — 複数スライドを1つのHTMLにまとめることは禁止
2. **テキスト最大3行** — 箇条書き・本文を合わせて1スライドあたり3行を超えない
3. **縦罫線禁止** — 表は `border-bottom` のみ使用、`border-left`/`border-right` は禁止
4. **1920×1080 固定** — `html, body { width: 1920px; height: 1080px; }` を変更しない
5. **CSS/JS 全インライン** — 外部 CSS/JS ファイルへの分割は禁止（Chart.js CDN の `<script src>` は例外）

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

**フォント**: `'Noto Sans JP', 'Inter', 'Meiryo', sans-serif`（Google Fonts CDN 使用）

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

## Quick Reference

### テンプレートの使い方

**単一スライド雛形（新規スライド作成時）:**
1. `assets/slide-base.html` をコピーして `slide-01.html` にリネーム
2. `<section class="slide">` の中身をスライド種別のスニペットに置き換える（`references/slide-templates.md` 参照）
3. `{{PLACEHOLDER}}` をコンテンツで埋める

**デザインパターンギャラリー（レイアウト確認・参考時）:**
`assets/template.html` をブラウザで開くと T-01〜T-12 の完成例を一覧で確認できる。
スライド内容に合わせて適切なテンプレートを選び、そのCSSとHTMLを `slide-base.html` に移植する。

### テンプレートギャラリー一覧 (`assets/template.html`)

| ID | 名称 | 用途 | 主な構成要素 |
|----|------|------|-------------|
| T-01 | グラフ強調 | 複数カテゴリ中の最大値を強調したい | 棒グラフ（SVG）+ 吹き出し + 右側結論メッセージ |
| T-02 | 範囲強調 | 連続する複数データをひとまとまりで強調したい | 帯状ハイライト（main-tint）+ メインカラー棒グラフ |
| T-03 | ステップ表現 | 手順・プロセスを段階的に見せたい | 4枚カード + STEPラベル + アイコン + 矢印 |
| T-04 | 研究結果テーブル | 論文の主要結果（OR/HR/RR等）を1枚にまとめたい | ヘッダーバー + アイコン付き4行テーブル + 出典 |
| T-05 | 要素分解 | 概念を親→中間→末端と階層分解して見せたい | 縦書きルート + ブラケット（SVGコネクタ）+ 数値パネル |
| T-06 | 強みテーブル | 自社・製品の強みを4項目で見せたい | ラベル列 + アイコン列 + チェック箇条書き列（4行） |
| T-07 | 対比比較 | 2つの選択肢を複数観点で比較したい | 縦軸4観点 × 横軸2項目 + 強調フレーム |
| T-08 | 因果図 | 原因→結果の因果関係を見せたい | 左パネル（原因）→ 矢印 → 右パネル（結論）|
| T-09 | 仕様比較表（行強調） | 複数製品を比較し特定の観点（行）で訴求したい | 3列仕様表 + 特定行をメインカラー帯で強調 |
| T-10 | 仕様比較表（列強調） | 複数製品を比較し特定の製品（列）を推薦したい | 3列仕様表 + 推薦列をメインカラー縦帯で強調 |
| T-11 | ロードマップ | プロジェクト計画を時系列で見せたい | 4フェーズ横並びタイムライン + フェーズ名 + 施策リスト |
| T-12 | 文章｜図解 | 文字情報と図解を同時に見せたい | 左列テキスト + 右列図解（2列分割） |

**テンプレート選択の目安:**
- データ（棒グラフ）の最大値を強調したい → T-01（グラフ強調）
- 複数データのうち特定グループをまとめて強調したい → T-02（範囲強調）
- 手順・プロセス・フローを見せたい → T-03（ステップカード）
- 統計結果・OR/HR/RR等の数値を一覧にしたい → T-04（研究結果テーブル）
- 概念・料金・構造を階層分解して見せたい → T-05（階層ブラケット）
- 自社・製品の強みを箇条書きで見せたい → T-06（強みテーブル）
- 2つの選択肢を複数観点で比較したい → T-07（対比比較）
- 原因と結果の因果関係を見せたい → T-08（因果図）
- 複数製品の比較で特定の観点（行）を訴求したい → T-09（仕様比較・行強調）
- 複数製品の比較で特定の製品（列）を推薦したい → T-10（仕様比較・列強調）
- プロジェクト計画を時系列フェーズで見せたい → T-11（ロードマップ）
- テキストと図解を並べて見せたい → T-12（文章｜図解）

### CSS 変数一覧

```css
:root {
  --base-color: #F9F9F9;  --text-color: #1A1A1A;
  --main-color: #0071BC;  --accent-color: #FF5050;
  --font-size-title: 50pt; --font-size-heading: 35pt; --font-size-body: 25pt;
  --margin-edge: 48px; --slide-w: 1920px; --slide-h: 1080px;
}
```

---

## Workflow

### Step 1 — 要件確認 & テンプレート提案

- スライド枚数・種別（タイトル/箇条書き/グラフ/比較/まとめ 等）
- 各スライドのタイトルとキーメッセージ（1スライド1メッセージ）
- データがある場合は数値（グラフ化する）
- 使いたいアイコン（theSVG slug または用途で判断）

**テンプレート提案（必須）**: 要件を把握したら、以下の選択基準でテンプレートを1つ選び、理由とともにユーザーに提案する。ユーザーが承認するか、別のテンプレートを希望するまで実装に進まない。

```
選択基準:
- データ（棒グラフ）があり、最大値を強調したい        → T-01（グラフ強調）
- 複数データのうち特定グループをまとめて強調したい    → T-02（範囲強調）
- 手順・プロセス・フローを見せたい                    → T-03（ステップ表現）
- 統計結果・OR/HR/RR等の数値を一覧にしたい            → T-04（研究結果テーブル）
- 概念・料金・構造を階層分解して見せたい              → T-05（要素分解）
- 自社・製品の強みを箇条書きで見せたい               → T-06（強みテーブル）
- 2つの選択肢を複数観点で比較したい                  → T-07（対比比較）
- 原因と結果の因果関係を見せたい                     → T-08（因果図）
- 複数製品の比較で特定の観点（行）を訴求したい        → T-09（仕様比較・行強調）
- 複数製品の比較で特定の製品（列）を推薦したい        → T-10（仕様比較・列強調）
- プロジェクト計画を時系列フェーズで見せたい          → T-11（ロードマップ）
- テキストと図解を並べて見せたい                     → T-12（文章｜図解）
- 上記に当てはまらない                               → references/slide-templates.md のスニペットを使う
```

提案例:
> 「データの最大値を強調したい内容なので **T-01（グラフ強調）** を提案します。
> `assets/template.html` の T-01 セクションで完成イメージが確認できます。
> このままで進めますか？それとも別のテンプレートにしますか？」

### Step 2 — テンプレート複製

ユーザーが承認したテンプレートを使って実装する。

```
assets/slide-base.html → slide-01.html  （単一スライド雛形をコピー）
```

`assets/template.html` の選択テンプレート（`.t-XX` ブロック）のCSSとHTML構造を `slide-01.html` に移植し、デザインを再現する。

### Step 3 — コンテンツ流し込み

`references/slide-templates.md` から種別に合うスニペットを `<section class="slide">` 内にコピーし、プレースホルダを埋める。

チェック: テキストが3行以内か？ 縦罫線がないか？ 略語に初出フルテキストがあるか？

### Step 4 — アイコン取得

```powershell
# ブランドアイコン（原色）
uv run skills/slide-making/scripts/fetch_icon.py --slug github --variant default

# 汎用装飾アイコン（recolor）
uv run skills/slide-making/scripts/fetch_icon.py --slug arrow-right --variant mono --recolor
```

詳細は `references/thesvg-usage.md` を参照。

### Step 5 — ブラウザ確認

Chrome / Edge で `file://` から HTML を開いて目視確認。

### Step 6 — PNG 化して PowerPoint へ

```powershell
# 初回のみ
uv run playwright install chromium

# 変換（3840×2160）
uv run skills/slide-making/scripts/render_slide.py --input slide-01.html --output slide-01.png
```

詳細は `references/powerpoint-handoff.md` を参照。

---

## Icon Pipeline

アイコンは `scripts/fetch_icon.py` で jsDelivr CDN から取得し、`cache/icons/` に永続保存する。

```
CDN fetch → cache/icons/{slug}/{variant}.svg → HTML に img src で参照
```

**IMPORTANT: AWS Architecture アイコン（slug が `aws-architecture-` で始まるもの）は CC BY-ND ライセンスのため recolor 禁止。必ず default バリアントを原色で使用すること。**

ブランドアイコン（GitHub, AWS, Python 等）も原色維持が原則。recolor は汎用装飾アイコンのみ。

詳細は `references/thesvg-usage.md` を参照。

---

## Verification Checklist

### デザイン
- [ ] 背景が `#F9F9F9` になっている
- [ ] テキスト色が `#1A1A1A` になっている
- [ ] メインカラー + アクセントカラーの合計使用率が 5% 以下
- [ ] フォントサイズが タイトル 50pt / 見出し 35pt / 本文 25pt
- [ ] 上下左右の余白が 48px 以上ある

### 内容
- [ ] テキストが1スライドあたり最大3行
- [ ] 1スライド1メッセージになっている
- [ ] データがある箇所は図表で視覚化している
- [ ] 略語の初出にフルテキスト or 日本語が付記されている

### 技術
- [ ] CSS/JS が全てインライン（外部ファイルへのリンクがない）
- [ ] `html, body` が `1920px × 1080px` 固定
- [ ] 表に縦罫線がない（`border-bottom` のみ）
- [ ] アイコンの `src` が `../cache/icons/...` を参照している

### 出力
- [ ] ブラウザで `file://` 開いて目視確認した
- [ ] `render_slide.py` で PNG 化して PowerPoint 貼付テストをした（最低1枚）

**Iron Law: 1 slide = 1 HTML file. Never combine.**

---

## Common Mistakes

| ミス | 問題 | 修正 |
|------|------|------|
| 本文を文章で書く | 情報過多・読まれない | キーワード＋数字＋アイコンに置き換える |
| 4行以上のテキスト | スライドの目的が分散 | 2枚に分割するか箇条書きを削る |
| 表に縦罫線を引く | デザインルール違反 | `border` を削除し `border-bottom` のみに |
| アイコン色を全部 recolor | ブランド識別消失 / AWS は ND 違反 | ブランド・AWS は原色のまま |
| 1 HTML に複数スライドを入れる | PowerPoint 貼付不可 | ファイルを分割する |
| 略語をフルテキストなしで初出 | 読者が意味を取れない | 初出は `略語（フルテキスト）` 形式 |

---

## References

- `references/design-rules.md` — 色/フォント/余白/強調/略語の詳細リファレンス（OK・NG 例付き）
- `references/slide-templates.md` — 8 種スライド種別の HTML スニペット集
- `references/thesvg-usage.md` — アイコン取得・recolor・ライセンス・よく使う slug
- `references/powerpoint-handoff.md` — HTML→PNG→PowerPoint 貼付の完全手順
- `scripts/fetch_icon.py` — theSVG CDN 取得＋キャッシュ（`uv run` で実行）
- `scripts/render_slide.py` — Playwright 経由で 3840×2160 PNG 化（初回: `uv run playwright install chromium`）
- `assets/slide-base.html` — 1920×1080 単一スライド HTML 雛形（新規スライド作成の出発点）
- `assets/template.html` — スライドデザインパターンギャラリー（T-01〜T-12、ブラウザで開いて確認）
