---
name: optimal-gen-models-table-and-new-model-eval
description: 現状ベスト生成モデル早見表(画像/動画×SFW/NSFW×参照画像)と、新着HFモデルの4軸評価チェックリスト
metadata: 
  node_type: memory
  type: reference
  originSessionId: cee1ee3b-cf5e-48e5-82d4-e8881a33670e
---

ローカルリグ(A6000 48GB×2)での**現状ベスト生成モデル早見表**と、新着HFモデルが出たときの評価フロー。ユーザー依頼(2026-06-24): 新着が出たら「画像/動画か・NSFW対応か・参照画像取れるか・ローカルで動くか」を確認し、判明したら現状最適モデルと比較生成する。

## 画像モデル4分類（ユーザー確定設定 2026-06-24）
画像は **NSFWか × 参照画像取れるか の2軸=4分類**。各分類の最適モデル:
| 分類 | 参照画像 | 最適モデル |
|---|---|---|
| **SFW + 参照なし** | t2i | **★6本セット(ユーザー恒久ルール 2026-06-28): Codex CLI / Grok CLI / OpenRouter gpt-5-image / OpenRouter grok-imagine-image-quality / Nano Banana 2 (gemini-3.1-flash-image) / Nano Banana Pro (gemini-3-pro-image)**。「SFWのプロンプトで画像生成して」と言われたらこの6つを生成して並べる。日本語プロンプトOK・「盗撮」は婉曲化([[openrouter-image-gen-quirks]])。Nano Banana 2は画面いっぱい没入スナップ向き/Proはスマホ実機枠を描きがち(プロンプト次第)。OpenRouterはcloud_openrouter.py image、CLIは各スキル(codex exec / grok image_gen) |
| **SFW + 参照あり** | edit/i2i | **Codex**（`codex exec -i ref.jpg`、prompt は stdin） |
| **NSFW + 参照なし** | t2i | **Grok・Z-Image・Chroma の3本常に**（Grokが拒否しても残2本は出る。[[grok-nsfw-refuse-chroma-fallback]]と整合） |
| **NSFW + 参照あり** | edit/i2i | **Qwen**（Qwen-Image-Edit, `gen_qwen_edit.py --image`、無検閲・同一性保持・cu121必須） |

注: Grokは露骨NSFW(盗撮+上半身裸+実写偽装)を拒否しうる→NSFW参照なしで3本並べる理由。Chromaは英語フォトリアルprompt必須。動画は別軸(下記、参照軸なしSFW/NSFWのみ)。

## 現状ベスト早見表（詳細）
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

**★ユーザー恒久ルール(2026-06-27): NSFW動画でリファレンス画像ありの場合は wan-2.7(クラウド/OpenRouter) か Wan2.2(ローカル) を使う**。他のクラウド動画モデル(seedance=ByteDance / happyhorse=Alibaba / kling / veo / sora)は**入力画像のNSFW検閲で弾く**(seedance=`InputImageSensitiveContentDetected`、happyhorse=阿里绿网`Green net check failed`を実証)。同じAlibaba製でも**wan-2.7だけ入力画像フィルタをすり抜ける**。クラウドで手軽なら wan-2.7、確実さ・無検閲ならローカル Wan2.2(ti2v-5b は単一GPU native/速い、i2v-a14b は2GPU分散で高品質)。詳細は [[openrouter-video-models-reference-support]]。クラウド wan-2.7 は `cloud_openrouter.py video --model alibaba/wan-2.7 --task i2v --image X`(3バグ修正済)。
注: `gen_wan_lora.py`はメモリ記載だが当スキルscripts/内に未確認→使用前に存在確認。LTX-2.3 NSFWは`--offload model`(seqは固まる)。

## 新着HFモデル4軸評価チェックリスト
1. **画像/動画判定**: `model_index.json`の`_class_name`(`*Pipeline`=画像/`*ToVideoPipeline`/`Wan*`/`LTX*`=動画)、`pipeline_tag`でも一次判定
2. **NSFW対応**: 露骨promptをLoRA無しで投げ素直に通るか。ローカルdiffusersは拒否せず、失敗はボヤけ or scheduler誤設定(検閲ではない)。NFAAタグ`not-for-all-audiences`はデフォ検索除外→`?other=not-for-all-audiences`
3. **参照画像**: (1)img2img/edit(`__call__`が`image=`=Qwen-Editクラス) (2)Kontext型(禁止) (3)IP-adapter/顔埋め込み(未配線=新規) (4)i2v first-frame。pipelineクラス名+siblingsで判定
4. **ローカル可否**: `model_index.json`=diffusers対応(Chroma/Flux2/QwenImage/LTX2はdiffusers git-main要)/単一safetensors`lora_A/B`キー=LoRA(公式baseにスタック、差替禁止)/`.gguf`=ComfyUI専用。**Qwen系はtorch cu121ピン必須**(cu128だとaccelerator not found)

**比較フロー**: 4軸判明後、その軸の現状最適モデルで同一被写体・同一promptを生成し新モデルと横並び。フォトリアルNSFWは常にZ-Image/Chroma/Grok複数本(既定)。タトゥー抑制を全生成適用。評価軸=肌リアルさ/構図忠実/無検閲素直さ/速度。

実証済み事例(2026-06-24): Krea-2-Turbo(SFW専用t2i,Krea2Pipeline,diffusers git-main,offload要,重複DL厳禁)、flux_uncensored_nsfw_v2(FLUX.1-dev用NSFW LoRA,`gen_flux_lora.py`で生成成功)。スクリプトは`~/media-out/model-compare/`(gen_flux_lora.py/gen_krea2.py/pcloud_link.mjs/compose2.sh)。

関連: [[grok-nsfw-refuse-chroma-fallback]], [[reference-image-gen-codex-vs-qwen]], [[nsfw-models-chroma-noobai-wan-lora]], [[ltx2-community-models-are-loras]], [[video-media-studio-skill]], [[hf-weekly-model-watcher]]
