---
name: reference-image-gen-codex-vs-qwen
description: 参照画像が要る生成は SFW=Codex / NSFW=Qwen-Image-Edit を使う。FLUX.1 Kontextは不採用（ユーザー指示）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1fdf83d2-555b-436f-8214-734280823ac5
---

参照画像（reference / 人物の同一性を保ちつつ新ポーズ・新シーン）が必要な画像生成では、ユーザー指示により以下を使い分ける（2026-06-23 確定）:

- **通常（SFW）→ Codex (GPT Image)**: `codex exec --skip-git-repo-check --sandbox workspace-write -i <ref.jpg> < prompt.txt`。参照を最も忠実に再現。出力は `~/.codex/generated_images/<sid>/ig_*.png`。**トップレス/ヌード＋実在人物参照は拒否**（女性着衣・男性のみ上半身裸なら通る）。
- **NSFW → Qwen-Image-Edit-2509**: ローカル `video-media-studio/scripts/gen_qwen_edit.py --image <ref> --prompt ...`。`-i`相当の参照入力を持ち、人物同一性を保持。**縦長9:16(832x1216)でそのまま出る・コンテンツ制限なし・Apache-2.0商用可・1〜3枚の複数参照対応**（男性＋女性＋背景を別々に合成できる）。
- **FLUX.1 Kontext は使わない**（`gen_kontext.py`は残すが不採用）。品質自体は高い（質感リアル・忠実）が、ユーザーが「FLUX1はダメ」と明言。非商用ライセンスでもある。

**Why**: 実機比較（2026-06-23、男性リファレンスから「同一男性＋女性＋浴室ミラーセルフィ」を生成）で Qwen-Image-Edit は縦長そのまま出力＋忠実＋商用可、Kontext は1024正方形固定（要--size）かつ非商用。Z-Imageは参照入力非対応（text-to-imageのみ）なので参照が要る時は使えない。

**How to apply**: 「この人物を保ったまま別シーン」の依頼が来たら、NSFW判定して Codex か Qwen を即選択（Kontextや他を提案しない）。Qwen実行時の注意は [[face-crop-tool-and-ltx-offload]] と同じく **cu121 torch ピン必須**（gen_qwen_edit.py は `torch==2.5.1`+`torchvision==0.20.1` を `pytorch-cu121` index にピン済み。これを外すと cu128 が入りドライバ12.2で accelerator not found になる）。初回モデルDLは `HF_HUB_ENABLE_HF_TRANSFER=1` で安定。

関連: [[video-media-studio-skill]] [[face-crop-tool-and-ltx-offload]] [[grok-prompt-keep-japanese]]
