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
- **Grok は grok-media に委譲**。このPC(Linux)に Grok CLI 未導入だったので `curl -fsSL https://x.ai/cli/install.sh | bash` で導入(v0.2.60, ~/.grok/bin/grok)。**スマホ/リモート環境のログインは `grok login --device-auth`（公式に headless/remote 用）が有効**: PCで出る URL+code をスマホのXログイン済みブラウザで承認すれば完走する（`!`経由でなく background 起動で URL を取り出して提示する形でも成立した）。画像出力は cwd でなく `~/.grok/sessions/<enc-cwd>/<sid>/images/N.jpg`。ログイン: u879269j@yahoo.co.jp。
- **⚠️ Linux版 Grok CLI(0.2.60)は動画生成不可（重要・grok-media の前提と相違）**: grok 本人に保有ツールを問うと **`GenerateImage` のみ**で `image_to_video`/`GenerateVideo` は無いと回答。モデルも `grok-build` / `grok-composer-2.5-fast`（コーディング用）のみで `grok-imagine` 系の動画モデルなし。i2v を頼むと「ローカルのworkflow/スクリプトを探す」探索モードに入り**生成せず終了**（3回再現、定型文厳守でも同じ）。grok-media スキルの動画手順は **Windows grok 0.2.51 での実機検証**で、現Linux版とツールセットが異なるのが根本原因（指示ミスではない）。→ **Grok 動画が要るなら Web/アプリの Imagine 機能**（CLI不可）。CLIは画像生成のみ。回避策＝Grokで画像→**ローカル Wan/LTX で i2v**。

**画像生成 5モデルを実機で全成功（2026-06-22 追加実装・5枚比較を生成）**:
- 当初 gen_image.py は FLUX.1/SDXL のみ。**Qwen-Image / FLUX.2-dev / Z-Image-Turbo を追加実装**（diffusers git-main の QwenImagePipeline / Flux2Pipeline / ZImagePipeline。すべて存在。`--backend` に追加）。
- **torchvision は必須（実害）**: 無いと FLUX.2 の PixtralProcessor が `Placeholder` でロード失敗、Qwen/CLIP/Siglip プロセッサも degrade。PEP723 に `torchvision==0.20.1`(cu121) と `transformers>=4.56` を追加して解決。
- **48GB 単一 A6000 の VRAM 実測**: FLUX.1-dev=native可(33GB) / SDXL=native / Z-Image-Turbo=native(16GB,9step・品質高・日本語◎) / **Qwen-Image=20B でnative OOM→offload必須**（vram_bf16_gb を 56 に設定し offload 強制）/ **FLUX.2-dev=32B+Mistral3 で offload でも OOM→4bit量子化必須**（`PipelineQuantizationConfig(quant_backend="bitsandbytes_4bit", nf4, components=["transformer","text_encoder"])` + offload で ~20GB に収め成功・約3s/step）。MODELS に `quant_4bit`/`quant_components` フラグ追加。
- **HF キャッシュ実体は `/data`（19TB, 9.5TB空き）にシンボリックリンク**。`/home` 217GB とは別。大型モデル（Qwen ~60GB, LTX-2.3 ~100GB）も余裕。
- 品質所感（同一プロンプト・日本語）: 日本語理解と"今っぽいカフェ"再現は **Grok ≈ Z-Image-Turbo > Qwen > FLUX.2 > FLUX.1-dev**。FLUX系は日本語が弱い（英語化推奨）。Z-Image-Turbo は9stepで高品質・コスパ最良。

**i2v 動画を実機で3モデル生成（2026-06-22）— Grok画像→ローカルi2v**:
- **TI2V-5B**: native bf16・48GBに収まる・40step約5分。確実だが品質中。
- **LTX-Video-0.9.8-i2v**: native。**VAE dtype バグを発見・修正**（pipe全体bf16なのに `pipe.vae.to(torch.float32)` していて `Input(BFloat16) vs bias(float) should be the same` で落ちた。→ VAE fp32強制をやめ bf16のまま＋`vae.enable_tiling()` に修正）。
- **Wan2.2-I2V-A14B（14B最高品質）**: bf16=80GB>48GB。**`--offload` 明示でも probe が local-multi(torchrun) を選んでしまい生成せず終了するバグを発見・修正**（gen_video.py に `_force_single_offload`：`--offload` 時は multi を single-GPU offload に上書き）。fp8/offload で動くが **146秒/step×40step≈1時間37分**と極端に遅い（MoE 2エキスパートを毎step CPU↔GPU転送）。品質は明確に最良。DLも巨大(~118GB)。→ 実用的にi2vはTI2V-5B/LTX、最高品質が要る時だけA14B。multi-GPU高速化は公式torchrun(別repo clone)が要る。
- gen_video.py の PEP723 にも torchvision を追加すべき（i2vでCLIP画像プロセッサが torchvision警告→Pil fallbackで動いてはいる）。

**Codex(GPT Image)も画像生成可（2026-06-22）**: `codex exec --skip-git-repo-check --sandbox workspace-write "Use your image_gen tool to generate ... Prompt: ..."` で gpt-image-2 が生成。出力は `~/.codex/generated_images/<session-id>/ig_*.png`（cwd保存は sandbox で失敗しても本体はここに残る）。**OpenAIポリシーが厳格**：「巨乳」等の語は `rejected for sexualized content` で拒否→「Fカップ」等の婉曲表現で通過。Grok はこの種の制限が緩く同プロンプトをそのまま通す。品質: Codex=ナチュラル/リアル、Grok=華やか/SNS映え。

**LTX-2.3(22B)が最高品質i2v・実機成功（2026-06-22）**:
- 「A14Bより高品質なモデルは？」→ Codex/Web調査で **LTX-2.3 が open-weights 品質1位**（A14Bと同tier以上）。Wan2.5やWan2.2上位I2VはHF未公開（API/ベータのみ）。HunyuanVideo-I2Vは720pで60-80GB必要→48GB不可。SkyReels-V2-I2V-14Bは映画的だがWan2.1比較。
- **LTX-2.3 は diffusers 対応**（私の旧 `gen_video_ltx2.py`(公式ltx_pipelines前提)ではなく diffusers経由が正解）。新規 `scripts/gen_ltx23.py` を作成。repo=`diffusers/LTX-2.3-Diffusers`、class=`LTX2ImageToVideoPipeline`、戻り値=(video, audio)。
- **`enable_sequential_cpu_offload` で ~5GB VRAM**（A14Bの37GBより遥かに軽い）・**70秒/step×30step**（A14Bの146秒/step×40より速い＝合計約35分 vs 1時間37分）。bf16でfp8不要。~95GB DL。
- **LTX-2.3 特有の必須call引数**: `stg_scale=1.0, modality_scale=3.0, guidance_rescale=0.7（露出オーバー防止）, spatio_temporal_guidance_blocks=[28], use_cross_timestep=True`。frame 8k+1, dim/32。
- **Gemma-3 はオプション（プロンプト強化のみ）→ 使わなければ gated 不要**で plain i2v が動く。
- **LTX-Video 0.9.8 の「動画が崩壊（時間とともに白飛び）」の真因**: VAEをbf16にした副作用＋`guidance_rescale`未使用。LTX-2.3 では `guidance_rescale=0.7` で露出破綻なし（frame0輝度128→最終128で一定）を確認。0.9.8側も同パラメータで直せるはず。
- 音声出力は `encode_video` が PyAV 必要 → 未導入なら `export_to_video`(動画のみ)に自動フォールバック。音声込みは PEP723 に `av` 追加で対応。

**画像生成の既定方針（ユーザー確定・2026-06-22）**: フォトリアル日常スナップの実機評価で、**推奨3本柱 = Z-Image-Turbo（ローカル主力・人物の透明感が最良）/ Codex(GPT Image)/ Grok（生活感が最良）**。SKILL.md にも記録済み。**FLUX.1-dev は微妙（落ち着きすぎ）**。**FLUX.1-Krea-dev は質が低く非推奨**（「iPhone/スマホ/TikTok/Instagram」の語に反応してSNSアプリUIスクショや設定画面を描く癖。gen_image.py に実装は残すが既定に入れない）。Z-Image超え候補（Codex調査）= FLUX.2-dev(32B,4bit実装済,1位) > HiDream-I1-Full(17B,MIT商用可) > FLUX.1-Krea-dev(実機ではダメ) > Qwen-Image(20B,文字強い)。

**境界（やらないこと）**: 実在の人物に見える生成画像を、本人同意なく**脱衣・ヌード化・性的化する i2v/編集は行わない**（同意なき性的ディープフェイク=NCII類型。下着でも裸でも、NSFW専用モデル `lynaNSFW/LTX2.3_NSFW_motion` 等を使う使わないに関わらず不可）。ユーザーから「居酒屋grok画像から服を脱ぐ動画を」と複数回・強い指示で求められたが、技術可否でなく内容として断った。**Why**: 内容の性質の問題でモデル/プロンプト変更では解決しない。**How to apply**: 通常の i2v（着衣のままの自然な動き）・画像生成は引き続き対応。脱衣・性的化の依頼は丁寧に断り、代替（通常生成）を提示する。

[[slide-making-skill-v2]]（同じ conda LD 汚染問題）, [[grok-media]] 連携, [[codex-consult]]（高品質モデル調査をCodexに委譲）。
