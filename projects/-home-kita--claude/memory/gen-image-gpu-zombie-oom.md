---
name: gen-image-gpu-zombie-oom
description: 複数ローカル画像生成を並列起動すると死にきらない前ジョブがGPUを占有し後続がOOM。生成前にnvidia-smiでゾンビkill
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a3a2873e-92d6-4c87-bc86-9f743e3a0ff0
---

video-media-studio の `gen_image.py` を複数バックエンド（z-image / chroma / qwen / flux）で**並列に `run_in_background` 起動**すると、前のジョブの worker python が exit 通知後も死にきらずに GPU VRAM を占有し続け、後続ジョブが**論理 GPU0 上で VRAM 枯渇 OOM**することがある（実機: FLUX ログに「GPU 0 has 47.54GiB of which 46MiB is free / Process 1256548 has 23.78GiB in use」と出てゾンビ占有が確定。Qwen が "OOM" に見えたのも実はこれで、ゾンビ掃除後は単独なら native で動く見込み）。`CUDA_VISIBLE_DEVICES=1` を付けても、ゾンビが物理 GPU1 を握っていれば同じ物理 GPU 上で競合する。

**Why:** harness の background task 完了通知（exit 0）と worker プロセスの実体終了が**ずれる**ことがあり、「通知が来た＝GPU が空いた」とは限らない。通知だけ信じて次を起動すると食い合う。

**How to apply:**
- 新しいローカル生成を起動する**前に必ず** `nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader` と `ps aux | grep gen_image` でゾンビを確認し、残っていれば `kill -9 <pid>`（worker + 親 uv + 親 bash の3階層）してから起動する。
- ファイル未生成なのに `saved`/`exit=` がログに無い → worker が SIGKILL/OOM で死んだサイン。`gen_image.py` は OOM 時に grok-media 委譲メッセージ（"falling back to grok-media"）をログ末尾に吐くので、それを grep すれば OOM 確定。
- 完了判定は通知でなく**出力 PNG の存在 + ログの `saved ->`** で行う（[[image-cache-volatile-use-media-out]] と同じ「ログでなく実ファイルで判定」の原則）。
- 安全策: GPU を食い合わせないなら**並列せず逐次**起動する（96GB リグでも単一 GPU を順番に使う方が確実）。
