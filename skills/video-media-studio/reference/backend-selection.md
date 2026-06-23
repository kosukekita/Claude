# backend-selection.md — How the backend ladder is chosen, and why

This is the prose companion to the flowchart in `SKILL.md` (the "バックエンド自動選択 / THE core decision" section). The flowchart shows *what* happens; this file explains *why* each rung exists, what each tier means operationally, and how a run degrades gracefully when VRAM is tight. The machine-readable thresholds live in `scripts/models.py` (mirrored in `gen_video.py`'s `FALLBACK_MODELS` and, when present, `scripts/probe_backend.py`). When numbers here and code disagree, **the code wins** — treat this as the rationale, not the source of truth.

The cardinal rule, repeated from `CLAUDE.md` discipline and SKILL.md: **never decide the backend in the model's head.** Selection is mechanical, done by code that reads real free VRAM from `nvidia-smi` and descends a fixed priority ladder. Your job is to read the decision and its `why`, not to guess it.

---

## The verified rig

Everything below is sized for one specific machine, measured (not spec-sheet):

- **2x NVIDIA RTX A6000, 49140 MiB each (~48666 MiB / ~48 GB free per card when idle)**, so **~96 GB aggregate**. Driver-level CUDA 12.2.
- **Ampere (compute capability 8.6).** This is the limiting fact behind several choices:
  - **No FlashAttention-3** (Hopper-only). Attention runs on SDPA or xformers. Don't plan FA3 kernels.
  - **fp8 matmul is limited.** fp8 still *saves VRAM* (it shrinks the weights you have to hold), which is why fp8 casting is a first-class lever here — but the *speedup* from fp8 is much smaller than on an H100. So we reach for fp8 to **fit**, not to go fast.
- `uv` at `/home/kita/.local/bin/uv`; ffmpeg 6.1.1; 217 GB free disk (HF cache must go on the big disk via `HF_HOME`); conda present but its `libtinfo.so.6` pollutes `LD_LIBRARY_PATH` — every spawning/torch-importing script scrubs conda paths first and never uses the conda python.

The practical upshot of 96 GB across two 48 GB cards: **almost everything we run is `local-single`.** A single A6000 holds Wan2.1-1.3B, Wan2.2-TI2V-5B, Wan2.2-A14B at fp8, LTX-Video, LTX-2.3 (bf16 fits, fp8 safer), FLUX.1, SD3.5, Z-Image, Qwen-Image, and FLUX.2 at fp8/4bit. Cloud and Grok are genuine last resorts on this box, reached only when both cards are busy or a model is unimplemented locally.

---

## The priority ladder, and why each rung exists

The probe descends this order and stops at the first rung that fits:

```
local-single  >  local-offload  >  local-multi (Wan-big only)  >  cloud-modal  >  cloud-fal  >  grok
```

### 1. `local-single` — preferred always
One model on one GPU (`CUDA_VISIBLE_DEVICES=0`, `device="cuda:0"`), weights resident, no CPU shuttling. Fastest per-clip latency and simplest failure mode. We take this whenever `free_vram >= required * margin` for some precision (bf16 first, then fp8) on a single card. On a 96 GB rig this is the common case.

### 2. `local-offload` — fit, at a latency cost
When the full bf16 model won't fit but the model's **offload floor** will, we enable `enable_model_cpu_offload()` on a **single device**. Submodules (text encoder, transformer, VAE) are moved to GPU only while active and parked in CPU RAM otherwise. This trades wall-clock time (PCIe shuttling each step) for a much smaller resident footprint — e.g. Wan2.2-A14B drops from ~80 GB bf16 to a ~40 GB floor, LTX-Video to ~10 GB, FLUX.1 fits comfortably. Offload is chosen automatically when `required*margin` doesn't fit but `offload_floor` does; you can force it with `--offload`. Note offload is **single-device** — it is *not* multi-GPU and does not split one clip across cards.

### 3. `local-multi` — Wan-big only, via the official torchrun path
This rung exists for exactly one purpose: running **Wan2.2 A14B / 14B at full bf16 quality** faster by sharding the model across both A6000s. It is gated to `wan_big` models *and* `want_quality=quality` *and* both GPUs being free. The mechanism is the **official Wan repo's** distributed launch, not diffusers:

```
torchrun --nproc_per_node=2 generate.py ... --ulysses_size 2 --dit_fsdp --t5_fsdp
```

`--ulysses_size 2` is Ulysses sequence parallelism across the 2 GPUs; `--dit_fsdp` / `--t5_fsdp` FSDP-shard the DiT and the T5 encoder so a model too big for one card spreads over both, at full precision.

**Why this is the *only* multi-GPU rung:** diffusers cannot shard a single clip's denoise across two cards. There is no diffusers "use both GPUs for one video" mode. So for everything except Wan-big, **multi-GPU does not help a single job at all.** The correct way to use the second card for throughput on diffusers models is therefore *not* sharding but **two parallel single-GPU jobs** — one on `cuda:0`, one on `cuda:1` — each a `local-single` run. That's the throughput strategy; `local-multi` is purely a Wan-big quality/speed lever.

### 4. `cloud-modal` — custom pipeline, cheapest GPU-seconds
Reached only when nothing local fits (VRAM short / both cards busy) **and** `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` are set. Modal runs *our* diffusers pipeline (`scripts/cloud_modal.py`) on a rented GPU from `["H100","A100-80GB","A100-40GB","L40S","A10G"]`, returning the mp4/png bytes to disk. Preferred over fal when we want our exact pipeline/params and the cheapest per-second cost, accepting that we maintain the code.

### 5. `cloud-fal` — hosted, fastest to a result
Reached when local fails and Modal creds are absent but `FAL_KEY` is set. fal hosts Wan/LTX/FLUX endpoints (`scripts/cloud_fal.py`), billed per output-second. Fastest path to a usable clip when we don't care about running our own pipeline.

### 6. `grok` — terminal fallback, delegated never reimplemented
Reached when no GPU fits and **no cloud creds** exist. We **delegate to the `grok-media` skill** (which wraps the xAI Grok Build CLI under the user's subscription OAuth, no metering). `gen_video.py` / `gen_image.py` only *print the delegation instructions* — they never call Grok's API or guess its flags. The seam: confirm auth (`grok models`), make a clean `mktemp -d`, invoke with natural-language tool naming (`image_gen` / `image_edit` / `image_to_video` / `reference_to_video`), then recover outputs from `~/.grok/sessions/.../{images,videos}/` or via `grok -r`. t2v on Grok is a 2-stage `image_gen` → `image_to_video`. Follow `grok-media/SKILL.md`; do not hardcode binary flags.

---

## The 1.1x VRAM safety margin (why `margin` defaults to 1.1)

The probe compares `free_vram` against `required_mb * margin`, with `margin` defaulting to **1.1**. The 10% cushion is not arbitrary padding — it specifically guards against **text-encoder activation spikes** that the static "weights" number doesn't capture.

These pipelines front-load a large text/vision encoder whose **transient activation peak** lands *before* the diffusion transformer is fully loaded or while both are briefly co-resident:

- **T5-XXL** (Wan, LTX-Video) — the classic ~11 GB encoder whose activations spike on long prompts.
- **Gemma-3** (LTX-2.3) and **Mistral-24B** (FLUX.2) — large gated encoders.
- **Qwen2.5-VL** (Qwen-Image) — a vision-language encoder with its own peak.

Without the margin, a model whose *resident* footprint "fits" 48 GB exactly will still **OOM at encode time** when the encoder's activation peak pushes past free VRAM. The 1.1x margin keeps such borderline models on the rung that actually survives a full run, rather than optimistically pinning them to `local-single` and crashing. It is deliberately conservative: better to fall to offload (slower but completes) than to fail mid-generation. Override with `--margin` only when you've measured a specific model has no such spike.

---

## The two entry points

There are two ways into the selection logic, for two different needs.

### a) `gen_video.py --backend auto` — the production path
This is what you actually run to generate. With `--backend auto` (the default) it resolves the backend by **calling the sibling `scripts/probe_backend.py` as a subprocess**:

```
probe_backend.py --task <t2v|i2v> --model <id> --want-quality <fast|quality> --margin <f> --json [--force <family>]
```

It parses the **last stdout line as JSON** and honors this exact contract:

| key | meaning |
|---|---|
| `backend` | one of `local-single` / `local-offload` / `local-multi` / `cloud-modal` / `cloud-fal` / `grok` |
| `device` | e.g. `"cuda:0"` or `null` |
| `precision` | `"bf16"` / `"fp8"` / `null` |
| `offload` | bool |
| `multigpu` | bool |
| `model` | resolved repo id or `null` |
| `why` | human-readable reason string |

`probe_backend.py` is **optional**: if it's absent, `gen_video.py` falls back to its own `builtin_select`, and when `scripts/models.py` is present it pulls specs via `models.get(model_id)` (else its built-in `FALLBACK_MODELS`). Either way the decision is mechanical. Use `--print-decision` to see the chosen backend + `why` **without generating** — always do this first on an unfamiliar model. When the result is `cloud-modal`/`cloud-fal`, the script points you at `cloud_modal.py` / `cloud_fal.py` with matching `--model/--task/--image/--out`; when `grok`, it prints the delegation instructions.

### b) `probe_vram.py --required-mb N` — the raw check
A stdlib-only tool (no torch, no deps) for when you just want to know "does N MB fit, and on which rung?" — independent of any model table. It prints JSON to stdout (human log to stderr, exit 0 on normal paths). With `--required-mb` it adds `required_mb`, `margin`, `effective_required_mb`, `backend` (here a coarse `local-single` / `local-offload` / `cloud`), `gpu_index`, and `reason`. Use it for ad-hoc sizing, for models not in the matrix, or as a sanity check that nvidia-smi agrees with what `gen_video.py` decided. Per-model `--required-mb` ballparks live in `reference/models.md`.

---

## What each tier means operationally (recap)

- **local-single** = one GPU, weights resident, pick bf16 if it fits else fp8 (fp8 = fit, not speed, on Ampere). Default and best.
- **local-offload** = `enable_model_cpu_offload()` on a *single* device. Smaller footprint, slower (PCIe shuttling). Not multi-GPU.
- **local-multi** = **Wan-big only**, full-bf16 quality, official `torchrun --ulysses_size 2 --dit_fsdp --t5_fsdp`. diffusers cannot shard one clip → for diffusers throughput, run **2 parallel single-GPU jobs** instead (one per card), each a `local-single`.
- **cloud-modal** = our pipeline on rented GPU; needs `MODAL_TOKEN_ID`+`MODAL_TOKEN_SECRET`; cheapest GPU-sec.
- **cloud-fal** = hosted endpoints; needs `FAL_KEY`; fastest to result.
- **grok** = delegate to `grok-media`; needs no creds (subscription); terminal fallback.

Cloud gating order, applied only after all local rungs fail: `MODAL_TOKEN_ID`/`MODAL_TOKEN_SECRET` → `cloud-modal`; else `FAL_KEY` → `cloud-fal`; else → `grok`.

---

## Worked example 1 — `wan2.2-i2v-a14b`, degrade gracefully

Wan2.2-I2V-A14B needs ~80 GB bf16, ~46 GB fp8, ~40 GB offload floor (an `i2v`, `wan_big`, MoE model — this is also the `DEFAULT_MODEL_FOR_TASK["i2v"]`). Watch one A6000's free VRAM drive the decision:

1. **One card has ~48 GB free, `want_quality=fast`.** bf16 (80 GB) fails `48 < 80*1.1`. fp8 (46 GB) passes `48 >= 46*1.1`? — 46*1.1 = 50.6, so it's *borderline* and the margin correctly rejects pinning it tight. In practice the probe lands it on **fp8 local-single** only if free comfortably clears 50.6 GB, otherwise it steps to offload. With a genuinely idle ~48.6 GB card, expect **`local-offload` (fp8 cast + cpu offload), device cuda:0** — it fits the 40 GB floor and completes. `why` cites the encoder-spike margin.
2. **Both GPUs free and `want_quality=quality`.** The `wan_big` + `quality` + both-idle gate fires → **`local-multi`**: official `torchrun --nproc_per_node=2 --ulysses_size 2 --dit_fsdp --t5_fsdp` for full-bf16 quality split across the pair.
3. **One card is already busy (e.g. a parallel job), the other has only ~20 GB free.** 20 GB clears neither fp8 (50.6) nor the 40 GB floor → local rungs all fail. Probe checks creds: `MODAL_TOKEN_*` set → **`cloud-modal`** (our pipeline on H100/A100). If only `FAL_KEY` → **`cloud-fal`** (`fal-ai/wan/v2.2-a14b/image-to-video`). If neither → **`grok`** (delegate `image_to_video`).

The single model walks `local-multi` (best) → `local-single fp8` → `local-offload` → `cloud-modal` → `cloud-fal` → `grok` purely as a function of free VRAM and creds, never a guess.

## Worked example 2 — `wan2.1-t2v-1.3b`, the trivial case

Wan2.1-T2V-1.3B needs ~13 GB bf16 with an 8 GB offload floor. On an idle ~48 GB card, `48 >= 13*1.1` (14.3) passes with enormous headroom → **`local-single` bf16, cuda:0**, fast iteration. It essentially never leaves rung 1. If you wanted to fill both cards for throughput, you would *not* use `local-multi` (it's not a `wan_big` model and wouldn't qualify anyway) — you'd launch **two `local-single` jobs**, one pinned to `cuda:0` and one to `cuda:1`, doubling clips/hour. This is the canonical illustration of "diffusers throughput = parallel single-GPU jobs, not sharding."