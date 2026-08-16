---
name: minimax-h3-single-image-edit
description: MiniMax H3 を単画像編集モデルとして使うレシピ（NSFW可・実機成功 2026-08-16・裸キャラシート実証）
metadata:
  type: project
---

# MiniMax H3 単画像編集（Reddit r/StableDiffusion 1vo1ab3 レシピのローカル移植・実機成功 2026-08-16）

**H3 で「参照画像→編集済み1枚絵」ができる。NSFW 完全対応（無検閲TEのまま）。**
実証タスク: 中島遥の正本キャラシート（着衣3面）→ 裸キャラシート（同レイアウト・同一人物・1920×1088）。
初回サーバ起動+モデルロード込み約3分、サンプリング自体は数十秒（8 steps）。

## 構成（すべて導入済み）
- **DiT**: `minimax_h3_hybrid_fl2va_ref2va_b25-49.safetensors`（21GB・smhfacct。FL2VAの画質×Ref2VAの参照追従のハイブリッド）→ diffusion_models/
- **VAE**: `minimax_h3_t1_image_vae_step1597.safetensors`（5.2GB・Mamad8。単画像用 t=1。通常VAE+5フレームだとボケ、フレーム抜きはグリッドノイズ）→ vae/。**参照エンコードとデコードの両方をこれにする**（audio VAE は接続だけ残す）
- **LoRA**: turbo 8step `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` @0.75 → ThisIsFine `MaxiMin-HHH-R2V-ThisIsFine_LoRA_V0_1.safetensors` @1.0 のチェーン → loras/
- **sampler**: sa_solver / simple / 8 steps / CFG1（BasicGuider）
- **★1フレームパッチ**: `/data/kita/ComfyUI-mmh3/comfy_extras/nodes_minimax_h3.py` に4点適用済み
  （align_frame_count に n<=1→1・video_latent_t に <=1→1・max(5,→max(1,・Int入力 min=1/step=1）。
  バックアップ `nodes_minimax_h3.py.orig-pre-1frame`。**ComfyUI 更新で消えるので更新後は再適用**。
  0.33 対応版パッチは pastebin iVXLjGZL（0.32版は d75sR1s8）。

## 実行手順
1. `gen_minimax_h3.py --dry-run` でベースグラフを出す（`--length 5`・768×1344 で通してから JSON 側で差し替え。
   ラッパーは length=1 と 1920×1088 を CLI 検証で弾くため）
2. 差し替え4点: VAE名→t1 / sampler→sa_solver / LoRA 2枚チェーン挿入（[1,0]参照を末尾LoRAへ付け替え）/
   出力を SaveImage 化（VAEDecodeAudio/CreateVideo/SaveVideo を除去）+ width/height/length を 1920/1088/1 に
3. 参照画像は POST /upload/image → LoadImage 名を差し替え → POST /prompt → /history ポーリング
4. 使い捨てスクリプトの原本: セッション scratchpad `submit_h3_image_edit.py`（恒久化するなら Codex/agy に
   gen_minimax_h3.py への `--image-edit` モード追加を委譲する）

## プロンプトの型（実証）
Ref2VA 6セクション（h3-prompt-writing スキル準拠）。detailed_description に
`single completely motionless photorealistic still frame` を明示。同一性は `<Subject 1>` 定義内で
`<Picture 1>` 出典引用+服の破棄明示（[[minimax-h3-ref2va-usage]] と同じ）、レイアウト転写は `<Picture 1>` を
composition anchor として別立て・retention_analysis で partially_preserved を明記。

## 結果メモ（1発目）
- 3面レイアウト・スタジオ背景・同一人物性・ホクロ・無検閲ヌード描写すべて成立。グリッドノイズなし・シャープ
- 軽微な逸脱: バストがペルソナ(G)よりやや控えめ／陰毛指定が薄め描写。強調するならプロンプトで反復強調
- Reddit 出典: 元投稿はキャラシート/ストーリーボード/服・体型・年齢・アングル替え/深度ベース再ポーズも実証。
  コメント知見「解剖が苦手な部位は追加参照画像を渡して 'use that in its place' で毎回正しくなる」
