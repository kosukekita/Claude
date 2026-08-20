---
name: minimax-h3-ref2va-usage
description: MiniMax-H3 Ref2VA(参照画像→動画)の実機成功構成 — 公式6セクションプロンプト形式・<Subject N>定義内引用で服/背景の焼き付き回避・APIのドット付きautogrowキー(2026-08-04)
metadata: 
  node_type: memory
  type: project
  originSessionId: 245c97d8-2c23-431f-91a9-69ed68025f10
  modified: 2026-08-04T10:34:53.862Z
---

MiniMax-H3 **Ref2VA bf16**（62GB・`minimax_h3_ref2va_bf16.safetensors`）を [[minimax-h3-local-comfyui-setup]] の環境で実機成功（2026-08-04・遥ペルソナ全裸ダンス・顔同一性◎・音声付き）。

**★プロンプトは公式 Full-Reference 6セクション形式が正**（`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`。ガイド全文写しは過去スクラッチパッドだが要点は下記）:
- **人物同一性だけ欲しい参照画像は独立 `<Picture N>` エントリにしない**（すると衣装・背景ごと焼き付く）。**`<Subject 1>` の定義内に「whose face comes from <Picture 1> and whose body proportions come from <Picture 2>」と出典引用**し、「Only her physical identity is referenced; the clothing in <Picture N> is not used」と明示 → retention_analysis で `partially_preserved - 服は破棄・着衣なし` と書く。実測で服（クリームニット）も背景（スタジオ白背景）も一切焼き付かず、寝室シーン全裸に完全置換された
- 参照画像の対応: `ref_image_0`→`<Picture 1>`, `ref_image_1`→`<Picture 2>`（type別1-based。画像→動画→音声の順で提示）
- detailed_description は生成タスクで350-500語・スタイル文を [Shot 1] より前に置く・カメラ/表情/音を時系列で

**API 投入の罠**: `MiniMaxH3ReferenceToVideo` の autogrow 入力はフラットキー `ref_image_0` だと execute() に素通りして TypeError。**`"ref_images.ref_image_0": ["node",0]` のドット付きパスが正解**（build_nested_inputs が dict に再構成）。

**★正式入口（2026-08-04 Codex 実装・検証済み）**: `video-media-studio/scripts/gen_minimax_h3.py`（t2v/i2v(FL2VA)/r2v(Ref2VA) 自動判定・17k+5検証・seed自動乱数・サーバ再利用/systemd-run起動・--dry-run/--free）。**NSFW 動画の既定モデルも MiniMax-H3 に変更済み**（★ユーザー決定 2026-08-04・SKILL.md 既定表が正本・wan-2.7-spicy はクラウド代替）。旧 `/data/kita/mmh3-setup/ref2va_submit.mjs` は開発時の使い捨て版。

**構成/実測**: FL2VA と同グラフで `MiniMaxH3ImageToVideo`→`MiniMaxH3ReferenceToVideo`（required に audio_vae 追加・出力は conditioning+latent で同じ）。768×1344/124f/20steps/CFGなし＝**21分**（FL2VA bf16 の20分とほぼ同じ・VRAM 44.5GB）。★**`ref_image_size` は既定の `match` ではなく `max` を使う**（ユーザー実測 2026-08-20 で訂正）。`match`（参照を生成画素面積へ縮小・速い）だと静止状態では似ていても**動き出した途端に顔が別人になる**ことがある。原因は入力段で顔の細部が落ちること。`max`（参照を高解像度のまま使う・遅い）に変えると元画像の顔の再現が明らかに強くなる。※2026-08-04 時点では「match で顔同一性は十分」と記録していたが、これは誤りだった。顔が崩れたときはプロンプトより先にここを疑う。

関連: [[minimax-h3-nsfw-and-int8-vs-bf16]]（bf16既定・NSFW無検閲）
