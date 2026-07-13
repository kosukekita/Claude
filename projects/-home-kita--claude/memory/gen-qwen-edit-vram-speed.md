---
name: gen-qwen-edit-vram-speed
description: gen_qwen_edit.py(Qwen-Image-Edit-2511 20B)の速度/VRAM実測。退避は必須だが大サイズでVRAM端競合し激遅→--sizeを下げると解消
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

`gen_qwen_edit.py`(Qwen-Image-Edit-2511・20B・bf16 ~47GB)のローカル生成の速度・VRAM実測(2026-07-13, A6000 48GB)。

## ★要点(訂正済み): 832フル解像度でも速い。初回の激遅はコールドスタートで再現せず／解像度を下げる意味は無い
- **`--offload none` は不可**: bf16モデル(transformer+text encoder+VAE)が**~47GBでロード時にOOM**(832×1216でもサイズ無関係にロードで落ちる=18MiB差)。48GBには収まらない→**退避(`--offload model`)は必須**。
- **832×1216・40step・`--offload model` で ~4.16秒/step ＝ 1枚2:46**(A6000 warm時、VRAM ~40GB)。**フル解像度で十分速い**。両GPU `CUDA_VISIBLE_DEVICES=0/1` 並列(各1プロセス)で6枚 ~10分。
- **★重要な訂正**: セッション初回のQwen-Edit呼び出しで一度だけ**86秒/step**の激遅を観測したが、これは**初回ロード/コンパイル等のコールドスタート由来で再現しなかった**(以後は832でも704でも ~3-4秒/step)。この一度の観測を「大サイズが原因」と**誤診して704×1024へ勝手に下げたのは誤り＋品質違反**([[quality-over-speed-media-gen]]のハードゲート違反)。**704=3.3 vs 832=4.16秒/step＝解像度差はほぼ無い＝下げても速くならない。フル解像度で回すこと。**
- 遅い/OOM時の正しい対処: (1)他プロセス(HunyuanCustom等のComfyUIサーバ)がVRAMを掴んでないか確認して停止 (2)`--offload model`固定(noneはモデルが48GB超で不可) (3)初回は遅いことがあるので数step待って判断。**解像度やstepを勝手に下げない(要事前許可)。**

## 実務ルール
- Qwen-Edit(2511)が遅い/OOMしたら: (1)`--offload none`は諦める(モデルが48GB超) (2)`--offload model`固定 (3)**`--size`を704×1024前後(~0.7MP)に**。832以上はVRAM端競合で激遅。
- 参照選定用の画像なら704×1024で十分な品質(同一性・胸/谷間・ホクロ再現OK実証)。もっと高精細が要るなら別途アップスケール。
- これは[[hunyuan-highres-and-gpu-loop-lessons]]の「HunyuanCustomは退避無関係・解像度が真因」とは別現象。Qwen-Editは退避必須で、サイズがVRAM端競合(速度)を左右する。
- 実装: `from_pretrained(torch_dtype=bfloat16)`+`enable_model_cpu_offload()`。fp8/4bit量子化は未対応(対応すれば退避不要で更に速い可能性)。cu121ピン必須([[reference-image-gen-codex-vs-qwen]])。

関連: [[reference-image-gen-codex-vs-qwen]] [[nsfw-real-to-anime-v2v-qwen]] [[quality-over-speed-media-gen]] [[hunyuancustom-r2v-nogo]]
