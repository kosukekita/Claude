# PPTX パス ガイド — ネイティブ python-pptx 生成

PPTX は **HTML を経由せず** `scripts/build_pptx.py` で直接生成する。外部 API（html2pptx 等）は使わない。
Claude の仕事は「ドラフト → JSON spec を書く」こと。EMU 計算・run 整形・罫線・画像配置といった機械的部分は
スクリプトが担う（`render_slide.py` と同じ役割分担）。

---

## 実行

```bash
uv run --with python-pptx scripts/build_pptx.py --spec deck.json --out deck.pptx
# stdin からも可:
cat deck.json | uv run --with python-pptx scripts/build_pptx.py --spec - --out deck.pptx
```

`images[].path` は **spec ファイルのあるディレクトリからの相対パス**で解決される（stdin 時は CWD 基準）。
デッキフォルダごと別 PC に持っていっても壊れない。

---

## spec スキーマ（完全例）

```json
{
  "slides": [
    {
      "title": "現状の課題",
      "subtitle": "2025 Q2 レビュー",
      "bullets": ["新規顧客の獲得コストが上昇", "解約率が前年比1.4倍に悪化"],
      "page_number": 3,
      "images": [
        {"path": "parts/icon-cost.png", "x_in": 1.0, "y_in": 4.2, "w_in": 1.2}
      ],
      "table": {
        "headers": ["指標", "前年", "今年"],
        "rows": [["CAC", "¥8,200", "¥11,500"], ["解約率", "2.1%", "2.9%"]],
        "x_in": 7.0, "y_in": 2.5, "w_in": 5.5, "h_in": 2.0,
        "emphasize_row": 1
      },
      "emphasis": [{"text": "1.4倍", "kind": "accent"}]
    }
  ]
}
```

| フィールド | 必須 | 意味 |
|-----------|------|------|
| `title` | ✓ | タイトル（50pt 太字） |
| `subtitle` | | サブタイトル（35pt） |
| `bullets[]` | | 箇条書き（先頭に `・` が付く、25pt） |
| `body` | | 段落テキスト（25pt） |
| `page_number` | | 右下のページ番号（18pt） |
| `images[]` | | `path`/`x_in`/`y_in`/`w_in`（`h_in` 省略でアスペクト比保持） |
| `table` | | `headers`/`rows`/位置・サイズ(inch)/`emphasize_row`(1始まり) |
| `emphasis[]` | | `text` を含む run を色付け。`kind`: `main`／`accent`／`underline`／`invert` |

座標系は**インチ**（スライドは 13.333in × 7.5in = 1920×1080px、余白 0.5in = 48px）。

---

## デザインシステム（スクリプト内定数）

`build_pptx.py` 冒頭に `design-rules.md` と同じ値を持つ:
`BASE=#F9F9F9 / TEXT=#1A1A1A / MAIN=#0071BC / ACCENT=#FF5050`、フォント `Noto Sans JP`、50/35/25/18pt。
強調の 5% ルール（メイン+アクセント合計 5% 以下）は **spec を書く側の責務**。スクリプトは spec のとおり描く。

---

## なぜ縦罫線が出ないか（実装の肝）

python-pptx には高レベルな罫線 API が無く、テーブルは既定でバンド塗り＋グリッド線が付く。
`build_pptx.py` は2段構えでこれを消す:

1. `_clear_table_style()` — テーブルスタイルを **"No Style, No Grid"**（`{2D5ABB26-0587-4C30-8999-92F81FD0307C}`）に設定し、`firstRow`/`bandRow` バンドフラグを除去。
2. `_bottom_border_only(cell)` — 各セルの `<a:tcPr>` に対し、左右上（`a:lnL`/`a:lnR`/`a:lnT`）を `<a:noFill>`、
   下（`a:lnB`）だけ `<a:solidFill>` で描く。`design-rules.md` の「横線のみ」を OOXML レベルで再現:
   - thead 行・最終行: 2pt（`width_pt=2.0`）
   - データ行: 1pt

この部分が一番壊れやすいので、テーブルを含む spec は生成後に必ず PNG 化して縦線が出ていないか目視する（下記）。

---

## 生成物の検証

LibreOffice があれば PNG 化して目視（PowerPoint で開いてもよい）:

```bash
# anaconda の lib 汚染を避けるため LD_LIBRARY_PATH を外す（この環境固有）
env -u LD_LIBRARY_PATH soffice --headless --convert-to png --outdir . deck.pptx
```

目視チェック: 背景 #F9F9F9 / タイトル・本文の改行 / **テーブルが横罫線のみ（縦線なし）** /
強調色（emphasize_row=青, accent=赤）/ パーツ画像の位置・サイズ / ページ番号。

---

## フォントの注意（cross-OS）

- python-pptx は**フォントを埋め込めない**（PowerPoint 専用機能）。`Noto Sans JP` 未導入の PC で開くと
  PowerPoint が代替フォントに置換する。run のフォント名は**単一文字列**で、CSS のようなフォールバック列は持てない。
- 対策: 開く側に Noto Sans JP を入れておく。入れられない環境向けには、`build_pptx.py` の `FONT` 定数を
  `Meiryo` か `Yu Gothic` に差し替えて生成する（1箇所変更で全体に効く）。
- CJK 文字は `_set_run()` が `<a:ea>`（east-asian）タイプフェイスも明示設定するので、英数と日本語でフォントが
  食い違う事故を防いでいる。

---

## パーツ画像の用意

アイコン・図版は GPT Image（`references/codex-imagegen-workflow.md`）か theSVG（`references/thesvg-usage.md`）で
`parts/*.png` に用意してから spec の `images[].path` に渡す。**テキストは画像に焼かない**（spec のテキスト
フィールドで正確に組む）。
