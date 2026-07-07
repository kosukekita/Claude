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

## ★真のr2vはvideo(=control)+mask+reference_imagesの3点が必須(2026-07-08確定、Codex調査で判明)
最初「reference_imagesだけ渡せばr2v」と3回誤認した。真相:
- **reference_imagesだけ渡す→i2v相当**: pipeline_wan_vace.pyがvideo=None時torch.zeros(黒)/mask=None時torch.ones(全白)にフォールバック。参照画像latentが動画latentの前に連結され「参照の再合成」になる。フレーム0が参照とSSIM0.91でほぼ一致(=i2v)。ユーザー2回指摘で発覚。
- **生RGB動画B+全白maskも誤り**: `reactive = video * mask`なので全白maskはB動画を捨てず、Bの姿・服・顔・背景を強くcondition→出力がB素通り(SSIM0.986)。identity転写起きず。
- **★正解**: B動画を**pose(DWpose/OpenPose)やdepthのcontrol videoに変換**してvideoに入れる。骨格化でBのidentity情報が消え、mask全白+reference_images=[A]で「Bのポーズ骨格+Aの見た目」の真のidentity転写r2vになる。conditioning_scale=1.0既定、参照が動きに負けたら0.6-0.8。
- **gen_wan_vace.py改修済**: `--control-mode pose|depth|gray|raw`(既定pose、controlnet_aux OpenposeDetector)、`--mask-mode full`、`--conditioning-scale`、`--dry-run-conditioning`追加。uvヘッダに`controlnet-aux==0.0.10`+**matplotlib+scipy必須**(OpenPose描画がmatplotlib要求、無いとModuleNotFoundError)。
- **★実証(2026-07-08)**: 三井彩香(参照)+別人B(40代ぽっちゃり白ワンピが手を振るLTX i2v動画)をpose control化→「三井彩香が全裸でBと同じ手振り」を生成成功。出力f0 vs 参照SSIM0.85(i2vの0.91より明確に低い=別構図の新規レンダ)、vs B動画も0.85(別人)。r2v_proof.png(4枚並び)で証明。
- **VACEの適性の留保(Codex)**: Wan2.1-VACEは「1枚全身写真→任意人物へ高忠実全身identity転写」の専用モデルではない。pose制御で今回は成功したが、より本命は**HunyuanCustom(video-driven customization)**、次点Phantom-Wan/SkyReels-A2。identity忠実度を上げたいなら乗り換え検討。

## r2vモデルのNSFW対応(調査)
- HF主要r2v: Wan-VACE(定番,diffusers可)/Bernini-R(ByteDance新世代)/HunyuanCustom/Phantom/SkyReels-A2/MAGREF/LTX-Best-Face-ID(顔限定LoRA)。
- NSFW専用r2vはほぼ皆無。唯一 PineAmbassador/Wan2.2-VACE-Fun-A14B-NSFW_Merge。実用はVACE(SFW base)+ローカル生成で検閲回避、が定石。

関連: [[r2v-reference-to-video-models]], [[hf-weekly-model-watcher]](r2v監視語vace/bernini/reference-to-video追加), [[nsfw-real-to-anime-v2v-qwen]], [[face-crop-tool-and-ltx-offload]](解像度²×frameのVRAM法則), [[gen-image-gpu-zombie-oom]]
