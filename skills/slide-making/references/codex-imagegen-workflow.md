# Codex Image Gen → HTML → PNG ワークフロー（動作確認済み）

2026-05-22 に動作確認済みのフロー。

---

## 前提

- Codex CLI `0.132.0` + ChatGPT アカウント認証済み
- デフォルトモデル: `gpt-5.5`（ChatGPT アカウントでは `o4-mini` 等は使用不可）
- `image_gen` ツールは `gpt-5.5` で利用可能

---

## 動作確認済みコマンド

```bash
mkdir -p ~/slides/my-deck
cd ~/slides/my-deck

codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  "
Image Genツール（image_gen）を使って、以下のプロンプトで参照画像を生成し、
reference-design.png として ~/slides/my-deck/ に保存してください。

プロンプト:
'Professional Japanese business consulting presentation slide,
McKinsey BCG style, white background, blue accent color,
3 cards layout, minimal clean design, 16:9 widescreen,
bold typography, high quality'

生成した画像を参考に、~/slides/my-deck/slide-01.html を作成してください。
必須制約:
- html, body { width: 1920px; height: 1080px; overflow: hidden; margin: 0; }
- font-family: 'Noto Sans JP'（Google Fonts CDN インポート必須）
- CSS全インライン
"
```

## Codex の内部フロー（ログで確認）

1. `imagegen` スキルの SKILL.md を読み込む
2. `image_gen` ツールで画像生成 → `~/.codex/generated_images/{session-id}/ig_*.png` に保存
3. `cp` で作業ディレクトリにコピー（`reference-design.png`）
4. 生成画像を視覚的に確認してデザイン言語を抽出
5. HTMLを `apply patch` で作成・保存

---

## 注意点

### モデル制限
- ChatGPT アカウントでは `o4-mini`, `codex-mini-latest` は使用不可
- `gpt-5.5`（デフォルト）のみ使用可能

### Image Genの保存先
- 生成画像は `~/.codex/generated_images/{session-id}/ig_*.png` に保存される
- Codex が自動で `cp` して作業ディレクトリに移動する

### html, body のサイズ固定（重要）
Codex が生成するHTMLは `.slide` div に `1920×1080` を設定するが、
`html, body` に設定しないことがある。
プロンプトで明示的に `html, body` への設定を要求すること：

```
html, body { width: 1920px; height: 1080px; overflow: hidden; margin: 0; }
```

### PNG化について
- Playwright は `libatspi` の問題でこの環境では動かない
- 代替: Codex の `image_gen` をスクリーンショットモードで使う（要検証）
- または: html2pptx.app でブラウザ経由で変換

---

## 出力例

- `reference-design.png` — 1.1MB、マッキンゼー風コンサル資料スタイル
- `slide-background.html` — 427行、グラデーション・カードアクセントライン・シャドウ付き

生成されたHTMLのCSS品質（グラデーション・カード上部のアクセントライン・シャドウ・
タイポグラフィ階層）は手書きより明らかに高い。
