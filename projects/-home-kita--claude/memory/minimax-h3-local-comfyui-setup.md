---
name: minimax-h3-local-comfyui-setup
description: MiniMax-H3(Hailuo3系・動画+音声同時生成)をHeretic無検閲TEでローカルComfyUI導入、実機動作確認済み(2026-08-04)
metadata: 
  node_type: memory
  type: project
  originSessionId: 30e2b450-b35d-4c1d-88b8-ccd7c0b9b44c
  modified: 2026-08-04T09:15:46.875Z
---

MiniMax-H3（動画+ステレオ音声の同時生成・Hailuo 3 のオープンウェイト・**LLMではない**）を akitaken でローカル稼働させた（2026-08-04 実機スモーク成功）。

**構成（正本）**:
- **専用 ComfyUI**: `/data/kita/ComfyUI-mmh3`（v0.30.0・uv venv py3.12 only-managed・torch 2.11.0+cu128・comfy-kitchen 0.2.26）。**既存 `/data/kita/ComfyUI`（HunyuanCustom/LTX 用）は無変更**。モデルは `extra_model_paths.yaml` で既存 `/data/kita/ComfyUI/models` を共有
- **DiT**: Comfy-Org/MiniMax-H3 `minimax_h3_fl2va_int8_convrot.safetensors`（32GB・非pruned int8=品質優先。Ref2VA 版は**未DL**）→ `models/diffusion_models/`
- **TE（無検閲）**: ethanfel/Qwen3-VL-32B-Ultra-Heretic-MiniMax-H3-ComfyUI-INT8-ConvRot（層0–49+vision tower 25GB。Heretic 編集層31–40は保持範囲内）+ 生成テール（層50–63・7.1GB・プロンプト強化用）→ **`models/text_encoders/MiniMax-H3/` サブディレクトリ**に2つとも配置。CLIPLoader type **`minimax`**
- **VAE**: video fp16 4.9GB + audio fp32 578MB → `models/vae/`
- **カスタムノード**: ethanfel/ComfyUI-MiniMax-H3-Guide（依存ゼロ・プロンプト整形+テール使用の強化ノード）

**起動/実行**:
- サーバ: `systemd-run --user --unit=comfyui-mmh3 --collect --setenv=CUDA_VISIBLE_DEVICES=0 bash /data/kita/mmh3-setup/serve-mmh3.sh`（port 8288・systemd-run 必須は [[ltx23-crossview-ic-lora-local]] と同じ理由）
- API グラフ雛形: `/data/kita/mmh3-setup/smoke_t2v.mjs`（UNETLoader+CLIPLoader(minimax)+MiniMaxH3ImageToVideo(prompt/width/height/length・optional first_frame/last_frame=FL2VA)→BasicGuider(CFG蒸留済み・CFGなし)+res_multistep/simple/20steps→SamplerCustomAdvanced→VAEDecode+VAEDecodeAudio→CreateVideo(24fps)→SaveVideo）
- 実測: 480×864/56f(2.3s)/20steps＝**458秒（初回ロード込み）**。出力 h264+AAC 32kHz ステレオ（音声同時生成を確認）
- 仕様: ネイティブ短辺768px（上限768×1344・32px倍数）、フレームは **17k+5** 刻み@24fps（124=約5秒・訓練域〜362）

**踏んだ罠**:
- 74GB DL と並行の uv install は既定30秒タイムアウトで大wheel が死ぬ → `UV_HTTP_TIMEOUT=1800`
- `ln -sfn "$(readlink -f <HFキャッシュのファイル>)" <dir>/` は**blobハッシュ名のリンク**を作る → snapshot パスを**宛先ファイル名明示**でリンクする
- 生成後サーバが GPU に約47GB 保持し続ける → `POST /free {"unload_models":true,"free_memory":true}` で解放（サーバは維持・次回は RAM キャッシュから再ロード）

**残タスク候補**: video-media-studio への正式ラッパー（gen_minimax_h3.py・Codex 委譲）。Ref2VA bf16 は導入済み→[[minimax-h3-ref2va-usage]]、NSFW 耐性実測済み→[[minimax-h3-nsfw-and-int8-vs-bf16]]。関連: [[optimal-gen-models-table-and-new-model-eval]] [[nsfw-auto-pipeline-explicit-video]]
