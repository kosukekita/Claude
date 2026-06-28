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

**★2026-06-26 追加の落とし穴（実害あり、繰り返すな）:**
- **tail -f を Monitor に使うと「古いバッファの `saved ->` 行」を再生して誤検出する**。chroma が 19/40 ステップでまだ推論中なのに Monitor が `saved ->` を報告 → それを信じて「完了した」と誤認した。さらに**保存前のワーカーをゾンビと勘違いして `kill -9` し、生成中のジョブを SIGKILL（EXIT=137）で殺してファイルを失った**。
- 教訓1: **生成中か終了かは tail のログ行でなく `pgrep -f "gen_image.py --backend <X>"` でプロセスの生死を直接見る**。プロセスが生きている間は絶対に kill しない。STAT=Rl は実行中。
- 教訓2: **「ゾンビ」と断定する前に、それが今走らせているジョブ自身でないか必ず確認する**。chroma_run*.log を Read して進捗バー（`n/40`）が進んでいれば正常稼働中。kill するのは「自分が起動していない・前セッションの残骸で・かつ新規ジョブが OOM する」ときだけ。
- 教訓3: Monitor の完了条件は「`pgrep` が空 → 2秒待つ → 実 PNG の存在を stat で確認」の順にする。tail -f の途中行をトリガにしない。
- chroma は native(22GB)で steps=40・約90秒/枚。z-image-turbo は steps=9・約6秒/枚(ロード4.5分)。flux.2-dev は 70GB 要求で単一48GB には収まらず必ず offload(激遅)になる→比較に入れるなら時間覚悟か外す。

**★2026-06-28 動画(gen_video.py Wan ti2v-5b)でも同じゾンビOOM、画像より厄介:**
- ti2v-5bワーカーは**完了後もGPUを27GB掴んだまま死なない**。次の動画ジョブが即OOM(363KB等の壊れmp4が残る=ffprobeが空/exit254ならファイル破損のサイン)。
- **複数の動画ジョブを完了検知ミスで重複起動すると地獄**: Monitorのファイルサイズ/ログ検出は書き込み途中や前ジョブの値を誤検出しやすく、「DONE」と言われてもlsにファイルが無い/壊れが頻発。さらに**ゾンビkillのタイミングを誤ると進行中の正規ジョブを巻き込んで殺す**(local zimageが何度も消えた)。
- **確実な手順(動画local)**: ①1本ずつフォアグラウンド寄りで起動 ②`nvidia-smi --query-compute-apps`でPID確認、**前ジョブのゾンビを次の起動前にkill -9**(ただし"今走っている自分のジョブ"でないことをpgrep -afのcmd内容で確認してから) ③完了判定は「pgrepワーカー不在 AND ffprobeが寸法を返す(=壊れてない) AND サイズ>1MB」の3条件。bgの完了通知もMonitorのサイズ検出も単独では信用しない。④cloud(wan-2.7 API)はGPU不使用でこの問題と無縁→**急ぐ/確実性優先なら動画はcloud wan-2.7を主、localは比較用と割り切る**。
