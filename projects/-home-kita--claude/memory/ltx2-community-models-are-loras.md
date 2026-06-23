---
name: ltx2-community-models-are-loras
description: "Community \"LTX-2.x models\" on HF are usually LoRAs, not full bases; stack on official LTX-2.3 via gen_ltx23_lora.py"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7a2f0ae3-e31e-4f93-8099-9825070ab91a
---

HF 上の "LTX-2.x モデル"（例 `lynaNSFW/LTX2.3_NSFW_motion`, `lynaNSFW/LTX2BFN`, `oumoumad/LTX-2-19b-LoRA-SPROUT`）は**単独フルモデルではなく LoRA**（単一 safetensors、キーは `diffusion_model.transformer_blocks.N.*.lora_A/B.weight`）。`base_model:` タグが別 LoRA を指すチェーン（NSFW_motion → LTX2BFN → SPROUT → Lightricks/LTX-2）になっていても、**唯一のフル base は `Lightricks/LTX-2` = diffusers の `diffusers/LTX-2.3-Diffusers`**。

**設定の正解**: フル base を差し替えるのではなく、公式 base に LoRA を `--lora` でスタックする。`video-media-studio` スキルに `scripts/gen_ltx23_lora.py` を新設（`gen_ltx23.py` + `load_lora_weights` 複数枚スタック・`--lora-scale` strength・`--nsfw-motion` ショートカット）。diffusers の `LTX2LoraLoaderMixin`（`_convert_non_diffusers_ltx2_lora_to_diffusers`, `non_diffusers_prefix='diffusion_model'`）が `diffusion_model.` プレフィックスを `transformer.` に自動変換 → ComfyUI/wan2gp 不要で `load_lora_weights()` 直接ロード。NSFW_motion は rank64・bf16・2496テンソル（audio_attn/audio_to_video_attn 含む）を全変換できることを実機確認。作者推奨 strength は 0.7。

**offload は `model` が正解（罠）**: `--offload sequential` は LTX-2.3 22B だと層を毎ステップ CPU↔GPU swap するため step0 で10分以上固まり実用外。`--offload model`（コンポーネント単位オフロード・22B transformer は 48GB A6000 に常駐）を使う。`none` は ~44GB+ 必要。`diffusers/LTX-2.3-Diffusers` は HF キャッシュ済み。

**実機の生成速度（A6000・model offload）**: 解像度依存が大きい。低解像 416x768/49f は数秒/step だが、本番 640x1152/121f/30step では **~23.6s/step → 全体約12分**（i2v from Grok 720x1280, NSFW_motion scale0.7, cfg3.0/rescale0.7, 音声48kHz付き 5.04秒mp4 を生成、2026-06-23 実証）。run_in_background 推奨。`av(PyAV)` 依存追加済み（音声 mux 用）。

関連: [[video-media-studio-skill]]。LTX-2.3 i2v は diffusers の `LTX2ImageToVideoPipeline` 対応（t2v は従来どおり `gen_video_ltx2.py` の公式 ltx_pipelines・専用 venv）。
