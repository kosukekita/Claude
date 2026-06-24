---
name: optimal-gen-models-table-and-new-model-eval
description: 現状ベスト生成モデル早見表(画像/動画×SFW/NSFW×参照画像)と、新着HFモデルの4軸評価チェックリスト
metadata: 
  node_type: memory
  type: reference
  originSessionId: cee1ee3b-cf5e-48e5-82d4-e8881a33670e
---

ローカルリグ(A6000 48GB×2)での**現状ベスト生成モデル早見表**と、新着HFモデルが出たときの評価フロー。ユーザー依頼(2026-06-24): 新着が出たら「画像/動画か・NSFW対応か・参照画像取れるか・ローカルで動くか」を確認し、判明したら現状最適モデルと比較生成する。

## 現状ベスト早見表
| 用途 | SFW最適 | NSFW最適 | 参照画像 | 備考 |
|---|---|---|---|---|
| t2i 人物フォトリアル | Z-Image-Turbo / 外部Grok・Codex | Z-Image+Chroma+Grok 3本並べ | ❌ | Chromaは英語フォトリアルprompt必須(でないとアニメ/デバイス誤生成) |
| t2i アニメ | NoobAI-XL(eps) | NoobAI-XL eps/vpred | ❌ | vpredは`v_prediction`+`rescale_betas_zero_snr=True`必須 |
| 画中テキスト t2i | Qwen-Image | Qwen-Image | ❌ | offload強制で遅い・商用可 |
| 参照画像→画像edit | Codex `-i ref.jpg`(stdin prompt必須) | Qwen-Image-Edit (`gen_qwen_edit.py --image`) | ✅Qwen1-3枚/Codex1枚 | Qwen無検閲・同一性保持・cu121必須。Codexはヌード拒否。FLUX Kontextは不採用 |


## 動画は2軸(SFW/NSFW)で記録 — 参照画像軸は廃止
ユーザー指摘(2026-06-24): **動画生成は参照あり(i2v)が全てなので参照画像軸は無意味**。動画はSFW/NSFWの2軸のみ。
| 動画用途 | 現状最適 | 速度代替 | 備考 |
|---|---|---|---|
| SFW 動画 | **Wan2.2**(i2v-a14b / t2v-a14b, 品質最上) | LTX-2.3 i2v(`gen_ltx23.py`, 音声付・実用速度・~12分) | Wan A14Bはbf16 80GB→fp8 46GB or torchrun multi。offloadだと激遅(81f/40stepで1h超)。frame: Wan=4k+1 / LTX=8k+1 |
| NSFW 動画 | **Wan2.2+LoRA**(`gen_wan_lora.py --lora HIGH --lora-low LOW`, 品質最上) | LTX-2.3+lynaNSFW(`gen_ltx23_lora.py --nsfw-motion --lora-scale 0.7`, ~12分実用) | LoRAセット`lkzd7/WAN2.2_LoraSet_NSFW`(HIGH→transformer_2=False/LOW→True)。LTXコミュニティ"LTX-2.x"はLoRAで公式baseにスタック(差替禁止) |

**現状は動画はSFW/NSFWともWan2.2が最適だが、今後最適モデルが増える可能性あり**(新着評価で更新する)。
注: `gen_wan_lora.py`はメモリ記載だが当スキルscripts/内に未確認→使用前に存在確認。LTX-2.3 NSFWは`--offload model`(seqは固まる)。

## 新着HFモデル4軸評価チェックリスト
1. **画像/動画判定**: `model_index.json`の`_class_name`(`*Pipeline`=画像/`*ToVideoPipeline`/`Wan*`/`LTX*`=動画)、`pipeline_tag`でも一次判定
2. **NSFW対応**: 露骨promptをLoRA無しで投げ素直に通るか。ローカルdiffusersは拒否せず、失敗はボヤけ or scheduler誤設定(検閲ではない)。NFAAタグ`not-for-all-audiences`はデフォ検索除外→`?other=not-for-all-audiences`
3. **参照画像**: (1)img2img/edit(`__call__`が`image=`=Qwen-Editクラス) (2)Kontext型(禁止) (3)IP-adapter/顔埋め込み(未配線=新規) (4)i2v first-frame。pipelineクラス名+siblingsで判定
4. **ローカル可否**: `model_index.json`=diffusers対応(Chroma/Flux2/QwenImage/LTX2はdiffusers git-main要)/単一safetensors`lora_A/B`キー=LoRA(公式baseにスタック、差替禁止)/`.gguf`=ComfyUI専用。**Qwen系はtorch cu121ピン必須**(cu128だとaccelerator not found)

**比較フロー**: 4軸判明後、その軸の現状最適モデルで同一被写体・同一promptを生成し新モデルと横並び。フォトリアルNSFWは常にZ-Image/Chroma/Grok複数本(既定)。タトゥー抑制を全生成適用。評価軸=肌リアルさ/構図忠実/無検閲素直さ/速度。

実証済み事例(2026-06-24): Krea-2-Turbo(SFW専用t2i,Krea2Pipeline,diffusers git-main,offload要,重複DL厳禁)、flux_uncensored_nsfw_v2(FLUX.1-dev用NSFW LoRA,`gen_flux_lora.py`で生成成功)。スクリプトは`~/media-out/model-compare/`(gen_flux_lora.py/gen_krea2.py/pcloud_link.mjs/compose2.sh)。

関連: [[grok-nsfw-refuse-chroma-fallback]], [[reference-image-gen-codex-vs-qwen]], [[nsfw-models-chroma-noobai-wan-lora]], [[ltx2-community-models-are-loras]], [[video-media-studio-skill]], [[hf-weekly-model-watcher]]
