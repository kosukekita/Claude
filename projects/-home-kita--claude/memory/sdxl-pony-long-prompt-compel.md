---
name: sdxl-pony-long-prompt-compel
description: gen_image.pyのSDXL系(Pony/NoobAI/Manga-Vision/SDXL)は77トークン超の長プロンプトをcompelで全部使う(2026-06-30実装)。これが無いと衣装/ポーズ/背景が無言で切り捨てられ同一人物量産も崩れる
metadata:
  node_type: memory
  type: project
  originSessionId: 8fa33f41-3f7a-4f60-88ef-8e22b991175d
---

**`gen_image.py` の SDXL 系バックエンド（pony / noobai-xl / noobai-xl-vpred / manga-vision-il / sdxl）は、77トークンを超える長プロンプトを compel==2.0.3 で全部使うように改修済み（2026-06-30）。**

**問題（改修前）**: CLIP は 77 トークンで打ち切る。Pony 流に「score_9... + 人物固定ブロック + 衣装 + ポーズ + 背景 + 光」を並べると 150〜160 トークンになり、**後半（衣装/ポーズ/背景/光）が無言で truncate されて効かない**。実機事故: 「白Tシャツ+デニムショーツ」指定が**着物風の白衣**に化け、「バストアップ」指定が**座り全身**に化け、無地グレー背景も曖昧化した。ログに `The following part of your input was truncated because CLIP can only handle sequences up to 77 tokens: [...]` が出ていたら切り捨て発生。

**対処（実装済み）**: `image = pipe(**kwargs).images[0]` の直前に、`want_cls == "StableDiffusionXLPipeline"` のとき compel で `prompt_embeds`/`pooled_prompt_embeds`（negative も `negative_prompt_embeds`/`negative_pooled_prompt_embeds`）を作り `kwargs` に入れる。成功時ログ `pony: compel long-prompt embeddings (no 77-token truncation)`。
- PEP723 依存に `compel==2.0.3` を追加（**2.0.3 ピン必須**。新しい compel 3.x 系は `'EmbeddingsProviderMulti' object has no attribute 'empty_z'` で落ちて truncated にフォールバックする）。
- `ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED` + `requires_pooled=[False, True]` + `truncate_long_prompts=False`。negative がある時だけ `pad_conditioning_tensors_to_same_length` で +/- を同長に揃える。
- ログに出る `Token indices sequence length is longer ... (160 > 77)` は内部 tokenizer の**情報行**で、compel が 77 窓に分割して結合するので**切り捨てではない**（無害）。
- compel 未導入/失敗時は従来の truncated prompt にフォールバック（ログ `compel unavailable (...)`）。

**How to apply（同一人物量産の前提）**: Pony 等で「同じ人物」を狙って量産するときは、**人物記述ブロックを全枚で一字一句共通**にし、**seed と 構図/角度/衣装タグだけ振る**。compel が無いと共通ブロックの末尾（＝人物固定に効く詳細）が消えて同一性も崩れるので、この改修が同一人物量産の土台になっている。Pony の他作法（先頭 `score_9, score_8_up, score_7_up, score_6_up,` + `source_anime`（`source_pony` 禁止）+ furry ネガ + force_euler）は [[nonreal-nsfw-default-set]] のまま。

**Codex リファクタレビュー済み**: 「責務分離・YAGNI とも妥当、関数化は呼び出し1箇所なので不要、変数名を pe/ne/pooled/npooled → フルネームにだけリネーム」→ 適用済み。

FLUX/Qwen/Z-Image/Chroma は native の prompt 経路のまま（長プロンプト対応を広げるなら必要時に pipeline 別 builder を作る）。正本は video-media-studio SKILL.md「SDXL系の長プロンプト対応＝compel」の注記。

関連: [[nonreal-nsfw-default-set]] [[manga-bw-nsfw-models]] [[person-image-6elements-confirm-before-fill]] [[video-media-studio-skill]]
