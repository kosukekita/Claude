---
name: feedback-slide-icon-approach
description: slide-makingスキルでアイコンが一致しない場合の確実な解決策（クロップ→base64埋め込み）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 74ac2027-d513-4203-b4db-bb125fe5dd2a
---

SVGでアイコンを手書きしても複雑な形状（棒グラフ+虫眼鏡・クリップボードなど）は必ず乖離する。3回失敗したらリファレンスPNGから直接クロップしてbase64埋め込みに切り替える。

**Why:** 2026-05スライド作成テストで全4アイコンが全て形状・サイズ不一致だった。SVGの繰り返し修正は収束しない根本的な限界。

**How to apply:**
1. PIL でリファレンスPNGからアイコン領域をクロップ（座標は目視測定）
2. `trim_whitespace()` で白余白を削除してアイコン本体のみに
3. base64エンコードして `icon_b64.json` に保存
4. Python f-string でHTML全体を再構築（正規表現置換は禁止 — imgタグ順序が崩れる）
5. Playwright でスクリーンショット → 目視確認

SKILL.md の Step 3-4 に完全な実装コードを記載済み（2026-05-23 追加）。
