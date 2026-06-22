# Setup — first run (do once)

This is the one-time setup that `SKILL.md` and the scripts defer to. Work through it
top to bottom the first time you use the skill on this box; afterward, every run is just
`source scripts/env.sh` then `"$UV" run scripts/<tool>.py ...`.

Checklist (full detail below):

- [ ] 1. Clean env: `scripts/env.sh` exists, scrubs conda `LD_LIBRARY_PATH`, exports `$UV` + `HF_HOME`.
- [ ] 2. HF token + accept gated licenses (FLUX.1-dev, FLUX.2-dev, Gemma-3 for LTX-2).
- [ ] 3. One-time model weights (first `uv run` resolves PEP723 deps; weights land in `HF_HOME`). 217 GB budget.
- [ ] 4. (Optional) Wan official repo clone — only for the multi-GPU torchrun path.
- [ ] 5. (Optional) Cloud keys — only when probe routes to cloud-modal / cloud-fal.
- [ ] 6. CUDA 12.2 wheel note — install cu124 (or cu121) torch; Ampere uses SDPA/xformers, NOT FA3.
- [ ] 7. Smoke test.

---

## 1. Clean environment (`scripts/env.sh`)

**Why this matters.** Anaconda ships `/home/kita/anaconda3/lib/libtinfo.so.6`, and conda's
activation leaks its `lib` dir onto `LD_LIBRARY_PATH`. That stale libtinfo emits
`no version information available` and has actually **broken spawned subprocesses before
(soffice)**. Since every tool here either imports `torch` or shells out to `ffmpeg` /
`torchrun`, the conda paths MUST be stripped before anything runs. **Never use the conda
Python** — always run through `uv`.

The fix lives in `scripts/env.sh`: it scrubs conda/anaconda/miniconda entries out of
`LD_LIBRARY_PATH`, exports `$UV` (so `"$UV" run ...` works), pins the HF cache to the big
disk via `HF_HOME`, and sets `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` to cut
fragmentation on the big two-expert loads. `gen_video.py` / `gen_image.py` ALSO scrub
in-process (`clean_ld_environment`) and re-exec through `env.sh` when present, so they are
safe even if you forget to source it — but **always source it anyway** for the ffmpeg /
torchrun / huggingface-cli calls that don't self-scrub.

The exact scrub (what `env.sh` does, and the one-liner to reproduce it by hand):

```bash
# remove every conda/anaconda/miniconda dir from LD_LIBRARY_PATH (keep system libs)
export LD_LIBRARY_PATH="$(printf '%s' "${LD_LIBRARY_PATH:-}" | tr ':' '\n' \
  | grep -vE 'anaconda|miniconda|/conda' | paste -sd: -)"
# in a throwaway shell the brute-force version is fine:
unset LD_LIBRARY_PATH
```

If `scripts/env.sh` is missing, create it once (idempotent — safe to source repeatedly):

```bash
cat > /home/kita/.claude/skills/generate-edit-video/scripts/env.sh <<'EOF'
# Source me before any python/ffmpeg/torchrun/huggingface-cli call.
# Scrubs the anaconda libtinfo LD pollution and pins the HF cache to the big disk.

# 1) strip conda/anaconda/miniconda from LD_LIBRARY_PATH (keeps system libs)
if [ -n "${LD_LIBRARY_PATH:-}" ]; then
  LD_LIBRARY_PATH="$(printf '%s' "$LD_LIBRARY_PATH" | tr ':' '\n' \
    | grep -vE 'anaconda|miniconda|/conda' | paste -sd: -)"
  if [ -n "$LD_LIBRARY_PATH" ]; then export LD_LIBRARY_PATH; else unset LD_LIBRARY_PATH; fi
fi

# 2) uv binary (scripts read $UV; fall back to the known path)
export UV="${UV:-/home/kita/.local/bin/uv}"

# 3) HF cache on the big disk (217 GB free on /). Override HF_HOME to relocate.
export HF_HOME="${HF_HOME:-/home/kita/.cache/huggingface}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-1}"  # faster gated pulls

# 4) cut CUDA fragmentation for the A14B / 22B loads
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
EOF
```

Then verify:

```bash
source /home/kita/.claude/skills/generate-edit-video/scripts/env.sh
echo "$UV"; echo "$HF_HOME"; echo "${LD_LIBRARY_PATH:-<empty, good>}"
"$UV" --version          # confirms uv resolves and LD is clean
```

> If `HF_HOME` points anywhere off `/` (e.g. a small home quota on a separate mount),
> repoint it before downloading — LTX-2.3 alone is ~100 GB.

---

## 2. HF token + accepting gated licenses

Three repos are **gated** and 401 until you both (a) log in and (b) click "Agree" on the
model page in a browser while logged into the same HF account:

| Repo | Used by | Note |
|------|---------|------|
| `black-forest-labs/FLUX.1-dev` | `gen_image.py` (quality default) | gated, **non-commercial** |
| `black-forest-labs/FLUX.2-dev` | cloud / diffusers-git-main path | gated, large (~32 GB fp8) |
| `google/gemma-3-12b-it-qat-q4_0-unquantized` | LTX-2.3 text encoder (`gen_video_ltx2.py`) | gated |

```bash
source scripts/env.sh
"$UV" run --with huggingface_hub huggingface-cli login   # paste a READ token -> sets HF_TOKEN
# then in a browser, logged into the SAME account, open each page and click Agree:
#   https://huggingface.co/black-forest-labs/FLUX.1-dev
#   https://huggingface.co/black-forest-labs/FLUX.2-dev
#   https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized
```

Without acceptance, `from_pretrained` / `snapshot_download` / `huggingface-cli download`
return **401** on those repos. The ungated alternatives (FLUX.1-schnell, SDXL, LTX-Video
0.9.x with T5, Wan) need no agreement.

---

## 3. One-time model downloads + disk budget

You usually don't need to pre-download: `"$UV" run scripts/<tool>.py` resolves the PEP723
inline deps into a uv-managed venv on first run, and `from_pretrained` then pulls weights
into `HF_HOME` automatically. Pre-stage only if you want to avoid a mid-job download or
warm the cache deliberately:

```bash
source scripts/env.sh
# small / fast (good first pulls):
"$UV" run --with huggingface_hub huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B-Diffusers   # Wan-1.3B (small)
"$UV" run --with huggingface_hub huggingface-cli download Lightricks/LTX-Video               # LTX-Video 0.9.x (ungated)
# larger:
"$UV" run --with huggingface_hub huggingface-cli download Wan-AI/Wan2.2-I2V-A14B-Diffusers   # Wan-A14B (large, ~moe)
"$UV" run --with huggingface_hub huggingface-cli download black-forest-labs/FLUX.1-dev       # gated
# LTX-2.3 (gated Gemma; NOT diffusers — loaded by gen_video_ltx2.py via from_pretrained):
#   These two repos are gated: `huggingface-cli login` + accept BOTH licenses first.
#   gen_video_ltx2.py pulls weights itself on first run (into HF_HOME) through the
#   official Lightricks/LTX-2 pipeline; you normally do NOT pre-stage these.
#   If you do want to warm the cache, pull the WHOLE repos — the exact per-file
#   names/layout inside Lightricks/LTX-2.3 are NOT verified here (the LTX-2 repo has
#   no diffusers support and gen_video_ltx2.py treats its file layout as unconfirmed;
#   see its `# TODO[VERIFY]` notes). Do not invent individual *.safetensors filenames.
"$UV" run --with huggingface_hub huggingface-cli download Lightricks/LTX-2.3               # gated, ~22B + upscalers (~large)
"$UV" run --with huggingface_hub huggingface-cli download google/gemma-3-12b-it-qat-q4_0-unquantized   # gated text encoder
```

Rough sizes / disk budget (**~217 GB free on `/`** — plan, don't fill it):

| Model | Approx on disk |
|-------|----------------|
| Wan2.1-T2V-1.3B | small (~tens of GB) |
| Wan2.2-TI2V-5B | medium |
| Wan2.2-*-A14B (MoE, two experts) | large |
| LTX-Video 0.9.x | medium |
| FLUX.1-dev | ~tens of GB |
| **LTX-2.3 (22B + Gemma + upscalers)** | **~100 GB** |

LTX-2.3 is by far the heaviest single item; do not stage it alongside everything else
without checking `df -h /` first. Set a roomy `HF_HOME` if `/` is tight.

---

## 4. (Optional) Wan official repo — multi-GPU torchrun path

diffusers does **not** do multi-GPU for a single clip. The only way to split one Wan-A14B
720p full-quality clip across both A6000s is the **official Wan repo's torchrun launcher**
(`local-multi` in the probe ladder). Skip this unless the probe actually routes to
`local-multi` or you want maximum throughput with both cards idle.

```bash
source scripts/env.sh
git clone https://github.com/Wan-Video/Wan2.2.git /home/kita/wan-official
cd /home/kita/wan-official && "$UV" pip install -r requirements.txt
# weights for torchrun = the PLAIN repo, NOT the -Diffusers one:
"$UV" run --with huggingface_hub huggingface-cli download Wan-AI/Wan2.2-T2V-A14B --local-dir ./Wan2.2-T2V-A14B
# launch (both GPUs):
torchrun --nproc_per_node=2 generate.py --task t2v-A14B --size 1280*720 \
  --dit_fsdp --t5_fsdp --ulysses_size 2 --ckpt_dir ./Wan2.2-T2V-A14B --prompt "..."
```

**Never combine `--offload` with a multi-GPU launch** — `enable_model_cpu_offload` pins
one device and fights FSDP.

---

## 5. (Optional) Cloud keys — only for the cloud fallback

You only need these when `probe_backend.py` returns `cloud-modal` or `cloud-fal` (VRAM
short or both GPUs busy). The gating order the scripts use: `MODAL_TOKEN_ID` +
`MODAL_TOKEN_SECRET` -> cloud-modal; else `FAL_KEY` -> cloud-fal; else -> grok (delegated
to the grok-media skill, no key needed beyond its own login).

```bash
# Modal (scripts/cloud_modal.py) — sets MODAL_TOKEN_ID / MODAL_TOKEN_SECRET in ~/.modal.toml
"$UV" run --with modal modal token new
# fal (scripts/cloud_fal.py):
export FAL_KEY=...                # put in your shell profile if you use it often
```

If neither is configured, the cloud rung is simply skipped and the skill falls through to
Grok. That's fine — local-single covers almost everything on this 96 GB rig.

---

## 6. CUDA 12.2 wheel compatibility

The driver is **CUDA 12.2**, but the CUDA runtime ships **inside the PyTorch wheel**. CUDA
minor-version compatibility means **cu124 (and cu121 / cu126) wheels run fine on a 12.2
driver** — you do NOT need a cu122-exact wheel. `uv run` handles this via the PEP723 deps,
but if you build a venv by hand, install from the cu124 index:

```bash
source scripts/env.sh
"$UV" pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
# (cu121 also works against the 12.2 driver if you prefer)
```

These are **Ampere** A6000s (no Hopper FA3, limited fp8 matmul):

- Use **SDPA or xformers** attention — **NOT FlashAttention-3** (Hopper-only).
- fp8 *weight cast* for VRAM is fine; fp8 *matmul* acceleration is limited — don't expect
  H100-class fp8 speedups. `nvfp4` (Blackwell) is N/A — use `fp8-cast` for LTX-2.3.
- If `torch.cuda.is_available()` is `False` after a manual install: it's almost always (a)
  leftover conda LD pollution (re-source `env.sh`) or (b) a CPU-only wheel — reinstall from
  the cu124 index inside a clean uv venv.

---

## 7. Smoke test

Run these in order; each should succeed before the next. All assume you've `cd`'d into the
skill dir or use absolute paths.

```bash
cd /home/kita/.claude/skills/generate-edit-video
source scripts/env.sh

# (a) env is clean + uv works
"$UV" --version
echo "HF_HOME=$HF_HOME  LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-<empty:good>}"

# (b) GPUs visible to the RAW probe (stdlib only, no deps to resolve) -> JSON on stdout
"$UV" run scripts/probe_vram.py --required-mb 13000 --task t2v --pretty
#   expect gpu_count:2, two ~48000 free_mb entries, backend:"local-single"

# (c) tool wiring + decision logic, no weights pulled (dry run)
"$UV" run scripts/gen_video.py --backend auto --task t2v \
  --prompt "a calm sea at dawn" --out /tmp/smoke.mp4 --print-decision
"$UV" run scripts/gen_image.py --backend auto --prompt "a red apple" \
  --out /tmp/smoke.png --dry-run

# (d) ffmpeg present (editing path)
ffmpeg -version | head -1

# (e) first REAL local gen — small + fast, confirms torch+CUDA+download end to end
"$UV" run scripts/gen_video.py --backend wan --task t2v --model wan2.1-t2v-1.3b \
  --prompt "a paper boat floating down a gentle stream" \
  --num-frames 33 --steps 20 --out /tmp/smoke.mp4
ffprobe /tmp/smoke.mp4 2>&1 | grep -i duration
```

If (b) shows two ~48 GB cards and `nvidia_smi_available:true`, and (e) writes a playable
`/tmp/smoke.mp4`, the local path is fully wired. From here, normal usage is just
`source scripts/env.sh` then `"$UV" run scripts/<tool>.py ...` per `SKILL.md`.

For deeper troubleshooting (OOM ladder, VAE fp32, diffusers-git-main for FLUX.2/Z-Image,
the libtinfo gotcha in detail), see `reference/backend-selection.md`.
