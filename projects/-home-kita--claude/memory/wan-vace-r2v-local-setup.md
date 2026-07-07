---
name: wan-vace-r2v-local-setup
description: Wan2.1-VACE-14B r2v(参照人物→新規動画)のローカル導入・gen_wan_vace.py・実証結果とハマりどころ(2026-07-07)
metadata: 
  node_type: memory
  type: project
  originSessionId: 962c799f-34d9-461f-8ff7-8e2af5af1210
---

r2v(reference-to-video=参照画像から人物特徴を抽出し新規動画生成、i2vとは別)をローカルで実現。NSFW可(検閲なし)。

## 導入
- モデル: `Wan-AI/Wan2.1-VACE-14B-diffusers`(~70GB, gated無し)。DL時 hf_transfer で複数プロセス競合すると固まる→`HF_HUB_ENABLE_HF_TRANSFER=0`の単一プロセスで確実。transformer 13shard完走を要確認。
- スクリプト新規: `~/.claude/skills/video-media-studio/scripts/gen_wan_vace.py`。`WanVACEPipeline`+`AutoencoderKLWan`(VAEはfp32固定)+`UniPCMultistepScheduler(flow_shift=3.0で480p/5.0で720p)`。`reference_images=[img,...]`が特徴源。--offload model で48GB A6000 1枚に収まる。--gpu Nはtorch初期化前にCUDA_VISIBLE_DEVICESへ反映(他gen同様cuda:0ハードコード衝突回避)。frame=4k+1(81=5s), dims/16。
- 既定: 480x832, 81f, steps30, cfg5.0, seed42。VACE 14Bロード数分+推論で全体20-30分。

## ★実証(2026-07-07)とハマりどころ
- **r2v成立を確認**: ペルソナ「三井彩香」のヌードシートから全身正面+顔アップを参照に投入→動画は同一人物のまま「手を振る」新規動作を生成(i2vの先頭フレーム再生でなく、参照特徴から新規モーション)。フレーム0と40で顔・髪一致、手のポーズは新規。
- **★参照画像の服装特徴を拾う**: 顔参照にSFW由来(白ブラウス着衣)を混ぜたら、プロンプト「全裸」を無視して動画も白ブラウスになった。→**全裸r2vは着衣の顔参照を混ぜない。全身ヌード参照のみ**にし、negativeに「服,ブラウス,布」を明示。参照画像はプロンプトより強い。
- VACEはreference_imagesの見た目(服/裸/髪型/体型)を強く再現するので、出したい状態の参照を渡すのが鉄則。

## r2vモデルのNSFW対応(調査)
- HF主要r2v: Wan-VACE(定番,diffusers可)/Bernini-R(ByteDance新世代)/HunyuanCustom/Phantom/SkyReels-A2/MAGREF/LTX-Best-Face-ID(顔限定LoRA)。
- NSFW専用r2vはほぼ皆無。唯一 PineAmbassador/Wan2.2-VACE-Fun-A14B-NSFW_Merge。実用はVACE(SFW base)+ローカル生成で検閲回避、が定石。

関連: [[r2v-reference-to-video-models]], [[hf-weekly-model-watcher]](r2v監視語vace/bernini/reference-to-video追加), [[nsfw-real-to-anime-v2v-qwen]], [[face-crop-tool-and-ltx-offload]](解像度²×frameのVRAM法則), [[gen-image-gpu-zombie-oom]]
