---
name: project_pcloud_rclone_ct_uzumasa
description: pCloud認証(rclone)手順とUzumasa頸部CT 195例の配置・DL先。ヘッドレスLinuxへのトークン受け渡し
metadata: 
  node_type: memory
  type: project
  originSessionId: 7acc947b-9ceb-4ffe-8d93-cc9d81fe2eef
---

pCloud を rclone で akitaken（ヘッドレスLinux）から使う設定と、Uzumasa（UZU）頸部CT 195例の在り処。関連: [[project_akitaken_remote_gpu_access]]

## pCloud認証（ヘッドレス機への標準手順）
モニタ無しのLinuxでbrowser認証できないので、**ブラウザのあるWindowsで `rclone authorize "pcloud"` を実行 → 出たトークンJSONをLinuxの rclone.conf に貼る**のが公式解。
1. Windows: `rclone authorize "pcloud"`（winget で `Rclone.Rclone` 導入。exe実体は WinGet\Packages 配下）。ブラウザでpCloudログイン→許可。ターミナルに `{"access_token":...}` が出る。
2. そのトークンをSSH越しにLinuxへ。**トークンはstdinパイプでリモートに渡し**、リモート側で `printf '[pcloud]\ntype = pcloud\nhostname = api.pcloud.com\ntoken = %s\n' "$TOKEN" > ~/.config/rclone/rclone.conf; chmod 600`。
3. **リージョン**: このアカウントは **US = `hostname = api.pcloud.com`**（EUなら `eapi.pcloud.com`）。`rclone lsd pcloud:` で疎通確認。
- ⚠️ トークンはpCloud全アクセス権を持つ機密。会話に出したら**pCloud設定→接続済みアプリでrclone失効**を推奨。一時ファイルは使用後 `shred -u`。
- `!` プレフィックス実行は**bash**に渡る（PowerShellではない）。`&`/`Tee-Object`等のPS構文は使わずbash構文で。Windowsパスはフォワードスラッシュ `/c/Users/u8792/...`。

## Uzumasa CT 195例の在り処（pCloud US）
- ルート `pcloud:Data/NAIST/Uzumasa/CT/` に mhd+raw ペア（MetaImage, 非圧縮）:
  - `CT_mhd2/` = 前半 **~110例**（UZU00001〜, **検証済みの00003/00005含む**）, **45.4 GiB**
  - `CT_mhd/` = 後半 **~85例**（UZU00120〜）, **35.6 GiB**
  - 合計 **~195例 / 81 GiB**
- 付随データ: `pcloud:Data/NAIST/Uzumasa/mhd_files/` にラベルmask（CT_label_msk等）、筋肉、DXA、`NAIST_CT_2025_merged data(_with_muscle_strength).xlsx` 等。
- DL先（2026-07-06実施）: **`/data/kita/Uzumasa_CT/{CT_mhd2,CT_mhd}`**。`~/.local/bin/rclone copy` を `--transfers 8 --checkers 16` でnohupバックグラウンド実行、ログ `~/rclone_logs/uzumasa_dl.log`、完了マーカー `~/rclone_logs/uzumasa_dl.done`。
