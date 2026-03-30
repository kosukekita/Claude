# theSVG アイコンリファレンス

[theSVG](https://github.com/glincker/thesvg) — 5,600+ ブランド SVG アイコン。CDN 経由で取得し、svglib + reportlab で PNG 変換して python-pptx に挿入する。

## アイコン検索

### API 検索

```
GET https://thesvg.org/api/icons?q={query}&category={category}&limit={limit}
GET https://thesvg.org/api/icons/{slug}         # 単一アイコンのメタデータ
GET https://thesvg.org/api/categories            # カテゴリ一覧
```

### CDN URL パターン

```
https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/{slug}/{variant}.svg
```

例: `https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/github/dark.svg`

## バリアント一覧

| バリアント | 説明 | 推奨用途 |
|-----------|------|---------|
| `default` | ブランドオリジナルカラー（複数色の場合あり） | ブランドを忠実に表現したい場合 |
| `dark` | 黒（#000000） | 明るい背景（`#F9F9F9` 等）のスライド |
| `light` | 白（#FFFFFF） | 暗い背景（`#00337D` セクション区切り等）のスライド |
| `mono` | currentColor 継承 | テーマに合わせた色制御が必要な場合 |
| `wordmark` | アイコン + テキストロゴ（横長） | ブランド名を併記したい場合 |
| `wordmarkLight` | 白テキストロゴ | 暗背景でのブランド名表示 |
| `wordmarkDark` | 黒テキストロゴ | 明背景でのブランド名表示 |

**重要**: 全アイコンに共通で存在するのは `default` と `mono` のみ。`dark`/`light`/`wordmark` は一部アイコン（github 等）でのみ利用可能。404 が返された場合は `default` にフォールバックする。

## よく使うカテゴリ

| カテゴリ | 内容 | 代表的なアイコン |
|---------|------|----------------|
| AI | AI/ML ツール | openai, huggingface, pytorch, tensorflow |
| Cloud | クラウドプラットフォーム | aws, gcp, azure |
| Database | データベース | postgresql, mongodb, redis, mysql |
| Language | プログラミング言語 | python, javascript, rust, go, r |
| Framework | フレームワーク | react, nextjs, django, flask |
| Design | デザインツール | figma, sketch, adobe |
| Analytics | 分析ツール | google-analytics, tableau |
| Devtool | 開発ツール | git, github, gitlab, vscode |
| Hosting | ホスティング | vercel, netlify, heroku |
| Library | ライブラリ | numpy, pandas, scikit-learn |

## 学会発表でよく使うアイコン

### データサイエンス・ML

| slug | 名称 | 用途例 |
|------|------|-------|
| `python` | Python | 解析言語の表示 |
| `r` | R | 統計解析の表示 |
| `pytorch` | PyTorch | 深層学習フレームワーク |
| `tensorflow` | TensorFlow | 機械学習フレームワーク |
| `jupyter` | Jupyter | ノートブック環境 |
| `numpy` | NumPy | 数値計算ライブラリ |
| `pandas` | pandas | データ操作ライブラリ |

### インフラ・環境

| slug | 名称 | 用途例 |
|------|------|-------|
| `docker` | Docker | 再現性環境の説明 |
| `github` | GitHub | コード共有・バージョン管理 |
| `aws` | AWS | クラウドインフラ |
| `gcp` | Google Cloud | クラウドインフラ |
| `azure` | Azure | クラウドインフラ |
| `linux` | Linux | サーバー環境 |

### 研究関連

| slug | 名称 | 用途例 |
|------|------|-------|
| `google-scholar` | Google Scholar | 文献検索 |
| `arxiv` | arXiv | プレプリント |
| `overleaf` | Overleaf | LaTeX 環境 |

## 複数アイコン挿入パターン

### 技術スタック横並び

```python
tech_stack = ["python", "pytorch", "docker", "github"]
start_x = Inches(2)
icon_size = Inches(0.8)
gap = Inches(1.2)

for i, slug in enumerate(tech_stack):
    x = start_x + gap * i
    add_icon(slide, slug, x, Inches(3), icon_size)
```

### アイコン + テキストラベル（縦並び）

```python
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

items = [("python", "Python 3.11"), ("pytorch", "PyTorch 2.0"), ("docker", "Docker")]
start_x = Inches(1.5)
gap = Inches(3)

for i, (slug, label) in enumerate(items):
    x = start_x + gap * i
    add_icon(slide, slug, x, Inches(2.5), Inches(0.8))
    # ラベル
    txBox = slide.shapes.add_textbox(x, Inches(3.5), Inches(1.2), Inches(0.4))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = label
    p.alignment = PP_ALIGN.CENTER
    apply_font(p.runs[0], 18)
```

## SVG→PNG 変換ライブラリ

### メイン: svglib + reportlab（推奨）

Windows でネイティブに動作する。SKILL.md のヘルパー関数で使用。

```python
# dependencies = ["python-pptx", "svglib", "reportlab", "requests"]
```

### 代替: cairosvg（高品質だが Windows でセットアップが必要）

cairosvg は内部で cairo ライブラリを使用する。Windows では追加セットアップが必要:

1. **GTK3 Runtime** をインストール（最も簡単）
2. **conda 経由**: `conda install -c conda-forge cairosvg`
3. **MSYS2 経由**: `pacman -S mingw-w64-x86_64-cairo`

cairosvg 版のヘルパー:
```python
# dependencies = ["python-pptx", "cairosvg", "requests"]
import cairosvg

def add_icon_cairo(slide, slug, left, top, width, *,
                   variant="default", height=None):
    url = f"{THESVG_CDN}/{slug}/{variant}.svg"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    png_bytes = cairosvg.svg2png(bytestring=resp.content, output_width=512)
    slide.shapes.add_picture(io.BytesIO(png_bytes), left, top, width, height)
```

## トラブルシューティング

### アイコンが見つからない (404)

- slug のスペルを確認（ハイフン区切り、小文字）
- API で検索して正しい slug を特定: `https://thesvg.org/api/icons?q={keyword}`
- バリアントが存在しない場合は `default` を試す

### PNG 変換後の品質が低い

- `output_width` を 1024 に上げる: `cairosvg.svg2png(bytestring=svg, output_width=1024)`
- アイコンサイズが大きい場合（2インチ以上）は `output_width=1024` 推奨

### ネットワークエラー

- CDN URL の到達性を確認
- プロキシ環境では `requests.get(url, proxies={"https": "..."})` を設定
- `add_icon_safe()` でフォールバックテキストを設定しておく

### cairosvg インストールエラー（Windows）

- `pip install cairosvg` で cairocffi がインストールされるが cairo DLL が見つからない場合がある
- 上記「Windows での cairosvg セットアップ」を参照
