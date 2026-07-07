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

## 症状 → 提案するカテゴリの対応

| ユーザーの症状・要望 | 提案 |
|---|---|
| 「AIっぽい」「バレたくない」全般 | スターター3個（①②㉚） |
| 肌がツルツルすぎる / 手指・顔が変 | ③人物（特に⑪⑮）＋㉘ |
| 照明・ツヤが作り物っぽい | ⑦⑯⑲㉘ |
| 背景が浮く / 合成っぽい | ④背景（⑯〜⑳、特に⑰生活感） |
| SNS アイコン・投稿用 | ⑥⑨＋⑤SNS（㉑㉒） |
| 仕上げ・最終チェック | ⑥仕上げ（㉖〜㉚） |

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

- ネガティブが効くのは z-image-turbo / sdxl系 / chroma / qwen-image。FLUX.1/2-dev・Klein は negative 非対応なのでポジティブ側に `no ...` で明示（入れ墨ルールと同じ流儀）。
- 既定のタトゥー禁止ネガ（`tattoo, tattoos, body ink, lettering on skin`）とは併存させる（置き換えない）。
