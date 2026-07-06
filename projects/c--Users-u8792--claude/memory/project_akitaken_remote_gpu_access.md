---
name: project_akitaken_remote_gpu_access
description: リモートGPU機 akitaken への接続方法と環境（Tailscale+SSH鍵、RTX A6000×2、/data 19TB、rclone配置）
metadata: 
  node_type: memory
  type: project
  originSessionId: 7acc947b-9ceb-4ffe-8d93-cc9d81fe2eef
---

リモートGPU機 **akitaken**（Ubuntu 24.04, user=`kita`）への接続・作業環境。TotalSegmentator等のGPU処理やpCloudからのデータDLはこの機で行う。関連: [[project_totalsegmentator_license]] [[project_pcloud_rclone_ct_uzumasa]]

## 接続（このWindows desktop-5c4jvob から）
- **Tailscale経由**でSSH到達。akitaken = `100.65.90.52`（tailnet名 `akitaken.tail7c9257.ts.net`）。
- **鍵認証確立済み**: Windowsの `~/.ssh/id_ed25519.pub`（`ssh-ed25519 AAAA...LjVt u8792@kosuke_20241029`）を akitaken の `~/.ssh/authorized_keys` に登録済み。`ssh -o BatchMode=yes akitaken '...'` でパスワード無しで通る。
- **sudoはパスワード必須**（BatchModeでは打てない）→ 管理者権限が要る操作は避け、ユーザーローカル（`~/.local/bin` 等）で完結させる。

## 環境
- GPU: **RTX A6000 ×2**（各48GB, 49140 MiB）。
- ディスク:
  - `/`（sda4）876G, **逼迫しやすい**（ホーム `/home/kita` が443G占有）。CドライブにDLしない。
  - **`/data`（sdb1）19T, 空き8.8T** ← 大容量データはここ。ただし `/data` 直下はroot所有で書けない。**書けるのは `/data/kita/`**（kita所有、既存プロジェクト多数）。
  - `/home/kita/pCloudDrive` に **pCloudが常時マウント済み**（18T）。rclone を使わずここ経由でも読める。
- rclone: **`~/.local/bin/rclone`**（v1.74.3, sudo無しでユーザーローカル導入済み）。PATH非対話には乗らないので**絶対パスで呼ぶ**。設定は `~/.config/rclone/rclone.conf`。
- uv: `~/.local/bin/uv`。pip: `~/anaconda3/bin/pip`（anaconda3同梱）。非対話SSHではPATHに無いので絶対パス or `bash -lic` で。

## ディスク掃除の定石（Cドライブ逼迫時）
- `~/.cache/uv`（数十GB規模）と `~/.cache/pip` が主犯になりやすい。**`uv cache clean` / `pip cache purge`（公式コマンド）で安全に削除**でき、既存venv・インストール済み環境は壊れない（cacheと環境は別物）。詳細: [[feedback_uv_pip_cache_clean_safe]]
- 2026-07-06に uv+pip cache を削除し `/` 空きを 71G→124G に回復した実績。
