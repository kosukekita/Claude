# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "transformers>=4.56",
#   "accelerate",
#   "safetensors",
#   "sentencepiece",
#   "protobuf",
#   "pillow",
#   "huggingface_hub",
#   "diffusers @ git+https://github.com/huggingface/diffusers",
# ]
#
# # Pin torch to the CUDA 12.1 build: this rig's NVIDIA driver is CUDA 12.2
# # (12020); default PyPI torch wheels target a newer CUDA runtime and fail with
# # "driver is too old". cu121 wheels run fine on 12.2. torchvision is REQUIRED
# # for FLUX.2's PixtralProcessor (else it degrades to a stub and load fails).
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
gen_klein.py — FLUX.2-klein-9B finetune runner.

Loads the official diffusers base (black-forest-labs/FLUX.2-klein-9B) with
Flux2Pipeline.from_pretrained, then SWAPS the transformer for a community
single-file finetune (default: wikeeyang/Flux2-Klein-9B-True-V3 bf16) via
Flux2Transformer2DModel.from_single_file. The community repos ship flat
single-file .safetensors / .gguf (no model_index.json), so the pipeline as a
whole is NOT from_pretrained-loadable — only the transformer is swapped.

9B fits bf16 on one 48GB A6000 (~30GB). FLUX.2 ignores negative_prompt, so put
suppression (no tattoos / clean skin) in the POSITIVE prompt.

  source scripts/env.sh
  "$UV" run scripts/gen_klein.py --prompt "..." --size 832x1216 --seed 7 --out k.png
  # use a different finetune file / repo:
  "$UV" run scripts/gen_klein.py --transformer-repo wikeeyang/Flux2-Klein-9B-True-V3 \
      --transformer-file Flux2-Klein-9B-True-V3-bf16.safetensors --prompt "..." --out k.png
  # use the plain official base (no finetune swap):
  "$UV" run scripts/gen_klein.py --no-swap --prompt "..." --out k.png
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys


def log(msg: str) -> None:
    print(f"[gen_klein] {msg}", file=sys.stderr)


def free_vram_gb() -> float:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15,
        )
        vals = [float(x) / 1024.0 for x in out.stdout.split() if x.strip()]
        return max(vals) if vals else 0.0
    except Exception as exc:  # noqa: BLE001
        log(f"nvidia-smi failed: {exc}")
        return 0.0


def parse_size(s: str) -> tuple[int, int]:
    w, h = s.lower().split("x")
    return int(w), int(h)


def main() -> int:
    p = argparse.ArgumentParser(prog="gen_klein.py")
    p.add_argument("--prompt", required=True)
    p.add_argument("--negative-prompt", default=None,
                   help="klein (Flux2KleinPipeline) accepts a negative prompt")
    p.add_argument("--out", required=True)
    p.add_argument("--size", default="832x1216", help="WxH (FLUX.2 likes /32)")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--steps", type=int, default=28)
    p.add_argument("--guidance", type=float, default=4.0)
    p.add_argument("--base-repo", default="black-forest-labs/FLUX.2-klein-9B")
    p.add_argument("--transformer-repo",
                   default="wikeeyang/Flux2-Klein-9B-True-V3")
    p.add_argument("--transformer-file",
                   default="Flux2-Klein-9B-True-V3-bf16.safetensors")
    p.add_argument("--no-swap", action="store_true",
                   help="use the official base transformer (skip finetune swap)")
    p.add_argument("--offload", action="store_true",
                   help="force model cpu offload (auto if VRAM tight)")
    args = p.parse_args()

    width, height = parse_size(args.size)

    import torch  # noqa: PLC0415
    # klein-9B uses a Qwen3 text encoder, NOT Mistral3 like FLUX.2-dev, so it
    # needs the dedicated Flux2KleinPipeline (diffusers main). The generic
    # Flux2Pipeline hardcodes the Mistral3 chat template and crashes on klein.
    from diffusers import (  # noqa: PLC0415
        Flux2KleinPipeline,
        Flux2Transformer2DModel,
    )

    free = free_vram_gb()
    log(f"free VRAM: {free:.1f}GB; base={args.base_repo}; "
        f"swap={'no' if args.no_swap else args.transformer_repo}")
    # 9B bf16 ~30GB; offload if we are not comfortably above that.
    offload = args.offload or (free and free < 34.0)

    log(f"loading base pipeline {args.base_repo} (Flux2KleinPipeline, bf16)")
    pipe = Flux2KleinPipeline.from_pretrained(
        args.base_repo, torch_dtype=torch.bfloat16
    )

    if not args.no_swap:
        from huggingface_hub import hf_hub_download  # noqa: PLC0415
        log(f"downloading finetune transformer "
            f"{args.transformer_repo}/{args.transformer_file}")
        tpath = hf_hub_download(
            repo_id=args.transformer_repo, filename=args.transformer_file
        )
        log(f"loading transformer via from_single_file: {tpath}")
        transformer = Flux2Transformer2DModel.from_single_file(
            tpath, torch_dtype=torch.bfloat16,
            config=args.base_repo, subfolder="transformer",
        )
        pipe.transformer = transformer
        log("transformer swapped to finetune")

    if offload:
        log("enable_model_cpu_offload (VRAM tight or forced)")
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")

    gen = None
    if args.seed is not None:
        gen = torch.Generator("cpu").manual_seed(args.seed)

    log(f"generating {width}x{height} steps={args.steps} "
        f"guidance={args.guidance} seed={args.seed} "
        f"neg={'yes' if args.negative_prompt else 'no'}")
    call_kwargs: dict = dict(
        prompt=args.prompt,
        width=width,
        height=height,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=gen,
    )
    if args.negative_prompt:
        call_kwargs["negative_prompt"] = args.negative_prompt
    image = pipe(**call_kwargs).images[0]

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    image.save(args.out)
    log(f"saved -> {os.path.abspath(args.out)}")
    print(os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
