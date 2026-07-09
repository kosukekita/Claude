---
name: feedback_character_sheet_no_text_no_crop
description: リファレンスシート作成の固定ルール2点（文字なし・元画像からアップ切り取り禁止）。ユーザー確定2026-07-07
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a913a1d6-25fa-4312-9f85-a1f61f737573
---

リファレンスシート（キャラクターシート／モデルシート）を作るときの固定ルール（ユーザー確定 2026-07-07・以後確認不要）:

1. **シートに文字・ラベルを一切入れない**。タイトル・パネル名・日本語ラベル・英語ラベルすべて禁止。画像パネルだけで構成（罫線・ボックスの区画整理は可）。
2. **元画像（参照シート）から顔アップ・表情パネルをクロップして流用しない。全パネルを生成で作る**。顔アップ・横顔・斜め・表情差分も参照条件生成（Qwen-Image-Edit / FLUX.2-dev editing / FLUX.1 Kontext / Codex `-i`）で新規に描き起こす。

**Why:** ①ラベルは資料用途（v2v `--face-ref` / i2v `--image` の素材切り出し元）に不要で文字化け・英語混入の事故源。パネルの意味はレイアウト位置で自明。②参照アップの切り貼りは、元の着衣（襟等）写り込み・全身生成パネルとの画質/ライティング不整合・元シートに無いビューを埋められない、という問題を起こす。全パネルを同一設定で生成すれば統一感が出て一貫する。

**How to apply:**
- 正本は video-media-studio の `reference/character-sheet-template.md` 冒頭「★固定ルール」節（本節が他記述より優先。プロンプトテンプレ内の「日本語ラベルのみ入れる」は上書き無効化済み）。
- 検証で「文字が入っていないか」を必ずチェック（入っていたら再生成）。
- 実装（PIL 合成）でもタイトル・ラベルの描画コードを入れない。素材は各ビューを個別生成→グリッド合成。

関連: [[project_nude_reference_sheet_hayase]] [[feedback_image_default_photoreal]] [[feedback_flux2_reference_image_editing]]
