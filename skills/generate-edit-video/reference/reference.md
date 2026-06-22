# reference.md — Backend & Model Reference (generate-edit-video)

Concise lookup for backend selection, model versions, install/setup, and troubleshooting.
For the prose flowchart rationale see `backend-selection.md`; for ffmpeg recipes see `ffmpeg-recipes.md`; for first-run setup see `setup.md`; for per-model deep dives see `models.md`. Single source of truth for thresholds = `scripts/models.py`.

---

## Verified environment (this rig)

- GPUs: 2x NVIDIA RTX A6000, 49140 MiB total / **~48666 MiB free each** (both idle), driver-level CUDA 12.2.
- Compute capability 8.6 (Ampere): SDPA/xformers attention; **no FlashAttention-3** (Hopper-only), native fp8 matmul limited (fp8 saves VRAM, speedup smaller than H100).
- Tooling: `uv` at `/home/kita/.local/bin/uv`, ffmpeg **6.1.1**, conda present (LD pollution risk — see troubleshooting).
- Disk: **217 GB free** on `/home`. RAM: 251 GB.
- Policy: **local-first**, cloud/Grok only as fallback. Always run `scripts/probe_backend.py` first; obey its JSON. Source `scripts/env.sh` before any python/ffmpeg call (cleans LD_LIBRARY_PATH, exports HF_HOME, sets `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`).

---

## Backend–model matrix

VRAM = approximate weight + activation peak. "Local on A6000 (48 GB)?" assumes one card unless noted. `*1.1` margin guards text-encoder spikes (T5-XXL / Mistral-24B / Qwen2.5-VL / Gemma-3).

| Backend | Model | Task | VRAM need | Local on A6000 (48 GB)? | Install / how | Fallback if it fails |
|---|---|---|---|---|---|---|
| local-single | wan2.1-t2v-1.3b | t2v | ~8–13 GB bf16 | YES, trivially (fast iter) | uv + diffusers git-main, `WanPipeline` | offload (rarely needed) |
| local-single | wan2.2-ti2v-5b | t2v/i2v 720p | ~24 GB w/ offload | YES (single card 720p@24fps) | diffusers, official 5B ckpt | cloud-fal wan-5b |
| local-single (fp8) | wan2.2-i2v-a14b / t2v-a14b | i2v/t2v | bf16 ~65–80 GB; fp8 ~40–50 GB | YES at fp8, 480p & 720p on one card | diffusers `WanImageToVideoPipeline`, fp8 cast, VAE fp32 | local-multi (torchrun) → cloud |
| local-multi | wan2.2-*-a14b | t2v/i2v 720p full | bf16 across 2 GPUs | YES (both idle): faster/full quality | OFFICIAL repo `torchrun --nproc_per_node=2 --ulysses_size 2 --dit_fsdp --t5_fsdp` | cloud-modal/fal |
| local-single | ltx-video-0.9.8 (13B/2B) | t2v/i2v | ~24 GB bf16; ~10 GB fp8+offload | YES easily | diffusers `LTXPipeline` (Apache-2.0, T5, no Gemma) | cloud-fal ltx |
| local-single (fp8) | ltx-2.3 (22B, +audio) | t2v/i2v/a2v | bf16 ~38–42 GB (48 GB ok); fp8 ~18–20 GB | YES (bf16 fits; fp8 safer) | `ltx_pipelines` (NOT diffusers) + gated Gemma-3, ~100 GB disk | cloud-fal ltx-2.3 → grok |
| local-single | flux.1-dev | t2i | ~24–33 GB bf16 | YES native (quality default) | diffusers `FluxPipeline`; **gated + non-commercial** | flux.1-schnell / cloud-fal |
| local-single | flux.1-schnell | t2i (1–4 step) | ~24 GB bf16 / 12 GB fp8 | YES (Apache-2.0, commercial OK) | diffusers, guidance 0 | cloud-fal flux |
| local-single | z-image-turbo | t2i (8–9 step) | ~16 GB bf16 / 8 GB fp8 | YES (fast, bilingual text) | diffusers **git-main** `ZImagePipeline`, guidance 0 | flux.1-schnell |
| local-single | qwen-image | t2i (in-image TEXT) | ~40 GB bf16 / 12–13 GB 4bit | YES (tight bf16 / use 4bit) | diffusers `QwenImagePipeline`, `transformers>=4.51.3` | sd3.5-large |
| local-single | sd3.5-large | t2i | ~18–20 GB bf16 | YES easily | diffusers `StableDiffusion3Pipeline` | sdxl / cloud |
| local-single (fp8/4bit) | flux.2-dev | t2i (newest, top quality) | bf16 >80 GB; fp8 ~32 GB; 4bit ~20 GB | YES at fp8/4bit on one card | diffusers **git-main** `Flux2Pipeline`, gated, sentencepiece+protobuf | flux.1-dev |
| cloud-modal | any above | all | provider GPU | n/a | `scripts/cloud_modal.py`, `MODAL_TOKEN_*`; H100/A100 per-sec | cloud-fal |
| cloud-fal | wan-2.2 / ltx-2.3 / flux | all | hosted | n/a | `scripts/cloud_fal.py`, `FAL_KEY`; per-output-sec | grok |
| grok (delegate) | image_gen / image_to_video / reference_to_video | t2i, i2v, ref2v (t2v=2-stage) | none (subscription) | n/a | **DELEGATE to grok-media skill** (OAuth, no metering) | (terminal fallback) |
| ffmpeg (local) | n/a (editing) | trim/concat/speed/subs/overlay/audio/resize/fps/frames/gif/thumb/reencode | CPU/GPU | YES (ffmpeg 6.1.1) | `scripts/edit_video.py` + `reference/ffmpeg-recipes.md` | — |

**Priority ladder** (probe descends it): local-single > local-with-offload > local-multi-GPU (Wan torchrun only) > cloud-modal > cloud-fal > grok. On this 96 GB rig almost everything is local-single; cloud/Grok are genuine last resort.

**Cloud pick (when VRAM short or GPU busy):** Modal = custom diffusers pipeline, cheapest GPU-sec, you maintain code (H100 ~$3.95/hr, A100-80GB ~$2.50/hr; $30/mo free credit). fal = hosted Wan/LTX/FLUX, fastest, per-output-sec (Wan2.2 t2v $0.04–0.08/s; LTX-2.3 $0.06–0.24/s). Grok = subscription quota, no metering, t2v as 2-stage image_gen→image_to_video.

---

## Latest model versions

### Wan (Alibaba Tongyi Wanxiang, `Wan-AI` on HF, Apache-2.0)

- **Wan2.1** (Feb 2025, open): T2V-1.3B (consumer-GPU favorite), T2V-14B, I2V-14B-480P/720P, FLF2V-14B-720P, VACE-1.3B/14B (controllable any-to-video).
- **Wan2.2** (Jul 2025, open, **CURRENT recommended local default**): MoE 27B-total/14B-active. **T2V-A14B**, **I2V-A14B** (two experts: high-noise + low-noise, one active per step). **TI2V-5B** (dense, unified t+i2v, 720p@24fps, single consumer GPU). Plus S2V-14B (speech), Animate-14B (character). Use the `*-Diffusers` repos for diffusers; plain `Wan-AI/Wan2.2-*` repos are for official `generate.py`.
- **Wan2.5** (Sep 2025): synchronized audio-visual, 1080p. **API/preview ONLY — no open weights. Do NOT plan local 2.5.**
- **Wan2.7** (~May 2026, open, Apache-2.0): newest open — T2V/I2V 14B (MoE lineage) + image gen/edit + instruction video edit + voice cloning. **Tooling/diffusers support lags 2.2.**
- **Sweet spot here:** Wan2.2-I2V-A14B / T2V-A14B (fp8 or bf16) for quality; Wan2.1-T2V-1.3B for fast iteration. Wan2.7 only if newest features needed.
- **Rules:** num_frames = **4k+1** (81 = 5s canonical). fps: A14B 16, TI2V-5B 24. flow_shift ~3.0 (480p) / ~5.0 (720p). **Keep VAE fp32** (bf16 VAE degrades decode). A14B = two-stage denoise (`transformer` + `transformer_2`, `boundary_ratio`, pass `guidance_scale_2`); LoRAs need `load_into_transformer_2=True` for the 2nd expert. `ftfy` is a required, easily-forgotten dep.

### LTX (Lightricks — two coexisting lines)

- **LTX-Video 0.9.x** (video-only, **Apache-2.0**, github.com/Lightricks/LTX-Video): latest **0.9.8** (Jul 2025). 13B/2B, dev/distilled/fp8 variants on `Lightricks/LTX-Video`. **Fully supported in diffusers** (`LTXPipeline`, `LTXImageToVideoPipeline`, 0.9.7 upscale via `LTXConditionPipeline` + `LTXLatentUpsamplePipeline`). T5 encoder (auto). Lightest VRAM (~10 GB fp8+offload). num_frames = **8k+1** (121/161/257), dims /32, fps up to 50.
- **LTX-2 / LTX-2.3** (22B, **audio+video**, LTX-2 Community License — NOT Apache, github.com/Lightricks/LTX-2): latest **2.3** (~Mar 2026). Checkpoints on `Lightricks/LTX-2.3` (dev / distilled-1.1 8-step / LoRA / upscalers); pre-quant `Lightricks/LTX-2.3-fp8`, `-nvfp4` (Blackwell). **diffusers does NOT support LTX-2 yet (Jun 2026)** — use official `ltx_pipelines` (`TI2VidTwoStagesPipeline` / `DistilledPipeline`) or ComfyUI core. Text encoder = **gated Gemma-3** (`google/gemma-3-12b-it-qat-q4_0-unquantized`). num_frames = **8k+1** (97/121/193), dims /32, frame_rate ~25, up to 4K@50fps. Distilled wants CFG=1.0 (8 steps); dev wants higher CFG (~40 steps). MultiModalGuiderParams: video cfg 3.0 / audio cfg 7.0, stg_blocks [28–29]. Needs ~100 GB disk.

### Local image models

- **FLUX.1** (BFL, 12B): `black-forest-labs/FLUX.1-dev` (gated, **non-commercial**, quality default, guidance ~3.5, 20–50 steps), `FLUX.1-schnell` (Apache-2.0, 1–4 step, guidance 0). FLUX.1-Kontext-dev for instruction edit. Stable diffusers OK.
- **FLUX.2** (Nov 2025, 32B): `black-forest-labs/FLUX.2-dev` (gated, top quality, fp8 ~32 GB / 4bit ~20 GB), FLUX.2-klein 9B/4B (Apache-2.0, Jan 2026). Text encoder Mistral-Small-3.1/3.2. **Needs diffusers git-main** + sentencepiece/protobuf.
- **Qwen-Image** (Alibaba, 20B MMDiT, Apache-2.0): best in-image multilingual TEXT rendering. `Qwen/Qwen-Image` (+ Edit variants). Needs `transformers>=4.51.3` (Qwen2.5-VL). Stable diffusers OK.
- **SD3.5** (Stability, 8B): `stabilityai/stable-diffusion-3.5-large` (+ -large-turbo 4-step, -medium 2.5B). Stability Community License. Stable diffusers OK.
- **SDXL** (3.5B): `stable-diffusion-xl-base-1.0` — tiny VRAM (~10–12 GB), huge LoRA/ControlNet ecosystem, lightweight workhorse.
- **Z-Image / Z-Image-Turbo** (Alibaba Tongyi, 6B, Apache-2.0, Nov 2025): speed champion, Turbo = 8–9 steps, guidance 0, bilingual, ~16 GB (8 GB fp8). **Needs diffusers git-main** (`ZImagePipeline`).
- **Default ladder:** FLUX.1-dev (quality) / Z-Image-Turbo (fast) / Qwen-Image (in-image text) / FLUX.2-dev (newest top). **Turbo/distilled (schnell, Z-Image-Turbo, SD3.5-turbo, klein) require guidance ≈ 0 + few steps** — high CFG breaks them.

---

## Install / setup commands

### Clean base env (uv)

```bash
source scripts/env.sh                     # cleans LD, exports HF_HOME, sets UV, alloc conf
uv venv .venv && source .venv/bin/activate
# CUDA 12.x wheels (cu124 works against the box's 12.2 driver — see troubleshooting)
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
# stable diffusers covers FLUX.1, SDXL, SD3.5, Qwen-Image, LTX-Video 0.9.x, Wan (mostly)
uv pip install diffusers transformers accelerate safetensors sentencepiece protobuf ftfy imageio imageio-ffmpeg
uv pip install bitsandbytes torchao        # NF4/8-bit + fp8/int8 quant
uv pip install "huggingface_hub[cli]"
```

PEP723 scripts pin their own deps inline; the above is for manual/REPL use.

### Newest models need diffusers git-main (FLUX.2, Z-Image, Wan2.2/2.7)

```bash
uv pip install "git+https://github.com/huggingface/diffusers"
# stable-release diffusers throws "no attribute Flux2Pipeline/ZImagePipeline"
```

### Hugging Face auth + gated-license acceptance

```bash
huggingface-cli login                      # paste a read token (HF_TOKEN)
# Then ACCEPT the license on the model's HF page (one-time, in browser):
#   black-forest-labs/FLUX.1-dev , FLUX.2-dev      (gated, non-commercial)
#   google/gemma-3-12b-it-qat-q4_0-unquantized     (gated — required for LTX-2.3)
# Without acceptance, from_pretrained / snapshot_download 401s.
```

### Model download (pre-stage; from_pretrained auto-downloads otherwise)

```bash
# Video
huggingface-cli download Wan-AI/Wan2.2-I2V-A14B-Diffusers
huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B-Diffusers
huggingface-cli download Lightricks/LTX-Video                       # 0.9.x base
huggingface-cli download Lightricks/LTX-2.3 ltx-2.3-22b-distilled-1.1.safetensors --local-dir ./weights
huggingface-cli download Lightricks/LTX-2.3 ltx-2.3-spatial-upscaler-x2-1.1.safetensors --local-dir ./weights
huggingface-cli download google/gemma-3-12b-it-qat-q4_0-unquantized --local-dir ./weights/gemma   # gated
# Image
huggingface-cli download black-forest-labs/FLUX.1-dev               # gated
huggingface-cli download Qwen/Qwen-Image
huggingface-cli download Tongyi-MAI/Z-Image-Turbo
huggingface-cli download black-forest-labs/FLUX.2-dev               # gated, ~large
```

### LTX-2.3 official repo (separate venv — torch 2.7 / Gemma stack)

```bash
git clone https://github.com/Lightricks/LTX-2.git && cd LTX-2
uv sync --frozen && source .venv/bin/activate
uv sync --extra xformers                   # attention opt on Ampere (A6000)
# system: Python 3.12+, torch 2.7. nvfp4 needs CUDA 12.7+ (N/A on Ampere — use fp8-cast).
```

### Wan official repo (only for multi-GPU torchrun)

```bash
git clone https://github.com/Wan-Video/Wan2.2.git && cd Wan2.2
uv pip install -r requirements.txt
huggingface-cli download Wan-AI/Wan2.2-T2V-A14B --local-dir ./Wan2.2-T2V-A14B   # plain repo, NOT -Diffusers
# 2x A6000 sequence-parallel (full-quality 720p, faster, no offload):
torchrun --nproc_per_node=2 generate.py --task t2v-A14B --size 1280*720 \
  --ckpt_dir ./Wan2.2-T2V-A14B --dit_fsdp --t5_fsdp --ulysses_size 2 --prompt "..."
```

### Cloud creds (only if local insufficient)

```bash
uv pip install modal && modal setup        # or MODAL_TOKEN_ID / MODAL_TOKEN_SECRET
export FAL_KEY=...                          # for scripts/cloud_fal.py
# Grok: do NOT configure here — delegate entirely to grok-media (its auth gate / login).
```

---

## Troubleshooting

### OOM → offload → cloud (escalation)

1. **Reduce first:** lower resolution (480p before 720p), fewer frames (Wan 81→49, LTX 121→97), fewer steps.
2. **Offload:** `pipe.enable_model_cpu_offload()` (pins to ONE device); or group offload `pipe.transformer.enable_group_offload(..., use_stream=True)` + `apply_group_offloading(pipe.text_encoder/vae, ...)`. LTX-Video fp8 layerwise-cast + group offload → ~10 GB.
3. **Quantize:** fp8 cast (Wan A14B ~40–50 GB, FLUX.2 ~32 GB) or 4bit bnb (`BitsAndBytesConfig`, Qwen/FLUX.2 ~12–20 GB).
4. **Set** `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (already in env.sh) to cut fragmentation.
5. **LTX-2 specifically:** wrap generate+encode in `torch.inference_mode()` (Gemma activations can pin ~37 GB otherwise — GitHub #152).
6. **Still OOM:** Wan-A14B 720p full quality → local-multi torchrun; else → cloud-modal/fal → grok. **Never combine `--offload` with a multigpu launch** (`enable_model_cpu_offload` pins one device).
7. Text-encoder spikes (T5-XXL/Mistral-24B/Qwen2.5-VL/Gemma-3) tip "fits native" into OOM — hence the 1.1x probe margin; on a borderline model, force offload.

### conda LD pollution fix

The box's bash itself prints `/home/kita/anaconda3/lib/libtinfo.so.6: no version information available` — conda's libtinfo leaks into `LD_LIBRARY_PATH` and has broken subprocesses (soffice) before. Mitigation:
- **Always** `source scripts/env.sh` before any python/ffmpeg call; it unsets/repins `LD_LIBRARY_PATH` to system libs.
- Run everything via `"$UV" run ...` (uv venv), **never** the conda/anaconda python.
- Quick manual fix in a one-off shell: `unset LD_LIBRARY_PATH` (then run the command).
- Symptom to watch for: `libtinfo.so.6: no version information` / cryptic loader errors from ffmpeg or soffice → LD is polluted.

### CUDA 12.2 wheel compatibility

- Driver-level CUDA is **12.2**, but the CUDA runtime ships **inside the PyTorch wheel** — the only constraint is `wheel CUDA minor ≤ driver` is NOT required; minor-version compat means **cu124 (and cu121/cu126) wheels run fine on a 12.2 driver**. Install `--index-url https://download.pytorch.org/whl/cu124`.
- **Ampere (sm_86):** use SDPA/xformers attention; do NOT install flash-attn-3 (Hopper) or rely on fp8-scaled-mm (needs Hopper) / nvfp4 (needs Blackwell + CUDA 12.7+). Plain **fp8-cast** and GGUF quant work on Ampere; speedup is modest vs H100 but VRAM savings are real.
- If `torch.cuda.is_available()` is False after install: usually LD pollution (see above) or a CPU-only wheel — reinstall with the cu124 index URL inside a clean uv venv.
- LTX-2's nvfp4 path is unusable here (Blackwell-only); always use `--quantization fp8-cast` or bf16 on the A6000.

### Quick gotcha checklist

- [ ] Wrong frame count → Wan 4k+1 (81), LTX 8k+1 (121/193); dims /32 (LTX) or /32–/64 (Wan).
- [ ] Washed-out turbo/distilled output → set guidance ≈ 0, few steps (schnell, Z-Image-Turbo, SD3.5-turbo, klein, LTX distilled).
- [ ] Degraded video decode → keep VAE `torch.float32` (Wan & LTX).
- [ ] `no attribute Flux2Pipeline/ZImagePipeline` → install diffusers from git main.
- [ ] LTX-2 won't load in diffusers → expected; use `ltx_pipelines` / ComfyUI.
- [ ] 401 on FLUX.1/2-dev or Gemma-3 → `huggingface-cli login` + accept the gated license in browser.
- [ ] Tokenizer load fails → Qwen needs `transformers>=4.51.3`; FLUX.2 needs sentencepiece + protobuf.
- [ ] Multi-GPU single clip in diffusers → not supported; use Wan official torchrun, or run two independent single-GPU jobs.
- [ ] Empty Grok response treated as failure → defer to grok-media's session-dir recovery (`grok -r` / glob `~/.grok/sessions/.../{images,videos}/`).
