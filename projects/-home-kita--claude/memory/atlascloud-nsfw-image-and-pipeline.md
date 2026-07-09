---
name: atlascloud-nsfw-image-and-pipeline
description: AtlasCloudのNSFW画像可否(z-image○/grok・wan・qwen×)と、完全AtlasCloud NSFWパイプライン(z-image先頭フレーム→spicy i2v)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

**AtlasCloud で NSFW（露骨な全裸）を出せるか — 2026-07-09 実地テストで確定。**

## ★NSFW画像は「ローカル z-image-turbo（無料・無検閲）」が最適（AtlasCloudに払う必要なし）
- **z-image-turbo はローカルにも同一モデルがある**: `gen_image.py --backend z-image-turbo`（スキルのローカル既定主力）。**ローカルなら課金ゼロ・無検閲で全裸を通す**（AtlasCloud版と同じモデル＝上位互換）。**NSFW の先頭フレーム/参照画像はローカル z-image で作るのが既定**。Qwen-Edit(顔固定が要る時)や Chroma とも使い分け。
- AtlasCloud の z-image は「ローカルGPUを使いたくない/塞がっている時」のホスト版フォールバック（$0.005）。

## t2i の NSFW 可否（AtlasCloudホスト版を裸プロンプトで実測・目視）
- **`z-image/turbo`（AtlasCloud） = ✅ 完全な全裸を通す**（大きな胸・実写・$0.005）。2人構図（ソープ嬢が男性の体を洗う）も seed を振れば一発で成立（複雑NSFW構図も可）。size は `"幅*高さ"`（アスタリスク。`x`不可）。seed は `--extra-json '{"seed":N}'`。※ローカル版が無料なので通常はローカルを使う。
- `xai/grok-imagine-image/text-to-image` = ❌ HTTP 400 `Content violates platform security policy`（ハードブロック）。
- `alibaba/wan-2.7/text-to-image` = ❌ ソフト検閲（タオル巻きにされる）。
- `qwen/qwen-image-2.0/text-to-image` = ❌ ソフト検閲（服を着た別人の顔になる）。
- 画像モデル100本に spicy/NSFW タグは0（タグでは判別不可＝実測必須）。Google(nano-banana)/OpenAI(gpt-image)は当然検閲。**要するに AtlasCloud で無検閲画像＝z-image/turbo 一択**（他は未検証だが上記4本の傾向から期待薄）。

## ★NSFW パイプライン（顔は新規ペルソナで良い場合・高速安価）
1. **NSFW 先頭フレーム = ローカル z-image-turbo（無料・無検閲）**で作る（2人構図も可）。GPUが塞がっている時だけ AtlasCloud z-image。
2. **spicy i2v** でそれを動画化。`atlascloud/wan-2.7-spicy/image-to-video`（$0.10・720P/1080P・約50秒）が画質良。安いのは `alibaba/wan-2.2-spicy/image-to-video`（$0.03）。ローカル等価は Wan2.2+spicy LoRA（`gen_wan_lora.py`・無料だが遅い）。
- 実証: ソープ嬢が男性客を洗うNSFW動画を z-image先頭フレーム→wan-2.7-spicy i2v で生成成功（2026-07-09）。洗う動作が自然にアニメ、無検閲、破綻少。spicy i2v は既定で音声トラックを付ける（不要ならffmpegで無音化）。
- 呼び出しは `cloud_atlascloud.py`（image / video サブコマンド）。ローカル画像は base64 データURLで渡る（`_resolve_media_input` 修正済）。

## 使い分け（NSFW r2v/i2v の現状整理）
- **顔を特定人物に固定したい NSFW r2v** → ローカル HunyuanCustom（`gen_hunyuan_custom.py`・無検閲・参照1枚+テキスト・約36分）。ただし体型/胸は参照画像が主決定なので Gカップを見せた参照が要る。→ [[openrouter-video-models-reference-support]]
- **顔は新規で良い NSFW 動画** → ★上の完全AtlasCloudパイプライン（z-image→spicy i2v）が速くて安い。
- AtlasCloud に NSFW の真の r2v（reference-to-video）は無い（spicy は全部 i2v/video-extend）。OpenRouter は残高切れ（[[openrouter-image-gen-quirks]]）。
- Codex(OpenAI) は露骨NSFWの手順を**ポリシーで拒否**する（NSFWの相談先には使えない）。

関連: [[openrouter-video-models-reference-support]] [[nsfw-models-chroma-noobai-wan-lora]] [[grok-nsfw-refuse-chroma-fallback]] [[optimal-gen-models-table-and-new-model-eval]]
