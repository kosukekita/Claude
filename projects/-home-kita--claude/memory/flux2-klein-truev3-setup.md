---
name: flux2-klein-truev3-setup
description: FLUX.2-klein-9B finetune(True-V3)をローカルで動かす正解構成。Flux2KleinPipeline必須(Qwen3エンコーダ)・transformerはfrom_single_file差替・cu121ピン・蒸留でguidance無視
metadata: 
  node_type: memory
  type: project
  originSessionId: 8fa33f41-3f7a-4f60-88ef-8e22b991175d
---

NSFW人物画像のローカル新主力候補 **`wikeeyang/Flux2-Klein-9B-True-V3`** を video-media-studio で動かす正解構成（2026-06-30 実機で完動・採用）。専用スクリプト `scripts/gen_klein.py` を新規追加した。

**ハマりどころ（順に踏んだ。全部回避済み）**:
1. **True-V3 は diffusers 形式でなく single-file 配布**（`*-bf16.safetensors` / GGUF のみ、`model_index.json`・`transformer/` フォルダ無し）。よって `from_pretrained(True-V3)` は不可。**公式ベース `black-forest-labs/FLUX.2-klein-9B`(diffusers, gated:auto, token必須) を読み、transformer だけ `Flux2Transformer2DModel.from_single_file(path, config=base, subfolder="transformer")` で差し替える**。`Flux2Transformer2DModel.from_single_file` は対応(True)だが `Flux2Pipeline.from_single_file` は非対応(False)。
2. **klein は text encoder が Qwen3**（FLUX.2-dev の Mistral3 と別物）。汎用 `Flux2Pipeline` は Mistral3 の chat template をハードコードしており、klein に使うと `TypeError: can only concatenate str (not "list") to str` で落ちる。**専用の `Flux2KleinPipeline`（Qwen3ForCausalLM + Qwen2TokenizerFast）を使う**。これは diffusers git-main にある（`Flux2KleinPipeline/Inpaint/Modular...`）。手元の 0.39.0.dev0 main に既に入っていた。
3. **`Flux2KleinPipeline.__call__()` は `negative_prompt` を受け付けない**（この版では unexpected keyword でエラー）。negative は使わず、抑制要素（入れ墨なし・ミラーセルフィでない等）は**ポジティブ本文に明示**する。
4. **True-V3 は step-wise 蒸留モデル** → `Guidance scale ... is ignored`。guidance は効かない（turbo系と同じ）。28step ~22秒/枚で良好。少step化も可。
5. **torch は cu121 ピン必須**（[[reference-image-gen-codex-vs-qwen]] と同じ）。ドライバ 535/CUDA12.2 に最新 torch wheel は "driver too old"。`gen_image.py` と同じ `torch==2.5.1`+`torchvision==0.20.1` を pytorch-cu121 index にピン。torchvision は FLUX.2 の PixtralProcessor に必要。

9B bf16 は単一A6000(48GB)に native で収まる(~30GB、free47.5で offload不要)。出力は `~/media-out/`（[[image-cache-volatile-use-media-out]]）。

**画力 vs 露骨さの傾向(2026-06-30 実機、絵画風プロンプトで比較)**: Klein True-V3 は**画力・筆致・解剖が最良**だが、**露骨な性的動作には保守的**(「乳首を舐めペニスをさする」を投げても両者着衣・手を握るだけに留め、明示的な性器/フェラ描写を出さない傾向)。一方 **Z-Image-Turbo は同プロンプトで指定の性的動作(口で性器・手で愛撫・全裸)を素直に描く**。よって使い分け: **構図/画力重視・ソフトNSFWなら Klein、ハード/露骨な行為描写が要るなら Z-Image(またはNoobAI系)**。絵画風は両者とも painting/oil painting/visible brush strokes をポジティブに、photo/photorealistic をネガティブ(Z-Imageのみ)に。

**まだ未反映**: SKILL.md / gen_image.py の backend 表に klein を載せていない（gen_klein.py 独立スクリプトのまま）。ユーザーは「chromaをクビにしてklein新主力」の認識なので、次は gen_image.py への backend 統合 or SKILL.md 追記を検討。関連: [[nsfw-models-chroma-noobai-wan-lora]] [[optimal-gen-models-table-and-new-model-eval]]
