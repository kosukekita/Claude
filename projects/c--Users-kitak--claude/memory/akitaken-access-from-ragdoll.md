---
name: akitaken-access-from-ragdoll
description: このPC(ragdoll)からリモートGPU機akitakenへの接続状況 — Tailscale復旧済み(key expiry無効化2026-08-04)、SSH鍵は未登録で登録待ち
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e37da7c-a675-4ad0-b8b0-4c6c537a53a2
  modified: 2026-08-04T08:30:58.863Z
---

リモートGPU機 **akitaken**（Ubuntu 24.04, user=`kita`, Tailscale `100.65.90.52`）への、このPC（ragdoll, Windows）からの接続状況。akitakenの環境詳細（GPU/ディスク/rclone）は別スラグの記憶 `projects/c--Users-u8792--claude/memory/project_akitaken_remote_gpu_access.md` にある（desktop機視点）。

## Tailscaleノードキー期限切れ事件（2026-08-04 解決）

- 症状: `ssh akitaken` がタイムアウト → `tailscale ping` で「**peer's node key has expired**」。
- 解決: Tailscale管理コンソール（https://login.tailscale.com/admin/machines）で該当機の ･･･ メニュー → **Disable key expiry**。機体がオンライン（Connected）のままなら**再認証不要で即復旧する**（実測: akitaken・kosuke-20241029 の2台で確認、ユーザー承認済み）。
- 以後 akitaken と kosuke-20241029 は key expiry 無効（サーバー用途の定石）。iphone172 は期限切れのまま放置（端末上で再認証すればよい）。
- 接続は DERP(tok) リレー経由（direct connection 未確立だが実用上問題なし）。

## SSH認証（★未解決 → 登録後にこの節を更新）

- ragdoll の鍵 `~/.ssh/id_ed25519.pub`（`kitak@ragdoll`）は akitaken の `authorized_keys` に**未登録**。BatchMode では Permission denied になる。
- 登録済みなのは kosuke-20241029 の鍵（`u8792@kosuke_20241029`）のみ。
- パスワード認証での登録は**失敗**（2026-08-04、IMEオフ確認済みで3回×2セット拒否 → ユーザーの入力パスワードが `kita` のものと不一致。パスワード認証自体はsshd側で有効）。
- 残る登録経路:
  1. **kosuke-20241029（鍵登録済みのWindows機）から追記**（パスワード不要・推奨）: `ssh kita@100.65.90.52 "echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJtQ7+RktzkLGohhtX63o7jH8ggdmJGODo1/byr5iI3t kitak@ragdoll' >> ~/.ssh/authorized_keys"`
  2. akitaken 本体で `sudo tailscale set --ssh`（Tailscale SSH有効化・恒久策。以後どのPCも鍵管理不要）。
- 豆知識: VS Codeターミナルの日本語IMEはWin32 API（imm32 `WM_IME_CONTROL`/`IMC_SETOPENSTATUS`）でPowerShellから強制OFFにできる（実証済み）。

## 経路の知見（他経路が全滅だった記録）

- desktop-5c4jvob / kosuke-20241029 とも port 22 閉 or オフラインで踏み台不可。
- akitaken の公開ポート（Tailscale面）: 8000=DICOM to Segmentation App、8080=RA治療反応率推定システム（どちらもuvicorn・シェル実行経路なし）。Jupyter/ollama/LiteLLM(4000)/ComfyUI は localhost バインドで外から見えない。
- agmsg はこのPC未導入（`~/.agents` なし）。
