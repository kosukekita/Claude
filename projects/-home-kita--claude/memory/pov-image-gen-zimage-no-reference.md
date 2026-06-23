---
name: pov-image-gen-zimage-no-reference
description: 真の一人称POV(ハメ撮り)画像はZ-Image-Turbo参照なしt2iが最適。Qwen-Editは立ち参照に引っ張られPOV不可、Grokは露骨NSFWをheadlessでブロック
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fa37c53f-75f8-403f-bc64-3847918c0990
---

NSFW の**真の一人称視点（first-person POV）**画像（例: ハメ撮り＝撮影者である寝た男性の目線で跨る女性を見上げる）を生成するときの定石。「真の一人称」とは**撮影者本人の手・スマホ・顔・上半身を一切フレームに写さない**こと（スマホが映っていたら一人称ではない＝三人称の自撮り写真になる。ユーザーの基準）。

**最適解 = Z-Image-Turbo（ローカル・参照画像なしの text-to-image）**。`gen_image.py --backend z-image-turbo --size 832x1216`、9step・guidance≈0、A6000 単発で数十秒。プロンプトはカメラ＝寝た男性の目の位置、主役は跨る女性、男性の体はほぼ写さない（手前下隅にわずか）と明記。男女とも全裸なら「全裸」を**両方に明示**（女性だけ「裸」だと男性が着衣で出る）。入れ墨抑制は negative に `tattoo, body ink, lettering on skin`。

**Why 参照画像はダメ**: [[reference-image-gen-codex-vs-qwen]] の通り NSFW で参照が要るなら Qwen-Image-Edit が定石だが、**一人称POVは参照と相性が最悪**。撮影者の体は写らないので体型リファレンス自体が不要。むしろ `male-body-reference.jpg`（立ちミラーセルフィ）を渡すと Qwen-Image-Edit がその「立ちポーズ・三人称フレーミング・スマホを構える構図」を強く保持し、テキストで「騎乗位・寝た男性・POV」と書いても**画像コンディショニングが勝って三人称の立ち/並び構図に倒れる**（cfg を 4→5 に上げても、プロンプトで立ちを明示否定しても、POVには到達しない。マスク・体型・ホテル背景は反映される）。

**Grok**: `image_gen` に露骨 NSFW（全裸＋騎乗位＋POV）を投げると、日本語プロンプトでもヘッドレス `-p` 実行では**無言終了でブロック**（画像が一切出ず、`grok -r` で聞くと NONE）。英語ラッパ指示文を混ぜるとさらに弾かれやすい。露骨度が高い NSFW は Grok でなくローカル Z-Image が確実。[[grok-prompt-keep-japanese]] の「日本語なら通る」は当たる露出表現の度合いによる。

**How to apply**: NSFW 一人称 POV → 迷わず Z-Image-Turbo 参照なし、seed 違いで複数枚出して当たりを選ぶ。三人称で人物の体型を寄せたいときだけ Qwen-Edit + 参照。出力は消えやすい untracked ディレクトリ（`image-cache/` 等）でなく scratchpad か `~/.claude/generated/` に置く（今回 image-cache が作業中に外部要因で丸ごと消えた）。
