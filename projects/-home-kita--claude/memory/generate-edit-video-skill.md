---
name: generate-edit-video-skill
description: new local-GPU-first video/image gen+edit skill; backend auto-select chain (probe_vram->probe_backend->gen_video) verified on A6000x2
metadata: 
  node_type: memory
  type: project
  originSessionId: 90ddda0a-24a1-4fc1-a7a7-1dd0531ce4a3
---

`~/.claude/skills/generate-edit-video/` — digitalsamba/claude-code-video-toolkit を土台に新規作成した動画/画像の生成・編集スキル（2026-06-22）。

**設計の核**: LOCAL-GPU-FIRST + graceful fallback。優先順位 `local-single > local-offload > local-multi(Wan only, 公式torchrun) > cloud-modal > cloud-fal > grok`。
- バックエンド選択は LLM の頭でやらず機械的に: `gen_video.py --backend auto` が subprocess で `probe_backend.py`（モデル認識・models.py 参照）を呼び、それが `probe_vram.py`（stdlib・nvidia-smi 実測）を呼ぶ。出力JSON契約 = `{backend,device,precision,offload,multigpu,model,why}`。**この3スクリプト連鎖は実機 A6000×2 でE2E動作確認済み**。
- 生成: Wan(diffusers)・LTX-Video 0.9.x(diffusers)・LTX-2.3(`gen_video_ltx2.py`・diffusers未対応で公式ltx_pipelines)・ローカル画像(FLUX.1/SDXL のみ実装)。Grok は **grok-media スキルに委譲**（`grok_delegate.sh` は signpost のみ、再実装しない）。Z-Image/Qwen-Image/FLUX.2/SD3.5 はローカル未実装→cloud/grok。
- 編集: `edit_video.py`(ffmpegラッパ, yuv420p/偶数寸法/+faststart/-shortest 既定) + `reference/ffmpeg-recipes.md`。
- クラウド退避: `cloud_modal.py`(Modal, gpu=["H100","A100-80GB","A100-40GB","L40S","A10G"] ← "any"は無効型) / `cloud_fal.py`(fal.ai, models.py の fal_id 使用)。

**環境事実（このPC）**: RTX A6000 ×2 = 各48GB(free ~47.5-48.6GB)・合計96GB, driver CUDA 12.2, Ampere(FA3不可→SDPA/xformers, fp8はVRAM節約のみ)。uv=/home/kita/.local/bin/uv, ffmpeg 6.1.1, disk 217GB free, RAM 251GB。

**conda LD汚染は実害あり（確認済み）**: anaconda の libtinfo.so.6 が LD_LIBRARY_PATH を汚染し subprocess を壊す。全スクリプトは `scripts/env.sh` を source して conda パスを LD から除去してから実行する。bash 起動毎に警告が出るのもこれ。[[slide-making-skill-v2]] の soffice 破壊と同根。

作成手順は Workflow 2本（設計+第1次生成17agent / 欠落ファイル生成+検証22agent）。スキル名・ファイル名の不整合は手で修復した。

**実機 E2E 検証（2026-06-22）— 両バックエンド動作確認済み**:
- **CUDA 12.2 ドライバ非互換の実害（重要）**: PEP723 の無印 `torch` は新しい CUDA ランタイム要求の wheel を入れ、このPCのドライバ CUDA 12.2(12020) で `RuntimeError: NVIDIA driver too old (found 12020)` で推論直前に落ちる。**修正済み**: gen_image.py / gen_video.py / gen_video_ltx2.py の PEP723 に `torch==2.5.1` + `[tool.uv.sources] torch={index="pytorch-cu121"}` + cu121 index を追加。`torch 2.5.1+cu121` は 12.2 ドライバで cuda available=True・matmul OK を確認。setup.md も実測事実に更新。cu124 でなく **cu121 が verified-good**。
- **FLUX.1-dev / SDXL は既に HF キャッシュにDL済み**（~/.cache/huggingface/hub, 既存307GB。Qwen2.5-72B 136GB / FLUX.2-dev 121GB 等もあり、空き217GB）。FLUX.1-dev で 832x1216 を A6000(33GB,100%)・約1.17it/s で生成成功。
- **FLUX の日本語プロンプト弱点**: CLIP テキストエンコーダが 77トークンで切り捨て（T5側は長文OK）。長い日本語は英語化推奨。
- **Grok は grok-media に委譲**。このPC(Linux)に Grok CLI 未導入だったので `curl -fsSL https://x.ai/cli/install.sh | bash` で導入(v0.2.60, ~/.grok/bin/grok)。**スマホ/リモート環境のログインは `grok login --device-auth`（公式に headless/remote 用）が有効**: PCで出る URL+code をスマホのXログイン済みブラウザで承認すれば完走する（`!`経由でなく background 起動で URL を取り出して提示する形でも成立した）。出力は cwd でなく `~/.grok/sessions/<enc-cwd>/<sid>/images/N.jpg` に出る（grok-media の回収手順通り）。ログイン: u879269j@yahoo.co.jp。

[[slide-making-skill-v2]]（同じ conda LD 汚染問題）, [[grok-media]] 連携。
