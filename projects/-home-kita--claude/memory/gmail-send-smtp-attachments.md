---
name: gmail-send-smtp-attachments
description: Gmail SMTPで(添付付き)メールを送る汎用手順。アプリパスワード+anaconda curl(smtps:465)。gws/MCPコネクタ不要
metadata: 
  node_type: memory
  type: reference
  originSessionId: 69e0d33d-bb56-4f32-a739-ff90d20e7612
---

このリモートPC(Linux, uid1002 kita)から**任意のメール(画像等の添付付き)を送る確立済みの手順**。`gws` CLI も claude.ai Gmailコネクタ(MCP)も使わず、Gmailアプリパスワード + SMTP で送る。これが一番速くて確実(MCPは未認証&添付対応が不確実、headlessで認証フローが面倒)。

**認証情報・送信パラメータ**
- アプリパスワード: `~/.config/gmail-smtp.pass`（16文字、`.trim()`して使う）
- 送信元/既定宛先: `u879269j@gmail.com`（EMAIL_FROM=EMAIL_TO）
- SMTP: `smtps://smtp.gmail.com:465`（SSL）。curlは **anaconda版 `/home/kita/anaconda3/bin/curl`**(SMTP+SSL対応)を優先、無ければ `/usr/bin/curl`。

**送信の核（curl 引数）** — raw MIME を stdin に流し込む:
```
curl --ssl-reqd --url smtps://smtp.gmail.com:465 \
  --user "u879269j@gmail.com:<pass>" \
  --mail-from u879269j@gmail.com --mail-rcpt <to> \
  --upload-file -    # ← MIME本文をstdinから
```
MIMEは自分で組む。日本語Subjectは `=?UTF-8?B?<base64>?=`、本文/添付は base64 + 76桁折返し、`multipart/mixed; boundary="..."`、添付は `Content-Type: image/png` + `Content-Disposition: attachment; filename="..."`。**改行は必ず CRLF(\r\n)**。

**実装の雛形**: `~/media-out/biz-cards/send_mail.mjs`（カード3枚を添付送信した実物。MIME組み立て～curl spawnSync まで完成形。流用可）。実行は **`/usr/bin/node`**(anaconda node 汚染回避)。成功時 `SENT OK ...` を出す。
**参考実装**: `~/media-out/hf-watcher/hf-watcher.mjs` の送信部(L360-402)が原型。テキストのみ通知ならこちら。

**Why**: 何度もやる定番作業なのに毎回手段を探していた。アプリパスワード+SMTPが既に用意されているのでこれが正解。MCP/gws を試すのは遠回り。

**How to apply**: 「メールで送って」「添付して送信」と言われたら、宛先を確認(既定は本人 u879269j@gmail.com)→ send_mail.mjs を雛形にMIMEを組み(添付ファイルパスとサブジェクト/本文を差し替え)→ `/usr/bin/node` で実行。新しい添付セットなら cards 配列やファイルリストだけ書き換える。

関連: [[hf-weekly-model-watcher]]（同じSMTP方式でGmail通知している既存システム） [[image-cache-volatile-use-media-out]]（送る生成物は ~/media-out に置く）
