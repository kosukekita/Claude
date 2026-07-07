---
name: r2v-reference-to-video-models
description: r2v(参照人物の特徴→新規動画)のHF主要モデル一覧とNSFW対応状況(2026-07-07調査)。i2v(先頭フレーム)とは別物
metadata: 
  node_type: memory
  type: reference
  originSessionId: 962c799f-34d9-461f-8ff7-8e2af5af1210
---

r2v = 参照画像から人物/被写体の特徴を抽出し、その特徴で**新しい**動画を生成（i2v=先頭フレームを動かす、とは別概念。ユーザーは両者を明確に区別する）。

**HFの主要r2vファミリー（2026-07-07実測、♥=likes）**:
- **Wan-AI/Wan2.1-VACE-14B / -1.3B**（♥501/♥136、diffusers版あり=WanVACEPipelineでローカル可）— R2V/V2V/編集オールインワンの定番
- **ByteDance/Bernini-R**（♥280、2026-06登場、image-text-to-video）— 新世代参照対応動画。Comfy-Org版・GGUF(⬇43k)・LightX2V 4step LoRA(rzgar)までエコシステム急成長中。mlx版タグに reference-to-video
- **tencent/HunyuanCustom**（♥192）— 参照人物の同一性保持動画
- **Skywork/SkyReels-V3-A2V-19B**（♥91、A2V=参照要素合成）/ SkyReels-A2（♥140）
- **Phantom-Wan 14B**（ByteDance Phantom、QuantStack GGUF ♥28）— subject-consistent S2V
- **MAGREF**（♥14、複数被写体参照、Wan2.1 GGUF移植あり）
- **Alissonerdx/LTX-Best-Face-ID**（♥28、2026-07-05新着）— LTX-2用の顔ID r2v LoRA（ArcFace projector+LoRAの2ファイル構成）。顔の同一性のみ
- mickmumpitz/VACE_Skyreels_V3_R2V_Merge-GGUF（♥10）

**NSFW対応r2v**: 専用モデルはほぼ皆無（NSFWタグ×i2v/t2vでr2v語を含むもの0件）。唯一の直球ヒット= **PineAmbassador/Wan2.2-VACE-Fun-A14B-NSFW_Merge**（♥8 ⬇755、Wan2.2-VACE-FunにNSFWマージ）。実用ルートはこれか「VACE/Phantom（Wan系ベース）+Wan NSFW LoRAをComfyUIでスタック」がコミュニティ定石。ローカル実行ならAPI検閲は無い。

関連: [[hf-weekly-model-watcher]]（監視語にvace/bernini等は未追加・ユーザー判断待ち）, [[openrouter-video-models-reference-support]]（クラウドのNSFW×参照はwan-2.7のみ）, [[nsfw-models-chroma-noobai-wan-lora]]（gen_wan_lora.pyはWan2.2 i2v用でVACE未対応）
