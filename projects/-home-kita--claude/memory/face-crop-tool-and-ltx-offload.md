---
name: face-crop-tool-and-ltx-offload
description: face_crop.py (YuNet顔検出で首から下だけ残す再利用ツール) と LTX-2.3の241フレームはmodel offloadだとOOM→sequential必須
metadata: 
  node_type: memory
  type: project
  originSessionId: 1fdf83d2-555b-436f-8214-734280823ac5
---

video-media-studio スキルに **`scripts/face_crop.py`** を追加（2026-06-23）。OpenCV YuNet で顔を検出し、口の上（あごライン）より上を自動トリミングして「首から下だけ」を残す再利用可能 CLI。i2v の入力前処理に使う。

**使い方**: `uv run scripts/face_crop.py --in img.png --out crop.png --mode chin --multi all [--debug]`
- `--mode chin`（既定）= 口の少し上で切り目鼻を消す。他に jaw/nose/eyes/hairline/keep-face。
- `--multi all`（既定）= 複数顔のうち最も下の顔基準で全員匿名化。`largest`/`highest` も可。
- `--margin 0.15` 等で切り位置を下げ微調整（鏡セルフィで上下にズレた2顔の片方の口が残るとき有効）。
- YuNet onnx は `scripts/models/face_detection_yunet_2023mar.onnx`（232589B, sha256 8f2383e4..）に同梱。DLは LFS media host (`media.githubusercontent.com/media/...`) でないと132Bポインタになる罠あり。

**LTX-2.3 の VRAM 実測（A6000 48GB, 832x672）**: 121フレーム=`--offload model`で収まる(~46GB)。**241フレーム(10秒@24fps)は `--offload model` だと CUDA OOM**（47.5GB使い切り）→ **`--offload sequential` 必須**（~24GBに低減するが大幅に遅い: 121f=8〜9分 vs 241f seq=40分強）。長尺はsequential、または5秒×2連結（part1の最終フレームを次の--imageにして繋ぎ、ffmpeg concatでstream-copy無劣化結合）を選ぶ。

関連: [[video-media-studio-skill]] [[ltx2-community-models-are-loras]] [[grok-prompt-keep-japanese]]。Grok image_gen は `--always-approve --max-turns 12` を付けないとヘッドレスでツール未発火(toolnotcalled)になりやすい。`--effort` はデフォルトモデル grok-composer-2.5-fast 非対応で400。Codexは実在人物参照＋トップレスを拒否（ローカルZ-Imageが確実）。
