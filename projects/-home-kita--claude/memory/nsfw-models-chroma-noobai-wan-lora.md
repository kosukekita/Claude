---
name: nsfw-models-chroma-noobai-wan-lora
description: video-media-studio に追加したNSFWモデル群（Chroma無検閲t2i・NoobAIアニメ・Wan2.2 LoRA動画）と各設定の要点。HFでのNSFW探索TIPS
metadata: 
  node_type: memory
  type: project
  originSessionId: 1fdf83d2-555b-436f-8214-734280823ac5
---

2026-06-24、video-media-studio スキルに高品質NSFWモデルを追加。すべて 2×A6000(各48GB) でローカル動作。

**NSFW画像（参照なし）の最適解 = Chroma / Z-Image / Grok の3本柱**（ユーザー確定 2026-06-24）。フォトリアル無検閲ならこの3つで出して見比べる。肌のリアルさはZ-Image最良、構図忠実・無検閲の素直さはChroma、生活感・シーンのリアルさはGrok。参照画像が要るNSFWだけは別＝Qwen-Image-Edit（[[reference-image-gen-codex-vs-qwen]]）。

## gen_image.py に追加した backend
- **`--backend chroma`** = `lodestones/Chroma1-HD`（FLUX.1-schnell刈込8.9B、**設計から無検閲のフォトリアルbase**、Apache-2.0）。jailbreak/LoRA無しで素のままNSFWフォトリアルが出る＝Z-Imageの穴を埋める。`ChromaPipeline`(diffusers git-main)。**画質改善が重要**: stockのFlowMatchEulerは眠い→**`FlowMatchEulerDiscreteScheduler.from_config(..., use_beta_sigmas=True, use_dynamic_shifting=True, base_shift=0.5, max_shift=1.15)` に差し替え**（`scipy`依存必須・入ってないとbeta sigmasで例外→stockにフォールバックし軟いまま）。steps=40、**1024×1024(≈1MP)が最適**、negativeは70トークン以上(`plastic skin, airbrushed, doll-like`等で滑らか禁止)。これらは gen_image.py に組込済(`chroma_schedule:True`)。**ユーザー指示(2026-06-24): Chromaで生成するときは guidance 3.0 と 6.5 の両方を出して並べる**（g3.0=自然で柔らかい/g6.5=コントラスト強くシャープ。ユーザーがこの2つを好む）。diffusersではbeta sigmasの alpha/beta(0.46等) を引数で渡せない（ComfyUI専用）ので質感はプロンプト/negative/guidanceで追い込む。**肌のリアルさ単体では Z-Image > Chroma**（Chromaはツルッとしやすい・質感調整しても覆らず）→ リアル肌はZ、構図忠実・無検閲の素直さはChroma、と使い分け。**Chromaは参照画像非対応**（ChromaImg2Imgは強度img2imgで同一人物維持不可、ip_adapter_image引数は中身無しの罠、FLUX用アダプタも改変アーキで不可）→参照NSFWは [[reference-image-gen-codex-vs-qwen]] の通りQwen-Image-Editのまま。
- **★Chromaは英語プロンプト必須（言語理解の問題・検閲ではない）**: ChromaはFLUX系なのでテキストエンコーダが **T5-XXL(google/t5-v1_1-xxl, 英語中心C4訓練)**。日本語語彙をほぼ持たず、日本語を入れると埋め込みがノイズ化して**プロンプトと無関係な画像**が出る(実証2026-06-27: 日本語の盗撮NSFW指示→金髪サングラスの白人男性。英語に直したら一発で意図通り)。**Chroma/FLUX系(flux.1/flux.2含む)は常に英語**で書く。対照: **Z-Image(Tongyi/アリババ)は多言語TE(CN/EN強・日本語OK)** なので日本語プロンプトで通る。→ NSFW3本柱は **Z-Image=日本語OK / Chroma=英語必須 / Grok=日本語(検閲は別)** と覚える。⚠️ OpenAI/Grokの「英語拒否→日本語で通る」は**検閲回避**の話、Chromaの英語必須は**言語理解**の話で**方向が逆**(混同注意)。日本語しか無いときは [[openrouter-image-gen-quirks]] の `sakana/fugu-ultra` 等で英訳前段を噛ませる。
- **`--backend noobai-xl`** = `Laxhar/noobai-XL-1.1`（**eps版**、アニメ/booruタグ、SDXL生態系の入口）。標準StableDiffusionXLPipelineで動く。**v-pred版 `Laxhar/noobai-XL-Vpred-1.0` は `--backend noobai-xl-vpred`**（`vpred:True`で scheduler を `prediction_type="v_prediction", rescale_betas_zero_snr=True` に再設定。**これを入れないと出力が真っ赤なノイズで破綻**）。booruプロンプト（masterpiece, best quality, 1girl, ...）で使う。NoobAI/SDXLのCLIPも英語前提＝英語booruタグで。

## gen_wan_lora.py（新規・Wan2.2-i2v + コミュニティLoRA）
- Wan2.2のNSFW動画品質は**LTX-2.3より上**（人体/肌/動きのリアルさ。2026比較の定説）。ただし**A14B MoE×`--offload model`は構造的に激遅**（81f/40stepで**1時間超**。各stepでGPU⇔CPUの巨大重み転送）。実用には速度LoRA(lightx2v/Lightning、**Low側のみ**)/fp8化が要る。
- **Wan2.2-A14BはMoE＝2エキスパート**: `transformer`(high_noise,前半)と`transformer_2`(low_noise,後半)。コミュニティLoRAはHIGH/LOWペアで配布され、**HIGH→`load_lora_weights(.., load_into_transformer_2=False)`／LOW→`load_into_transformer_2=True`** に振り分け必須（diffusersネイティブAPI、キー変換不要）。`gen_wan_lora.py --lora <HIGH> --lora-low <LOW> --lora-scale 0.8`。frame=4k+1(81=5s@16fps)。
- `lkzd7/WAN2.2_LoraSet_NSFW` = Wan2.2-I2V用の行為別NSFW LoRA集（53本=26行為×HIGH/LOW。missionary/doggy/cowgirl/blowjob/handjob等）。ベースでなくアドオン。

## HuggingFaceでのNSFWモデル探索（実務TIPS）
NSFWは単一タグ `not-for-all-audiences`(NFAA)でゲートされ**デフォルト検索/一覧から除外+Inference API無効化**。Settings→Content Preferencesで「Show not-for-all-audiences」をONにしないと直リンクすら警告で弾く。URL: `?other=not-for-all-audiences` / `?other=nsfw` / `?pipeline_tag=image-to-video&other=nsfw`。**最強は base_model ツリー(Wan/LTX/Qwen/FLUXページのAdapters/Finetunes)を辿る**。`huggingface.co/search/full-text?q=nsfw&type=model`。**一次ハブはCivitAI、HFは二次/ミラー**＝CivitAIで発見→HFから重みpull。HFバルクミラー例: `wiikoo/WAN-LORA`, `Phr00t/WAN2.2-14B-Rapid-AllInOne`(全部入り,速度優先), `Phr00t/Qwen-Image-Edit-Rapid-AIO`。Wan2.5+はAPI専用で**公開重みなし＝ローカルでは2.2が最新Wan**。

関連: [[video-media-studio-skill]] [[reference-image-gen-codex-vs-qwen]] [[ltx2-community-models-are-loras]] [[face-crop-tool-and-ltx-offload]] [[image-cache-volatile-use-media-out]]
