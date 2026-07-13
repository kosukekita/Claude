---
name: gen-qwen-edit-vram-speed
description: gen_qwen_edit.py(Qwen-Image-Edit-2511 20B)の速度/VRAM実測。退避は必須だが大サイズでVRAM端競合し激遅→--sizeを下げると解消
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

`gen_qwen_edit.py`(Qwen-Image-Edit-2511・20B・bf16 ~47GB)のローカル生成の速度・VRAM実測(2026-07-13, A6000 48GB)。

## ★要点: 遅い時は「退避」でなく「出力サイズ」を疑う
- **`--offload none` は不可**: bf16モデル(transformer+text encoder+VAE)が**~47GBでロード時にOOM**(832×1216でもサイズ無関係にロードで落ちる=18MiB差)。48GBには収まらない→**退避は必須**。
- **`--offload model` は必須だが、大サイズだと激遅**: 832×1216(ネイティブ~1MP)だと退避モデルとactivationがVRAM端で競合し **86秒/step**(30-40step=1枚57分の地獄)。
- **★`--size 704x1024`(~0.72MP)に下げると 3.3秒/step**(≈26倍速・退避設定は同じ`--offload model`)。VRAM 40GB使用。activationに余裕ができ退避モデルが安定resident化するため。**30step/704×1024で ~1.5分/枚**。
- **両GPU並列**: `CUDA_VISIBLE_DEVICES=0/1` で別プロセスを1枚ずつ流す(各~40GBなので1GPU1プロセス)。6枚を3+3で ~7分。

## 実務ルール
- Qwen-Edit(2511)が遅い/OOMしたら: (1)`--offload none`は諦める(モデルが48GB超) (2)`--offload model`固定 (3)**`--size`を704×1024前後(~0.7MP)に**。832以上はVRAM端競合で激遅。
- 参照選定用の画像なら704×1024で十分な品質(同一性・胸/谷間・ホクロ再現OK実証)。もっと高精細が要るなら別途アップスケール。
- これは[[hunyuan-highres-and-gpu-loop-lessons]]の「HunyuanCustomは退避無関係・解像度が真因」とは別現象。Qwen-Editは退避必須で、サイズがVRAM端競合(速度)を左右する。
- 実装: `from_pretrained(torch_dtype=bfloat16)`+`enable_model_cpu_offload()`。fp8/4bit量子化は未対応(対応すれば退避不要で更に速い可能性)。cu121ピン必須([[reference-image-gen-codex-vs-qwen]])。

関連: [[reference-image-gen-codex-vs-qwen]] [[nsfw-real-to-anime-v2v-qwen]] [[quality-over-speed-media-gen]] [[hunyuancustom-r2v-nogo]]
