# PowerPoint Handoff — slide-making

HTML スライドを画像化して PowerPoint に貼り付ける手順。

---

## 2 通りの方法

| 方法 | 解像度 | 依存 |
|------|--------|------|
| A. Snipping Tool（手動） | 画面解像度に依存 | なし |
| B. Playwright（自動・推奨） | 3840×2160 | playwright |

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

## PowerPoint への貼付

1. 「挿入」→「画像」→「このデバイス」で PNG を選択
2. 「書式」→「サイズ」で幅 `33.87cm`（13.33インチ、16:9フル幅）に設定
3. 位置を左上 `(0, 0)` に合わせる

---

## 推奨ワークフロー

```
1. fetch_icon.py でアイコンをキャッシュ
2. ブラウザで file:// 開いて目視確認
3. render_slide.py で PNG 化（--scale 2）
4. PowerPoint に挿入 → 幅 33.87cm / 位置 (0,0)
```

---

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| フォントが違う | オンラインで一度開いて Google Fonts をキャッシュさせる |
| アイコンが表示されない | `fetch_icon.py` でキャッシュを事前生成する |
| 貼付後にボケる | `--scale 2` 以上で再取得 |
| グラフが表示されない | `--wait 500` で待機時間を増やす |
