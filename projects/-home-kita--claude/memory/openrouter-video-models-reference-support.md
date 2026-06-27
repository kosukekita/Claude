---
name: openrouter-video-models-reference-support
description: OpenRouter動画生成16モデルの参照画像対応分類(i2v first-frame / last-frame / reference画像セット)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 94a9eabd-f430-420d-a163-ed1231755d7f
---

OpenRouter動画生成モデル(`cloud_openrouter.py video`, 2026-06-27時点16本)の**参照画像の取り方**分類。APIは `GET /api/v1/videos/models` の各モデル `supported_frame_images`(["first_frame","last_frame"]) と description の "reference images" 記述で判定。`cloud_openrouter.py` は i2v用 `--image`→`frame_images`、参照用 `--reference`→`input_references` を送れる。

## 参照画像は2種類(混同注意)
- **first_frame (i2v)**: 1枚を動画の開始コマにして動かす。最も一般的。
- **last_frame**: 終点フレーム指定(始点と合わせて補間)。
- **reference画像セット**: 人物/スタイルの同一性を保つ参照(first_frameとは別概念)。

## ★reference画像セット対応 = 4本のみ
| モデル | first | last | **ref** | 尺 | 備考 |
|---|:-:|:-:|:-:|---|---|
| **alibaba/wan-2.7** | ✅ | ✅ | ✅ | 2-10s | **最多機能**(first/last/ref全部)。ローカルWan2.2のクラウド最新版 |
| **alibaba/happyhorse-1.1** | ✅ | — | ✅ | 3-15s | audio対応、長尺15sまで |
| alibaba/happyhorse-1.0 | ✅ | — | ✅ | 3-15s | |
| **minimax/hailuo-2.3** | ✅ | — | ✅ | 6-10s | |

## first_frame(i2v)のみ対応(refセット不可) = 多数
kling-v3.0-pro/std, kling-video-o1, google/veo-3.1(/fast/lite), bytedance/seedance-2.0(/fast)/seedance-1-5-pro は **first+last frame** 対応(refセットは×)。x-ai/grok-imagine-video と alibaba/wan-2.6 は first_frame のみ。

## t2v専用(画像参照不可) = openai/sora-2-pro のみ
sora-2-proは `supported_frame_images=[]`。テキストからのみ。

## 結論
- 1枚を開始フレームにするだけ(i2v) → **sora以外ほぼ全部OK**。
- **人物の同一性を保つ参照画像セットが要る → wan-2.7(最柔軟) / hailuo-2.3 / happyhorse-1.1**。
- 動画はもともと i2v が主([[optimal-gen-models-table-and-new-model-eval]]の動画は参照軸廃止しSFW/NSFW2軸)。ローカルNSFW動画はWan2.2+LoRA最適、クラウドで手軽に参照→動画ならwan-2.7。

関連: [[optimal-gen-models-table-and-new-model-eval]] [[openrouter-image-gen-quirks]] [[nsfw-models-chroma-noobai-wan-lora]] [[video-media-studio-skill]]
