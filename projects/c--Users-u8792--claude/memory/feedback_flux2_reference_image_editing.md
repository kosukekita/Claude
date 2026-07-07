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
**実機で判明した2つの壁（akitaken 2026-07-07）**:
1. **ロードが激重**: FLUX.2-dev は 166GB リポジトリ＋単一 `flux2-dev.safetensors`。単一48GBカードで 4bit+offload だと**GPU util 0%のまま17分スラッシング**（実質進まない）。`--multi-gpu`（device_map='balanced' bf16）にすると両GPUに配置されるが、**巨大 checkpoint の CPU デシリアライズに ~12-15分**かかる（RSS が 64GB まで増える）。ロード完了後の推論自体は GPU0 単独 util 100% で ~1-2分と速い。つまりボトルネックは推論でなくロード。実用するならロード後にパイプを保持して複数枚バッチ推論すべき（1枚ごとに再ロードは非現実的）。RAM 不足ではない（197GB空きでも遅い＝I/O とデシリアライズが律速）。
2. **★NSFW（脱衣）を拒否**: FLUX.2-dev に「服を脱がして nude に」と参照編集を指示したら、**顔・体型の同一性は完璧に保ったまま、脱衣指示だけ無視して元の着衣（白ブラウス＋パンツ）を維持**して出力した（実機確認）。公式 gated モデルのセーフティ層のため。**よって FLUX.2-dev は nude 用途では使えない**（Codex/Grok と同じ壁）。klein も同系統なので同様の見込み。→ **NSFW（nude 等）で参照同一性を保つローカル経路は Qwen-Image-Edit 一択**（Apache/検閲なし）。FLUX 系（.2-dev / .1 Kontext とも公式 gated）は SFW 編集向き。

- NSFW（nude 等）は Codex/Grok/FLUX.2-dev/Kontext がいずれも拒否 → **Qwen-Image-Edit のみ**。SFW の参照編集なら FLUX.2-dev/klein・FLUX.1 Kontext も可。

関連: [[feedback_character_sheet_no_text_no_crop]] [[project_nude_reference_sheet_hayase]] [[project_akitaken_remote_gpu_access]]
