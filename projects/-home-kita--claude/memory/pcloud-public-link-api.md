---
name: pcloud-public-link-api
description: pCloud公開リンク/画像直URLをAPIで発行する正しい方法(digest式の落とし穴)。~/media-out/model-compare/pcloud_link.mjs
metadata: 
  node_type: memory
  type: reference
  originSessionId: cee1ee3b-cf5e-48e5-82d4-e8881a33670e
---

pCloud(アカウント u879269j@gmail.com, **USリージョン api.pcloud.com**)の公開リンク・画像直URLをヘッドレスでAPI発行する方法。スクリプト: `~/media-out/model-compare/pcloud_link.mjs`(`--path '/Data/AIGenerated/file.png' [--direct]`、認証は環境変数`PCLOUD_USER`/`PCLOUD_PASS`)。

**2つの落とし穴(2026-06-24に解決、Codex確認)**:
1. **digest式が直感と逆**。正解は `passworddigest = sha1( password + sha1(lowercase(username)) + digest )`。`sha1(user+sha1(pass)+digest)`は誤り→`2000 Log in failed`になる。
2. **digest認証はauthトークンを返さない**。`userinfo?getauth=1`しても`auth`キーは無し(`result:0`だが`haspassword`等のみ)。→**authトークンを取ろうとせず、各APIコールにdigest認証パラメータ(username/digest/passworddigest)を毎回直接添える**(getdigestは使い捨て)。

**動く手順**:
1. `getdigest`でdigest取得(使い捨て、呼ぶ毎に新規)
2. `getfilepublink?username=...&digest=...&passworddigest=...&path=/Data/AIGenerated/file.png` → `result:0`なら`code`が返る → ページURL `https://u.pcloud.link/publink/show?code=<code>`(恒久)
3. `--direct`時: **`getfilelink?username=...&digest=...&passworddigest=...&path=/Data/AIGenerated/file.png`** → `hosts[0]+path`で画像直URL `https://ptokN.pcloud.com/.../file.png`(.png直接表示・**期限付き数時間**)。⚠️**`getpublinkdownload`は使わない**(code渡しで`7001 Invalid link 'code'`、linkid渡しで`1028 Please provide code`の矛盾エラー。pcloud_link.mjsの旧実装はこのバグで`--direct`が常に失敗していた→2026-06-24に`getfilelink`へ修正済み)。前回メールで届いた`ptok2.pcloud.com/...`URLの正体はこの`getfilelink`の直URL。

**重要事実**:
- パスワード `osakau19901214` は正しい(Google/Facebook連携が有効でも**ネイティブpCloudパスワードは存在**した)。最初の失敗はdigest式バグであってパスワードや2FAではなかった。
- リージョンはUS(`api.pcloud.com`)。EUは`2000`。スクリプトはUS→EUの順で自動判定。
- Gmail送信は別途 [[hf-weekly-model-watcher]] のSMTP(アプリパスワード`~/.config/gmail-smtp.pass`, smtps465)を流用。

関連: [[optimal-gen-models-table-and-new-model-eval]], [[image-cache-volatile-use-media-out]]
