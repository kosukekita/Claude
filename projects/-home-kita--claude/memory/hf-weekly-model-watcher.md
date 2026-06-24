---
name: hf-weekly-model-watcher
description: 週次でHF新着の画像/動画生成モデル(NSFW含む)を検知しGmail通知するsystemd --userタイマー。設定場所・閾値・送信の仕組み
metadata: 
  node_type: memory
  type: project
  originSessionId: cee1ee3b-cf5e-48e5-82d4-e8881a33670e
---

リモートPC(Linux, uid1002, akitaken)で週次にHuggingFaceの新着 画像/動画生成モデル(NSFW含む)を検知し、新着がある週だけGmailに通知する仕組みを構築済み。ターミナルが閉じても動く(`Linger=yes`)。

**ファイル構成**
- 本体: `~/media-out/hf-watcher/hf-watcher.mjs`（`/usr/bin/node` で動かす。anaconda汚染回避が必須）
- 状態: `~/media-out/hf-watcher/seen.json`（model `id` で差分検知。sha不可=毎commit変わる）
- ログ: `~/media-out/hf-watcher/hf-watcher.log` / 直近digest: `last-digest.txt`
- SMTP秘密: `~/.config/gmail-smtp.pass`（mode600, Gmailアプリパスワード16桁）
- ユニット: `~/.config/systemd/user/hf-watcher.{service,timer}`（月曜09:00, Persistent=true）

**設計判断**
- 通知チャネルはGmail一択が確実。Claude PushNotificationはヘッドレス不可(ライブのエージェントターン内のみ発火)。`notify-send`はベストエフォートのローカルping
- 送信は `curl smtps://smtp.gmail.com:465 --ssl-reqd --user user:apppass --upload-file -`（anaconda curlはSMTP対応。`LD_LIBRARY_PATH=""`で起動）
- HF API: `https://huggingface.co/api/models` を `pipeline_tag`×4(t2i/i2i/t2v/i2v) + NSFWタグ(`not-for-all-audiences`) + free-text search(nsfw系/family名) で走査。`sort=createdAt&direction=-1` + `Link: rel="next"` カーソルページング。`createdAt`は一覧レスポンスに含まれる
- 2段ゲート: (1)relevance=画像/動画生成のみ(uncensored LLMを除外) (2)notability=likes≥100 OR dl≥5000 OR trendingScore≥80。閾値は env `HFW_MIN_LIKES/HFW_MIN_DL/HFW_MIN_TREND` で調整可
- **ユーザー希望で「週1件あるかどうか」に超厳選**（2026-06-24）。実測分布: 7d gen模型約1100件 → likes≥10で25件 / likes≥50で4件 / likes≥100で3件 / likes≥200で0件。likes≥100採用で7日3件(Krea-2-Turbo等のメジャーリリースのみ、無名LoRA全除外)
- バイパス(主要familyのbase新規 / NSFW傾向)は **OFF がデフォルト**（`HFW_BYPASS=1` で再有効化）。超厳選ではNSFWも同一閾値=likes100超のバズったものだけ通知（NSFWは稀にしか出ない、ユーザー了承済み）
- trendingScoreはlikesと連動するので緩い閾値だと「1like=通知」になる。MIN_TREND=80で実体化

**運用コマンド**
- 手動ドライラン: `cd ~/media-out/hf-watcher && /usr/bin/node hf-watcher.mjs --dry-run --window-days 7`
- 即時1回実行: `systemctl --user start hf-watcher.service`
- 次回確認: `systemctl --user list-timers hf-watcher.timer`
- ログ: `journalctl --user -u hf-watcher.service -n 30`

**環境制約(再掲・重要)**: PATH `node`/`jq`/`python3`/`curl` は anaconda版で `libtinfo.so.6` 警告を出し汚染する。systemdユニットは `PATH=/usr/bin:/bin`, `LD_LIBRARY_PATH=`(空) を明示。関連: [[nsfw-models-chroma-noobai-wan-lora]]（HF探索TIPS・追跡family）, [[image-cache-volatile-use-media-out]]（durableデータは~/media-out）
