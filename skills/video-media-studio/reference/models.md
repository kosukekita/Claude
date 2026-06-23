# models.md — Per-Model Deep Reference (video-media-studio)

Per-model lookup that `SKILL.md` defers to. Numbers here are
**authoritative for the agent** and match `scripts/gen_video.py` FALLBACK_MODELS /
`scripts/gen_image.py` MODELS exactly. Single source of truth at runtime =
`scripts/models.py` / `scripts/probe_backend.py` (this file mirrors them).

Conventions:
- **VRAM** = approximate single-card peak (weights + activations + text-encoder spike), per clip/image.
- **bf16 / fp8 / offload-floor** in GB. "—" = not applicable for that model.
- **`--required-mb`** = the value to pass `scripts/probe_vram.py --required-mb N` =
  `round(bf16_GB * 1024)`. probe_vram then applies its own `--margin` (default 1.1) on top.
- **frame rule `(k,1)`** = `num_frames` must be `k*n + 1` (e.g. (4,1)→81, (8,1)→121). **dim multiple** = width & height must be divisible by it.
- **Rig** = 2× RTX A6000 48 GB (Ampere, no FA3, limited fp8 matmul). "local on 2×A6000?" judged against ~48.6 GB free per card.

---

## 1. Video models — local pipelines (in CONTRACTS)

| model id | task | pipeline / diffusers class | repo id | bf16 | fp8 | offload-floor | `--required-mb` | frame rule | dim mult | steps | guid | fps | size | license | local on 2×A6000? | cloud fal_id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `wan2.1-t2v-1.3b` | t2v | wan · `WanPipeline` | `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | 13 | — | 8 | **13312** | (4,1) | 16 | 40 | 5.0 | 16 | 832×480 | Apache-2.0 | YES, trivially | `fal-ai/wan/v2.2-5b/text-to-video` |
| `wan2.2-ti2v-5b` | t2v (also i2v) | wan · `WanPipeline` | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | 28 | — | 24 | **28672** | (4,1) | 16 | 40 | 5.0 | 24 | 1280×704 | Apache-2.0 | YES, single card | `fal-ai/wan/v2.2-5b/text-to-video` |
| `wan2.2-t2v-a14b` | t2v | wan(MoE) · `WanPipeline` | `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | 80 | 46 | 40 | **81920** | (4,1) | 16 | 40 | 3.5 | 16 | 1280×720 | Apache-2.0 | with-fp8 / with-offload (bf16 needs multi) | `fal-ai/wan/v2.2-a14b/text-to-video` |
| `wan2.2-i2v-a14b` | i2v | wan(MoE) · `WanImageToVideoPipeline` | `Wan-AI/Wan2.2-I2V-A14B-Diffusers` | 80 | 46 | 40 | **81920** | (4,1) | 16 | 40 | 3.5 | 16 | 1280×720 | Apache-2.0 | with-fp8 / with-offload (bf16 needs multi) | `fal-ai/wan/v2.2-a14b/image-to-video` |
| `ltx-video-0.9.8` | t2v | ltx · `LTXPipeline` | `Lightricks/LTX-Video` | 24 | — | 10 | **24576** | (8,1) | 32 | 50 | 3.0 | 24 | 768×512 | Apache-2.0 | YES easily | `fal-ai/ltx-2.3/text-to-video` |
| `ltx-video-0.9.8-i2v` | i2v | ltx · `LTXImageToVideoPipeline` | `Lightricks/LTX-Video` | 24 | — | 10 | **24576** | (8,1) | 32 | 50 | 3.0 | 24 | 768×512 | Apache-2.0 | YES easily | `fal-ai/ltx-2.3/image-to-video` |
| `ltx-2.3` | t2v | ltx2 · **NOT diffusers** → `gen_video_ltx2.py` | `Lightricks/LTX-2.3` | 42 | 20 | 18 | **43008** | (8,1) | 32 | 40 | 3.0 | 25 | 768×512 | LTX-2 (needs gated **Gemma-3**) | YES (bf16 fits one card; fp8 safer) | `fal-ai/ltx-2.3/text-to-video` |

Notes (video):
- **All Wan / LTX-Video are Apache-2.0** → commercial OK, no gating. Use the `*-Diffusers` Wan repos for the diffusers path; plain `Wan-AI/Wan2.2-*` repos are for the official `generate.py`/torchrun path.
- **`vae_fp32: True` on every video model** — bf16 VAE visibly degrades decode. gen_video.py forces this.
- **Wan A14B (MoE)** = two-stage denoise (`transformer` + `transformer_2`, `boundary_ratio`, second-expert `guidance_scale_2`). LoRAs need `load_into_transformer_2=True`. `ftfy` is a required, easily-forgotten dep. On 48 GB: run **fp8** (≈46 GB) or **offload** (floor 40); full bf16 (80 GB) needs `local-multi` (torchrun across both cards).
- **Wan frame canon**: `4k+1`, 81 = 5 s. A14B fps 16, TI2V-5B fps 24. flow_shift ~3.0 (480p)/~5.0 (720p).
- **LTX-Video 0.9.8** = lightest VRAM (≈10 GB with fp8+offload). T5 encoder auto-loaded, **no Gemma**. `decode_timestep=0.03`, `decode_noise_scale=0.025`. Frames `8k+1` (121/161/257), dims /32, fps up to 50.
- **LTX-2.3** = newest LTX (22B, +audio). **Not in diffusers** → gen_video.py sets `defer_to_ltx2` and hands off to `scripts/gen_video_ltx2.py` (`ltx_pipelines`). Requires **gated Gemma-3** access on HF and ~100 GB disk. bf16 (42) fits one A6000; fp8 (20) is safer headroom.
- **i2v default** (`DEFAULT_MODEL_FOR_TASK[i2v]`) = `wan2.2-i2v-a14b` → on this rig means fp8/offload. **t2v default** = `wan2.1-t2v-1.3b` (fast iteration).

---

## 2. Image models — local pipelines (implemented in `gen_image.py`)

| model id | task | diffusers class | repo id | bf16 | fp8/4bit | offload-floor | `--required-mb` | steps | guid | size | license | local on 2×A6000? | cloud/grok fallback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `flux.1-dev` | t2i | `FluxPipeline` | `black-forest-labs/FLUX.1-dev` | 33 | — | 12 | **33792** | 40 | 3.5 | 1024×1024 | **FLUX.1 community — non-commercial, GATED on HF** | YES native (quality default) | flux.1-schnell → cloud-fal `fal-ai/flux/dev` → grok `image_gen` |
| `flux.1-schnell` | t2i (1–4 step turbo) | `FluxPipeline` | `black-forest-labs/FLUX.1-schnell` | 24 | — | 12 | **24576** | 4 | 0.0 | 1024×1024 | **Apache-2.0 (commercial OK)** | YES | cloud-fal `fal-ai/flux/schnell` → grok |
| `sdxl` | t2i | `StableDiffusionXLPipeline` | `stabilityai/stable-diffusion-xl-base-1.0` | 12 | — | 8 | **12288** | 30 | 7.0 | 1024×1024 | CreativeML OpenRAIL++-M | YES easily | cloud / grok |

Notes (local image):
- `gen_image.py` implements **only these three**. `auto` ladder = `[flux.1-dev, sdxl]`; `--fast` swaps in `flux.1-schnell`.
- **flux.1-schnell** pins **guidance 0** and 1–4 steps — high CFG breaks turbo models.
- **flux.1-dev is gated + non-commercial** — accept the HF license and `huggingface-cli login` first; do not ship commercial output from it (use schnell/SDXL or a permissive cloud model for commercial work).
- dims rounded to multiples of 16 (SDXL/FLUX-safe) by gen_image.py.

---

## 3. Image models — reference-only (cloud / Grok, NOT implemented locally)

These are **not** in `gen_image.py`. When requested, route to cloud (Modal/fal) or delegate to grok-media.
`--required-mb` shown for reference if someone *did* run them locally via a custom script; the skill does not.

| model id | task | (would-be) class | repo id | bf16 | fp8/4bit | offload-floor | `--required-mb` | notes | license | local on 2×A6000? | cloud/grok fallback |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `z-image-turbo` | t2i (8–9 step, bilingual text) | `ZImagePipeline` (diffusers **git-main**) | `Tongyi-MAI/Z-Image-Turbo` | 16 | 8 | 8 | **16384** | turbo: guidance 0, very fast; strong CN/EN in-image text | Apache-2.0 | YES if implemented (fast, light) | grok `image_gen` / cloud |
| `qwen-image` | t2i (accurate in-image TEXT) | `QwenImagePipeline` (needs `transformers>=4.51.3`) | `Qwen/Qwen-Image` | 40 | 12–13 (4bit) | 13 | **40960** | best for rendering long/precise text in image | Apache-2.0 | with-4bit (bf16 tight on one card) | cloud-fal `fal-ai/qwen-image` / grok |
| `flux.2-dev` | t2i (newest, top quality) | `Flux2Pipeline` (diffusers **git-main**) | `black-forest-labs/FLUX.2-dev` | 80 | 32 (fp8) / 20 (4bit) | 20 | **81920** | needs `sentencepiece`+`protobuf`; gated | **FLUX.2 community (gated, non-commercial)** | with-fp8 / with-4bit on one card | cloud-fal `fal-ai/flux-2` / grok |
| `sd3.5-large` | t2i | `StableDiffusion3Pipeline` | `stabilityai/stable-diffusion-3.5-large` | 18 | — | 10 | **18432** | MMDiT 8B; needs HF license accept (gated) | Stability Community (gated) | YES easily if implemented | sdxl / cloud / grok |

Notes (reference-only):
- The skill deliberately keeps the local image surface to FLUX+SDXL. Everything in this table goes **cloud or Grok** by design — implementing them locally is out of scope unless explicitly added to `gen_image.py` + `models.py`.
- **qwen-image** and **z-image-turbo** are the two worth running locally if you ever extend the skill (light + permissive + good text rendering). **flux.2-dev** is the quality ceiling but heavy (fp8/4bit only on 48 GB).

---

## 4. Which model when (decision guide)

**Text-to-video (t2v):**
- Fast iteration / draft / cheap → **`wan2.1-t2v-1.3b`** (default; fits trivially, 832×480@16fps).
- Best open quality, 720p → **`wan2.2-t2v-a14b`** at **fp8** (or offload). Full bf16 → `local-multi` torchrun.
- One-card 720p@24 dense (no MoE hassle) → **`wan2.2-ti2v-5b`**.
- Lightest VRAM / longest clips / high fps → **`ltx-video-0.9.8`** (Apache, no Gemma).
- Newest LTX with audio, willing to set up gated Gemma-3 + 100 GB → **`ltx-2.3`** (bf16 fits one A6000).

**Image-to-video (i2v):**
- Quality default → **`wan2.2-i2v-a14b`** (fp8/offload on this rig).
- Lighter / faster animate-a-still → **`ltx-video-0.9.8-i2v`**.

**Text-to-image (t2i):**
- Quality, non-commercial OK → **`flux.1-dev`** (gated, native on one card).
- Turbo / commercial / 1–4 step → **`flux.1-schnell`** (Apache).
- Tiny VRAM / safe everywhere → **`sdxl`**.
- Need accurate **in-image text** → `qwen-image` (cloud/grok, or 4bit if added locally).
- Need bilingual fast text → `z-image-turbo` (cloud/grok).
- Absolute top quality, heavy → `flux.2-dev` (cloud/fp8).
- Open MMDiT alternative → `sd3.5-large` (cloud).

**Backend ladder (probe descends):** local-single → local-offload → local-multi (Wan torchrun only) → cloud-modal → cloud-fal → grok. On this 96 GB rig almost everything is local; cloud/Grok are last resort.

**Commercial-use cheat sheet:** OK = Wan (Apache), LTX-Video 0.9.8 (Apache), flux.1-schnell (Apache), z-image-turbo/qwen-image (Apache). **Not OK / restricted** = flux.1-dev, flux.2-dev (non-commercial), sd3.5-large & ltx-2.3 (community/gated — check terms), sdxl (OpenRAIL++ — permissive but read the use restrictions).
