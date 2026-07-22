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
4. **★ Camera angle of the still = DIAGONAL / three-quarter, NOT frontal.** The still's camera angle sets the i2v camera's range: **a frontal first frame can only pan slightly (it looks like a straight-on shot the whole time); a diagonal (≈45° three-quarter) first frame lets the i2v camera sweep the full ~120° arc from one diagonal across to the opposite diagonal while keeping the subject/chest in frame** (user insight, verified 2026-07-11). Prompt: `photographed from a three-quarter diagonal camera angle, ~45 degrees to her side, dynamic diagonal composition, NOT a straight-on frontal view, but her chest/upper body still facing the lens`.
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

**★ Freeze prompt cookbook (2026-07-22 beer-foam freeze-orbit session, Codex-reviewed — apply ALL whenever prompting a freeze/bullet-time i2v. Scope: single-session empirical findings on Seedance 2.0, not universal laws; treat thresholds as starting points):**
1. **Gaze: freeze it in WORLD space, never "locked on camera".** A frozen statue must NOT keep eye contact while the camera orbits — prompting eye-contact tracking = eye movement = freeze break. Write: `Her eyes and her gaze stay frozen in world space exactly as in the first frame — she never blinks, her eyes never move, her expression never changes.` (Seedance obeys this.) In QC, the gaze "looking away" at the end of the orbit is CORRECT physics (world-fixed gaze + camera moved), not a violation.
2. **Foam/liquid = temporal-consistency failure modes; prompt against EACH.** Ambiguous fine structure (foam, splash, droplets, hair) can fail several ways: flow/fall, silhouette drift, expansion, duplication, lattice-like proliferation, attachment to the face (one 15s take grew a lattice ~3× the original and stuck to her face). This is consistency breakdown, NOT a universal "liquids always grow". Counter: `The foam, splash and every droplet remain frozen in world space exactly as in frame 1 — no flow, no fall, no growth, no spreading, no duplication, no merging, no new droplets, no silhouette change, no contact with her face.` Negative (subject motion + shape change, systematized): `liquid flow, falling droplets, growing foam, multiplying foam, spreading splash, new droplets, lattice pattern, blink, eye movement, expression change, breathing, hair movement, clothing movement, body warping`.
3. **Long durations are a RISK FACTOR for drift, not a proven cause.** One 15s take failed (foam growth) while the same prompt at 10s passed — a single uncontrolled comparison (seed variance and duration-dependent sampling not excluded). Practical rule: prefer ≤10s takes for freezes; for longer deliverables generate 10s and retime (`setpts=1.5*PTS` — a constant-speed orbit retimes cleanly; only the camera slows, a genuinely frozen subject is unaffected). Add optical-flow interpolation ONLY if duplicated-frame judder is visible (it warps foam/hair/occlusion edges). Don't chain two takes (continuity seam at the join).
4. **Wide arcs hallucinate the revealed background** — text signboards and crowd figures appeared once the arc exceeded ~45° into unseen space. `≤40–45°` is this scene's empirical safe range, not a model constant: **start with a 10–20° test arc and widen only after QC passes.** Add: `The arc is short enough that NO new background area is ever revealed — the background stays exactly what is visible in the first frame, only shifting with parallax; no signs, no text, no letters, no people ever appear.` Negative: `wide arc, new background revealed, text, letters, signboard, banner, extra people`.
5. **Pivot the arc on the body area that must stay centered**: `the camera arc pivots around <area> — kept approximately centered, without warping, while her face stays fully visible in the upper part of the frame.` (An over-strict "exact center" can induce body-warp / fake-stabilizer artifacts on some models.)
6. **Kill the opening static hold**: i2v tends to hold the first frame before moving — `already in smooth orbital motion at the very first frame, no static hold`. Not guaranteed; if a hold remains, trim the first frames in edit rather than re-rolling.
7. **Seedance i2v accepted duration 15** (this provider's schema, range 4–15; provider/API-version dependent) — but per #3, prefer ≤10s for freezes.
8. **Freeze success is narrow — select across seeds.** Several short random-seed takes + picking the least-drifting one beats betting on a single long take.

**Method B — generate the explosion, subject holds pose**:
```
"$UV" run cloud_atlascloud.py video --model bytedance/seedance-2.0/image-to-video \
  --image calm_still.png \
  --prompt "In dramatic slow motion, the <food/water/drink> explodes and bursts into the air all around her. She stays completely still, holding her exact pose and looking at the camera. Only the <food/water> explodes." \
  --out explode.mp4 --extra-json '{"duration":5,"resolution":"720p","ratio":"adaptive","negative_prompt":"person moving, changing pose"}'
```

## Model choices (verified 2026-07-10)

- **Still**: Codex GPT Image = best realism + scene (no face-consistency need). Seedream 5 = reference-consistent, slightly gravure-idealized. Local Qwen-Edit-2511 = keep a persona's exact face, uncensored.
- **i2v**: **Seedance 2.0 = most dramatic burst / cleanest freeze-orbit (recommended)**. **Kling = not recommended for frozen-person orbits** (2026-07-22 single-session evidence: kwaivgi/kling-v3.0-pro i2v kept animating the subject — expression cycled through a live laugh, foam became a pouring stream — despite an aggressive freeze prompt + cfg_scale 0.7; cfg_scale is not a freeze control). Not proof Kling can never freeze — re-evaluate on new versions; meanwhile use Seedance for freeze-orbits.
- Verify motion objectively, never by eye. Static camera → `ffmpeg ... ssim` between first/last frame (SSIM≈1.0 = static). **Orbiting camera → first-vs-last is INVALID (huge parallax); extract 1 fps frames and compare ADJACENT pairs** for splash-silhouette constancy (grow/fall/multiply = fail), plus a full-speed scrub for blinks/expression changes.

## Realism (default)

Apply `video-media-studio`'s realism naturalization by default (visible pores, real-camera, no CG/plastic-skin) unless the user asked for a non-realistic style. For Codex/Qwen-Edit pass it as Japanese natural text; for cloud prompt models add English keywords `natural skin texture with visible pores, unretouched, real camera, no CG, no plastic skin`.

## Common mistakes (each cost real iterations)

- **Used reference-to-video / animated the subject** → subject moves, not a freeze. Use i2v on a still with the freeze/pose prompt.
- **Tried single-image 3D reconstruction (TripoSR/LGM/TripoSplat/Hunyuan3D)** for a person+scene → breaks; those are object-only. Don't.
- **DepthFlow single-layer 2.5D parallax** → "cardboard"/edge-tearing, not clean 3D. Also: CLI default is **static** (no animation preset); needs `WINDOW_BACKEND=headless` + a Python `DepthScene` subclass whose `update()` animates `self.state.offset/isometric` (see `depthflow/examples/presets.py`). Use only for small, strictly-frozen parallax; not for big clean orbits.
- **i2v on water expecting it to freeze** → fluid falls. Solid food/plates freeze; for water use Method B or a very explicit "freeze frame, only camera" prompt and accept some motion.
- **Prompted "eyes locked on the camera" during an orbit** → forces eye tracking = the "statue" moves. Freeze the gaze as in the first frame (cookbook #1).
- **Let the arc run wide (>45°) into unseen background** → hallucinated text signboards / crowd figures late in the clip (cookbook #4).
- **Judged motion by eye** → measure objectively (SSIM for static camera; 1 fps adjacent-pair comparison for orbits).

## Related

- **REQUIRED TOOLING:** `video-media-studio` (cloud_atlascloud.py, env.sh, realism-naturalization-prompts.md, gen_qwen_edit.py).
- `codex-consult` for a second opinion on technique when stuck.
