---
name: face-blur-tool-default-strength
description: 顔ぼかしツールface_blur.py(YuNet検出→楕円フェザーblur/pixelate)。ユーザー既定strength=0.4
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 94a9eabd-f430-420d-a163-ed1231755d7f
---

生成画像の顔を匿名化するツール `face_blur.py` を video-media-studio スキルに追加(2026-06-27)。
パス: `/home/kita/.claude/skills/video-media-studio/scripts/face_blur.py`

**機能**: OpenCV YuNet(`cv2.FaceDetectorYN`, モデルは同スキルの `models/face_detection_yunet_2023mar.onnx`)で顔を検出し、**bboxの形に合わせた楕円フェザーマスク**で顔領域だけぼかす。横顔/部分的に切れた顔は score を 0.6→0.5→0.4→0.3 と自動で下げて再検出。複数顔は全部処理。
- `--mode blur`(GaussianBlur, 既定) / `--mode pixelate`(モザイク)
- `--strength`(大きいほど強。blur=ぼかし量、pixelate=大きいほど粗ブロック)
- `--expand`(検出枠を各辺この割合で拡大、既定0.35) / `--score` / `--debug-box`

**★ユーザー既定: `--strength 0.4`**(2026-06-27確定)。0.4 = 顔の雰囲気はうっすら残しつつ匿名化される「極弱〜弱の中間」。スイープ0.20〜0.50を見せて本人が選択。スクリプトの argparse default も 0.4 に変更済みなので、**今後は `--strength` 無指定でこの強度**になる。強めたい時だけ明示指定。

**Why:** ユーザーは「AI生成と気づかれない実写風スナップ + 撮られちゃった演出」を作る。顔は完全に消すより薄く残す方が自然(盗撮/友人スナップのリアリティ)。

**How to apply:** 顔ぼかし依頼は `cd .../video-media-studio/scripts && uv run ./face_blur.py --in X --out Y`(strengthは既定0.4でよい)。形状は楕円(円ではない、ユーザー指示2026-06-27)。出力は ~/media-out へ([[image-cache-volatile-use-media-out]])。

関連: [[face-crop-tool-and-ltx-offload]](同スキルのYuNet顔crop別ツール), [[optimal-gen-models-table-and-new-model-eval]]
