---
name: powerpoint
description: >
  python-pptx を使って PowerPoint (.pptx) ファイルを作成する際のデザインルール・ベストプラクティスを提供。
  Use when user requests PowerPoint, presentation, slide, .pptx creation, or asks for
  パワーポイント, スライド作成, プレゼン, pptx, プレゼンテーション作成.
  IMPORTANT: Never use Marp — always generate .pptx directly with python-pptx.
---

# PowerPoint スキル

## 重要ルール

- **Marp 使用禁止**: スライド作成に Marp は使用しない。python-pptx で直接 .pptx を生成すること。
- **python-rules スキルを参照**: Python 実行環境は uv + PEP 723 インラインスクリプトで管理。

## デザイン設定

| 項目 | 値 | 備考 |
|------|-----|------|
| 背景 | `#F9F9F9` | 装飾なし無地白 |
| テキスト | `#1A1A1A` | 視認性を確保した黒 |
| アクセント | `#004BB1` | 青 |
| サブアクセント | `#E3F2FD` | 淡青 |
| フォント（英数字） | `Segoe UI` | 優先 |
| フォント（日本語） | `Meiryo` | sans-serif |
| タイトル | 50pt | |
| 見出し | 35pt | |
| 本文 | 25pt | |

**スタイル方針**: モノクローム基調、図解・強調のみ青の濃淡使用、コントラスト抑制＋視認性確保、十分な余白

## python-pptx 実装ガイド

### 基本セットアップ（PEP 723 インラインスクリプト）

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["python-pptx"]
# ///
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# カラー定数
COLOR_BG       = RGBColor(0xF9, 0xF9, 0xF9)
COLOR_TEXT     = RGBColor(0x1A, 0x1A, 0x1A)
COLOR_ACCENT   = RGBColor(0x00, 0x4B, 0xB1)
COLOR_SUB      = RGBColor(0xE3, 0xF2, 0xFD)
```

### スライドサイズ（16:9）

```python
prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
```

### 背景色設定

```python
def set_slide_background(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color
```

### フォント設定

```python
def apply_font(run, size_pt: int, bold=False, color=COLOR_TEXT):
    run.font.name  = "Segoe UI"   # 英数字
    run.font.size  = Pt(size_pt)
    run.font.bold  = bold
    run.font.color.rgb = color
    # 日本語: PowerPoint が Meiryo にフォールバック
```

## スライド種別テンプレート

### タイトルスライド
- タイトル: **50pt**、ACCENT色（`#004BB1`）、中央揃え
- サブタイトル: **25pt**、TEXT色
- 背景: BG色無地

### コンテンツスライド
- スライドタイトル: **35pt**、ACCENT色、左揃え
- 本文箇条書き: **25pt**、TEXT色
- 余白: 上下左右 0.5インチ以上

### セクション区切りスライド
- 見出し: **35pt**、白文字
- 背景: ACCENT色（`#004BB1`）

## 完了チェックリスト

- [ ] 背景色が `#F9F9F9`
- [ ] テキストが `#1A1A1A`
- [ ] アクセントは `#004BB1` / `#E3F2FD` のみ使用
- [ ] フォントサイズがルール通り（50 / 35 / 25pt）
- [ ] 余白が十分（窮屈でない）
- [ ] Marp を使っていない（python-pptx で生成）
