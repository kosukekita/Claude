---
name: reference-selection-use-swipe-app
description: 参照画像の選択は必ず既存Tinder風swipeアプリ+リンクのみメールを使う。NSFW画像を自作グリッドでGmail等に載せない(プライバシー)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

★★恒久ルール（2026-07-13 ユーザー「今までにも何回もしてきたのでルール化」）: **参照画像(reference)を選ばせるときは、必ず既存の Tinder風 swipe Webアプリ + リンクのみメール を使う。自作のHTMLグリッドメール等で代替しない。**

**Why:** ①UXが確立済み（iPhoneで1枚ずつ○/✕スワイプ）②**★NSFW画像を第三者サーバ(Gmail等)に絶対載せない設計**＝メールには画像を入れず**アプリのリンクだけ**送る。画像は Tailscale 内の常駐アプリからのみ配信。

**How to apply（既存資産をそのまま使う。作り直さない）:**
- アプリ: `~/media-out/nsfw-auto/swipe_app.py`（Flask・systemd `nsfw-swipe.service` 常駐・`http://100.65.90.52:8710/`・Tailscale限定・PIN不要）。稼働確認 `systemctl --user is-active nsfw-swipe` / `curl -s -o /dev/null -w '%{http_code}' http://100.65.90.52:8710/img/1`。
- 手順: バッチフォルダに **`1.png..N.png`** ＋ **`manifest.json`**（`{"1":{"outfit":"...","view":"front","label":"..."},...}`）＋ **`persona.json`**（`name`必須）＋ **`status.txt`=`PENDING_REF_SELECTION`** を置き、**`swipe_state.json`を削除**。→ **`node send_swipe_link.mjs <batchFolder>`**（リンクをメール送信＋`latest_ref_batch.txt`を更新）。
- アプリは `latest_ref_batch.txt`→フォルダの `status==PENDING_REF_SELECTION` かつ `manifest.json` 有のときだけそのバッチを出す。○画像は `persona.name`(記号/空白除去)→ `pCloudDrive/Data/NSFW/AIgenerated/<name>/reference/<衣装(OUTFIT_JPに無ければ「その他」)>/ref_NN_<outfit>_<view>.png` に冪等cp。
- 詳細runbook: video-media-studioスキル `reference/tinder-swipe-selection.md`（再アーム＝`latest_ref_batch.txt`書換＋status戻し＋`swipe_state.json`削除）。
- 実例(2026-07-13): 長谷川バーテンダー6枚 → `~/media-out/nsfw-auto/manual_hasegawa_bartender/`（1-6.png+manifest+persona+status）→ send_swipe_link.mjs でリンク送信。

**★違反履歴（2026-07-13・二重の失敗）:** バーテンダー6枚を**自作HTMLの"Tinder風カード"グリッドで Gmail にインライン画像送信**した。(1)UI違反＝既存swipeアプリを使わなかった (2)**プライバシー違反＝NSFW画像を Gmail(第三者サーバ)に漏らした**。ユーザー「UIが全然違う」「ルール化しといて」。→ 以後この種の"参照を選ばせる"依頼は反射的に本ルール(swipeアプリ+リンクのみ)を適用する。

関連: [[image-cache-volatile-use-media-out]] [[gmail-send-smtp-attachments]] [[nsfw-auto-pipeline-explicit-video]] [[quality-over-speed-media-gen]]
