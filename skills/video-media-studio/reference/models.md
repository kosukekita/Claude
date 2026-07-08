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
| `hunyuan-custom-720p` | **r2v** | comfyui · **NOT diffusers** → `gen_hunyuan_custom.py` (headless ComfyUI/Kijai) | `Kijai/HunyuanVideo_comfy` + `Comfy-Org/HunyuanVideo_repackaged` | 60 | 24 | 24 | **24576** | (4,1) | 16 | 30 | 7.5 | 24 | 512×896 | Tencent Hunyuan (no gating, no safety checker) | YES (fp8+block-swap on one card) | — |

Notes (video):
- **All Wan / LTX-Video are Apache-2.0** → commercial OK, no gating. Use the `*-Diffusers` Wan repos for the diffusers path; plain `Wan-AI/Wan2.2-*` repos are for the official `generate.py`/torchrun path.
- **`vae_fp32: True` on every video model** — bf16 VAE visibly degrades decode. gen_video.py forces this.
- **Wan A14B (MoE)** = two-stage denoise (`transformer` + `transformer_2`, `boundary_ratio`, second-expert `guidance_scale_2`). LoRAs need `load_into_transformer_2=True`. `ftfy` is a required, easily-forgotten dep. On 48 GB: run **fp8** (≈46 GB) or **offload** (floor 40); full bf16 (80 GB) needs `local-multi` (torchrun across both cards).
- **Wan frame canon**: `4k+1`, 81 = 5 s. A14B fps 16, TI2V-5B fps 24. flow_shift ~3.0 (480p)/~5.0 (720p).
- **LTX-Video 0.9.8** = lightest VRAM (≈10 GB with fp8+offload). T5 encoder auto-loaded, **no Gemma**. `decode_timestep=0.03`, `decode_noise_scale=0.025`. Frames `8k+1` (121/161/257), dims /32, fps up to 50.
- **LTX-2.3** = newest LTX (22B, +audio). **Not in diffusers** → gen_video.py sets `defer_to_ltx2` and hands off to `scripts/gen_video_ltx2.py` (`ltx_pipelines`). Requires **gated Gemma-3** access on HF and ~100 GB disk. bf16 (42) fits one A6000; fp8 (20) is safer headroom.
- **i2v default** (`DEFAULT_MODEL_FOR_TASK[i2v]`) = `wan2.2-i2v-a14b` → on this rig means fp8/offload. **t2v default** = `wan2.1-t2v-1.3b` (fast iteration).

### r2v (reference-to-video) — HunyuanCustom via headless ComfyUI (`gen_hunyuan_custom.py`)

**r2v = ONE reference person image + text → that person in an ARBITRARY new scene** (subject customization). This is a different task from i2v (animate a still) and from Wan-VACE r2v (transfer a *driving motion video's* pose onto a reference). **HunyuanCustom needs NO motion video** — the scene/action comes entirely from the text prompt. That is exactly what VACE cannot do (VACE requires a driving clip to produce any motion). The identity is carried into every frame by the **CLIP-Vision encoder** (`llava_llama3_vision.safetensors`), not by a pose skeleton.

- **NOT a diffusers pipeline.** Runs on a headless ComfyUI server (Kijai `ComfyUI-HunyuanVideoWrapper` + `ComfyUI-KJNodes` + `ComfyUI-VideoHelperSuite`) living in its OWN venv at `/data/kita/ComfyUI/.venv` (uv-managed CPython, NOT anaconda). gen_video.py `--task r2v` defers to `gen_hunyuan_custom.py`; the wrapper spawns/queries the server over HTTP (`/upload/image` → `/prompt` → `/history` → `/view`).
- **Setup (first run, ~22 GB, all on D drive so no eviction):** clone ComfyUI + the 3 custom nodes into `/data/kita/ComfyUI`; `hunyuan_fetch.py` downloads 5 files (fp8 transformer 13 GB, llava fp8 8.7 GB, clip_l, clip-vision, VAE) into `models/{diffusion_models,text_encoders,clip_vision,vae}`. Launch with `comfyui_serve.sh` (`--gpu N --no-sage` if sageattention isn't built).
- **Workflow template** = `reference/hunyuan_custom_api_template.json` (API-format, produced from the Kijai sample UI JSON by `ui_to_api.py`, which resolves widget order from the live `/object_info` so it survives node-version drift). The wrapper patches ref-image / prompt / dims / steps / seed / cfg / block-swap / fps by **class_type**, not node id.
- **Settings (Tencent-recommended):** 512×896 (low-VRAM) or 720×1280, `num_frames` 129 (≈5 s @24), steps 30, **cfg 7.5**, **flow_shift 13.0**, `use_cfg_zero_star` OFF. Frame rule `4k+1`.
- **VRAM / speed (measured on one A6000 48 GB):** fp8 + block-swap 20 + fp8 text-encoder runs 512×896/129f fine; **~70 s/step → ~36 min for 129f/30 steps.** The 2nd GPU is for a parallel job (separate port + `--gpu`), not sharding.
- **NSFW:** no safety checker anywhere in the wrapper; the base is uncensored → full nudity from the prompt alone (no LoRA). ★**fp8_scaled does NOT accept LoRAs** (Kijai) — a motion/NSFW LoRA would need the bf16 custom transformer (out of scope for v1).
- **Identity fidelity vs VACE:** measure with `compare_face_sim.py` (ArcFace/insightface `buffalo_l`, cosine Face-Sim). ★**The metric is only fair when both videos show a FRONTAL face** — HunyuanCustom's action shots (e.g. shower, head turned/down) tank ArcFace even though the person is clearly the same by eye. Always confirm with the tile + full video, per the SKILL.md verification discipline.

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

## 5a. ★NSFW real video → anime (v2v, `gen_v2v_qwen.py`) — THE recommended path

Per-frame **Qwen-Image-Edit + anime LoRA**. Keeps the SAME person (the edit model conditions on the input frame itself, so identity transfers — unlike SDXL+IP-Adapter which regenerates a different face). ComfyUI-free, diffusers-native, fully local (NSFW OK). `local-single` w/ `--offload model` (`--offload none` OOMs at 1280px on 48GB).

| role | HF id | note |
|---|---|---|
| edit base | `Qwen/Qwen-Image-Edit-2511` | less drift + better identity than 2509. `QwenImageEditPlusPipeline`, bf16 ~40GB w/ offload |
| anime LoRA | `prithivMLmods/Qwen-Image-Edit-2511-Anime` | trigger `"Transform into anime."`, 4-8 step lightning, cfg≈1. Preserves pose/proportions/viewpoint. **Required** (without it the edit reinvents pose/expression) |
| NSFW LoRA (optional) | `ScottzillaSystems/qwen-image-edit-plus-nsfw-lora` | stack as 2nd `--lora` for explicit shots |
| anime→real LoRA (reverse) | `Hyperccino/Qwen-Edit-2511-Anime-to-Photoreal-v1.1` or `WarmBloodAban/Anything_to_Real_Characters_2511` | reverse direction; semi-realistic, identity moderate; pair with NSFW LoRA |

**Knobs:** `--steps 8 --guidance 1.0` (lightning LoRA), `--seed` fixed across frames (coherence), `--max-side 1280` (~1MP), `--offload model`, `--gpu N`, `--fps 24` (8-12 = limited-anime, faster; output restored to source duration). **Verified 2026-06-30:** 23s clip @24fps (554 frames) kept the same person end-to-end. **Don't post-blend** (`minterpolate=blend` softens/doubles edges — raw > smoothed); raise fps for smoothness instead. Residual per-frame flicker is inherent to image-edit-per-frame. Long clips: split frame range across both GPUs (`--work-dir` shared, `--start/--end`), concat all frames manually at the end.

## 5b. Video-to-video style transfer (v2v, `gen_v2v_style.py`) — SDXL path (general / strong motion lock)

> ⚠️ For NSFW real→anime use 5a (Qwen). This SDXL path regenerates faces → **identity drifts** (real→anime gives a generic different anime face). Use only for generic style transfer or when you need strong ControlNet motion lock.

Per-frame SDXL img2img + ControlNet + IP-Adapter Plus-Face. ComfyUI-free, diffusers-native. `local-single` on one A6000, fp16, ~12–16 GB.

**Style base (`--style-model`)** — any plain SDXL checkpoint accepts the SDXL ControlNet/IP-Adapter:

| key | repo | scheduler quirk | use for |
|---|---|---|---|
| `pony` | `votepurchase/ponyDiffusionV6XL` | force Euler (eps/scaled_linear) | anime (needs `score_9, score_8_up, ... , source_anime`) |
| `noobai-xl` | `Laxhar/noobai-XL-1.1` | none (eps) | anime / booru tags |
| `noobai-xl-vpred` | `Laxhar/noobai-XL-Vpred-1.0` | v_prediction + zero-SNR | sharper anime |
| `manga-vision-il` | `John6666/manga-vision-il-v1-sdxl` | none | B/W manga pages |
| `sdxl` | `stabilityai/stable-diffusion-xl-base-1.0` | none | real-ish base (swap real-photo SDXL via `--style-repo`) |

**Control / reference weights** (auto-downloaded on first run):

| role | HF id | note |
|---|---|---|
| ControlNet OpenPose | `xinsir/controlnet-openpose-sdxl-1.0` | motion lock (pose). default scale 1.0 |
| ControlNet Depth | `xinsir/controlnet-depth-sdxl-1.0` | motion lock (depth). default scale 0.6 |
| ControlNet Canny | `xinsir/controlnet-canny-sdxl-1.0` | optional edge lock |
| Annotators | `lllyasviel/Annotators` (via `controlnet_aux`) | OpenposeDetector / MidasDetector preprocessors |
| SDXL VAE | `madebyollin/sdxl-vae-fp16-fix` | avoids fp16 black frames |
| IP-Adapter Plus-Face | `h94/IP-Adapter` → `sdxl_models/ip-adapter-plus-face_sdxl_vit-h.bin` | character/face lock, **no insightface** |
| IP-Adapter encoder | `h94/IP-Adapter` → `models/image_encoder` (ViT-H) | required for Plus-Face (NOT `sdxl_models/image_encoder`) |

**Knobs:** `--strength` (denoise; default 0.72 — real→anime faces want 0.65–0.8; lower keeps source texture), `--face-scale` 0.5–0.9 (identity strength), `--cn-scale` (per-ControlNet, matches `--controlnet` order), `--seed` fixed across frames, `--gpu N` (pin), `--max-side` **≥1024** (face collapse fix — see below).

**Face-collapse fix (the big one):** per-frame img2img turns faces into "melted ghosts" when the face is too few latent pixels (SDXL latent = pixels/8; a face that is ~10% of frame = ~8–10 latent px → no eyes/nose/mouth). Three defenses, all ON by default: (1) **`--max-side` ≥1024** (768 collapsed faces; 1024 fixed them on its own), (2) **`--face-ref-crop auto`** crops `--face-ref` to the detected face before IP-Adapter Plus-Face (which expects a *cropped face*, not a full body), (3) **`--face-refine auto`** = ADetailer-style 2nd pass: detect face → crop → upscale to `--face-refine-size` (512) → img2img with ControlNet off → feather-paste back; fires only for small faces. OpenPose face keypoints are off by default (they fight face redraw; identity comes from IP-Adapter).

**Anti-flicker:** fixed seed + same prompt/model/negative + ControlNet(pose+depth). **`--blend-prev` defaults to 0 (OFF)** — feeding the previous output into the next init *accumulates degradation* (verified: 0.25 → faces + background rot in the back half of a clip; 0 → all frames clean). Only try ~0.1 on very short clips and inspect the tail.

**License note:** SDXL ControlNet (xinsir, OpenRAIL) + IP-Adapter (Apache) are permissive; the **style base license dominates** (Pony/NoobAI = Fair-AI public; SDXL = OpenRAIL++). NSFW use is local-only by design.
