---
name: openrouter-image-gen-quirks
description: OpenRouter画像生成の2系統モダリティ・プロバイダ別NSFW拒否パターン・cloud_openrouter.py修正
metadata: 
  node_type: memory
  type: reference
  originSessionId: 94a9eabd-f430-420d-a163-ed1231755d7f
---

OpenRouter (`cloud_openrouter.py`, video-media-studioスキル) で画像生成する際の実地知見。キーは `~/.config/openrouter.key`。`models --modality image` で生きたID一覧。

## モデルは output_modality で2系統に分かれる（重要）
`GET /models?output_modalities=image` の `architecture.output_modalities` を見ると:
- **`out=[image,text]`** … google/gemini-*, openai/gpt-5*-image, openrouter/auto。chat/completions に `modalities:["image","text"]` を送る。結果は `choices[0].message.images[0].image_url.url`(data URL)。
- **`out=[image]` のみ** … flux.2-*, openai/gpt-image-1/2, recraft/*, sourceful/riverflow-*, bytedance/seedream-*, microsoft/mai-image-*, x-ai/grok-imagine-*。`["image","text"]` を送ると **404 "No endpoints found that support the requested output modalities: image, text"**。`modalities:["image"]` だけにすれば通り、画像は同じ `message.images[0]` に入る。

→ `cloud_openrouter.py` 修正済み(2026-06-26): `["image","text"]`を投げ、その404文言なら`["image"]`で自動リトライ。さらに 500/502/"Provider returned error" の一時障害に指数バックオフ4回リトライを追加。

## 出力は比率・形式がモデル任せ（プロンプトの"9:16"は効かないことが多い）
chat経路では aspect_ratio を渡せず各モデルのデフォルト寸法になる。実測: gemini-3-pro=768x1376(9:16✓), grok-imagine=720x1280(9:16✓), flux.2-pro=1024x768(横長), seedream-4.5=2048x2048(正方形), recraft-v4.1-pro=1536x2688(縦). 形式もPNG/JPEG/WEBP混在。拡張子.pngでも中身はJPEG/WEBPのことがある→マジックバイトで判定。

## プロバイダ別 NSFW/コンテンツ拒否（盗撮風・"big breast"等で実証）
- **openai** … gpt-image-2はOpenRouter側で500頻発(不安定)。gpt-5.4-image-2は **テキストで明示拒否**("I can't help create sexualized imagery of a real-person-looking woman...")。openaiはこの種の題材は通らない。
- **microsoft/mai-image-2.5** … Azureの content_safety_violation (MultiSeverity_SexualScore) で 400拒否。"big breast" 程度でも弾く。
- **sourceful/riverflow (pro/fast両方)** … 502を繰り返す＝プロバイダ全体がダウンしている時間帯あり(ポリシーでなくインフラ障害、時間をおけば回復見込み)。
- **通った系**: google/gemini-3-pro-image, black-forest-labs/flux.2-pro, bytedance/seedream-4.5, x-ai/grok-imagine-image-quality, recraft/recraft-v4.1-pro。SFW寄り(露出指示なし)の盗撮風スナップはこの5社で生成可。

関連: [[optimal-gen-models-table-and-new-model-eval]] [[grok-nsfw-refuse-chroma-fallback]] [[image-cache-volatile-use-media-out]](出力は~/media-outへ)
