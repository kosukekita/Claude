---
type: reference
title: カメラワーク技法 → 再現プロンプト集 (t2v/i2v)
description: 動画生成でカメラの動きを指定したいときの、46技法(7カテゴリ)の再現プロンプト全文。出典 aicameramovements.com の原文
tags: [camera, movement, prompt, t2v, i2v, dolly, pan, tilt, zoom, orbit, crane, drone, tracking, whip-pan]
---

# カメラワーク技法 → 再現プロンプト集

動画生成(t2v / i2v)のプロンプトに足して、狙ったカメラの動きを出すための語彙集。**下の各プロンプトは出典サイト aicameramovements.com の原文(コピー用テキスト)を機械抽出したもの**。全46技法・7カテゴリ。

## 使い方(適用の指針)
- **1クリップ＝1つの動き**。相反する動き(dolly in と zoom out 等)は混ぜない。例外は狙ってやる **dolly zoom(vertigo/めまい)** だけ。複数の動きを繋ぐなら分割して `chain_video.py`。
- **i2v は1枚目から無理のない動きだけ**。orbit は被写体の周囲に空間が要る／pass-through は前景物が要る／crane up は上の空間が要る。1枚目に無い要素へは動けない。
- **技法名(jargon)だけより、下の "Camera: … Movement: … Speed: … Framing: … End: …" の平叙文フル記述の方が Wan/LTX で確実**(実機知見)。原文がこの構造なのはそのため。強すぎる動きは i2v で破綻するので控えめから。
- **★NSFWパイプライン(wan-2.7-spicy i2v・臍より上/POV)では控えめな動きを選ぶ**: slow zoom in / handheld / pedestal 系。大きな orbit・crane・crash zoom は「臍より上」の枠や結合部を映さない構図を壊すので避ける。
- 構図も固定したいなら先頭にショットサイズ(close-up / medium / wide)とアングル(low/high/eye level/bird's-eye)を足す。

## 関連
- **時間停止＋周回(凍った爆発の周りをカメラが回る)** は専用スキル **bullet-time-video**(このパレットの orbit の特殊ジャンル)。
- 動画生成の入口・バックエンド選択は `SKILL.md`「動画生成フロー」。多クリップ連結は `chain_video.py`。

## PAN / TILT（首振り：カメラ位置は固定）
- **Static shot**
  `Camera: locked-off static shot. Movement: hold one fixed camera position for the full clip. Speed: still and steady. Framing: keep the same angle, height, lens distance and composition. End: finish with the same framing and camera position.`
- **Pan right**
  `Camera: pan right. Movement: rotate the camera horizontally from left to right from one fixed point. Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the right side of the frame. End: settle on a clear final composition.`
- **Pan left**
  `Camera: pan left. Movement: rotate the camera horizontally from right to left from one fixed point. Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the left side of the frame. End: settle on a clear final composition.`
- **Whip pan right**
  `Camera: whip pan right. Movement: rotate rapidly from the starting direction toward a new target on the right. Speed: fast snap with brief motion blur during the rotation. Framing: begin on one readable composition and land on a second readable target. End: settle into a sharp final frame.`
- **Whip pan left**
  `Camera: whip pan left. Movement: rotate rapidly from the starting direction toward a new target on the left. Speed: fast snap with brief motion blur during the rotation. Framing: begin on one readable composition and land on a second readable target. End: settle into a sharp final frame.`
- **Tilt up**
  `Camera: tilt up. Movement: rotate the camera upward from one fixed point. Speed: smooth constant tilt. Framing: keep the vertical subject or architecture centered as the frame travels upward. End: land on the upper target.`
- **Tilt down**
  `Camera: tilt down. Movement: rotate the camera downward from one fixed point. Speed: smooth constant tilt. Framing: keep the vertical subject or architecture centered as the frame travels downward. End: land on the lower target.`

## ZOOM / LENS（ズーム）
- **Slow zoom in**
  `Camera: slow zoom in. Movement: slowly increase lens focal length toward a tighter frame. Speed: gradual and even. Framing: keep the main visual target readable as it becomes larger in frame. End: finish on a stable tighter composition.`
- **Slow zoom out**
  `Camera: slow zoom out. Movement: slowly decrease lens focal length toward a wider frame. Speed: gradual and even. Framing: keep the main visual target readable as more surrounding space appears. End: finish on a stable wider composition.`
- **Fast zoom in**
  `Camera: fast zoom in. Movement: quickly increase lens focal length toward the main visual target. Speed: quick decisive zoom. Framing: keep the target centered or clearly readable during the scale change. End: finish on a stable tighter composition.`
- **Fast zoom out**
  `Camera: fast zoom out. Movement: quickly decrease lens focal length away from the main visual target. Speed: quick decisive zoom. Framing: keep the target readable as the surrounding space appears. End: finish on a stable wider composition.`
- **Crash zoom in**
  `Camera: crash zoom in. Movement: snap the lens rapidly toward the main visual target. Speed: very fast and punchy. Framing: keep the target readable through the sudden scale change. End: land on a bold tighter composition.`
- **Crash zoom out**
  `Camera: crash zoom out. Movement: snap the lens rapidly away from the main visual target. Speed: very fast and punchy. Framing: keep the target readable as the surrounding space appears. End: land on a bold wider composition.`

## DOLLY / TRACK（カメラ本体が前後・追従）
- **Dolly in**
  `Camera: dolly in. Movement: move the camera physically forward in a straight line toward the main subject. Speed: smooth controlled push. Framing: keep camera height, lens direction and subject position consistent while distance closes. End: finish in a tighter composition.`
- **Dolly out**
  `Camera: dolly out. Movement: move the camera physically backward in a straight line away from the main subject. Speed: smooth controlled retreat. Framing: keep lens direction and camera height consistent while more environment enters frame. End: finish in a wider composition.`
- **Tracking shot**
  `Camera: tracking shot. Movement: move through the scene with the main subject. Speed: match the subject's pace. Framing: keep the subject consistently readable while the environment moves around them. End: maintain a clear moving composition.`
- **Follow shot / over-the-shoulder**
  `Camera: follow shot from behind. Movement: move behind the subject along their route at shoulder height. Speed: match the subject's pace. Framing: keep the back, shoulder or head as the foreground guide while the route ahead stays readable. End: continue following with the subject leading the frame.`
- **Reverse tracking / walk-and-talk**
  `Camera: reverse tracking shot. Movement: move backward in front of the walking subject. Speed: match the subject's forward pace. Framing: keep front-facing face and body framing stable as the background moves behind them. End: hold a clear front-facing moving composition.`
- **Side tracking**
  `Camera: side tracking shot. Movement: move parallel beside the subject along their direction of travel. Speed: match the subject's motion. Framing: keep the subject in side profile or three-quarter profile at a stable distance. End: continue the parallel movement with clear horizontal motion.`
- **Low tracking**
  `Camera: low tracking shot. Movement: move at ground or below-waist height alongside the subject's movement path. Speed: match the subject, footsteps or wheels. Framing: keep the low detail readable while the ground plane moves through frame. End: finish with the low perspective clearly maintained.`
- **Vehicle tracking**
  `Camera: vehicle tracking shot. Movement: move with the vehicle along its route. Speed: match the vehicle's pace. Framing: keep the vehicle stable in frame while the road or environment moves past. End: maintain a clear moving vehicle composition.`
- **Chase shot**
  `Camera: chase shot. Movement: follow a moving subject quickly along the action route. Speed: fast, reactive and physically close. Framing: keep the subject visible while allowing energetic reframing. End: stay connected to the subject in motion.`

## PHYSICAL MOVES（平行移動・弧・周回）
- **Truck right**
  `Camera: truck right. Movement: move the camera physically to the right on a straight horizontal path. Speed: smooth constant lateral travel. Framing: keep the lens facing the same direction while the scene slides across frame. End: finish on a clean lateral composition.`
- **Truck left**
  `Camera: truck left. Movement: move the camera physically to the left on a straight horizontal path. Speed: smooth constant lateral travel. Framing: keep the lens facing the same direction while the scene slides across frame. End: finish on a clean lateral composition.`
- **Pedestal up**
  `Camera: pedestal up. Movement: move the entire camera vertically upward in a straight line. Speed: smooth constant lift. Framing: keep the lens level and pointed in the same direction during the vertical move. End: finish with the higher framing clearly readable.`
- **Pedestal down**
  `Camera: pedestal down. Movement: move the entire camera vertically downward in a straight line. Speed: smooth constant descent. Framing: keep the lens level and pointed in the same direction during the vertical move. End: finish with the lower framing clearly readable.`
- **Slider right**
  `Camera: slider right. Movement: slide the camera a small distance to the right. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new right-side angle visible.`
- **Slider left**
  `Camera: slider left. Movement: slide the camera a small distance to the left. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new left-side angle visible.`
- **Push past / pass-by shot**
  `Camera: push past. Movement: move forward past a visible foreground object, edge or opening. Speed: smooth forward glide. Framing: let the foreground pass close to the lens while the space beyond becomes clearer. End: arrive inside or beyond the foreground layer.`
- **Arc right**
  `Camera: arc right. Movement: move on a shallow curved path around the main subject toward the right side. Speed: smooth measured curve. Framing: keep distance, height and subject readability consistent while the angle changes. End: finish from a new right-side angle.`
- **Arc left**
  `Camera: arc left. Movement: move on a shallow curved path around the main subject toward the left side. Speed: smooth measured curve. Framing: keep distance, height and subject readability consistent while the angle changes. End: finish from a new left-side angle.`
- **Orbit clockwise**
  `Camera: clockwise orbit. Movement: circle clockwise around the main subject at a consistent radius. Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates around them. End: complete the intended arc or full circle with stable framing.`
- **Orbit counterclockwise**
  `Camera: counterclockwise orbit. Movement: circle counterclockwise around the main subject at a consistent radius. Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates around them. End: complete the intended arc or full circle with stable framing.`

## HUMAN CAMERA（手持ち・体感）
- **Handheld shot**
  `Camera: handheld shot. Movement: hold the camera at human operator height with natural body movement. Speed: responsive and organic. Framing: keep the subject readable while the frame has subtle sway and micro-adjustments. End: finish with a natural handheld composition.`
- **Body-mounted camera / snorricam**
  `Camera: body-mounted Snorricam. Movement: keep the camera fixed relative to the subject's torso or face while the subject moves. Speed: match the subject's body motion. Framing: keep the subject close, centered and facing the camera as the background moves around them. End: finish with the subject still locked in frame.`

## DRONE / CRANE（空撮・大移動）
- **Crane up**
  `Camera: crane up. Movement: travel smoothly upward through open space. Speed: slow controlled vertical lift. Framing: keep the subject or location readable as the camera rises. End: finish with the higher scale clearly visible.`
- **Crane down**
  `Camera: crane down. Movement: travel smoothly downward through open space. Speed: slow controlled vertical descent. Framing: keep the subject or location readable as the camera descends. End: finish with the lower subject or destination clearly visible.`
- **Drone push in**
  `Camera: drone push in. Movement: fly smoothly forward through open space toward the subject or destination. Speed: controlled aerial glide. Framing: keep the route and destination readable as the camera approaches. End: arrive at a closer aerial composition.`
- **Drone pull back**
  `Camera: drone pull back. Movement: fly smoothly backward away from the subject or destination. Speed: controlled aerial retreat. Framing: keep the subject readable as more landscape appears. End: finish on a wider aerial composition.`
- **Helicopter shot**
  `Camera: helicopter-style aerial shot. Movement: move from high altitude along a broad gradual flight path. Speed: steady controlled aerial motion. Framing: keep the landscape or distant moving subject readable at wide scale. End: finish on a stable high-altitude composition.`

## SPECIALS（特殊）
- **First-person view**
  `Camera: first-person view. Movement: move forward at human eye height from the character's perspective. Speed: natural walking or reaching pace. Framing: use visible hands, arms or body edges as the viewer's physical reference. End: arrive at the next point of action from the same point of view.`
- **Tilt-shift**
  `Camera: tilt-shift miniature view. Movement: hold or glide from a high angled view over the scene. Speed: small precise movement. Framing: keep a narrow band of sharp focus across the key subject area with soft blur above and below. End: finish with the miniature-scale view intact.`
- **Infinite zoom**
  `Camera: infinite zoom. Movement: zoom continuously inward toward the exact center target. Speed: smooth accelerating zoom. Framing: keep the circular target centered as it expands. End: finish when the next visual world fills the frame.`
- **Earth zoom out**
  `Camera: earth zoom out. Movement: pull upward from the starting point through street, city, landscape and planet scale. Speed: rapid expanding zoom out. Framing: keep the original location centered as scale grows. End: finish on a planet-scale view with the starting point still implied at center.`
- **Time-lapse**
  `Camera: locked-camera time-lapse. Movement: hold one fixed camera position while time moves rapidly forward. Speed: fast time compression with a stable camera. Framing: keep the same composition and horizon as motion passes through the frame. End: finish from the same camera angle with visible passage of time.`
- **Pass-through objects**
  `Camera: pass-through movement. Movement: move forward toward a visible object, surface or barrier and continue into the space beyond. Speed: smooth centered glide. Framing: keep the opening or surface centered as the transition point. End: arrive inside the revealed space beyond.`

---
出典: **aicameramovements.com**(46 movements / 7 categories)。上記プロンプトは同サイトのコピー用テキスト(data-copy)を機械抽出した原文。使い方の指針は本スキル用の追記。
