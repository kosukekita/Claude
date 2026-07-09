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

## ★r2v の画質序列＋真の対応モデル（2026-07-09 実カタログ精査で確定・NSFW不問）
実カタログ精査でメモの分類を更新。**画質最優先の SFW r2v の答え**:
- **OpenRouter 第一 = `bytedance/seedance-2.0`**（TRUE r2v・同一人物性最強格・縦9:16可・1080p ≈$0.34/s）。保険 = `alibaba/wan-2.7`（フラット$0.10/s）。
- **AtlasCloud 第一 = `google/veo3.1/reference-to-video`**（★純画質の頂点。1080p/8秒/参照1〜3枚 base64、2026-07-09 実証で最高画質＝枕広告風パジャマ動画が実写級に出た）。安価な高画質量産 = `bytedance/seedance-2.0/reference-to-video`（base $0.09・参照1〜9枚）。
- **★重要な訂正**: **OpenRouter の veo-3.1 と kling-v3 は r2v ではない**（first/last frame のみ＝i2v）。プレイグラウンドの "Reference Images" スロットはモデル非依存の汎用UIで機能に効かない。真の参照セット r2v は OpenRouter だと8本（seedance-2.0/-fast, wan-2.7, wan-2.6【一覧では隠れる】, hailuo-2.3【1080p 16:9横のみ音声なし】, happyhorse-1.0/1.1, grok-imagine）。**真の veo3.1 r2v と真の kling(o3) r2v は AtlasCloud 側にだけある**（`.../reference-to-video`、AtlasCloud は r2v 21本）。
- **cloud_atlascloud.py video が r2v で実動**（generateVideo→prediction ポーリング）。ローカル参照は **base64 データURL** で渡す（`_resolve_media_input` を uploadMedia でなく base64 化に修正済＝uploadMedia は未検証のまま不使用）。`--images a.png,b.png`（CSV分割後に各々base64化するのでdataURLのカンマ問題は起きない）。veo3.1 は既定で音声トラックを付ける（不要ならffmpegで無音化/差し替え）。

## ★wan-2.7 r2v の実測（2026-07-09・キャラシートを参照に実行）
- **参照画像は最低 240×240 が必須**。小さいと submit は通るが job が `failed` "image resolution must be at least 240x240, got WxH"（`InvalidParameter` code400）。★キャラクターシート（グリッド1枚）からパネルを切り出すと 160×280 等になり必ず弾かれる → Lanczos で min-side 320 に拡大すれば通る（実証）。
- **参照はグリッド全体を渡さず、綺麗な単一パネル（全身正面＋顔正面など）を切り出して複数 `--reference` で渡す**（コラージュ認識で同一性が崩れるのを防ぐ）。SFW 服装の参照＋NSFW 文章プロンプトで、裸のシャワー動画が同一人物性を保って生成できた（r2v は identity=参照 / シーン=プロンプトの分業）。
- **`--aspect-ratio 9:16` は無視され 1280×720 の横で出る**（画像同様、比率はモデル任せ）。縦が要るなら生成後に 9:16 センタークロップが確実（再指定しても横になりやすい）。5s/150f/30fps。
- r2v の呼び方: `cloud_openrouter.py video --model alibaba/wan-2.7 --task t2v --reference A --reference B --prompt ...`（first-frame を与えない＝input_references のみ＝r2v。i2v にしたいなら `--task i2v --image`）。プロンプトは日本語で通る（NSFW も wan-2.7 はすり抜ける）。生成 ~130s。

関連: [[optimal-gen-models-table-and-new-model-eval]] [[openrouter-image-gen-quirks]] [[nsfw-models-chroma-noobai-wan-lora]] [[video-media-studio-skill]] [[hunyuancustom-r2v-nogo]] [[wan-vace-r2v-local-setup]]
