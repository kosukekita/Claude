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

## C(/home/kita)→D(/data/kita) 移動の定石（データはDへ、symlinkで繋ぐ）
`/home/kita/Jupyter_Lab/<proj>/` は **コード＋成果物**、`/data/kita/<proj>/` は **元データ**、という役割分担で二重に存在することが多い（同名でも中身は別）。容量を食うのは大抵/home側の巨大データ（動画・画像・DICOM）。これを/dataへ移し、元の場所にシンボリックリンクを張ると**コード・パス・環境変数を一切変えずに**Cを空けられる。
- **方式**: `mv "$SRC" "$DST"`（別FS間はコピー+削除を自動）→ 移動先存在＋元消失＋サイズ/ファイル数一致を検証 → `ln -s "$DST" "$SRC"`。失敗時は元を残す。**`rm -rf` は使わない**（後述フックでブロックされるし、mvなら不要）。
- **移動先が既存**なら衝突を避け、サブフォルダ単位で入れる（例 Chest2DXAは `Sumitomo/` だけを `/data/kita/Chest2DXA/Sumitomo` へ。既存のDICOM/JPEGと同居）。
- **実行上の注意（重要）**:
  - 保護フック `block-dangerous.ps1` が**ローカルのコマンド文字列**に対し `rm\s+-rf` や `/tmp` を検知してブロックする。リモート実行でも文字列に含めない。作業ディレクトリに `/tmp` を使わず `~/.cache/...` 等にする。
  - ヒアドキュメント(`<<'EOF'`)にスクリプトを書くと**日本語コメントが化ける**。スクリプトは**ローカルにASCIIで Write → `tr -d '\r'` でLF化 → `scp` で送る**のが確実。`bash -n` で構文チェックしてから `nohup ... &` 起動、完了は `.done` マーカーで判定。
- **実績（2026-07-06）**: uv+pip cache削除(53G) + Pig_Pain/High(101G,動画25本)・Videos(16G)・.totalsegmentator(14G)・Chest2DXA/Sumitomo(20G) をD移動。**`/` 使用率 92%→69%、空き 71G→273G**。残候補: Perimeter_AI(19G)/Common(14G)/Private(28G)/media-out(22G)。
