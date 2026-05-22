# PowerPoint Handoff — slide-making

HTML スライドを PowerPoint に渡す手順。用途に応じて 3 つの方法を選ぶ。

---

## 3 通りの方法

| 方法 | 出力 | 編集可否 | 依存 |
|------|------|---------|------|
| A. Snipping Tool（手動） | PNG（画面解像度） | 不可 | なし |
| B. Playwright（自動・推奨） | PNG 3840×2160 | 不可 | playwright |
| C. html2pptx.app（API） | .pptx（編集可能） | 可（テキスト・図形） | httpx + API キー |

---

## 方法 A — Snipping Tool

1. Chrome / Edge でファイルを開く
   `file:///C:/path/to/slide-01.html`

2. ブラウザウィンドウを 1920px 幅に調整する

3. Windows キー + Shift + S → 四角形の領域でスライド全体を選択

4. PowerPoint に Ctrl+V で貼付

---

## 方法 B — Playwright（推奨）

### 初回セットアップ

```powershell
uv run playwright install chromium
```

### 変換

```powershell
# 1枚変換（3840×2160 出力）
uv run skills/slide-making/scripts/render_slide.py --input slide-01.html --output slide-01.png

# バッチ変換
uv run skills/slide-making/scripts/render_slide.py --input "slides/*.html" --output-dir ./png

# 等倍（1920×1080）
uv run scripts/render_slide.py --input slide-01.html --output slide-01.png --scale 1
```

---

## 方法 C — html2pptx.app（編集可能 .pptx）

テキスト・図形を PowerPoint 上で後から編集したい場合に使う。

### 前提

```powershell
$env:HTML2PPTX_API_KEY = "sk_live_xxxx"  # https://html2pptx.app で取得
```

### 変換

```powershell
# 1枚変換
uv run skills/slide-making/scripts/export_to_pptx.py --input slide-01.html --output slide-01.pptx

# バッチ変換（複数スライドを1つの.pptxに）
uv run skills/slide-making/scripts/export_to_pptx.py --input "slides/*.html" --output deck.pptx
```

**注意:** 変換精度は CSS 解釈に依存するため複雑なレイアウトはズレる場合がある。詳細は `references/html2pptx-guide.md` 参照。

---

## PowerPoint への貼付（方法 A/B の場合）

1. 「挿入」→「画像」→「このデバイス」で PNG を選択
2. 「書式」→「サイズ」で幅 `33.87cm`（13.33インチ、16:9フル幅）に設定
3. 位置を左上 `(0, 0)` に合わせる

---

## 推奨ワークフロー

### デザイン完全保持（PNG 貼付）
```
1. fetch_icon.py でアイコンをキャッシュ
2. ブラウザで file:// 開いて目視確認
3. render_slide.py で PNG 化（--scale 2）
4. PowerPoint に挿入 → 幅 33.87cm / 位置 (0,0)
```

### 編集可能 .pptx（html2pptx.app 使用）
```
1. $env:HTML2PPTX_API_KEY = "sk_live_xxxx"
2. ブラウザで file:// 開いて目視確認
3. export_to_pptx.py --input "slides/*.html" --output deck.pptx
4. deck.pptx を PowerPoint で開いて確認・編集
```

---

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| フォントが違う | オンラインで一度開いて Google Fonts をキャッシュさせる |
| アイコンが表示されない | `fetch_icon.py` でキャッシュを事前生成する |
| 貼付後にボケる | `--scale 2` 以上で再取得 |
| グラフが表示されない | `--wait 500` で待機時間を増やす |
| .pptx のレイアウトがズレる | html2pptx は CSS 解釈依存。複雑なレイアウトは方法 B（PNG）推奨 |
