---
name: gen-image-controlnet-lora-character
description: gen_image.pyにControlNet追加(SDXL専用)。キャラLoRA×ControlNet×compelで四肢破綻を解消し同一人物をポーズ拘束で量産する手順
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8fa33f41-3f7a-4f60-88ef-8e22b991175d
---

video-media-studio の `scripts/gen_image.py` に **ControlNet(SDXL専用)** を追加した(2026-06-30)。連作NSFW漫画で同一キャラを多数コマ一貫させる用途。[[manga-bw-nsfw-models]] [[sdxl-pony-long-prompt-compel]] の続き。

## なぜ要るか(実証済みの根本原因)
キャラLoRA(Pony V6XL ベース, dim32, 25枚, 立ち/正面中心)は、**学習データに無い複雑ポーズ(座って膝抱え等)で四肢が増殖**する(脚3本)。主因は「未学習ポーズにLoRAを強く当てて人体構造が歪む」+「SDXL系の素の手足破綻」の合わせ技(Codexと所見一致)。破綻画像をOpenPose検出器に通すと骨格自体が脚3〜4本に出て裏付けられた。→ **推論側でControlNetで骨格拘束すれば再学習なしで破綻が直る**ことを実機実証(座り3本脚→正常2本)。

## 使い方
```
--control openpose=img.png        # 実写/イラストから骨格抽出して拘束(検出器内蔵)
--control depth=ref.jpg           # 深度マップ(前後関係=絡み/拘束/複数人に有効)
--control canny=line.png          # エッジ
--control openpose=a.png --control depth=b.png   # 複数スタック(漫画の絡みは併用が定番)
--control-weight 0.9              # 各controlのconditioning scale(既定0.9。座りは1.0が効いた)
--no-control-preprocess           # 画像が既製ヒント(手描き骨格/深度)なら検出器skip
```
- ControlNetは **SDXL backends(pony/noobai/manga-vision/sdxl)専用**。非SDXLは警告して無視。
- **xinsir の SDXL ControlNet がローカルキャッシュ済**: `xinsir/controlnet-openpose-sdxl-1.0` / `-depth-` / `-canny-`。検出器重みは `lllyasviel/Annotators`(キャッシュ済)。DL不要。
- **ControlNet × LoRA fuse × compel長プロンプトが同一パイプラインで共存**することを確認済(StableDiffusionXLControlNetPipeline)。

## 推奨設定(複雑ポーズ・量産)
- **LoRA strength 0.6**(0.8だと正面立ちの学習偏りで複雑ポーズが歪む。下げるとベースの人体一般化が戻りControlNet骨格に素直に従う)。顔が薄れたら後段で顔inpaint(LoRA強め)してキャラ性を戻す=「構図はControlNet/絵柄はLoRA」の役割分離。
- ControlNet weight 0.9〜1.0、steps 30、解像度は座り等は832x1216でもCN拘束あれば破綻しない。
- ネガに `extra legs, extra limbs, three legs, fused legs, malformed limbs` 追加。

## 40コマ量産ワークフロー(Codex推奨=採用)
OpenPose/Depthで構図固定 → LoRA弱め(0.6) → 二段アップスケール(denoise0.3) → 顔/手足は局所inpaint。複数人は人物ごとに骨格を先に用意。ポーズ素材は**実写/イラストを探して骨格抽出**が最自然(ユーザー選択)。

## 実装の注意(Codexレビュー反映済)
- PEP723依存に `controlnet-aux, Pillow, matplotlib, opencv-python-headless` 追加(matplotlibはOpenPose描画に必須・忘れるとModuleNotFoundError)。
- `--control` の不正(type不明/ファイル無し)は **main側で事前validate→exit 2**(run_local内で投げると汎用exceptがgrok誤フォールバックに流す。parse_sizeと同じ層に置く)。
- weight正規化は `_expand_weights()` でLoRA/Control共通化。
