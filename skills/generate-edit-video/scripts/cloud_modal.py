#!/usr/bin/env python3
"""Modal cloud-GPU fallback for diffusers video/image generation.

WHEN TO USE THIS
================
This is the LAST-but-one rung of the backend ladder in `probe_backend.py`
(local-single > local-offload > local-multi-GPU > **cloud-modal** > cloud-fal > grok).
On the local 2x RTX A6000 rig (96 GB) almost every model fits locally, so this
script runs ONLY when probe selects `cloud-modal` — i.e. local VRAM is busy /
insufficient AND you want a CUSTOM diffusers pipeline (specific weights/revision,
LoRAs, your own pre/post) on the cheapest raw GPU-seconds. If you just want a
hosted endpoint with zero infra, prefer fal.ai / Replicate (see the bottom notes).

WHAT IT DOES
============
Defines a Modal app that:
  * builds a container image with torch + diffusers (git main) + deps,
  * caches model weights on a persistent Volume (download once, reuse forever),
  * loads the requested pipeline once per warm container (@modal.enter),
  * runs t2v / i2v (Wan, LTX-Video) OR t2i (FLUX, Z-Image, SD3.5, Qwen-Image,
    FLUX.2) on a cloud GPU (@modal.method), and
  * returns the rendered bytes; a @app.local_entrypoint writes the mp4/png to a
    path ON YOUR machine.

--------------------------------------------------------------------------------
MODAL TOKEN SETUP (one time)
--------------------------------------------------------------------------------
  uv tool install modal            # or: uv pip install modal  (inside a venv)
  modal setup                      # opens a browser, writes ~/.modal.toml
    # headless / CI alternative (service-user token):
    #   export MODAL_TOKEN_ID=ak-...
    #   export MODAL_TOKEN_SECRET=as-...
  # Gated weights (FLUX.1/2-dev, LTX-2's Gemma-3) need a HuggingFace token baked
  # in at build time as a Modal secret:
  #   modal secret create huggingface-token HF_TOKEN=hf_xxx   # read scope
  # New accounts get ~$30/month of free compute credit.

  # Deploy (persistent endpoint, optional):  modal deploy scripts/cloud_fallback_modal.py
  # One-shot run from local:
  #   source scripts/env.sh   # clean LD_LIBRARY_PATH (anaconda libtinfo gotcha), pin $UV
  #   "$UV" run modal run scripts/cloud_fallback_modal.py --task t2v \
  #       --model ltx-video-0.9.8 --prompt "a red fox running through snow" --out out.mp4
  #   "$UV" run modal run scripts/cloud_fallback_modal.py --task i2v \
  #       --model wan2.2-i2v-a14b --image in.jpg --prompt "she turns to camera" --out out.mp4
  #   "$UV" run modal run scripts/cloud_fallback_modal.py --task t2i \
  #       --model flux.1-dev --prompt "cinematic portrait, neon street" --out out.png

--------------------------------------------------------------------------------
ROUGH COST (Modal on-demand, per-SECOND, billed only while the function runs;
no idle charge, scale-to-zero; cold-start weight download IS billed once — that
is what the Volume cache avoids on subsequent calls)
--------------------------------------------------------------------------------
  GPU            ~$/s        ~$/hr
  H100           0.001097    3.95
  A100-80GB      0.000694    2.50
  A100-40GB      0.000583    2.10
  L40S          0.000542    1.95
  A10G          0.000306    1.10
  (+ small CPU/RAM charges)
  Practical figures (warm container, weights already cached):
    * LTX-Video 480p short clip on H100/A100: seconds  -> a few cents/clip.
    * Wan-14B (A14B) clip on H100/A100-80GB, ~1-3 min  -> ~$0.07-0.20/clip.
    * FLUX.1-dev image on A100-80GB, ~10-20s            -> ~$0.01-0.02/image.
  First-ever call per model adds a one-time weight-download cost (minutes) — keep
  it on the Volume so you never pay it twice.

--------------------------------------------------------------------------------
ALTERNATIVE, EVEN-SIMPLER FALLBACKS (no infra to maintain)
--------------------------------------------------------------------------------
  * fal.ai  -> hosted Wan / LTX / FLUX endpoints, billed per OUTPUT-second
              (pay only for successful output). Fastest to integrate; no image
              build, no Volume, no pipeline code. Use when one of their hosted
              endpoints already serves the exact model. See scripts/cloud_fal.py.
                - fal-ai/wan/v2.2-a14b/{text,image}-to-video  ($0.04-0.08/out-s)
                - fal-ai/ltx-2.3/{text,image}-to-video[/fast] ($0.04-0.24/out-s)
                - fal-ai/flux/* for images.
  * Replicate -> run published models (lightricks/ltx-video, wan-video/*) via a
              one-line `replicate.run(...)`, billed per HARDWARE-second. Per-second
              GPU rates run ~2-4x Modal's for the same silicon (convenience
              premium) but you write ZERO pipeline code.
  DECISION: model already hosted + want it working in 10 min -> fal/Replicate.
            Need a custom pipeline / specific revision / LoRA / cheapest GPU-s,
            and you maintain the code -> Modal (this file).
  (Grok is the terminal fallback below all of these; it is delegated entirely to
   the grok-media skill — never re-implemented here. See SKILL.md.)
--------------------------------------------------------------------------------
"""

from __future__ import annotations

import base64
from pathlib import Path

import modal

# --------------------------------------------------------------------------- #
# Model registry (mirrors scripts/models.py MODEL_REQUIREMENTS keys so the same
# --model id used locally also works in the cloud). Kept inline so this file is
# runnable on Modal's builders without importing the local sibling module.
# --------------------------------------------------------------------------- #
# task: t2v | i2v | t2i
# repo: HuggingFace repo loaded with diffusers from_pretrained
# pipe: diffusers pipeline class name
# fp32_vae: keep the VAE in float32 (Wan/LTX decode degrades visibly in bf16)
# turbo: distilled/turbo model -> guidance ~0, few steps
# gated: needs the huggingface-token secret (gated/non-commercial license)
MODELS: dict[str, dict] = {
    # ---- video: Wan (Alibaba) ----
    "wan2.1-t2v-1.3b": dict(
        task="t2v", repo="Wan-AI/Wan2.1-T2V-1.3B-Diffusers", pipe="WanPipeline",
        fp32_vae=True, fps=16, frames=81, steps=40, guidance=5.0, gated=False,
    ),
    "wan2.2-ti2v-5b": dict(
        task="t2v", repo="Wan-AI/Wan2.2-TI2V-5B-Diffusers", pipe="WanPipeline",
        fp32_vae=True, fps=24, frames=81, steps=40, guidance=5.0, gated=False,
    ),
    "wan2.2-t2v-a14b": dict(
        task="t2v", repo="Wan-AI/Wan2.2-T2V-A14B-Diffusers", pipe="WanPipeline",
        fp32_vae=True, fps=16, frames=81, steps=40, guidance=3.5, gated=False,
    ),
    "wan2.2-i2v-a14b": dict(
        task="i2v", repo="Wan-AI/Wan2.2-I2V-A14B-Diffusers",
        pipe="WanImageToVideoPipeline",
        fp32_vae=True, fps=16, frames=81, steps=40, guidance=3.5, gated=False,
    ),
    # ---- video: LTX-Video 0.9.x (diffusers; LTX-2.3 is NOT in diffusers, use
    #      scripts/gen_video_ltx2.py / fal for that) ----
    "ltx-video-0.9.8": dict(
        task="t2v", repo="Lightricks/LTX-Video", pipe="LTXPipeline",
        fp32_vae=False, fps=24, frames=121, steps=40, guidance=3.0, gated=False,
    ),
    "ltx-video-0.9.8-i2v": dict(
        task="i2v", repo="Lightricks/LTX-Video", pipe="LTXImageToVideoPipeline",
        fp32_vae=False, fps=24, frames=121, steps=40, guidance=3.0, gated=False,
    ),
    # ---- image ----
    "flux.1-dev": dict(
        task="t2i", repo="black-forest-labs/FLUX.1-dev", pipe="FluxPipeline",
        steps=40, guidance=3.5, turbo=False, gated=True,
    ),
    "flux.1-schnell": dict(
        task="t2i", repo="black-forest-labs/FLUX.1-schnell", pipe="FluxPipeline",
        steps=4, guidance=0.0, turbo=True, gated=False,
    ),
    "flux.2-dev": dict(
        task="t2i", repo="black-forest-labs/FLUX.2-dev", pipe="Flux2Pipeline",
        steps=50, guidance=4.0, turbo=False, gated=True,
    ),
    "qwen-image": dict(
        task="t2i", repo="Qwen/Qwen-Image", pipe="QwenImagePipeline",
        steps=50, guidance=3.5, turbo=False, gated=False,
    ),
    "sd3.5-large": dict(
        task="t2i", repo="stabilityai/stable-diffusion-3.5-large",
        pipe="StableDiffusion3Pipeline",
        steps=40, guidance=4.0, turbo=False, gated=False,
    ),
    "z-image-turbo": dict(
        task="t2i", repo="Tongyi-MAI/Z-Image-Turbo", pipe="ZImagePipeline",
        steps=9, guidance=0.0, turbo=True, gated=False,
    ),
}

CACHE_DIR = "/cache"

app = modal.App("generate-edit-video-cloud-fallback")

# Persistent weight cache so a model downloads exactly once across all calls.
weights_volume = modal.Volume.from_name(
    "gev-hf-cache", create_if_missing=True
)

# Container image: torch CUDA wheels + diffusers from git main (FLUX.2 / Z-Image /
# Wan2.2 land in main before stable). uv_pip_install for fast resolves.
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .uv_pip_install(
        "torch==2.7.0",
        "torchvision",
        "git+https://github.com/huggingface/diffusers.git",
        "transformers>=4.51.3",
        "accelerate",
        "safetensors",
        "sentencepiece",
        "protobuf",
        "ftfy",
        "imageio",
        "imageio-ffmpeg",
        "bitsandbytes",
        "huggingface-hub",
        "pillow",
        extra_index_url="https://download.pytorch.org/whl/cu126",
    )
    .env(
        {
            "HF_HOME": CACHE_DIR,
            "HF_HUB_ENABLE_HF_TRANSFER": "0",
            # reduce fragmentation OOM for big two-stage / two-expert models
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        }
    )
)

# HF token secret is OPTIONAL (only gated repos need it). We attach it always;
# Modal tolerates a missing secret only if you remove it — so create it once with
#   modal secret create huggingface-token HF_TOKEN=hf_xxx
# If you never touch gated models you may delete `secrets=[...]` below.
try:
    HF_SECRET = [modal.Secret.from_name("huggingface-token")]
except Exception:  # secret not created yet; gated models will then 401
    HF_SECRET = []


@app.cls(
    image=image,
    # try the best available GPU, fall back down the list if unavailable.
    # NOTE: "any" is NOT a valid Modal GPU type — use concrete types only.
    gpu=["H100", "A100-80GB", "A100-40GB", "L40S", "A10G"],
    volumes={CACHE_DIR: weights_volume},
    secrets=HF_SECRET,
    timeout=30 * 60,          # generous: cold download + long video render
    scaledown_window=5 * 60,  # keep warm 5 min between calls (skip reload cost)
)
class Generator:
    # `model` is a Modal parameter so each distinct model gets its own warm
    # container (avoids reloading a different pipeline on every call).
    model: str = modal.parameter(default="ltx-video-0.9.8")

    @modal.enter()
    def load(self):
        import torch
        import diffusers

        spec = MODELS[self.model]
        pipe_cls = getattr(diffusers, spec["pipe"])
        kwargs = dict(torch_dtype=torch.bfloat16)

        # Wan/LTX: load a float32 VAE separately for clean decode.
        if spec.get("fp32_vae"):
            try:
                from diffusers import AutoencoderKLWan
                if spec["repo"].startswith("Wan-AI/"):
                    kwargs["vae"] = AutoencoderKLWan.from_pretrained(
                        spec["repo"], subfolder="vae", torch_dtype=torch.float32
                    )
            except Exception:
                pass  # LTX handles its own VAE; fall through

        self.pipe = pipe_cls.from_pretrained(spec["repo"], **kwargs)
        # Cloud GPUs are big; move whole pipe to GPU for speed. If a model is
        # too large for the selected card, enable_model_cpu_offload() instead.
        try:
            self.pipe.to("cuda")
        except Exception:
            self.pipe.enable_model_cpu_offload()

        # persist anything newly downloaded into the Volume
        weights_volume.commit()
        self.spec = spec

    def _gen_video(self, prompt, negative, image_b64, width, height,
                   num_frames, steps, guidance, seed):
        import tempfile
        import torch
        from diffusers.utils import export_to_video, load_image

        spec = self.spec
        gen = torch.Generator("cpu").manual_seed(seed) if seed is not None else None
        call = dict(
            prompt=prompt,
            negative_prompt=negative,
            height=height,
            width=width,
            num_frames=num_frames or spec["frames"],
            num_inference_steps=steps or spec["steps"],
            guidance_scale=guidance if guidance is not None else spec["guidance"],
            generator=gen,
        )
        if spec["task"] == "i2v":
            if not image_b64:
                raise ValueError("i2v requires --image")
            tmp_in = Path(tempfile.mkdtemp()) / "in.png"
            tmp_in.write_bytes(base64.b64decode(image_b64))
            call["image"] = load_image(str(tmp_in))
        # Wan2.2 A14B is a two-stage (MoE) denoiser; pass guidance_scale_2 too.
        if "a14b" in self.model:
            call["guidance_scale_2"] = call["guidance_scale"]

        frames = self.pipe(**call).frames[0]
        out = Path(tempfile.mkdtemp()) / "out.mp4"
        export_to_video(frames, str(out), fps=spec["fps"])
        return out.read_bytes()

    def _gen_image(self, prompt, negative, width, height, steps, guidance, seed):
        import tempfile
        import torch

        spec = self.spec
        gen = torch.Generator("cpu").manual_seed(seed) if seed is not None else None
        g = guidance if guidance is not None else spec["guidance"]
        if spec.get("turbo"):
            g = 0.0  # turbo/distilled models break with high CFG
        img = self.pipe(
            prompt=prompt,
            negative_prompt=negative,
            height=height,
            width=width,
            num_inference_steps=steps or spec["steps"],
            guidance_scale=g,
            generator=gen,
        ).images[0]
        out = Path(tempfile.mkdtemp()) / "out.png"
        img.save(str(out))
        return out.read_bytes()

    @modal.method()
    def generate(self, task: str, prompt: str, negative: str = "",
                 image_b64: str | None = None, width: int = 768,
                 height: int = 512, num_frames: int | None = None,
                 steps: int | None = None, guidance: float | None = None,
                 seed: int | None = None) -> bytes:
        if task in ("t2v", "i2v"):
            return self._gen_video(prompt, negative, image_b64, width, height,
                                   num_frames, steps, guidance, seed)
        if task == "t2i":
            return self._gen_image(prompt, negative, width, height, steps,
                                   guidance, seed)
        raise ValueError(f"unknown task {task!r}")


@app.local_entrypoint()
def main(
    task: str = "t2v",
    model: str = "ltx-video-0.9.8",
    prompt: str = "a red fox running through snow, cinematic, golden hour",
    negative: str = "worst quality, blurry, distorted, watermark, text",
    image: str = "",          # local path for i2v (becomes base64 over the wire)
    out: str = "out.mp4",
    width: int = 768,
    height: int = 512,
    num_frames: int = 0,      # 0 -> model default
    steps: int = 0,           # 0 -> model default
    guidance: float = -1.0,   # <0 -> model default
    seed: int = -1,           # <0 -> random
):
    """Run a generation on a cloud GPU and save the result locally.

    The chosen `model` must exist in MODELS above and match `task`.
    """
    if model not in MODELS:
        raise SystemExit(
            f"unknown model {model!r}; choose one of: {', '.join(MODELS)}"
        )
    spec = MODELS[model]
    if spec["task"] != task:
        raise SystemExit(
            f"model {model!r} is a {spec['task']} model, not {task!r}"
        )

    image_b64 = None
    if image:
        image_b64 = base64.b64encode(Path(image).read_bytes()).decode()

    gen = Generator(model=model)
    data: bytes = gen.generate.remote(
        task=task,
        prompt=prompt,
        negative=negative,
        image_b64=image_b64,
        width=width,
        height=height,
        num_frames=num_frames or None,
        steps=steps or None,
        guidance=None if guidance < 0 else guidance,
        seed=None if seed < 0 else seed,
    )
    out_path = Path(out)
    out_path.write_bytes(data)
    print(f"saved {out_path.resolve()} ({len(data):,} bytes) "
          f"[model={model} task={task}]")
