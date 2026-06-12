# Codex GPT Image — パーツ生成ワークフロー

スライドの**パーツ（アイコン・イラスト・図版）だけ**を Codex の GPT Image で生成する手順。
**スライド全体やテキストは生成しない**（日本語テキストは焼き込むと崩れる）。テキストは必ず
HTML / python-pptx 側で正確に組む。

---

## 前提（現行・2026-06 時点）

- Codex CLI `0.132.0`、ChatGPT アカウント認証済み
- **既定は Codex の組み込み `image_gen` ツール**。`OPENAI_API_KEY` は**不要**（ChatGPT 認証で動く）
- 組み込みツールが画像を `$CODEX_HOME/generated_images/{session-id}/ig_*.png`（既定 `~/.codex/...`）に保存し、
  指示すれば作業ディレクトリへ `cp` する
- CLI フォールバック（`scripts/image_gen.py`）は**ユーザーが明示要求した時だけ**。既定モデル `gpt-image-2`、
  真の透過が必要な時のみ `gpt-image-1.5`（`--background transparent`）で、こちらは `OPENAI_API_KEY` が要る

> 旧版にあった「モデルは `gpt-5.5`」「Playwright は libatspi で動かない」は**誤り・古い**。現行は上記。
> Playwright は `scripts/render_slide.py` で正常動作する（PNG/PDF とも）。

---

## 基本フロー（不透明パーツ）

作業ディレクトリ（例 `slides/my-deck/`）配下に `parts/` を作り、そこへ生成物を集める。

```bash
codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  --cd "{出力ディレクトリ}" \
  "image_gen ツールで以下のパーツ画像を生成し parts/ に保存してください。
   テキスト・文字・数字は一切含めないこと（装飾/アイコン/図のみ）。

   1) parts/icon-cost.png — フラットなラインアイコン『上昇する矢印付きコスト』、
      単色 #0071BC、背景は白、1:1、余白少なめ
   2) parts/figure-flow.png — 4ステップの横並びフロー図（矢印のみ、ラベルなし）、
      モノクロ #1A1A1A、横長

   完了条件: parts/*.png が出力ディレクトリに存在し、各ファイルサイズを報告。
   HTML やスライドは作らないこと。"
```

> ⚠️ `--dangerously-bypass-approvals-and-sandbox` はサンドボックスを無効化する。
> プロンプトに含めるのは**信頼できるコンテンツのみ**。

生成後、`parts/*.png` を HTML では `<img src="parts/icon-cost.png">`、PPTX では spec の
`images[].path` に `"parts/icon-cost.png"` として渡す（原本 `$CODEX_HOME` 側ではなく、必ず
作業ディレクトリにコピーされた相対パスを使う）。

---

## 透過アイコン（背景を抜く）

組み込み `image_gen` は透過背景を直接は出さない。**フラットなクロマキー背景で生成 → ローカルで除去**する。

```bash
# 1) クロマキー背景（例 純緑 #00ff00）で生成
codex exec --dangerously-bypass-approvals-and-sandbox --cd "{出力ディレクトリ}" \
  "image_gen で『歯車のラインアイコン、単色 #1A1A1A、背景は一様な純緑 #00ff00、
   フラット、影なし、1:1』を parts/_raw-gear.png に保存。文字は含めない。"

# 2) クロマキー除去ヘルパーで透過 PNG 化（パスは Python で解決すると Windows でも安全）
CODEX_HOME_DIR=$(python3 -c "import os;print(os.environ.get('CODEX_HOME', os.path.expanduser('~/.codex')))")
python "$CODEX_HOME_DIR/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input parts/_raw-gear.png --out parts/gear.png \
  --auto-key border --soft-matte --despill
```

`remove_chroma_key.py` は Codex 同梱（既存・**改変禁止**）。`--auto-key border` で縁の色を自動採取し、
ソフトマット＋despill でアンチエイリアス境界をきれいに抜く。

真にネイティブな透過が必要（クロマキーで抜けない複雑な縁）なら、ユーザー確認の上で CLI フォールバック:
```bash
OPENAI_API_KEY=... python "$CODEX_HOME_DIR/skills/.system/imagegen/scripts/image_gen.py" \
  generate --model gpt-image-1.5 --background transparent --output-format png \
  --prompt "歯車のラインアイコン 単色 #1A1A1A 透過背景" --output parts/gear.png
```

---

## ベクターアイコンで足りる場合（GPT Image を使わない選択肢）

ブランドロゴや汎用ラインアイコンは、生成より `scripts/fetch_icon.py`（theSVG CDN）が速く確実:
```bash
uv run scripts/fetch_icon.py --slug github --variant default          # ブランドは原色保持
uv run scripts/fetch_icon.py --slug arrow-right --variant mono --recolor  # 装飾は currentColor 化
```
詳細は `references/thesvg-usage.md`。HTML パスなら SVG をそのままインライン/`<img>`、PPTX パスなら
一度 PNG 化してから `images[].path` に渡す。

---

## よくある失敗

| 失敗 | 対策 |
|------|------|
| テキストを画像に焼いて日本語が崩れる | パーツのみ生成。文字は HTML/PPTX 側。プロンプトに「no text / 文字なし」を明記 |
| `gpt-5.5` 等の古いモデルを指定 | 既定は組み込み `image_gen`（モデル指定不要）。CLI 時のみ `gpt-image-2` |
| `OPENAI_API_KEY` が必要と思い込む | 組み込みツールは不要。CLI フォールバック時のみ必要 |
| `$CODEX_HOME` 原本を直接参照 | 作業ディレクトリにコピーした `parts/*.png` を使う |
| 透過が白背景になる | クロマキー背景で生成 → `remove_chroma_key.py` で除去 |
