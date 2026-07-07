---
name: feedback_flux2_reference_image_editing
description: FLUX.2はオープンウェイト(dev/klein)で参照画像編集ができる。gen_image.pyがt2iのみだったのは実装漏れ。pro/flexはAPI専用
metadata: 
  node_type: memory
  type: reference
  originSessionId: a913a1d6-25fa-4312-9f85-a1f61f737573
---

**FLUX.2-dev / FLUX.2-klein はオープンウェイトで参照画像編集ができる**（single/multi-reference editing、最大10枚）。HF に weights あり。diffusers の `Flux2Pipeline.__call__` / `Flux2KleinPipeline.__call__` / `Flux2KleinKVPipeline`（KVキャッシュで4step高速参照）は `image: PIL.Image | list[PIL.Image] | None` を受け付ける。`image=[PIL,...]` を渡すだけで参照条件編集になる。公式ドキュメントで確認済み（2026-07-07）。

**非自明な落とし穴（当初誤答した点）**: video-media-studio の `gen_image.py --backend flux.2-dev` は **t2i のみ**実装で、`image=` 引数を渡していなかった。そのため「FLUX.2 は参照画像を取れない」と誤認しやすいが、**モデル/パイプライン自体は参照編集可能**でスクリプトの実装漏れだっただけ。参照編集したいなら image を渡す専用スクリプト（`gen_flux2_edit.py`）を書く。

- **ローカルで動くオープンウェイト** = FLUX.2-dev（32B、Mistral3 text-enc、4bit で ~20GB／48GB A6000 に収まる）、FLUX.2-klein（9B、Qwen3 text-enc）。
- **FLUX.2 [pro] / [flex] はオープンウェイトではなく API 専用**（Replicate / fal / BFL）。ローカル不可。
- **FLUX.1 系で参照編集** = FLUX.1 Kontext（`gen_kontext.py`、`FluxKontextPipeline`、image 1枚＋指示文で人物同一性保持編集、bf16 ~24GB）。
- NSFW（nude 等）は Codex/Grok が拒否するのでローカル（Qwen-Image-Edit / FLUX.2-dev editing / Kontext）一択。

関連: [[feedback_character_sheet_no_text_no_crop]] [[project_nude_reference_sheet_hayase]] [[project_akitaken_remote_gpu_access]]
