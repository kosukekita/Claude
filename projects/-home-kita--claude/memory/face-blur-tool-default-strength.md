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

## 動画版 face_blur_video.py(2026-06-27追加, 近接対応版に改良)
動画の顔ぼかしは **`face_blur_video.py`**(同スキルscripts/)。**2パス方式**: ①全フレームでYuNet検出(最大面積の顔を主顔とし小さい誤検出は無視)→②誤検出/欠落を**前後フレームから線形補間**→③枠を移動平均で時系列平滑化(ちらつき除去)→④**顔が大きいほどexpandを動的拡大**(近接時に髪/額/顎まで覆う)→⑤顔が画面の`--maxcover`(既定0.55)超なら**全画面ぼかしにクランプ**(確実に隠す)→楕円フェザーでぼかし→**元音声をffmpeg muxで保持**→libx264 crf18。`uv run ./face_blur_video.py --in X.mp4 --out Y.mp4`(既定strength 0.4)。

★**真因(2026-06-27実証・重要)**: 「顔アップで隠れない」のは未検出ではなく、近接フレームでYuNetが**本物の大きい顔(504x625等)と小さい誤検出(97x113=耳/首)を同時に返し、フレームによって小さい方を拾って顔がはみ出す**のが原因(検出スコアも大顔で0.3-0.6に低下し不安定)。対策=主顔は最大面積で選ぶ+サイズが局所中央値45%未満の枠は誤検出として捨て前後補間+全画面クランプ。単純な「最大スコア1個」では近接で破綻する。

★ユーザー指示(2026-06-27): 顔が画面の大半を占める近接フレームは**全画面ぼかしで確実に隠す**を優先(谷間/背景が一緒にぼけてよい)。顔だけ残したいなら--maxcoverを上げる。

## ★★接写の「顔が隠れないフレーム」真因と決定的対処(2026-06-27, 5回反復で確立)
動画で顔がカメラに極端に近づく(キス迫り等)と、**YuNetもInsightFace/SCRFDもメインの大きい顔を検出できなくなる**(顔がデカすぎて検出器の想定外)。実測: メイン顔がフレーム高さの50%を占めるf110で `maxfrac=0.001`(=背景の小さい他人しか検出できていない)。
**罠**: 背景の小さい他人の顔は検出されるので「検出数>0」になり、「検出ゼロなら全画面化」ロジックを**すり抜けて**、メイン顔が何もぼかされず露出する(これがユーザー指摘の"顔アップで隠れてないフレーム"の正体)。
**決定的対処**: 判定を「検出ゼロ」でなく **「メイン顔喪失」=このフレームの最大顔frac < bigfrac かつ 前後±12フレーム以内に大顔(frac>=bigfrac)が存在 → 全画面ぼかし**。これで接写区間が連続カバーされる。bigfrac=0.06(顔がフレーム面積6%超で大顔扱い)が実用値。face_blur_video.py に実装済(`big`/`lost`配列+窓判定+穴埋め)。InsightFace SCRFD(buffalo_l, det_size 960)は中遠距離の全顔検出はYuNetより上だが**接写破綻は同じ**=検出器を替えても接写問題は解決しない、判定ロジックで解くのが正解。
**背景の他人**: SCRFDで大半ぼかせるが極小顔は残る場合あり。メイン被写体の匿名化が目的なら上記で達成。全員消すは別途minfrac下げ+det-size上げ(ただし接写全画面化と両立調整要)。
**速度注意**: uv環境のonnxruntime-gpuが **CUDAExecutionProvider未認識→CPU推論にフォールバック**して激遅(150fで数分)。要修正(onnxruntime↔onnxruntime-gpu競合 or CUDA/cuDNNパス)。直せば10倍速。

関連: [[face-crop-tool-and-ltx-offload]](同スキルのYuNet顔crop別ツール), [[optimal-gen-models-table-and-new-model-eval]]
