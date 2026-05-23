# リファレンスPNGクロップ方式 — アイコン base64 埋め込み手順

SVGで複雑なアイコン（棒グラフ+虫眼鏡、クリップボード+戦略図 など）を再現しようとすると、
形状・サイズ・太さの細部が必ず乖離する。これは原理的な限界であり、繰り返しても収束しない。

**発動条件**: 同じアイコンを3回修正しても目視で改善が見られない場合。

**解決策**: リファレンスPNGからアイコン領域を直接クロップして base64 埋め込みする。
これによりピクセル単位の完全一致が保証される。

---

## Step A: アイコン座標を特定してクロップ

```python
# uv run --with pillow python crop_icons.py
import os, base64, io, json
from PIL import Image

# パスを環境に合わせて変更
ref_path = r"C:\Users螒\slides\my-deck\reference-01.png"
temp_dir = r"C:\temp"

ref = Image.open(ref_path)
print(f"Reference size: {ref.size}")  # 実際のサイズを確認して座標を計算

# 各アイコン領域のクロップ座標（リファレンス画像を目視で測定）
# 例: 4枚カードの場合、各カード中心X ± 幅、アイコンY範囲
crops = {
    'icon1': (left1, top1, right1, bot1),
    'icon2': (left2, top2, right2, bot2),
    'icon3': (left3, top3, right3, bot3),
    'icon4': (left4, top4, right4, bot4),
}

icons = {}
for key, bbox in crops.items():
    crop = ref.crop(bbox)
    icons[key] = crop
    crop.save(os.path.join(temp_dir, f"{key}_check.png"))  # 確認用
    print(f"{key}: {crop.size}")
```

> **座標の決め方**: PIL で `ref.size` を確認 → 参照画像を目視して各アイコンのX中心・Y範囲を推定。
> タイトルテキストを含めないよう、アイコン本体より少し内側から始める。
> クロップ画像を Read ツールで確認してから次に進む。

---

## Step B: 白余白をトリミングしてアイコン本体だけに

```python
import numpy as np

def trim_whitespace(img, threshold=240, padding=15):
    arr = np.array(img)
    is_content = ~((arr[:,:,0] > threshold) & (arr[:,:,1] > threshold) & (arr[:,:,2] > threshold))
    rows = np.any(is_content, axis=1)
    cols = np.any(is_content, axis=0)
    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    r0, r1 = max(0, r0-padding), min(arr.shape[0]-1, r1+padding)
    c0, c1 = max(0, c0-padding), min(arr.shape[1]-1, c1+padding)
    return img.crop((c0, r0, c1+1, r1+1))

trimmed = {}
for key, img in icons.items():
    t = trim_whitespace(img)
    trimmed[key] = t
    print(f"{key}: {img.size} → trimmed {t.size}")
```

> `object-fit: contain` が白余白込みで縮小するためアイコンが小さく見える。
> 必ずトリミングしてから base64 化すること。

---

## Step C: base64 エンコードして JSON に保存

```python
b64_icons = {}
for key, img in trimmed.items():
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    b64_icons[key] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

json_path = r"C:\Users螒\slides\my-deck\icon_b64.json"
with open(json_path, 'w') as f:
    json.dump(b64_icons, f)
print(f"Saved {list(b64_icons.keys())} to icon_b64.json")
```

---

## Step D: HTML を Python f-string で全体再構築（正規表現置換は禁止）

```python
with open(json_path, 'r') as f:
    icons = json.load(f)

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  ...（CSS等）
</head>
<body>
  <section class="slide">
    <div class="step-card">
      <div class="step-icon"><img src="{icons['icon1']}" alt="" style="width:80px;height:80px;object-fit:contain;"></div>
    </div>
    <div class="arrow"><img src="{icons['arrow']}" alt=""></div>
    <div class="step-card">
      <div class="step-icon"><img src="{icons['icon2']}" alt="" style="width:80px;height:80px;object-fit:contain;"></div>
    </div>
  </section>
</body>
</html>"""

html_path = r"C:\Users螒\slides\my-deck\slide-01.html"
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
```

> **⚠️ 正規表現による img src 置換は禁止。**
> HTMLに複数の base64 img タグがある場合、置換スクリプトが「出現順」で差し替えるため
> アイコンと矢印の順序が崩れる。必ず f-string で変数を直接埋め込んで HTML を全体再構築すること。

---

## Step E: スクリーンショット → 目視確認 → 座標微調整

1. Playwright でスクリーンショットを取得
2. 「タイトルテキストが混入している」「アイコンが切れている」場合は座標を調整して Step A からやり直す
3. 全項目 PASS になるまで繰り返す
