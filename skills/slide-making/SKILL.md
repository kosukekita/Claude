---
name: slide-making
description: >
  Codex の Image Gen で参照画像を生成し、Claude Code が HTML を書いて
  diff ≈ 0 になるまでフィードバックループで修正する一気通貫スライド作成スキル。
  1スライド=1ファイル（slide-01.html, slide-02.html…）、1920×1080固定、
  CSS/JS全インライン、最大3行テキスト、T-01〜T-12テンプレート。
  Use when user requests HTMLスライド作成, スライドHTML, PowerPoint貼付用スライド,
  1920x1080 slide, スライドメイキング, slide-making, スライドデザイン,
  発表スライド HTML, PNG出力.
  Do NOT trigger for .pptx generation (use python-pptx directly — no dedicated skill exists),
  multi-slide single-file decks (use infographic),
  academic poster (use make-poster).
---

# slide-making — Image Gen → HTML → diff ループ → PNG 統合スキル

## Overview

**役割分担：**

| フェーズ | 担当 | 内容 |
|----------|------|------|
| Phase 1 | Claude Code | 要件確認・テンプレート提案 |
| Phase 2 | Codex | Image Gen で参照画像を生成するだけ |
| Phase 3 | Claude Code | HTML 生成 → PNG → diff 計算 → CSS 修正ループ |
| Phase 4 | Claude Code | PPTX 変換・PNG 貼付（オプション） |

```
[Codex] Image Gen → reference.png
     ↓
[Claude Code] HTML 初版作成
     ↓
[Claude Code] Playwright → screenshot.png
     ↓
[Claude Code] PIL で diff 計算
     ↓ diff > 5 なら CSS 修正して再ループ
[Claude Code] diff ≈ 0 で完了
     ↓
（オプション）PPTX 変換
```

**収束目標: diff ≤ 5**（フォント antialiasing 差で下げ止まったら打ち切り可）

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

### Phase 1 — 要件確認 & テンプレート提案（Claude Code）

1. スライド枚数・各スライドのタイトルとキーメッセージを確認
2. T-01〜T-12 から最適テンプレートを選んでユーザーに提案
3. 出力ディレクトリを決定（例: `~/slides/my-deck/`）
4. 承認後に Phase 2 へ

---

### Phase 2 — Codex で Image Gen（参照画像生成のみ）

**Codex の役割はここだけ。HTML は書かせない。**

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

### Phase 3 — HTML生成 + diff フィードバックループ（Claude Code が全て担当）

**このフェーズは Claude Code が自律的に実行する。Codex は呼ばない。**

#### Step 3-1: HTML 初版作成

`assets/slide-base.html` を基に、参照画像のデザイン言語（色・レイアウト・余白・カード構造）を
忠実に再現した HTML を `{出力ディレクトリ}/slide-{番号}.html` として作成する。

#### Step 3-2: Playwright でスクリーンショット取得

```python
# uv run --with playwright で実行
import asyncio
from playwright.async_api import async_playwright

async def screenshot(html_path: str, out_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto(f'file:///{html_path}')
        await page.wait_for_timeout(2000)  # Google Fonts 読み込み待ち
        await page.screenshot(path=out_path, full_page=False)
        await browser.close()

asyncio.run(screenshot('{html_path}', '{out_path}'))
```

Windows では `file:///C:/...` 形式でパスを渡すこと。

#### Step 3-3: diff 計算

```python
import numpy as np
from PIL import Image

def diff_score(ref_path: str, cur_path: str) -> float:
    ref = Image.open(ref_path).resize((1920, 1080), Image.LANCZOS).convert('RGB')
    cur = Image.open(cur_path).convert('RGB')
    return float(np.abs(np.array(ref, dtype=float) - np.array(cur, dtype=float)).mean())

score = diff_score('reference-01.png', 'screenshot-01.png')
print(f'diff: {score:.2f}')
```

#### Step 3-4: フィードバックループ（必須・diff ≤ 5 まで繰り返す）

**ループを絶対に省略しない。diff > 5 の間はループを継続すること。**

```
while diff > 5:
    1. PIL で差分画像を生成し、ズレているエリアを特定する
       - 色・背景のズレ → CSS カラー変数を修正
       - レイアウト・余白のズレ → padding / margin / gap を調整
       - カードサイズのズレ → width / height を px 単位で合わせる
       - タイポグラフィのズレ → font-size / line-height / letter-spacing を調整
    2. HTML の CSS を Edit ツールで修正（**修正前の diff を記録しておく**）
    3. Playwright で再スクリーンショット
    4. diff_score() で再評価
    5. **diff が前回より悪化していたら即座に変更を元に戻し（Revert）、別のアプローチを考える**
       → 悪化した修正を重ねてはいけない。必ずベストスコア時点に戻してから別手を打つ
    6. diff ≤ 5 なら完了、それ以外は 1 に戻る
```

**⚠️ diff悪化時の鉄則（絶対に守ること）：**
- 修正のたびに「前回 diff」と「今回 diff」を比較する
- **今回 diff > 前回 diff** なら → その修正は失敗。Edit を Revert して前の状態に戻す
- 悪化した状態のまま次の修正を積み重ねてはいけない
- ベストスコアの状態を常に保持し、そこから別の修正を試みる

**差分画像の生成方法：**

```python
import numpy as np
from PIL import Image

def make_diff_image(ref_path: str, cur_path: str, out_path: str):
    ref = np.array(Image.open(ref_path).resize((1920, 1080), Image.LANCZOS).convert('RGB'), dtype=float)
    cur = np.array(Image.open(cur_path).convert('RGB'), dtype=float)
    diff = np.abs(ref - cur)
    # 差分を8倍に増幅して可視化
    diff_img = Image.fromarray(np.clip(diff * 8, 0, 255).astype('uint8'))
    diff_img.save(out_path)
```

**収束判定：**
- **diff ≤ 5 で完了**
- diff が 5〜8 でループが3回以上進まない場合のみ、残差がフォントの antialiasing 差と判断して打ち切り可
- それ以外はループを継続すること

**⚠️ Codex フォールバック（3回連続改善なしで発動）：**
- diff のベストスコアが **3回連続で更新されなかった** 場合、Claude Code によるループを打ち切り Codex に引き継ぐ
- Codex には以下を渡す：
  1. 参照画像（`reference-XX.png`）
  2. 現在の HTML ファイル
  3. 差分画像（`diff-XX.png`）
  4. 現在の diff スコアと「どのエリアがズレているか」の分析結果
- Codex プロンプト例：
  ```
  /goal 添付のHTML（slide-01.html）を参照画像（reference-01.png）に近づけてください。
  差分画像（diff-01.png）の明るいエリアがズレている箇所です。
  現在の diff スコアは XX.XX です。CSS のみ修正し、HTMLのコンテンツは変えないでください。
  修正後は Playwright でスクリーンショットを撮り、diff を計算して報告してください。
  ```

**⚠️ 収束しない差異（無視してよい）：**
- Image Gen のラスター画像とブラウザのフォント antialiasing は原理的に異なる（フォント周辺の微細なピクセル差）
- Google Fonts のカーニング差（読み込みタイミングによる微細なズレ）

**⚠️ CSS の SVG サイズ上書き罠：**
```css
/* グローバルに svg { width:100%; } を設定するとアイコンサイズが制御不能になる */
/* 特定コンテナには !important またはインラインスタイルで個別上書きする */
.card-icon svg { width: 80px !important; height: 80px !important; }
```

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

> ⚠️ export_to_pptx.py のダウンロード部分（`client.stream()`）が 400 エラーになる場合は
> ジョブが返す `downloadUrl` を `curl -o output.pptx` で直接ダウンロードすること。

PPTX → PNG 変換は PowerShell + PowerPoint COM で行う：

```powershell
$pptxPath = "$env:USERPROFILE\.claude\...\slide-01.pptx"
$outPng   = "$env:USERPROFILE\.claude\...\pptx-slide-1.png"
$pptApp   = New-Object -ComObject PowerPoint.Application
$pptApp.Visible = 1
$pres = $pptApp.Presentations.Open($pptxPath, 0, 0, 0)
$pres.Slides[1].Export($outPng, "PNG", 1920, 1080)
$pres.Close(); $pptApp.Quit()
```

詳細は `references/html2pptx-guide.md` を参照。

---

## HTML の基本構造（ベーステンプレート）

`assets/slide-base.html` を出発点として使う。

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

### 技術
- [ ] `html, body` が `1920px × 1080px; overflow: hidden` 固定
- [ ] CSS/JS が全てインライン（Google Fonts CDN は除く）
- [ ] 表に縦罫線がない（`border-bottom` のみ）

### PNG 出力
- [ ] 1920×1080px で出力されている
- [ ] diff ≤ 5 を達成している（フィードバックループ完了）
- [ ] フォント・アイコンが正しく表示されている

**Iron Law: 1 slide = 1 HTML file. Never combine.**

---

## Common Mistakes

| ミス | 問題 | 修正 |
|------|------|------|
| diff ループを省略する | 参照画像とHTMLが乖離したまま完了する | **diff ≤ 5 になるまで必ずループを継続する** |
| diff が悪化した修正を積み重ねる | どんどんスコアが悪化し収束しない | **修正後に前回より diff が大きければ即 Revert。ベストスコア時点から別手を打つ** |
| 改善が止まっても Claude Code でループを続ける | 時間を無駄にして収束しない | **3回連続でベストスコアが更新されなければ Codex フォールバックに切り替える** |
| Codex に HTML を書かせる | 担当外・フィードバックループが機能しない | HTML は Claude Code が書く。Codex は Image Gen のみ |
| `html, body` にサイズ指定しない | スライドサイズが崩れる | `width:1920px; height:1080px; overflow:hidden` を必ず設定 |
| 4行以上のテキスト | スライドの目的が分散 | 2枚に分割か箇条書きを削る |
| 表に縦罫線を引く | デザインルール違反 | `border-bottom` のみに |
| 1 HTML に複数スライドを入れる | PNG化・PowerPoint貼付不可 | ファイルを分割する |
| `svg { width:100%; height:100% }` でグローバル設定 | 個別アイコンのサイズが制御不能 | 特定コンテナには `!important` で上書き |
| diff 10 以下で「フォント差」と早期打ち切り | 参照画像との乖離が残る | diff 5 以下まで修正を続ける。5〜8 でループ停滞時のみ打ち切り可 |
| `settings.local.json` の env をシェルから直接参照 | Bash ツールには自動注入されない | `python -c "import json; ..."` で明示的に取得する |

---

## References

- `references/design-rules.md` — 色/フォント/余白/強調の詳細リファレンス
- `references/slide-templates.md` — T-01〜T-12 HTMLスニペット集
- `references/thesvg-usage.md` — アイコン取得・recolor・ライセンス
- `references/html2pptx-guide.md` — HTML→PPTX変換ガイド
- `references/powerpoint-handoff.md` — HTML→PNG→PowerPoint 貼付の完全手順
- `scripts/fetch_icon.py` — theSVG CDN取得＋キャッシュ
- `scripts/render_slide.py` — Playwright経由でPNG化
- `scripts/export_to_pptx.py` — html2pptx.app REST API経由で編集可能 .pptx 出力
- `assets/slide-base.html` — 1920×1080単一スライドHTML雛形
- `assets/template.html` — デザインパターンギャラリー（T-01〜T-12）
