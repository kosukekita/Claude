---
name: haruka-shower-pipeline
description: 毎晩の遥シャワー動画パイプライン（稼働中）の構成と、2026-08-18に直したQC誤判定・mp4_path欠落の罠
metadata:
  type: project
---

# haruka-shower（毎晩の遥30秒シャワー動画・**稼働中**）

`~/media-out/haruka-shower/`。**[[haruka-nightly-resume]] とは別物**（あちらは3分動画でタイマー無効のまま）。
こちらが実際に毎晩回っているパイプライン。

## 構成
- systemd --user timer 3本: **gen 01:00**（`shower_pipeline.py`）→ **mail 06:00**（`send_shower_mail.py`）
  → **autofix 06:25**（`autofix_runner.sh`）
- 生成は `gen_minimax_h3.py` 直呼び（Ollama 不使用）。**362フレーム×2ショットを連結して30秒**・
  768×1344・steps30。1ショット約2時間＝1晩で約4時間
- 参照は `~/media-out/haruka-daily/runs/<stamp>/angle1_front.png` の**1枚参照モード**
- 部屋スタイル・演目は台帳（`ledger_XX`）からランダム選択
- QC: 尺 / 音声実在 / 顔照合（閾値0.45）/ モザイク。メールは**URLのみ**（NSFW本文なし）・宛先 u879269j

## ★2026-08-18 に直した2つの罠（同型の再発に注意）

**罠1: ArcFace顔照合が「顔が小さい・非正面」の演目で良品を落とす。**
実害: 演目 `ledger_02「顔を仰いで口元から水滴をこぼす」`（全身の引き画・上向き・濡れガラス越し）で
face sim **0.1234**（良品実測は0.5866）→ QC FAILED。動画は目視で完全に良品だった。
**修正**: 全フレーム平均をやめ、**顔が画面面積の1%以上 かつ yaw/pitch ±30°以内のフレームだけ**を選び、
その**最大値**で判定。適合フレーム0枚なら `face_check="skipped_no_frontal_face"` で**落とさない**。
閾値0.45は据え置き（比較対象が代表値に変わっただけ）。正面大顔があれば従来どおり照合する（検証0.9901）。
★**残リスク**: 最後まで正面を向かない演目では顔QCが常にスキップ＝別人化を検出できない。承知の上の割り切り。

**罠2: 失敗時に `mp4_path` が状態に残らず、メールが動画を見つけられない。**
`shower_pipeline.py` は成功パスでしか `run_meta["mp4_path"]` を書かず、QC失敗時は書かなかった。
`send_shower_mail.py` は `state["mp4_path"]` だけ見るので**アップロードを一度も試さず**、
「動画リンク（動画ファイルなし、または pCloud アップロード失敗）」と誤報した（pCloud認証もスクリプトも正常だった）。
**修正**: mp4_path の記録を**QCより前**に前倒し＋メール側に `run_dir/final_video.mp4` フォールバック探索を追加。
文面も「（動画ファイルなし）」と「（pCloud アップロード失敗）」に**分離**したので次回は原因が一目で分かる。

## 運用メモ
- 手動アップロード: `set -a; . ~/.config/pcloud-link.env; set +a;`
  `node ~/media-out/haruka-nightly/bin/upload_pcloud.mjs <mp4>` → 公開URLを stdout に出す
- メールの検証は必ず `send_shower_mail.py --dry-run`（実送信しない）。state パスは絶対パス直書きなので、
  別状態で試すときは**モジュールを import して `LATEST_STATE_FILE` を差し替える**（ライブの latest.json を触らない）
- `short_test/run_short_test_243.py` が別途 GPU を使う開発用短尺テスト。朝の失敗と混同しない
- 関連: [[minimax-h3-local-comfyui-setup]] [[minimax-h3-ref2va-usage]] [[haruka-nightly-resume]]
