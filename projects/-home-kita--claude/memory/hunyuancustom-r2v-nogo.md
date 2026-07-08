---
name: hunyuancustom-r2v-nogo
description: HunyuanCustom(顔忠実r2v)への乗り換えは調査の結果no-go(2026-07-08、9agent実機検証)。理由と代替、goに要る判断ゲート
metadata: 
  node_type: memory
  type: project
  originSessionId: 200959a5-a45c-4159-a506-8fc428432c92
---

三井彩香ペルソナのNSFW r2vで「顔忠実度を上げたい」→ HunyuanCustom(tencent, arXiv 2505.04512, video-driven customization)導入を検討。Workflow 9agentで4軸(diffusers対応/VRAM・ディスク/NSFW検閲/顔忠実度主張)を並列調査+敵対的検証した結論=**no-go-stay-vace**(全面乗り換え見送り、既存 Wan2.1-VACE-14B 継続)。

## no-goの確定事実(実機確認)
1. **diffusers非対応**: diffusers 0.37に HunyuanCustom pipelineは無い(grep 0、t2v/i2v/framepack/skyreelsの4本のみ)。重みは`mp_rank_00_model_states.pt`のMegatron/ZeRO形式でfrom_pretrained不可。公式は`diffusers==0.33/transformers==4.41/torch==2.4/py3.10`ピン→既存envに相乗り不可。gen_wan_vace.py同型の単一diffusers.pyにならず、公式hymm_sp cloneをsubprocessで叩く薄いラッパー確定。--offload modelも公式--cpu-offloadへ手動マッピング要。
2. **顔優位が未証明**: 論文のFace-Sim 0.204→0.627(約3倍)は比較対象が**VACE-1.3B**。ユーザー実運用の75点は**VACE-14B**で、14B相手の顔優位の一次実証は無い(アーキ説明の外挿)。
3. **NSFW未実証**: 焼き込みフィルタは無い(gated=False, safety_checker無)が「拒否されない」だけ。base HunyuanはSFW寄り、Custom専用NSFW LoRAはHFほぼ皆無、base用NSFW LoRAはhyperscale finetuneで効かない公算大。主目的がNSFW高忠実なのでここが致命的。
4. **モーション制御喪失**: HunyuanCustomはpose/depth control videoの入力口が無い。gen_wan_vaceの--control-mode pose/depth+全白maskの厳密モーション転写が使えない。
5. **ディスク薄氷/実速度**: 残63GB(93%使用)。fp8最小≈46GB(fp8 tr24.5+LLaVA16.8+CLIP1.7+VAE3)はDL前に80GB確保必須。速度はA100 80GBでもcpu_offload強制1本1時間超(公式Issue#11)、A6000はfp8ネイティブ演算無く速度稼げない。

## 代替(低リスク順、ユーザー判断待ち)
1. **VACE内で顔底上げ(最優先・乗り換えゼロ)**: 顔クロップ高解像化+`--ref`複数枚、`--openpose-include-face`、480→720p、Wan NSFWキャラLoRAで顔焼き。
2. **Stand-Inアダプタ(0.63GB)をWanに重ねる**: 顔特化ID。ただしベースWan2.1-**T2V-14Bが未キャッシュ(~70GB追加DL、今のディスクに入らない)**、単独モーション制御不可でVACE統合要。三重スタックの干渉未実証。
3. **HunyuanCustomは判断ゲートでだけ試す**: 全面移行でなく、フェーズ0のSFW小尺プローブ1本でVACE-14BをFace-Sim(ArcFace buffalo_l)で実際に上回るか実測→上回り&NSFWも出せて初めて本実装。

## 判断ゲート(goに要る、フェーズ0)
①DL前80GB確保(Wan2.2 I2V 118GB or TI2V-5B 32GB退避、VACE-14B 70GBは絶対消さない) ②別env(0.33/4.41/2.4/3.10.9) ③公式repo clone+fp8 46GB選択DL(allow_patternsでaudio/editing変種除外、誤ると191GB全落ち即死、HF_HUB_ENABLE_HF_TRANSFER=0) ④SFWプローブ512x896/77f/30step/fp8/cpu-offload→Face-Sim比較 ⑤NSFWプローブ。

## 顔A/B比較の測り方
ArcFace(insightface buffalo_l)のFace-Sim(コサイン類似)が主指標。SSIMは顔ID不適(補助のみ)。同参照・同モーション記述・同解像度/seedでVACE版とHunyuanCustom版を生成→各動画から等間隔Nフレーム抽出→参照顔埋め込みとのコサイン平均±SD比較。+0.05以上&SD小でgo寄り。compare_face_sim.py(insightface+numpy)を別途書く。

成果物: 判定レポート artifact https://claude.ai/code/artifact/4c9efc0c-9dc5-462f-909b-aa8eb21af75e

関連: [[session-resume-hf-watcher-r2v]], [[wan-vace-r2v-local-setup]], [[r2v-reference-to-video-models]], [[nsfw-models-chroma-noobai-wan-lora]], [[optimal-gen-models-table-and-new-model-eval]]
