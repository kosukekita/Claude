---
name: feedback_uv_pip_cache_clean_safe
description: uv/pip の cache 削除は既存環境を壊さない。cacheと環境(venv)は別物。ディスク逼迫時の第一手
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7acc947b-9ceb-4ffe-8d93-cc9d81fe2eef
---

ディスク逼迫時、`~/.cache/uv`（数十GB規模になりやすい）と `~/.cache/pip` の削除は**環境を壊さず安全**。ユーザーが「消したら環境を再設定しないといけない?」と不安がる典型ポイント。

**Why:** cache（`~/.cache/uv`, `~/.cache/pip`）は「パッケージのDL保管庫」にすぎず、実際に使う環境（`~/xxx_venv/`, `~/anaconda3/envs/`, インストール済みライブラリ）とは別ディレクトリ。cacheを消しても既存環境は無傷で動き続ける。唯一の影響は「次に新パッケージを install するとき再DLで少し遅い」だけ。環境の作り直しは発生しない。

**How to apply:**
- 削除は `rm -rf` でなく**公式コマンド** `uv cache clean` / `pip cache purge` を使う（cacheだけを正しく消す正規手段）。
- 消す前に「本体・環境がcache外にある」ことを実測で示すと安心: `uv cache dir`（=消す対象）と `which uv`/venv実体（=cache外）が別であることを見せる。
- 2026-07-06 akitaken で uv(59G)+pip(17G) cache を削除し `/` 空きを 71G→124G に回復。既存の wan2_venv / anaconda3 / .totalsegmentator 等は無傷。関連: [[project_akitaken_remote_gpu_access]]
