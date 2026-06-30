---
name: nsfw-painterly-models-research
description: 絵画/イラスト調NSFWローカルモデルのdeep research結論(2026-06-30)。Chromaより明確に優れる新baseは無し。アニメ露骨=SDXL系(NoobAI/Illustrious/Pony)+画風LoRA、油彩写実絵画=Chromaの2軸
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8fa33f41-3f7a-4f60-88ef-8e22b991175d
---

絵画/イラスト調NSFWのローカル実行モデルを deep-research した結論（2026-06-30、RTX A6000 48GB前提）。**問い「Chroma1-HD/NoobAI/Manga Vision/Z-Image/Klein より絵画NSFWで明確に優れる新baseはあるか」への回答=「単一の万能新baseは無い」**。

**2軸で使い分けるのが正解（業界主流）**:
1. **アニメ/イラスト調の露骨NSFW = SDXL系 + 画風LoRA**。base候補:
   - **NoobAI-XL**(`Laxhar/noobai-XL-1.1` / `Laxhar/noobai-XL-Vpred-1.0`、手元にあり) — Danbooruネイティブ・無検閲・LoRA資産最大。これが本命の一つ。
   - **Illustrious-XL**(`OnomaAIResearch/Illustrious-xl-early-release-v0`) — NoobAIの上流。
   - **Pony Diffusion V6 XL**(Civitai 257749) — スコアタグ式(`score_9`等)で構図制御が効く。**手元に無いので追加候補No.1**。SDXL系8–12GB。
   - ★気づき: 「絵画NSFWの新base」を待つより **NoobAI(手元)に油彩/厚塗り系スタイルLoRAを足す**のが費用対効果最大。
2. **油彩/写実寄りの絵画NSFW = Chroma 一択**(`lodestones/Chroma1-HD`、手元)。代替の決定打は見つからず。ユーザー実機でも絵画露骨で破綻しなかった唯一格。

**新アーキ実験枠 = Anima**(`circlestone-labs/Anima`、Civitai 2458426): NVIDIA Cosmos-Predict2-2Bベースの**非SDXL/非FLUX**新アーキ、アニメ/イラスト/painterly特化(realism非対応)。`safe/sensitive/nsfw/explicit`の4タグでNSFW制御(ハード検閲でない)、2B・6-8GB VRAM、2026-05リリース。**ただし独立レビュー(lilting.ch)は批判的**: SDXL比で実用優位ほぼなし・推論約10倍遅・手の破綻・テキストエンコーダ弱(0.6B Qwen3)・エコシステム未成熟・非商用のみ・preview段階。→ 試す価値はあるが現状スタックの置き換え根拠なし。

**反証された主張(信じない)**: Z-Imageが絵画NSFWに強い→**反証**(実機で絵画露骨が破綻、ユーザー指摘と一致)。FLUX.1/SD3.5/Qwen-Imageの「絵画NSFW向き」は一次情報で裏付け弱い(SD3.5は検閲+ライセンス制約、Qwenはテキスト描画が強みでNSFW絵画の定評薄)。Pony V7/Illustrious優劣やWAI-Illustriousのcensored/uncensored両版主張は検証で全てrefuted/無投票→不採用(=Pony追加候補の確証は今回得られず、SKILL.md表からは外す)。Z-ImageのNSFW可否/絵画適性/ライセンスは一次ソース未確認のまま(中核3軸不明)。

**限界**: Civitaiは認証必須でアクセス制限、直近1–2ヶ月の新規/Civitai限定公開モデルは取りこぼし可能性あり。次にやるなら NoobAI用の油彩/厚塗りスタイルLoRA探索が有望。ライセンス: NoobAI=Fair AI Public、Pony=独自、Chroma=Apache-2.0。

関連: [[grok-nsfw-refuse-chroma-fallback]] [[flux2-klein-truev3-setup]] [[nsfw-models-chroma-noobai-wan-lora]] [[manga-bw-nsfw-models]] [[optimal-gen-models-table-and-new-model-eval]]
