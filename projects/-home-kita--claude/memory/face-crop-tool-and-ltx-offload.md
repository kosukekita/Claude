---
name: face-crop-tool-and-ltx-offload
description: face_crop.py (YuNet顔検出で首から下だけ残す再利用ツール) と LTX-2.3のOOM真因は解像度²×frames(frames数でない)。241f(10秒)も max-side を下げれば --offload model で完走可
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

**LTX-2.3 の OOM 真因は解像度²×frames（frames数そのものではない）**（2026-06-23 訂正、Codex診断で確定）。アテンション中間テンソルは `frames × (W/32 × H/32)` のトークン数に比例。**`gen_ltx23_lora.py` の `--max-side` 既定 1152 が高すぎる**のが OOM の主因で、縦長入力(832x1216)だと 768x1152 になり、ここで 193f すら step 突入時(transformer norm1)に CUDA OOM。**`--max-side 704`（→480x704 等）に下げれば 241f(10秒@24fps) が `--offload model` で問題なく完走**（A6000単枚, ~47.5GB常駐, GPU100%, 約20.7s/step×30=step約10分+重みロード5分。検証済み: 241f×2本を各完走→ffmpeg concatで20秒納品）。**`--offload sequential` は不要**（むしろ step0 で固まり実用外。以前「sequential必須」と書いたのは誤りで、真因は解像度だった）。VAE tiling は `--offload model` 時に既に有効(script line264)だがOOM箇所はデコード前なので無関係。長尺の作法: **解像度を下げて 241f(10秒)を直接出す** か、10秒×2連結（part1の最終フレーム `ffmpeg -sseof -0.1 -update 1` で抽出→次の `--image` にチェーンi2v→繋ぎ目シームレス、ffmpeg concat demuxer `-c copy` で無劣化結合）。`--num-frames` は 8k+1（121/193/241…）。実測の max-side 目安（A6000 48GB, --offload model）: 241f(10秒)=704まで / 121f(5秒)=896まで通る。**121f(5秒)でも max-side 1152 はOOM**（解像度²×frames の裏付け＝frames が半分でも解像度を上げると落ちる）。OOM失敗後は次の起動前に必ず `ps`で残プロセス無し+`nvidia-smi`でGPU解放(各48.6GB free)を確認してから再実行（残骸が残ると連続OOM）。

関連: [[video-media-studio-skill]] [[ltx2-community-models-are-loras]] [[grok-prompt-keep-japanese]]。Grok image_gen は `--always-approve --max-turns 12` を付けないとヘッドレスでツール未発火(toolnotcalled)になりやすい。`--effort` はデフォルトモデル grok-composer-2.5-fast 非対応で400。Codexは実在人物参照＋トップレスを拒否（ローカルZ-Imageが確実）。
