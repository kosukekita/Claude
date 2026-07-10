---
name: seed-randomize-always-image-gen
description: 画像/動画生成でseedを設定できる時は再現目的以外は必ずランダム化する恒久ルール(固定seedで別ペルソナが同一人物化した事故)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

★ユーザー恒久ルール（2026-07-10 確定）: **画像/動画生成で seed を設定できる場合は、ローカルであれ API であれ、再現目的で明示的に固定したい時を除き、必ず毎回ランダムな seed にする。**

**Why**: 固定 seed ＋ 似たプロンプトは「別ペルソナのはずが同じ顔・同じ動画」を生む。2026-07-10 に実際に発生—NSFW auto パイプライン（`~/media-out/nsfw-auto/phase1_generate.mjs`）が z-image の seed を `--seed 8` にハードコードしていたため、名前・職業だけ違う別ペルソナ（山本彩乃→桜井彩子、どちらも29歳・黒ストレート・slim・正常位POV）が前回と**同一人物・同一動画**になった。名前/職業は z-image プロンプトに入らず、画像を決めるのは年齢/髪/体型/体位＋seed だけなので、seed 固定＋属性収束で顔がロックされた。ユーザー「こんなの当たり前」。

**How to apply**:
- **ローカル `gen_image.py` / `gen_qwen_edit.py`**: `--seed` 未指定なら自動でランダム seed を引き、引いた値をログに残す（＝毎回ランダム かつ 再現可能）に修正済み。旧 `gen_qwen_edit.py` は default=0 固定だった（＝同じ入力で毎回同じ出力）のを None→random に修正。**呼び出し側でハードコード seed を渡さない**。
- **クラウド `cloud_atlascloud.py` / `cloud_openrouter.py`**: `--seed` 未指定なら送信せずプロバイダ側でランダム。特定 seed を記録したいならラン毎に乱数を生成して渡す。
- **例外（固定してよい唯一の時）**: 同一人物を意図的に量産する（キャラの別カット等）ときだけ、人物ブロックを固定し seed も固定/明示管理する。「別人・別バリエーションが欲しい」局面での固定 seed は事故。
- パイプライン `phase1_generate.mjs` は `persona.frameSeed = 1+random(1e6)` をラン毎に生成し persona.json に保存（再現可能）＋ z-image に渡すよう修正済み。
- SKILL.md（video-media-studio）画像生成フロー冒頭に恒久ルールとして明記済み。

関連: [[nsfw-auto-pipeline-explicit-video.md]] [[gen-image-gpu-zombie-oom.md]] [[optimal-gen-models-table-and-new-model-eval.md]]
