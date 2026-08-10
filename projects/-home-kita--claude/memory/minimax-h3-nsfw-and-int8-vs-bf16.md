---
name: minimax-h3-nsfw-and-int8-vs-bf16
description: MiniMax-H3ローカルのNSFW耐性は完全無検閲(明示的性行為+喘ぎ声を生成)、int8_convrotとbf16の画質差はほぼ無く速度もbf16の方が速い実測(2026-08-04)
metadata: 
  node_type: memory
  type: project
  originSessionId: 30e2b450-b35d-4c1d-88b8-ccd7c0b9b44c
  modified: 2026-08-10T06:43:50.570Z
---

MiniMax-H3（[[minimax-h3-local-comfyui-setup]]）の A/B と NSFW 耐性を同時実測（2026-08-04・Haruka ペルソナ・POV騎乗位・768×1344/124f/20steps・同一seed 58222004・同一キーフレーム）。

**★NSFW 耐性＝完全に通る（検閲ゼロ）**:
- 全裸・明示的な性行為（挿入が見える結合部）・POV を**拒否も後退もせず**そのまま生成。ぼかし・服の付与・構図の逃げが一切なかった
- **音声も無検閲**: 喘ぎ声・吐息を動作と同期して生成（bf16 max -17.3dB / int8 -27.9dB＝bf16 の方が声がはっきり出た）。**音声付き NSFW をローカル生成できる初の手段**（既存の wan/LTX/Hunyuan は無音）
- 使った TE は Heretic 無検閲版だが、**DiT 側にも検閲挙動は観測されなかった**

**★int8_convrot vs bf16 = 画質差はほぼ無く、bf16 の方が速い（結論: bf16 を既定にする）**:
- 画質: 同一 seed で構図・動き・顔の同一性はほぼ同一。等倍比較で bf16 がわずかに輪郭とハイライトが締まる程度で、**32GB の容量差に見合う差ではない**
- 速度: **bf16 20分 / int8 27分**（bf16 の方が7分速い）。int8_convrot は Ampere でネイティブカーネル（convrot_w4a4）が使えず逆量子化のオーバーヘッドが乗るため。**「量子化＝速い」は A6000 では成立しない**
- 96GB リグかつ RAM 251GB のこの機では **bf16 一択**。int8 の存在意義は VRAM の小さいカード向け

**実測パラメータ**: 768×1344・124フレーム（5.17秒）@24fps・20 steps・res_multistep/simple・CFGなし（蒸留済み）。GPU0 単体、生成中の VRAM 約39〜48GB（残りは RAM オフロード）。

**キーフレーム作成の知見**（Qwen-Image-Edit-2511 + `ScottzillaSystems/qwen-image-edit-plus-nsfw-lora`・768×1344・40steps）:
- POV 騎乗位は**プロンプトで「男は下端に腹部だけ」と明示しないと男の胴が画面を占有する**（v1 失敗）
- 表情は放置すると苦悶・絶叫顔になる → `blissful, half-closed dreamy eyes, soft smile` を positive、`screaming, grimace, wide open mouth, distressed` を negative に必須
- 「fully seated astride his pelvis」と書くと結合位置が正しく骨盤上に来る（v1 は腹の上に浮いた）

**モザイク後処理**: `/data/kita/mmh3-setup/apply_mosaic.sh`（x300,y770,200×310 の固定ボックスで縦バウンス全域をカバー・22分割ピクセレート）。動画は縦運動するので**フレーム単位検出でなく運動範囲を包む固定ボックス**が確実。

関連: [[nsfw-auto-pipeline-explicit-video]]（従来の explicit 動画は「男を描かない/臍より上」で破綻回避していたが、H3 は結合部を描いても破綻しない）、[[optimal-gen-models-table-and-new-model-eval]]

**追記 2026-08-10（Turbo LoRA 統合）**: `gen_minimax_h3.py --turbo` で少ステップ高速化を統合
（既定オフ＝従来20step・turbo時steps既定8・t2v/i2v/r2v全モード可・`--turbo-lora`で差替可）。
実測124f温間: 20step 12.5分 → 8step 5.5分(2.3×) / 4step 3.0分(4.1×)。**NSFW無検閲は維持**
（無検閲性はTE側・LoRAはDiTのみ）。プロンプト反映は盲検で20stepと同等、微細部（手指）のみ
4stepでやや劣る→6〜8step推奨。★尺の上限は**362f=15.08秒**（124は既定値であって上限ではない。
訓練域〜362f、実測完走80.5分）。正本は video-media-studio SKILL.md。
