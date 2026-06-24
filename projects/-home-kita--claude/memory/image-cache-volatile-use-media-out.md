---
name: image-cache-volatile-use-media-out
description: ~/.claude/image-cache はセッション中に自動クリアされる（生成物が消える）。永続させたい生成物は ~/media-out に出力する
metadata: 
  node_type: memory
  type: project
  originSessionId: 1fdf83d2-555b-436f-8214-734280823ac5
---

**`~/.claude/image-cache/` はセッション中に予告なく自動クリアされる**（2026-06-24 に実害確認）。長時間の生成中でも中身（生成済み画像/動画・入力画像・ログ・サブディレクトリ）が丸ごと消えることがある。日付が変わるタイミング等で発生した。

**How to apply**:
- 残したい生成物は **`~/media-out/`（image-cache の外、消えない）に直接出力する**。`--out /home/kita/media-out/xxx.png` のように。
- 走行中で出力先を変えられないジョブには、**完成検知→`~/media-out`へ即コピーするガード**（Monitorで `mkdir -p` し続けつつ、出力が出たらcpして退避）を付ける。実際これでWan動画(437KB)を消える前に確保できた。
- スキル本体のファイル（`~/.claude/skills/.../scripts/*.py` や reference/assets）は image-cache ではないので**消えない**（今回 face_crop.py / gen_qwen_edit.py / gen_wan_lora.py / male-body-reference.jpg は全て無事だった）。資産はスキル内、生成物は media-out、と置き場所を分ける。

**Why**: image-cache を一時作業場と見なすクリーンアップ機構があるらしい。長尺動画生成（Wanは1時間超）では完成前に消えるリスクが現実的。

関連: [[nsfw-models-chroma-noobai-wan-lora]] [[video-media-studio-skill]]
