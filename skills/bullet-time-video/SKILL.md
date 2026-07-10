---
name: bullet-time-video
description: Use when creating a viral "frozen moment / bullet-time / time-freeze" short video — an explosion (food, water, a spilled drink) suspended motionless in mid-air while the camera orbits the frozen scene, or a subject holding a cool pose while something bursts around them. Triggers: バズ動画 時間停止, バレットタイム, フリーズフレーム, 爆発が空中で静止, freeze frame, frozen explosion, food/water splash suspended, camera orbit around frozen scene.
---

# Bullet-Time / Freeze-Frame Video

## Overview

The viral "frozen explosion + moving camera" effect (food/water/drink bursting and suspended in mid-air, subject holding a cool pose). Core insight (learned the hard way, 2026-07-10):

- It is **NOT** reference-to-video / image-to-video that animates the *subject* — that moves the person and breaks the freeze.
- It is **NOT** true single-image 3D reconstruction (Gaussian Splatting: TripoSR/LGM/TripoSplat) — those are object-centric and **break on a photographic person+scene**.
- It **IS**: make one photorealistic still, then use an image-to-video model to add **only camera motion (scene frozen)** OR to **generate the explosion while the subject holds a pose**.

## The two proven methods

Pick by *what is frozen* in your still.

| | Still contains | i2v prompt does | Best for |
|---|---|---|---|
| **A. Frozen → orbit** | the explosion already frozen mid-air | move ONLY the camera in a dynamic orbit; keep scene frozen | true bullet-time; solid objects (food, plates, ice) |
| **B. Calm → explode** | a calm scene (no burst yet) | generate the burst in slow-mo while the subject holds pose | dynamic reveal; the person stays identical |

**Method A is the truest bullet-time.** Solid objects freeze well; **fluid water tends to un-freeze (falls/flows)** in i2v, so for water prefer Method B or accept slight motion.

## Exact commands (verified working)

Uses `video-media-studio`'s `cloud_atlascloud.py` (AtlasCloud) for i2v. `$UV` from that skill's `env.sh`.

**Still generation** (choose one).

**★ DEFAULTS for freeze stills (user-confirmed 2026-07-11), unless the user says otherwise:**
1. **Cinematic phrase** — always append `映画のワンシーンのようなハイクオリティな写真` / `cinematic movie-scene quality, dramatic lighting, shallow depth of field`. Verified to noticeably improve realism, lighting, and composition (low-angle, moody light) vs the same prompt without it.
2. **Framing = upper body** (`upper body shot, from the waist up`). Default to upper-body composition unless the user asks for full body.
3. **Reference use = lock face AND outfit** — when a reference image is given, the prompt MUST say `keep this exact same woman: her face, identity, and her outfit — do not change the face or the clothing`. To preserve a persona you MUST use a reference-based **edit** endpoint (Seedream 5 edit / Nano Banana 2 / Qwen-Image-Edit), NEVER text-to-image (text-to-image = a different face; a real mistake made 2026-07-11).
- **Codex GPT Image** — best scene build + realism, no reference needed (SFW scenes):
  `codex exec --skip-git-repo-check --sandbox workspace-write "Use your image_gen tool to generate ONE tall vertical photorealistic image. Prompt: <scene>, frozen in mid-air / bullet time, cinematic. リアルな実写写真: 毛穴・肌の質感を残す, CG/3Dレンダーっぽさをなくし実際のカメラで撮った写真に"` → output in `~/.codex/generated_images/<newest>/ig_*.png`.
- **AtlasCloud Seedream 5 / Nano Banana 2** (reference-consistent) — see 75Gravity `scripts/gen_ref_image.py` (base64 refs in HTTP body).
- **Local Qwen-Image-Edit-2511** to keep a specific persona's face: `gen_qwen_edit.py --image <ref.png> --repo Qwen/Qwen-Image-Edit-2511 --prompt "<new scene>, keep this exact face" --offload model --size 896x1600` (`CUDA_VISIBLE_DEVICES=N`, **no `--gpu` flag**).

**Method A — camera orbit on a frozen still** (Seedance is best; solid objects stay frozen):
```
"$UV" run cloud_atlascloud.py video --model bytedance/seedance-2.0/image-to-video \
  --image frozen_still.png \
  --prompt "A completely static frozen photograph, time is completely stopped. Absolutely nothing in the scene moves at all - the <objects>, droplets, splash and the person are all perfectly still and frozen solid, zero motion, NOT slow motion, no liquid flow, no changing splash. The ONLY thing that moves is the camera, which performs a smooth dynamic 180 degree orbit around the frozen subject." \
  --out orbit.mp4 --extra-json '{"duration":10,"resolution":"720p","ratio":"adaptive"}'
```
**★ Freeze reality (confirmed 2026-07-11):** Seedance/Kling i2v have NO motion/static control param and **cannot be forced to perfectly freeze — they always add slight slow-motion**, especially for liquids (solid objects freeze better). The aggressive "completely static / zero motion / NOT slow motion" prompt above minimizes it but does not eliminate it. **A mathematically perfect freeze + moving camera is only achievable with DepthFlow depth-parallax (see below) — but that has "cardboard" 3D.** So: single-image → (perfect freeze + cardboard 3D via DepthFlow) OR (clean 3D + slight slow-mo via i2v). Pick one; you cannot have both. For most viral clips the slight slow-mo i2v reads fine (bullet-time is itself slow-mo + camera).

**Method B — generate the explosion, subject holds pose**:
```
"$UV" run cloud_atlascloud.py video --model bytedance/seedance-2.0/image-to-video \
  --image calm_still.png \
  --prompt "In dramatic slow motion, the <food/water/drink> explodes and bursts into the air all around her. She stays completely still, holding her exact pose and looking at the camera. Only the <food/water> explodes." \
  --out explode.mp4 --extra-json '{"duration":5,"resolution":"720p","ratio":"adaptive","negative_prompt":"person moving, changing pose"}'
```

## Model choices (verified 2026-07-10)

- **Still**: Codex GPT Image = best realism + scene (no face-consistency need). Seedream 5 = reference-consistent, slightly gravure-idealized. Local Qwen-Edit-2511 = keep a persona's exact face, uncensored.
- **i2v**: **Seedance 2.0 = most dramatic burst / cleanest freeze-orbit (recommended)**. Kling v3 pro = more controlled/subtle.
- Always verify motion with `ffmpeg ... ssim` between first/last frame — do not judge "it moved" from two eyeballed frames (SSIM≈1.0 = static).

## Realism (default)

Apply `video-media-studio`'s realism naturalization by default (visible pores, real-camera, no CG/plastic-skin) unless the user asked for a non-realistic style. For Codex/Qwen-Edit pass it as Japanese natural text; for cloud prompt models add English keywords `natural skin texture with visible pores, unretouched, real camera, no CG, no plastic skin`.

## Common mistakes (each cost real iterations)

- **Used reference-to-video / animated the subject** → subject moves, not a freeze. Use i2v on a still with the freeze/pose prompt.
- **Tried single-image 3D reconstruction (TripoSR/LGM/TripoSplat/Hunyuan3D)** for a person+scene → breaks; those are object-only. Don't.
- **DepthFlow single-layer 2.5D parallax** → "cardboard"/edge-tearing, not clean 3D. Also: CLI default is **static** (no animation preset); needs `WINDOW_BACKEND=headless` + a Python `DepthScene` subclass whose `update()` animates `self.state.offset/isometric` (see `depthflow/examples/presets.py`). Use only for small, strictly-frozen parallax; not for big clean orbits.
- **i2v on water expecting it to freeze** → fluid falls. Solid food/plates freeze; for water use Method B or a very explicit "freeze frame, only camera" prompt and accept some motion.
- **Judged motion by eye** → measure with SSIM.

## Related

- **REQUIRED TOOLING:** `video-media-studio` (cloud_atlascloud.py, env.sh, realism-naturalization-prompts.md, gen_qwen_edit.py).
- `codex-consult` for a second opinion on technique when stuck.
