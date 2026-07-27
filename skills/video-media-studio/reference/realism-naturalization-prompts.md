# realism-naturalization-prompts.md — リアル写真の自然化プロンプト全30個（video-media-studio）

`SKILL.md` の「リアル写真の自然化プロンプト」節が defer する正本。
リアル/実写風/フォトリアル画像の「AIっぽさ」（肌ツルツル・作り物っぽい照明・完璧すぎる顔・背景が浮く）を消すための
日本語自然文プロンプト集。人物の肌・手・表情、照明の整合性、全体のリアル感を底上げする。
出典: X スレッド https://x.com/fukugyo_clinic/status/2073874603647316331

## 使い方の原則（SKILL.md のルールと同じ）

1. **勝手に足さない — 提案して確認してから足す。** ユーザーがリアル画像を求めたら「この中からこれを足しませんか」と提案する。無断追記は 6 要素テンプレートの確認ルールと同じ違反。
2. **まずスターター3個**を既定の提案にする（下記）。症状が具体的なら該当カテゴリから追加で 2〜3 個選んで見せる。30 個全部を一度に足さない（プロンプトが薄まる）。
3. **バックエンドで渡し方が違う**（下の対応表）。自然文をそのまま理解するのは指示追従系のみ。ローカル diffusion 系はキーワードに変換する。

## スターター3個（迷ったらまずこれを提案）

- ① 「SNSに実在しそうな自然な写真にしてください」
- ② 「過度な加工感はなくしてください」
- ㉚ 「100点に近づけるために自然さを最優先してください」

## 全30個（6カテゴリ）

### ① AIっぽさを消す
1. 「SNSに実在しそうな自然な写真にしてください」
2. 「過度な加工感はなくしてください」
3. 「現実にありそうな1枚として成立させてください」
4. 「完璧すぎない自然な雰囲気にしてください」
5. 「AIっぽく見える要素は避けてください」

### ② 写真っぽさが上がる
6. 「スマホで撮影したような質感にしてください」
7. 「自然光で撮ったようにしてください」
8. 「背景を少しだけぼかしてください」
9. 「日常のワンシーンのようにしてください」
10. 「カメラ目線ではなく自然な視線にしてください」

### ③ 人物の違和感を消す
11. 「手や指に違和感が出ないようにしてください」
12. 「顔のパーツを自然なバランスにしてください」
13. 「表情を作り込みすぎず自然にしてください」
14. 「髪の流れを自然に整えてください」
15. 「肌をなめらかにしすぎないでください」

### ④ 背景となじませる
16. 「人物と背景の光の向きを合わせてください」
17. 「生活感のある背景を入れてください」
18. 「背景だけ浮かないよう自然にしてください」
19. 「影の位置を現実的にしてください」
20. 「服・髪・背景の境目を自然にしてください」

### ⑤ SNSで使いやすくする
21. 「XやInstagramに流れてきても違和感ない雰囲気で」
22. 「アイコンにも投稿にも使いやすい構図にしてください」
23. 「文字を載せても見やすい余白を作ってください」
24. 「一目で雰囲気が伝わる画像にしてください」
25. 「見る人が保存したくなる自然な雰囲気で」

### ⑥ 最後の仕上げ
26. 「不自然な加工・歪み・破綻をなくしてください」
27. 「細部まで高品質に整えてください」
28. 「作り物っぽいツヤや照明を抑えてください」
29. 「読者目線で違和感がないか確認してください」
30. 「100点に近づけるために自然さを最優先してください」

## ⑦ シネマ／広告・商品映像調（動画・CM・商品カット向けの追加キュー・上の30個とは別枠）
実写の広告/商品/シネマ調（例: 商品開封・食品・POV ハンド）で"高級な実写"に寄せたいとき、STYLE ブロックや各ショットに足す。日本語で言われたら英語キュー化して渡す（ローカル diffusion はキーワード、Codex/Grok は自然文）。
- `soft natural lighting with gentle shadows`（柔らかい自然光・作り物っぽい照明を避ける）
- `shallow depth of field, creamy background bokeh`（浅い被写界深度・背景ボケ＝被写体が浮く）
- `cinematic look, subtle filmic color grade`（シネマ調の色）
- `real camera product photography, premium commercial style`（本物のカメラの商品撮影・高級広告調）
- `warm practical light, warm wooden table surface, window light`（暖色の実光源・木のテーブル等の生活感）
- `POV first-person, hands only, no face visible`（一人称・手だけ・顔を映さない POV ハンド）
- `visible steam, condensation, moisture, natural reflections`（湯気・水滴・自然な反射＝食品/飲料で効く）
- `subtle motion blur on moving hands, natural handheld feel`（手の自然なブレ・手持ち感）

## ⑧ ファウンドフッテージ／民生機の粗で「本物の素人撮影」に見せる（動画向け・⑦とは逆レバー・別枠）
①〜⑦の「きれいなフォトリアル／高級シネマ」とは**逆方向**のリアル化。動画AIが"バレる"最大要因は **画が綺麗すぎ・安定しすぎ・露出が完璧すぎ**。これをわざと壊し、特定の民生機（カムコーダ/VHS/古スマホ）の粗を再現すると、vlog・POV・"隠し撮り風"・素人自撮り動画は一気に本物に見える。**⑦（premium/clean/cinematic/studio）と同時に入れない**（狙いが真逆で打ち消す）。用途: gym vlog・日常自撮り動画・found-footage・POVハンド・"ガチ投稿"風。

- **(a) 撮影デバイスを1つ固定してアンカーにする**（全体の質感を決める）: `DV / MiniDV handheld camcorder footage` / `Hi8 or VHS camcorder tape look` / `early-2000s point-and-shoot video` / `filmed on an old phone, vertical phone video`。1つ選び STYLE に固定。
- **(b) 素人オペレータの粗**（動画でしか出せない＝"完璧な三脚"を捨てる）: `natural handheld shake, unstabilized` / `soft focus, delayed (late) focus pulls, hunting autofocus`（甘い＆遅れて合うピント） / `clumsy zoom, sudden reframing, imperfect framing`（下手ズーム・雑な構図） / `auto-exposure flicker and hunting as light changes`（自動露出のふらつき）。
- **(c) アナログ/テープの粗**: `tape noise, video grain, slight blur, muted washed-out contrast` / `bloomed highlights around lights`（光源のにじみ＝ブルーム） / `slightly crushed blacks, low dynamic range`。※`timecode / date stamp` は「画面内文字を入れない」既定の**例外＝明示要望時のみ**。
- **(d) ダイエジェティックな撮影者＋カメラを映さない**（found-footage の肝）: `POV, the character holds or props the camera on a surface; the camcorder is never visible in frame`（人物がカメラを持つ/置く・カメラは絶対に映さない）。
- **(e) 物理状態の時間連続**（"生っぽさ"・シーンをまたいで進行させる）: `glowing skin with increasing sweat over the clip, breathless, flushed`。開始→中盤→終盤で状態（汗・息切れ・化粧崩れ等）を段階指定する。

渡し方: Codex/Grok は自然文で STYLE と各ショットに。ローカル diffusion は下の変換表 ⑧ 行のキーワードで（⑦の premium/studio 系キューは併用しない）。

## ⑨ NSFW（透け/裸）を実写級にする2段パイプライン（Qwen→承認→nano-banana・実測確立 2026-07-28）
nano-banana / Higgsfield 画像モデルは**露骨なヌード・乳首が透けて見える画像を nsfw 拒否**する。一方 nano-banana の実写質感は最高。**Qwenのrealismパスは肌が荒れる（そばかす）ので使わず、realismは nano-banana に任せる**。手順:
1. **local Qwen-Image-Edit（無検閲）で「着せる/裸透け」を作る**: 人物ref＋服装ref（＋ホテルref）。胸サイズ・ポーズ・**45度アングル**を指定（真正面は乳首が正面に出るので斜めにして目立たせない）。9:16なら `--size 864x1536` 等（Qwenは9:16生成可）。
2. **必要なアップに 9:16 クロップ**（顔検出で顔中心・上半身。乳首が枠内なら「乳首ぼかし＋クロップ」で枠外化/ぼかす）。
3. **★ユーザー承認ゲート**（生成器＝評価者にしない＝人が構図/露出/角度を確認してから次へ）。
4. **nano-banana でリアル化**: そのクロップを `--image-references` に「ultra-photorealistic real photograph, same angle/pose/robe, natural skin, film grain...」＋`--aspect-ratio 9:16 --resolution 2k`。**45度＋ローブが胸を覆う or 乳首ぼかしならモデレーション通過**し、クリーンな実写質感になる。
- **モデレーション事実（実測 2026-07-27/28）**: nano-banana/Higgsfield 画像＝乳首見え/see-through-nude は拒否（乳首を**クロップ/ぼかし/45度**で覆えば通る）。**Higgsfield `wan2_7`（動画）は透け裸＝乳首入りでもそのまま受理**（動画から静止画も抜ける）。無検閲の静止画はローカル（Qwen/z-image）。SFWの服装抽出/ゴーストマネキンは Higgsfield 優先（通るし高品質・2026-07-28確認）。

## 症状 → 提案するカテゴリの対応

| ユーザーの症状・要望 | 提案 |
|---|---|
| 「AIっぽい」「バレたくない」全般 | スターター3個（①②㉚） |
| 肌がツルツルすぎる / 手指・顔が変 | ③人物（特に⑪⑮）＋㉘ |
| 照明・ツヤが作り物っぽい | ⑦⑯⑲㉘ |
| 背景が浮く / 合成っぽい | ④背景（⑯〜⑳、特に⑰生活感） |
| SNS アイコン・投稿用 | ⑥⑨＋⑤SNS（㉑㉒） |
| 仕上げ・最終チェック | ⑥仕上げ（㉖〜㉚） |
| 「素人っぽく」「vlog / POV / 隠し撮り風」「本物のスマホ/ビデオっぽく」（動画） | ⑧ファウンドフッテージ（★⑦とは混ぜない） |

## バックエンド別の渡し方（重要）

| バックエンド | 渡し方 |
|---|---|
| **Codex(GPT Image) / Grok image_gen / OpenRouter 画像（gpt-5-image, Nano Banana 等）/ Qwen-Image-Edit** | **日本語自然文のまま末尾に追記**（指示追従系は「〜してください」を理解する）。Grok は翻訳禁止ルールどおり日本語のまま。6 要素テンプレートの後ろに仕上げ層として置く |
| **ローカル diffusion（z-image-turbo / FLUX / SDXL / Chroma / Klein）** | 自然文の命令形は効かない。**下のキーワード変換表でポジ/ネガに変換**して渡す |

### ローカル diffusion 用キーワード変換

| 元プロンプト | ポジティブに足す | ネガティブに足す（対応モデルのみ） |
|---|---|---|
| ①⑥⑨ SNS実在感・スマホ質感・日常 | `candid smartphone photo, casual everyday snapshot, amateur photography` | `professional studio photo, promotional photo` |
| ②⑮㉘ 加工感・肌ツルツル・ツヤ | `natural skin texture with visible pores, unretouched` | `airbrushed, plastic skin, overly smooth skin, glossy retouched look, oversaturated` |
| ④⑬ 完璧すぎない・表情 | `relaxed candid expression, slightly imperfect framing` | `perfect symmetry, posed studio portrait` |
| ⑦⑯⑲ 自然光・光と影の整合 | `natural window light, consistent ambient lighting, realistic soft shadows` | `studio lighting, harsh flash, rim light` |
| ⑧ 背景ぼかし | `shallow depth of field, slightly blurred background` | — |
| ⑩ 視線 | `looking away from camera, natural gaze` | `looking at viewer`（構図次第） |
| ⑰ 生活感 | `lived-in interior, everyday clutter in background` | `empty sterile background` |
| ㉖ 破綻防止 | —（既定ネガで対応済み） | 既定の `deformed hands, extra fingers, watermark, text` を維持 |
| ⑧ 素人ビデオ・vlog・found-footage（動画） | `handheld camcorder footage, natural handheld shake, soft focus, hunting autofocus, tape noise, video grain, bloomed highlights, muted contrast, auto-exposure flicker` | `stabilized, tripod, clean sharp footage, cinematic color grade, studio lighting`（⑦系と併用しない） |

- ネガティブが効くのは z-image-turbo / sdxl系 / chroma / qwen-image。FLUX.1/2-dev・Klein は negative 非対応なのでポジティブ側に `no ...` で明示（入れ墨ルールと同じ流儀）。
- 既定のタトゥー禁止ネガ（`tattoo, tattoos, body ink, lettering on skin`）とは併存させる（置き換えない）。

## 年齢リアリズム（★2026-07-21 ユーザー確定・年齢が分かる人物に自動適用）

**被写体の年齢が分かっている人物（ペルソナの age・ユーザー指定年齢）は、汎用リアル化に加えて「年齢相応の肌サイン」を明示的に列挙する。** 汎用の `visible pores` レベルでは皺・シミは出ない（実測 2026-07-21: 青木彩乃35歳・Seedance 2.0 r2v の v5→v6 比較。v5=毛穴指定のみ→アイドル的ツル肌、v6=下の定型追加→目尻の小皺・シミ・ほくろ・自然な肌トーンが出た）。原因は2つ: ①生成モデルは放置すると若く・滑らかに倒す ②r2v/i2v の参照写真自体がツル肌だと同方向に引っ張る。

**実機検証済みの英文定型（AGE-REALISTIC SKIN 段落・年齢と部位は差し替え）** — 動画(Seedance/wan等)・指示追従系画像(Codex/Qwen-Edit)にそのまま使える:

```
AGE-REALISTIC SKIN (critical): she is in her mid-30s and her skin must honestly show it — fine lines at the corners of her eyes and a subtle crease at the edge of her mouth when she smiles, faint nasolabial lines, a few small faint sun spots and tiny moles scattered on her face, neck, chest and shoulders, slightly uneven natural skin tone, visible pores and fine skin texture everywhere including her chest. NOT airbrushed, NOT porcelain-smooth, NOT a flawless idol look — a beautiful real woman of 35 photographed on a real camera.
```

- 年齢帯で強度を調整する（20代前半=ほぼ汎用リアル化のみ／30代=上の定型／40代以降=皺・シミの語彙を段階的に強める）。「beautiful real woman of <age>」の年齢を必ずペルソナに合わせる。
- **年齢不明の人物には適用しない**（勝手に老けさせない）。適用・不適用で迷ったらユーザーに確認。
- ローカル diffusion 向けキーワード変換: ポジ `fine lines around eyes, faint sun spots, small moles, uneven natural skin tone, mature skin texture` ／ ネガ `porcelain skin, flawless skin, baby face, airbrushed`（対応モデルのみ）。
- 日本語自然文で渡す場合（Grok等）: 「35歳相当の肌にしてください。微笑んだときの目尻・口元の小皺、うっすらしたほうれい線、顔・首・胸元の薄いシミやほくろ、均一すぎない自然な肌トーンを残し、陶器のような完璧な肌にしないでください」。
