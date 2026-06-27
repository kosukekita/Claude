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

## 動画版 face_blur_video.py(2026-06-27追加)
動画の顔ぼかしは **`face_blur_video.py`**(同スキルscripts/)。全フレームをYuNetで検出→各フレーム顔追従で楕円ぼかし→**元動画の音声をffmpegでmuxして保持**→libx264 crf18で再エンコード。既定 --strength 0.4・--mode blur(pixelate可)、`--hold N`(検出漏れ時に直前検出をNフレーム流用しちらつき防止、既定6)。`uv run ./face_blur_video.py --in X.mp4 --out Y.mp4`。実証: wan-2.7の150f/5s動画で150/150フレーム顔検出・追従成功(顔がカメラ最接近する場面も枠が追従)。顔が動く動画でも静止画のぼかしは追従しないので必ずこの動画版を使う。

関連: [[face-crop-tool-and-ltx-offload]](同スキルのYuNet顔crop別ツール), [[optimal-gen-models-table-and-new-model-eval]]
