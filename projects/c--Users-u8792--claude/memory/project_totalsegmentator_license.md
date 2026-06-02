---
name: project_totalsegmentator_license
description: TotalSegmentatorのアカデミックライセンス取得済み。番号はconfig.jsonに保存、追加タスクが利用可能に
metadata:
  type: project
---

# TotalSegmentator ライセンス（アカデミック）

2026-06-02 にアカデミックライセンスを取得（登録メール: kita.kosuke@naist.ac.jp）。これにより非オープンの追加タスク（heartchambers_highres / tissue_types / tissue_4_types / vertebrae_body / brain_structures / appendicular_bones / thigh_shoulder_muscles / coronary_arteries / aortic_sinuses ほか、MR版含む）が利用可能になった。

## 有効化と保存場所
- 有効化コマンド: `totalseg_set_license -l <ライセンス番号>`（番号は秘密情報。ここには記載しない）
- 保存先: `C:\Users\u8792\.totalsegmentator\config.json`（JSONキー `"license_number"` に平文保存）。**別マシンへの引き継ぎはこのファイルを各自で設定/コピーする。番号はメモリやGitに置かない**
- 既定パスは `C:\Users\u8792\.totalsegmentator`（= Path.home()/.totalsegmentator）。環境変数 `TOTALSEG_HOME_DIR` で変更可
- 確認コマンド: `totalseg_get_license`

**Why:** 一度実行すればマシン上でずっと有効に見えるのは、OSの認証ストアではなく上記の単なるJSONファイルから毎回読み出すため。秘密情報なのでメモリ本文には番号を残さない方針。

**How to apply:** 追加タスクを使う前提として totalsegmentator 本体のインストールと、上記コマンドでのライセンス設定が必要。番号が必要なときは取得元（登録メール）を参照。
