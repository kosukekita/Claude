---
name: hf-model-cache-do-not-delete
description: ★HFモデル本体は消すな。毎朝の自動生成(nsfw-phase1)が--offlineで依存。2026-07-18にディスク掃除で.cache/huggingface削除→障害。保護場所へ移設済み
metadata: 
  node_type: memory
  type: project
  originSessionId: a2794230-5b57-41fe-9266-054958a3de72
---

★2026-07-18 実障害: ディスク掃除（"public_cleanup"・一度きりの手動/エージェント操作）が
`/data/kita/.cache/huggingface`（1.3TB, HFモデルキャッシュ全体）を「再DL可能なキャッシュ」と判断して削除。
その中に毎朝06:00の自動生成パイプライン `nsfw-phase1.service`（`phase1_generate.mjs`）が
`--offline` で必須依存する **`Tongyi-MAI/Z-Image-Turbo`(33GB)** と **`Qwen/Qwen-Image-Edit-2511`(57GB)** が含まれ、
翌朝(07-19)フレーム生成が `FileNotFoundError: .../hub` → grok委譲(無人で不能) → PNG未生成 → `fail("frame")` exit 1。
**失敗経路はメールを送らないので沈黙**し、ユーザーは「朝の画像もメールも来ない」と気づいた。

**Why（恒久教訓）:** 「cache」という名前でも、**--offline の本番パイプラインが依存するモデル本体は"消してよいキャッシュ"ではない**。
ディスクを空ける掃除で HFモデルを消すと、翌朝の無人ジョブが静かに壊れる。

**How to apply（ディスク掃除・キャッシュ破棄をするとき必ず守る）:**
- **`/data/kita/models/huggingface/` は削除禁止**（運用資産）。ここに `.do-not-delete` マーカーあり。掃除対象に入れない。
  - ここが HFモデル本体の**新しい保護場所**（2026-07-19 に `.cache/huggingface` から移設）。`~/.cache/huggingface` は
    このディレクトリへの symlink（張り替え済み）。realpath が `.cache` 配下でなくなったので、cache掃除で消えにくい。
- ディスクを空けたいときの対象は **実験用キャッシュ**（`~/.uv_cache`・`~/.pcloud/Cache`・`~/.cache/*`(hf除く)・`ltxdl_tmp` 等）に限る。
- **モデルディレクトリ（*/hub/models--* を含む場所）を消す前は必ず止まって確認**。特に nsfw-phase1 / video-media-studio が --offline で使うモデルは消さない。
- 掃除は dry-run 既定・削除前に df とトップレベルをmanifest化（今回の public_cleanup はmanifestは残したが確認ゲートが無かった）。

関連: [[nsfw-auto-pipeline-explicit-video]] [[pcloud-cache-wipe-playbook]] [[video-media-studio-skill]] [[file-revert-prevention-playbook]]
