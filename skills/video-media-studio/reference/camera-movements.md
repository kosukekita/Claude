---
type: reference
title: カメラワーク技法 → 再現プロンプト集 (t2v/i2v)
description: 動画生成でカメラの動きを指定したいときの、46技法(7カテゴリ)の名前付き再現プロンプト。Wan/LTX/wan-2.7-spicy/HunyuanCustom 向け
tags: [camera, movement, prompt, t2v, i2v, dolly, pan, tilt, zoom, orbit, crane, drone, tracking, whip-pan]
---

# カメラワーク技法 → 再現プロンプト集

動画生成（t2v / i2v）のプロンプトに足して、狙ったカメラの動きを出すための語彙集。分類は aicameramovements.com（46技法・7カテゴリ）を土台に、各フレーズは自作（逐語転載ではない）。

## 使い方（重要な原則）
- **技法名(jargon)より「`the camera` + 動作動詞」の平叙文が効く**（Wan/LTX は実機で declarative の方が確実）。名前は補助。→ 下表は「そのまま貼れる英語フレーズ」を主に載せる。
- **1クリップ＝1つの動き**。相反する動き（dolly in と zoom out 等）を混ぜない。例外は狙ってやる **dolly zoom（vertigo/めまい）** だけ。複数の動きを繋ぐなら分割して `chain_video.py`。
- **i2v は1枚目から無理のない動きだけ**。orbit は被写体の周囲に空間が要る／pass-through は前景物が要る／crane up は上の空間が要る。1枚目に無い要素へは動けない。
- **速度・強さの修飾語**を付けて調整: `slow / fast / sudden / gradual / smooth / steady / subtle / sweeping / continuous one-take`。強すぎる動きは破綻するので i2v は控えめから。
- **構図も固定したいなら**先頭にショットサイズ（`extreme close-up / close-up / medium shot / wide shot / extreme wide`）とアングル（`low angle / high angle / eye level / bird's-eye / worm's-eye`）を足す。
- **★NSFWパイプライン（wan-2.7-spicy i2v・臍より上/POV）では控えめな動きを選ぶ**: `slow push in / subtle handheld sway / slight pedestal up / gentle vertical bounce`。大きな orbit・crane・crash zoom は「臍より上」の枠や結合部を映さない構図を壊すので避ける。

## PAN / TILT（首振り：カメラ位置は固定）
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| Static | `a locked-off static shot, the camera holds one fixed position with no movement` | 完全固定 |
| Pan Right | `the camera pans right, rotating horizontally from left to right` | |
| Pan Left | `the camera pans left, rotating horizontally from right to left` | |
| Whip Pan Right | `a fast whip pan to the right, rotating rapidly with heavy motion blur` | 転換に |
| Whip Pan Left | `a fast whip pan to the left, rotating rapidly with heavy motion blur` | |
| Tilt Up | `the camera tilts up, rotating upward from a fixed point to reveal what is above` | |
| Tilt Down | `the camera tilts down, rotating downward from a fixed point` | |

## ZOOM / LENS（レンズ）
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| Slow Zoom In | `a slow zoom in, the lens gradually magnifies toward the subject while the camera stays in place` | |
| Slow Zoom Out | `a slow zoom out, the lens gradually widens away from the subject` | |
| Fast Zoom In | `a fast zoom in, the lens quickly magnifies toward the subject` | |
| Fast Zoom Out | `a fast zoom out, the lens quickly widens out` | |
| Crash Zoom In | `a sudden crash zoom punching in fast onto the subject's face` | 激ズーム |
| Crash Zoom Out | `a sudden crash zoom snapping rapidly away from the subject` | |

## DOLLY / TRACK（カメラ本体が前後・追従）
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| Dolly In | `a dolly in, the whole camera moves physically forward in a straight line toward the subject` | zoomと別物(遠近が変わる) |
| Dolly Out | `a dolly out, the whole camera moves physically backward away from the subject` | |
| Tracking | `a tracking shot, the camera moves through the scene keeping pace with the moving subject` | |
| Follow | `a follow shot from behind, the camera moves behind the subject along their path` | |
| Reverse Tracking | `a reverse tracking shot, the camera moves backward in front of the advancing subject, facing them` | lead shot |
| Side Tracking | `a side tracking shot, the camera moves parallel alongside the subject` | |
| Low Tracking | `a low-angle tracking shot skimming just above the ground, following the subject` | 地面すれすれ |
| Vehicle Tracking | `a vehicle tracking shot, the camera moves alongside the moving vehicle at its speed` | |
| Chase | `a dynamic chase shot, the camera follows the fast-moving subject quickly along the action` | |

## PHYSICAL MOVES（平行移動・上下・弧・周回）
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| Truck Right | `a truck right, the whole camera slides physically to the right` | crab |
| Truck Left | `a truck left, the whole camera slides physically to the left` | |
| Pedestal Up | `a pedestal up, the entire camera rises straight vertically upward keeping its angle` | boom up |
| Pedestal Down | `a pedestal down, the entire camera lowers straight vertically downward` | |
| Slider Right | `a slider move, the camera glides a short smooth distance to the right` | 小移動 |
| Slider Left | `a slider move, the camera glides a short smooth distance to the left` | |
| Push Past | `the camera pushes forward past a foreground object that sweeps close by the lens` | 前景を舐める |
| Arc Right | `an arc shot, the camera moves along a shallow curved path to the right around the subject` | 半周 |
| Arc Left | `an arc shot, the camera moves along a shallow curved path to the left around the subject` | |
| Orbit CW | `the camera slowly orbits clockwise all the way around the subject, keeping it centered` | 全周・要空間 |
| Orbit CCW | `the camera slowly orbits counterclockwise around the subject, keeping it centered` | bullet-time系は専用skill |

## DRONE / CRANE（大移動・空撮）
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| Crane Up | `a crane up, the camera travels smoothly upward through open space, rising high above the scene` | jib |
| Crane Down | `a crane down, the camera travels smoothly downward toward the subject` | |
| Drone Push In | `a drone push in, the camera flies smoothly forward through open space toward the subject` | |
| Drone Pull Back | `the camera cranes up and pulls back into a sweeping aerial drone shot, revealing the entire scene` | reveal・引きで全景 |
| Helicopter | `a helicopter-style aerial shot, the camera sweeps at high altitude over the landscape` | |

## HUMAN CAMERA（手持ち・体感）
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| Handheld | `a handheld shot at human operator height, with natural subtle shake and sway` | shaky cam。滑らかにしたいなら `steadicam / gimbal smooth` |
| Snorricam | `a body-mounted Snorricam shot rigidly fixed to the subject, so they stay still in frame while the background moves` | 体固定 |

## SPECIALS
| 技法 | 貼れる英語フレーズ | メモ |
|---|---|---|
| First-Person POV | `a first-person POV shot, the camera moves forward at eye height as if seen through the person's own eyes` | 一人称 |
| Tilt-Shift | `a tilt-shift miniature effect, a high angled view with a narrow band of focus making the scene look like a tiny model` | |
| Infinite Zoom | `an infinite zoom, the camera pushes continuously inward toward the exact center in a seamless endless zoom` | |
| Earth Zoom Out | `an earth zoom out, the camera pulls upward and back, rising higher and higher toward a satellite view of the planet` | |
| Time-Lapse | `a locked-camera time-lapse, one fixed position while time races by (clouds, light, crowds speeding)` | hyperlapse=移動版 |
| Pass-Through | `the camera flies forward and passes through a solid foreground object, emerging on the other side in one continuous move` | 窓/壁/葉 |

## 併用の定番コンボ
- **Dolly zoom / Vertigo（めまい）**: `a dolly zoom, the camera dollies in while zooming out (the background warps and stretches)` — 相反する動きを"狙って"混ぜる唯一のケース。
- **Reveal**: arc/orbit または crane up + pull back で、隠れていた被写体・全景を最後に見せる。

## 関連
- **時間停止＋周回（凍った爆発の周りをカメラが回る）**は専用スキル **bullet-time-video** を使う（このパレットの orbit の特殊ジャンル）。
- 動画生成の入口・バックエンド選択は本スキル `SKILL.md`「動画生成フロー」。多クリップ連結は `chain_video.py`。

出典（分類の土台）: aicameramovements.com（46 movements / 7 categories）。プロンプト文言は本スキル用に自作。
