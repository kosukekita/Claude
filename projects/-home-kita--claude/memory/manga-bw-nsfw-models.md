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

## ★複数コマ・ページ構成 = 「1枚に直描画」は2コマ・吹き出し無しが鉄則(2026-06-29実証)
`gen_image.py`は1枚絵t2iのみ(コマ割りレイアウト機能なし)。それでも複数コマ漫画を1枚で狙うときの確定知見:
- **失敗**: `manga page, multiple panels, panel layout`を強く効かせると、SDXL系(NoobAI/MangaVision)はコマ枠の分割だけ実行し各コマの中身(キャラ/シーン)が空になる。MangaVisionは顔の断片を格子状に並べるだけ・NoobAIは枠+崩れ吹き出しでスカスカ。コマ数が多いほど各コマが小さく中身が消える。
- **成功(v2)**: ①コマ数は**2まで**(`2koma, two panels`)②構造タグ控えめ・**キャラ描写を主役**に前へ(`1girl, nude, lying on bed, top panel close-up of face, bottom panel full body`)③**speech bubbles/text/dialogueはネガに入れ外す**(SDXLは日本語を描けず崩れた偽文字になるだけ、台詞は後でPILで載せる)。seed違えば絵柄別。NoobAI-vpred 832x1216/steps30/guidance5.5で2コマとも中身ありの白黒漫画成立。
- **真に多コマ(各コマ作り込み)が要るなら**: 「1ページ=1大ゴマ」で中身を確実に描いた画像を複数枚生成→`scripts/manga_page.py`(今回追加, PILでガター+黒枠+RTL読み順でページ合成。`--panels ... --rows "2,1,2" --rtl`)で合成。これが結局きれい(当初の「個別コマ生成→ページ合成」と同結論)。
- 出力: `~/media-out/manga-compare/page/`(noobai_v2_2koma=本命 / _page_compare / prompts.md)。

出力: `~/media-out/manga-compare/`(noobai_manga / mangavision_manga / qwen_photo2manga_*)。
関連: [[nsfw-models-chroma-noobai-wan-lora]](NoobAI設定詳細), [[reference-image-gen-codex-vs-qwen]](Qwen-Edit), [[optimal-gen-models-table-and-new-model-eval]], [[video-media-studio-skill]](manga_page.py)
