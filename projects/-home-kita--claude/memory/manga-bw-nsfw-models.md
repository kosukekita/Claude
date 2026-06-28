---
name: manga-bw-nsfw-models
description: 白黒漫画(モノクロ・トーン・コマ)NSFW画像の最適モデル。ローカルNoobAI/Manga Vision IL、実写→漫画化はQwen-Image-Edit。クラウドは不可
metadata: 
  node_type: memory
  type: reference
  originSessionId: 94a9eabd-f430-420d-a163-ed1231755d7f
---

白黒の日本漫画(monochrome・screentone・コマ割り・線画)でNSFW(無検閲)を生成する手段(2026-06-28確定)。

## ローカル(本命・無検閲) — 一から白黒漫画を生成
1. **NoobAI-XL** `--backend noobai-xl-vpred`(既存)。アニメ系SDXL+booruタグ。`greyscale, monochrome, manga, comic, screentones, lineart, halftone, hatching`タグで白黒漫画化。トーン豊富・吹き出しも自動生成・劇画調。vpred版はコントラスト強い。
2. **Manga Vision IL** `--backend manga-vision-il`(今回gen_image.pyに追加, repo=`John6666/manga-vision-il-v1-sdxl`, Illustrious-XLベース=NoobAI同系・無検閲, diffusers形式6.5GB)。**白黒漫画専用**でクリーン線画・同人誌風・あっさり。tag不要でも墨+トーンになる。
- 共通: 英語booruタグ(`masterpiece, best quality, 1girl, large breasts, ...`)。negativeに`color, colored, photorealistic, rgb`を入れ白黒固定(★`monochrome/greyscale/manga`をnegativeに入れない)。832x1216(縦コマ向き)、steps28、guidance5-6。両者seed同じでも絵柄は別。
- LoRA候補(未導入): CivitAIのClassic B&W Manga(`m4ng41nk`)、HF実在の`artificialguybr/LineAniRedmond-LinearMangaSDXL-V2`(線画寄りトーン弱)。まずは上記2チェックポイントで十分。

## ★実写→そのまま漫画化(参照画像→漫画, 同一人物保持) = Qwen-Image-Edit
**`gen_qwen_edit.py --image <実写写真> --prompt "この写真の女性をそのまま白黒漫画スタイルに変換。モノクロ,線画,スクリーントーン,ハッチング,コマ風。顔/髪型/体型/服装はそのまま保つ。" --negative-prompt "color, colored, photorealistic, photo, 3d, realistic skin" --size 832x1216`**。実証(2026-06-28): Z-Image実写女性→顔立ち/髪型/体型/脱衣所シーンを保持したまま白黒漫画絵に変換成功。同一人物性◎。[[reference-image-gen-codex-vs-qwen]]の参照NSFW=Qwenルールが漫画化にも有効。

## クラウド(OpenRouter等) = NSFW不可・全滅
OpenRouter画像モデル(gemini/gpt-image/flux.2/seedream/grok)は全て商用フィルタ付き→白黒漫画"スタイル"は出てもNSFWは弾く。無検閲漫画はローカル一択。クラウドが要るならfal/Modalで自前NoobAI系サーブ([[grok-nsfw-refuse-chroma-fallback]]と同型)。

出力: `~/media-out/manga-compare/`(noobai_manga / mangavision_manga / qwen_photo2manga_*)。
関連: [[nsfw-models-chroma-noobai-wan-lora]](NoobAI設定詳細), [[reference-image-gen-codex-vs-qwen]](Qwen-Edit), [[optimal-gen-models-table-and-new-model-eval]]
