---
name: marp
description: |
  Marp CLI を活用した Markdown → PowerPoint/PDF/HTML スライド生成。
  Markdown でスライドを作成し、PPTX/PDF/HTML に変換。
  Infographic スキルで生成した SVG を埋め込み可能。

  Use when user creates presentations from Markdown, converts slides to PowerPoint/PDF,
  or needs slide deck generation workflow.

  Trigger phrases: "スライド作成", "プレゼン作成", "PowerPoint生成", "PPTX変換",
  "Markdown→スライド", "Marp", "スライドデッキ", "PDF変換", "プレゼンテーション",
  "slide creation", "presentation", "pptx", "markdown to slides"
---

# Marp - Markdown to Slides

Marp CLI で Markdown からプレゼンテーションスライドを生成します。

**公式サイト**: https://marp.app/

## インストール

```bash
# npm（推奨）
npm install -g @marp-team/marp-cli

# npx（インストール不要）
npx @marp-team/marp-cli slide.md

# Homebrew（macOS/Linux）
brew install marp-cli
```

## 基本構文

### スライド区切り

`---`（水平線）でスライドを区切ります。

```markdown
---
marp: true
theme: default
---

# スライド 1

内容

---

# スライド 2

内容
```

### フロントマター（必須）

```yaml
---
marp: true
theme: default
paginate: true
header: "ヘッダーテキスト"
footer: "フッターテキスト"
---
```

### 利用可能なテーマ

| テーマ | 特徴 |
|--------|------|
| `default` | シンプルな白背景 |
| `gaia` | カラフルでモダン |
| `uncover` | ミニマルデザイン |

## ディレクティブ

### グローバルディレクティブ（フロントマター）

```yaml
---
marp: true
theme: gaia
class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('bg.png')
---
```

### ローカルディレクティブ（スライド単位）

```markdown
<!-- _class: lead -->
<!-- _backgroundColor: #123 -->
<!-- _color: white -->

# このスライドのみに適用
```

### クラス

| クラス | 効果 |
|--------|------|
| `lead` | タイトルスライド（中央寄せ） |
| `invert` | 色反転（ダークモード） |

## 画像配置

### 基本構文

```markdown
![](image.png)
![width:500px](image.png)
![height:300px](image.png)
![w:500 h:300](image.png)
```

### 背景画像

```markdown
![bg](background.png)
![bg left](image.png)      <!-- 左半分に配置 -->
![bg right:40%](image.png) <!-- 右40%に配置 -->
![bg fit](image.png)       <!-- フィット -->
![bg contain](image.png)   <!-- アスペクト比維持 -->
![bg cover](image.png)     <!-- 全面カバー -->
```

### 複数背景（分割レイアウト）

```markdown
![bg left](left.png)
![bg right](right.png)
```

### SVG（Infographic）の埋め込み

```markdown
![w:600](./figures/flowchart.svg)
![bg right:50%](./figures/timeline.svg)
```

## テキスト装飾

### サイズ自動調整

```markdown
<!-- fit --> で長いテキストを自動縮小

# <!-- fit --> 長いタイトルが自動でフィットします
```

### 数式（KaTeX）

```markdown
インライン: $E = mc^2$

ブロック:
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

### コードブロック

````markdown
```python
def hello():
    print("Hello, World!")
```
````

## 2カラムレイアウト

```markdown
<div class="columns">
<div>

## 左カラム
- 項目1
- 項目2

</div>
<div>

## 右カラム
- 項目A
- 項目B

</div>
</div>

<style>
.columns { display: flex; gap: 1rem; }
.columns > div { flex: 1; }
</style>
```

## スピーカーノート

```markdown
# スライドタイトル

内容

<!--
ここにスピーカーノートを書きます。
プレゼンターモードで表示されます。
-->
```

## 変換コマンド

### PowerPoint 出力

```bash
marp --pptx slide.md -o presentation.pptx
marp --pptx --allow-local-files slide.md  # ローカル画像を含む場合
```

### PDF 出力

```bash
marp --pdf slide.md -o presentation.pdf
marp --pdf --allow-local-files slide.md
```

### HTML 出力

```bash
marp slide.md -o presentation.html
marp --html slide.md  # HTML タグを有効化
```

### 画像出力

```bash
marp --images png slide.md  # 全スライドを PNG に
marp --images jpeg slide.md
```

### プレビュー

```bash
marp -p slide.md     # プレビューウィンドウ
marp -w slide.md     # ウォッチモード（自動更新）
marp -s slide.md     # サーバーモード
```

## 設定ファイル

### marp.config.mjs

```javascript
export default {
  allowLocalFiles: true,
  html: true,
  theme: 'default',
  pdf: false,
  pptx: false,
}
```

### .marprc.yml

```yaml
allowLocalFiles: true
html: true
theme: default
```

## Infographic との連携ワークフロー

### 1. Markdown でスライド構成を作成

```markdown
---
marp: true
theme: gaia
paginate: true
---

# プロジェクト概要

## 背景と目的

---

# 開発フロー

![w:800](./figures/dev-flow.svg)

<!-- Infographic で生成した SVG を埋め込み -->

---

# タイムライン

![bg right:60%](./figures/timeline.svg)
```

### 2. Infographic で図を生成

必要な図を AntV Infographic スキルで生成し、SVG として保存:
- フローチャート → `figures/dev-flow.svg`
- タイムライン → `figures/timeline.svg`
- 組織図 → `figures/org-chart.svg`

### 3. PowerPoint に変換

```bash
marp --pptx --allow-local-files slide.md -o presentation.pptx
```

## テンプレート例

### プレゼンテーション基本構成

```markdown
---
marp: true
theme: gaia
class: lead
paginate: true
footer: "© 2026 Your Name"
---

# プレゼンテーションタイトル
## サブタイトル

発表者名
2026年2月

---

<!-- _class: lead -->

# セクション 1

---

## 概要

- ポイント 1
- ポイント 2
- ポイント 3

---

## 図解

![w:700](./figures/diagram.svg)

---

<!-- _class: lead -->

# まとめ

---

## 結論

1. 結論 1
2. 結論 2
3. 今後の展望

---

<!-- _class: lead -->

# ご清聴ありがとうございました

質疑応答
```

## トラブルシューティング

### ローカル画像が表示されない

```bash
marp --allow-local-files slide.md
```

### 日本語フォントが崩れる

カスタムテーマで日本語フォントを指定:

```markdown
<style>
section {
  font-family: "Noto Sans JP", "Hiragino Sans", sans-serif;
}
</style>
```

### PDF/PPTX 変換にブラウザが必要

Chrome、Edge、Firefox のいずれかをインストール:

```bash
# ブラウザを明示的に指定
marp --pdf --browser chrome slide.md
```
