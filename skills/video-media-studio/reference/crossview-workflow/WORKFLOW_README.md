# LTX Video 2.3 — IC-LoRA CrossView Prompt (v1 pilot) WORKFLOW

**Model:** LTX Video 2.3 — 22B Dev (FP8) + distilled speed LoRA
**Type:** Video-to-Video

Video-to-Video workflow using LTX Video 2.3 with IC-LoRA (In-Context LoRA) guidance. A reference video clip is fed to the IC-LoRA guide, and the [CrossView IC-LoRA](https://huggingface.co/Cseti/LTX2.3-22B_IC-LoRA-CrossView-Prompt) re-renders the same scene from a new virtual camera angle described in the prompt — like a second camera on the same take. This is the **v1 pilot** checkpoint (step 13,700), run on the 22B **dev** transformer with the distilled speed LoRA and a 2x latent spatial upscaler.

---

## Preview

<video src="https://huggingface.co/datasets/Cseti/ComfyUI-Workflows/resolve/main/ltx/2.3/ic-lora-crossview-v1-pilot/media/preview-montage.mp4" controls width="720"></video>

Each clip shows the reference input on top and the new-angle generated output below.

<!-- Replace YOUTUBE_VIDEO_ID with your video ID after uploading -->
<!-- [![Watch on YouTube — click to open](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID) -->
<!-- *Click to open on YouTube* -->

---

## Requirements

- **ComfyUI:** recent stable build
- **Model:** `ltx-2.3-22b-dev_transformer_only_fp8_scaled.safetensors` — [Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/blob/main/diffusion_models/ltx-2.3-22b-dev_transformer_only_fp8_scaled.safetensors)
- **Distilled speed LoRA:** `ltx-2.3-22b-distilled-1.1_lora-dynamic_fro09_avg_rank_111_bf16.safetensors` — [Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/blob/main/loras/ltx-2.3-22b-distilled-1.1_lora-dynamic_fro09_avg_rank_111_bf16.safetensors)
- **Video VAE:** `LTX23_video_vae_bf16.safetensors` — [Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/blob/main/vae/LTX23_video_vae_bf16.safetensors)
- **Audio VAE:** `LTX23_audio_vae_bf16.safetensors` — [Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/blob/main/vae/LTX23_audio_vae_bf16.safetensors)
- **Preview VAE:** `taeltx2_3.safetensors` — [Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/blob/main/vae/taeltx2_3.safetensors)
- **Text encoder:** `gemma_3_12B_it_fp8_scaled.safetensors` — [Comfy-Org/ltx-2](https://huggingface.co/Comfy-Org/ltx-2/blob/main/split_files/text_encoders/gemma_3_12B_it_fp8_scaled.safetensors)
- **Text projection:** `ltx-2.3_text_projection_bf16.safetensors` — [Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/blob/main/text_encoders/ltx-2.3_text_projection_bf16.safetensors)
- **Spatial upscaler:** `ltx-2.3-spatial-upscaler-x2-1.1.safetensors` — [Lightricks/LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3/blob/main/ltx-2.3-spatial-upscaler-x2-1.1.safetensors)
- **IC-LoRA:** `lora_weights_step_13700.safetensors` — [Cseti/LTX2.3-22B_IC-LoRA-CrossView-Prompt](https://huggingface.co/Cseti/LTX2.3-22B_IC-LoRA-CrossView-Prompt)
- **Custom nodes:**
  - [ComfyUI-LTXVideo](https://github.com/Lightricks/ComfyUI-LTXVideo)
  - [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes)
  - [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)
  - [rgthree-comfy](https://github.com/rgthree/rgthree-comfy)
  - [RES4LYF](https://github.com/ClownsharkBatwing/RES4LYF)
  - [comfyui-int-and-float](https://github.com/danTheMonk/comfyui-int-and-float)

---

## Notes

- **Input:** a reference video clip is the IC-LoRA guide (loaded via the `Load Video` node). No start image is required for the angle change — the reference frame in this graph is only used to set the output resolution.
- **Prompt format:** prefix with the `crossview.` trigger, then describe the new camera angle on three axes: `crossview. new camera angle: <horizontal>, <height>, <distance>.` The LoRA was trained on the full 7×3×3 = 63-combination grid of these terms:
  - **horizontal:** `far to the left`, `to the left`, `slightly to the left`, `same angle`, `slightly to the right`, `to the right`, `far to the right`
  - **height:** `lower`, `same height`, `higher`
  - **distance:** `closer`, `same distance`, `further`
  - e.g. `crossview. new camera angle: slightly to the left, higher, closer.`
- **v1 pilot:** this is an early pilot checkpoint (step 13,700) — expect experimental results; angle following is not always reliable.
- IC-LoRA strength is set to `1.5` and the distilled speed LoRA to `0.6`.
- Two-pass: an 8-step base pass (~960x544, 241 frames @ 24fps, with audio) followed by a 2x latent spatial upscale pass.

---

## Changelog

- `2026-07-11` — Initial upload

---

## Training

This IC-LoRA was trained on [RunPod cloud GPUs](https://runpod.io?ref=vpp0cion).

---

## Support

Producing and sharing this kind of open-source work requires renting cloud GPUs, which gets expensive quickly. If you find it useful and would like me to keep contributing, your support is very much appreciated:

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/chetyart) [![Liberapay](https://img.shields.io/badge/Liberapay-Donate-F6C915?style=for-the-badge&logo=liberapay&logoColor=black)](https://liberapay.com/chetyart/donate)
