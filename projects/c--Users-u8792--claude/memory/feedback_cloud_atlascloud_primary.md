---
name: cloud-atlascloud-primary
description: 2026-07-14 ユーザー指示「OpenRouterは今後使わない。クラウドはAtlasCloudに一本化」。Seedream/Seedance/wan-2.7 の指名クラウド経路は cloud_atlascloud.py
metadata:
  type: feedback
---

2026-07-14、ユーザーが「OpenRouter は今後使わないので、これからは AtlasCloud を使うようにグローバルに設定して」と指示（OpenRouter 残高 $0.29 で /images の与信が通らず生成停止したのが契機）。

**Why:** OpenRouter の残高を今後補充しない決定。課金レイヤーを AtlasCloud に一本化する。

**How to apply:**
- クラウドの指名経路（Seedream 画像・Seedance 動画・wan-2.7 NSFW動画）はすべて `video-media-studio/scripts/cloud_atlascloud.py` を使う。OpenRouter（`cloud_openrouter.py`）はユーザーが明示的に復帰を指示しない限り使わない。
- キーは `~/.config/atlascloud.key`。Linux（akitaken）と Windows 機の両方に配置済み（2026-07-14）。
- 参照画像つき画像生成は `bytedance/seedream-v5.0-pro/edit`（`--image` 複数可・最大10枚・`--size W*H` でアスペクト明示。2048*1152=16:9 は 1.5K 課金帯）。動画は `bytedance/seedance-2.0/image-to-video`（`--image`+`--last-image` でキーフレーム連鎖）。
- `--backend auto` の VRAM 階段（local→modal→fal→grok）には AtlasCloud を入れない方針は従来どおり（指名経路のみ）。
- 正本は video-media-studio SKILL.md（既定モデル表・OpenRouter 節の停止バナー・AtlasCloud 節を 2026-07-14 に更新済み）。
