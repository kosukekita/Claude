---
name: pcloud-cache-wipe-playbook
description: pCloudクライアントのアップロード詰まりとキャッシュ破棄の安全手順。キャッシュ破棄は未同期データを黙って捨てる（457件消失を実測→退避で全復元）
metadata: 
  node_type: memory
  type: reference
  originSessionId: d067b6fc-7d1c-46e7-adf2-f2c98dec84b1
---

**pCloud Linux クライアントのアップロード詰まりと、キャッシュ破棄の安全手順**（2026-07-08 akitaken 実障害で確立。[[sheet-factory-daily-sfw-loop]] の同期検証実装の背景）。

- **症状**: FUSEマウント正常・小ファイル（数KBのmd等）は同期するのに、**数MB以上のファイルだけ無言でサーバー未到達**。長期常駐（数ヶ月）で発生。「FUSEに書けた＝クラウドに届いた」は成り立たない。
- **診断**: ①pCloud API listfolder でサーバー側と突合（digest認証、creds=`~/.config/pcloud-link.env`）②`~/.pcloud/data.db` の **fstask テーブルがアップロード待ちキュー**（type3=新規アップロード, type5/6=git tmp→rename対, type9=既存修正。folder テーブルへ WITH RECURSIVE でパス復元可）。sqlite3 は anaconda 版を db のコピーに対して使う。
- **★最重要: キャッシュ破棄（rm -rf ~/.pcloud/Cache）は未同期データを黙って捨てる**。再起動後キューは数分で「消化」されるが、それは**アップロードではなくタスク破棄**（実測: 457/459がサーバー消失）。**必ず先に退避**する: 未同期リスト（API突合＋fstask）→ マウントからローカルへコピー → 停止→Cache削除（data.dbは残す=認証維持）→ 再起動 → `checksumfile`(sha1)で全件検証 → 欠落を `uploadfile` API で復元。
- **停止/再起動の注意**: pcloud.bin は SIGTERM を無視することがある→ kill -KILL → `fusermount -uz`（古いシェルがcwd保持でbusyになるためlazy必須）。**AppImage 再起動は `env -i` でクリーン環境必須**（anaconda LD_LIBRARY_PATH 汚染で `libgdk_pixbuf: g_once_init_leave_pointer` エラーで起動失敗する。soffice/bash と同根）。リモートなら DISPLAY/XDG_RUNTIME_DIR/DBUS_SESSION_BUS_ADDRESS を `/proc/<pid>/environ` から採ってから殺す。
- **★デーモン死亡時の復旧（2026-07-09 akitaken 実障害）**: 症状は `ls ~/pCloudDrive` が「通信端点が接続されていません」（FUSE マウントは残るが pcloud.bin が居ない）。手順: ①`fusermount -uz ~/pCloudDrive` で stale マウントを剥がす ②**`xvfb-run` 上で AppImage を起動**する。pCloud は Electron なので実 X ディスプレイが要る。**ヘッドレス/SSH セッションには使える DISPLAY が無い**（`:0` はあっても Xauthority が通らず `Missing X server or $DISPLAY` で即終了、`:10.0` は ssh 転送で消えている）:
  ```bash
  env -i HOME=$HOME XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus PATH=/usr/bin:/bin \
    setsid xvfb-run -a -s "-screen 0 1280x800x24" ~/Downloads/pCloud.AppImage &
  ```
  GPU/libnotify の ERROR ログは出るが無害。`mount | grep pCloud.fs` と `ls ~/pCloudDrive` で復旧確認。
- **効果**: キャッシュリセット後はクライアント自身のアップロードが復活（2MBテスト・2.3MBシートとも数十秒で到達）。退避コピーは `~/media-out/pcloud-rescue/`（確認後に削除可）。

**Why**: pCloudはアップロードキューの実データをCacheに置くため、Cache破棄=キュー実データ破棄。クライアントはエラーも出さずタスクを落とす。
**How to apply**: pCloud同期がおかしい時はまず fstask 件数とAPI突合で「何が未同期か」を確定し、退避してから触る。重要ファイルのpCloud書き込みは書きっぱなしにせずAPI検証を入れる（sheet-factoryは実装済み）。
