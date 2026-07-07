#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers",
#   "transformers>=4.56",
#   "accelerate",
#   "bitsandbytes",
#   "pillow",
#   "sentencepiece",
#   "protobuf",
#   "safetensors",
# ]
#
# # cu121 torch: this rig's driver is CUDA 12.2; default wheels target newer CUDA
# # and fail. torchvision is REQUIRED for FLUX.2's PixtralProcessor. Same pin as
# # gen_image.py / gen_qwen_edit.py.
# [tool.uv.sources]
# torch = { index = "pytorch-cu121" }
# torchvision = { index = "pytorch-cu121" }
#
# [[tool.uv.index]]
# name = "pytorch-cu121"
# url = "https://download.pytorch.org/whl/cu121"
# explicit = true
# ///
"""
gen_flux2_edit.py — FLUX.2-dev reference-conditioned image EDITING for the
video-media-studio skill.

Unlike gen_image.py's flux.2-dev backend (which only does text-to-image), this
passes `image=[PIL, ...]` to Flux2Pipeline, which the official pipeline supports
for SINGLE- and MULTI-reference editing (up to ~10 refs). FLUX.2 keeps subject
identity/body-type from the reference(s) while following the instruction prompt.

The 32B transformer + Mistral3 text encoder does not fit bf16 on one 48GB A6000,
so this ALWAYS loads bitsandbytes 4-bit NF4 (transformer + text_encoder, ~20GB)
plus model cpu-offload for headroom (same approach as gen_image.py flux.2-dev).

NOTE: FLUX.2 [dev] license is community / NON-COMMERCIAL and GATED on HF (accept
the license + set HF token). FLUX.2 ignores negative_prompt — steer with positive
phrasing. For FLUX.2-klein (9B, lighter, Qwen3 encoder) pass --repo/--pipeline.

Usage:
  source scripts/env.sh
  "$UV" run scripts/gen_flux2_edit.py --image ref.png \
      --prompt "Edit this photo: remove all clothing ..." --out out.png
  # multi-reference (identity + pose ref etc.): repeat --image (max ~10)
"""

import argparse
import sys
import torch
from PIL import Image, ImageOps


def log(msg):
    print(f"[gen_flux2_edit] {msg}", file=sys.stderr, flush=True)


def load_img(p):
    im = Image.open(p)
    return ImageOps.exif_transpose(im).convert("RGB")


def main():
    ap = argparse.ArgumentParser(
        description="FLUX.2-dev reference-conditioned image editing (image=[...])")
    ap.add_argument("--image", action="append", required=True,
                    help="reference image (repeat 1-10 times for multi-reference)")
    ap.add_argument("--prompt", required=True, help="edit instruction")
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo", default="black-forest-labs/FLUX.2-dev",
                    help="HF repo. Default FLUX.2-dev. Use black-forest-labs/FLUX.2-klein-9B "
                         "with --pipeline klein for the lighter 9B editor.")
    ap.add_argument("--pipeline", choices=["dev", "klein"], default="dev",
                    help="dev=Flux2Pipeline (Mistral3 enc), klein=Flux2KleinPipeline (Qwen3 enc)")
    ap.add_argument("--size", default=None, help="WxH for output (FLUX.2 likes /32; default: model default)")
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--guidance", type=float, default=4.0,
                    help="guidance_scale (FLUX.2 default 4.0; try 2.5-4.0)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-quant", action="store_true",
                    help="disable 4-bit quantization (needs >48GB; only for smaller repos)")
    ap.add_argument("--offload", choices=["none", "model", "sequential"], default="model")
    ap.add_argument("--multi-gpu", action="store_true",
                    help="shard the model across all visible GPUs with device_map='balanced' "
                         "(bf16, NO quant, NO offload). On 2x48GB this fits FLUX.2-dev bf16 (~64GB) "
                         "WITHOUT the 4-bit+offload slashing that stalls a single 48GB card. "
                         "Do NOT set CUDA_VISIBLE_DEVICES to one GPU when using this.")
    args = ap.parse_args()

    if len(args.image) > 10:
        log(f"WARN: {len(args.image)} images given; FLUX.2 conditions on up to ~10. Using first 10.")
        args.image = args.image[:10]
    imgs = [load_img(p) for p in args.image]
    log(f"refs={len(imgs)} sizes={[im.size for im in imgs]} pipeline={args.pipeline}")

    if args.pipeline == "klein":
        from diffusers import Flux2KleinPipeline as PipeCls
    else:
        from diffusers import Flux2Pipeline as PipeCls

    from_kwargs = dict(torch_dtype=torch.bfloat16)

    # Multi-GPU sharding: bf16 across all visible cards. This AVOIDS the 4-bit +
    # cpu-offload path that thrashes/stalls FLUX.2-dev on a single 48GB A6000
    # (verified: 17min at 0% GPU util). device_map='balanced' splits the 64GB
    # bf16 model across 2x48GB. Force no quant + no offload in this mode.
    if args.multi_gpu:
        args.no_quant = True
        args.offload = "none"
        from_kwargs["device_map"] = "balanced"
        log("multi-gpu: device_map='balanced' bf16 across all visible GPUs (no quant, no offload)")

    # 4-bit NF4 so the 32B (+Mistral3) fits on one 48GB card. Same config as
    # gen_image.py flux.2-dev. klein (9B) also benefits but can run bf16 if desired.
    if not args.no_quant:
        try:
            from diffusers import PipelineQuantizationConfig
            comps = ["transformer", "text_encoder"]
            from_kwargs["quantization_config"] = PipelineQuantizationConfig(
                quant_backend="bitsandbytes_4bit",
                quant_kwargs={
                    "load_in_4bit": True,
                    "bnb_4bit_quant_type": "nf4",
                    "bnb_4bit_compute_dtype": torch.bfloat16,
                },
                components_to_quantize=comps,
            )
            log(f"loading with bitsandbytes 4-bit NF4 (components={comps})")
        except Exception as exc:  # noqa: BLE001
            log(f"4-bit quantization unavailable ({exc}); trying bf16 (may OOM)")

    log(f"loading {args.repo} ({PipeCls.__name__}); offload={args.offload} multi_gpu={args.multi_gpu}")
    pipe = PipeCls.from_pretrained(args.repo, **from_kwargs)

    if args.multi_gpu:
        # device_map already placed the modules across GPUs; do NOT call .to()/offload.
        log("multi-gpu: pipeline already sharded via device_map; skipping .to()/offload")
    elif args.offload == "model":
        pipe.enable_model_cpu_offload()
    elif args.offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.to("cuda")

    gen = torch.Generator(device="cpu").manual_seed(args.seed)
    kw = dict(
        image=imgs if len(imgs) > 1 else imgs[0],
        prompt=args.prompt,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=gen,
    )
    if args.size:
        w, h = (int(x) for x in args.size.lower().split("x"))
        kw["width"], kw["height"] = w, h
    log(f"generating: steps={args.steps} guidance={args.guidance} seed={args.seed}")
    out = pipe(**kw).images[0]
    out.save(args.out)
    log(f"WROTE {args.out} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
