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

## ★NSFW入力画像のi2v: 検閲で弾かれるモデルが多い(実証2026-06-27)
上半身裸のChroma画像をi2v開始フレームにしたら:
- **seedance-2.0 / 2.0-fast (ByteDance)**: 400 `InputImageSensitiveContentDetected`(入力画像NSFW検閲)→拒否
- **happyhorse-1.1 (Alibaba)**: job failed "Green net check failed for image (input): inappropriate content"(阿里绿网検閲)→拒否
- **wan-2.7 (Alibaba)**: ✅ 通る。同じAlibaba製でも**wan-2.7だけ入力画像フィルタをすり抜ける**(happyhorseは弾く)。
→ **OpenRouterで露骨NSFW入力のi2vは事実上 wan-2.7 一択**。他は入力画像検閲で全滅。SFW入力なら各モデル使える見込み。露骨NSFW i2vはローカルWan2.2(無検閲)が確実。

## ★★ユーザー恒久ルール(2026-06-27): NSFW動画・リファレンスありはWanのみ
**動画生成で「NSFW かつ リファレンス画像あり(i2v/参照)」のときは wan-2.7(クラウド) か Wan2.2(ローカル) を使う**。他モデル(seedance/happyhorse/kling/veo/sora等)は入力画像のNSFW検閲で弾かれるか未検証。seedance/happyhorseで露骨入力が拒否されたのを実証済み。→ NSFW i2vの第一候補=ローカルWan2.2(無検閲・確実)、クラウドで手軽なら=wan-2.7。SFW i2vなら他モデルも可。

## 結論
- 1枚を開始フレームにするだけ(i2v) → **SFW入力ならsora以外ほぼ全部OK**。**NSFW入力はWan(2.7 or ローカル2.2)のみ**(↑恒久ルール)。
- **人物の同一性を保つ参照画像セットが要る → wan-2.7(最柔軟) / hailuo-2.3 / happyhorse-1.1**(ただしNSFW入力はWanのみ)。
- 動画はもともと i2v が主([[optimal-gen-models-table-and-new-model-eval]]の動画は参照軸廃止しSFW/NSFW2軸)。ローカルNSFW動画はWan2.2+LoRA最適、クラウドで手軽に参照→動画ならwan-2.7。

## ★cloud_openrouter.py video の3バグ修正(2026-06-27, 修正済)
wan-2.7のi2vが3つの連鎖バグで動かなかった→全て修正済。同種の動画API実装で再発しうるので記録:
1. **frame_imagesスキーマ**: 旧`[{"url":...}]`はZodErrorで400。正しくは `[{"type":"image_url","frame_type":"first_frame","image_url":{"url":...}}]`(type=image_url固定、frame_type∈first_frame|last_frame)。`input_references`も`{"type":"image_url","image_url":{"url":...}}`。
2. **poll/download GETのContent-Type**: 空ボディGETに`Content-Type: application/json`を付けるとゲートウェイがcookie認証にフォールバック→401「No cookie auth credentials found」。GETは`Authorization`(+任意でReferer/X-Title)のみの`_get_headers()`を使う(Content-Type抜く)。
3. **unsigned_urlsのkey欠落**: 完了時`unsigned_urls[0]`は`.../videos/{id}/content?index=0`(api/v1配下)で**名前に反しBearer必須**。`_download(urls[0], out)`がkeyを渡さず401。`_download(urls[0], out, key=key)`に修正。
切り分け教訓: submit(POST)もpoll(GET)も200なのにスクリプトだけ401 → 怪しいのは(a)GETのContent-Type (b)完了後のダウンロード認証。手動pollで「どのステップで401か」を切る(submit/poll/downloadのどれか)。wan-2.7は約66秒でcompleted、150f/30fps/5sの.mp4が出る。

関連: [[optimal-gen-models-table-and-new-model-eval]] [[openrouter-image-gen-quirks]] [[nsfw-models-chroma-noobai-wan-lora]] [[video-media-studio-skill]]
