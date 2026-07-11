---
type: runbook
title: メール通知 + Tinder風スワイプ画像選択システム (nsfw-auto)
description: 毎朝の生成バッチから参照画像をiPhoneで○/✕選択する常駐Webアプリの構成・操作・運用・設計判断
tags: [nsfw-auto, swipe, tinder, tailscale, systemd, reference-selection]
---

# メール通知 + Tinder風スワイプ画像選択システム

毎朝の生成パイプラインが作る「参照候補18枚」から、ユーザーが **iPhoneで1枚ずつ ○(keep)/✕(reject)** して残す画像を選ぶ、セッション非依存の常駐Webアプリ。メールには18枚を添付せず「**スワイプアプリのリンクだけ**」を送る。○にした画像は衣装別 `reference/` フォルダに保存される。NSFW画像を第三者に渡さないため Tailscale 内に閉じる。

## アクセス (iPhone)
- URL: `http://<このマシンのTailscale IP>:8710/`（現状 `http://100.65.90.52:8710/`）
- 前提: iPhoneで **Tailscale ON**（同一tailnet）。アプリは Tailscale IP のみに bind → tailnet 外からは到達不可。
- **PIN不要**（`~/.config/nsfw-swipe.pin` があれば PIN 認証、無ければ認証スキップ。tailnet 限定 bind が認証境界）。
- URLは毎朝メールで届く（件名「【スワイプで選択】r2v参照18枚 - <名前>」）。
- Safari が https に昇格すると繋がらない → `http://` を明示。

## 使い方 / 保存先
1枚ずつ表示 → **右スワイプ/○ = keep、左スワイプ/✕ = reject、↶ = Undo** → 全部投票後、オレンジの「**確定して保存**」。keep にした枚数だけ保存（枚数自由）。
保存先: `~/pCloudDrive/Data/NSFW/AIgenerated/<ペルソナ名(記号除去)>/reference/<衣装>/ref_NN_<outfit>_<view>.png`（衣装 = 浴衣/シャツ/水着、該当外は その他）。`cp` で冪等コピー。確定と同時に `status.txt=DONE`。

## 構成ファイル / サービス
| 役割 | 実体 |
|---|---|
| 生成 + リンク通知 | `~/media-out/nsfw-auto/phase1_generate.mjs`（systemd `nsfw-phase1.timer` 毎朝 07:00 JST） |
| リンクメール | `send_swipe_link.mjs`（`http://<ts-ip>:8710/` を送信し `latest_ref_batch.txt` を書く） |
| スワイプアプリ | `swipe_app.py`（Flask / systemd `nsfw-swipe.service` 常駐・`Restart=always`・`ExecStartPre`でtailscale IP待ち） |
| (旧)番号返信poller | `phase2b_refselect.py`（無効化。`status==PENDING`のときだけ動くフォールバック） |

## ★バッチが表示される条件
`current_batch()` は `latest_ref_batch.txt` が指すフォルダの `status.txt` が **ちょうど `PENDING_REF_SELECTION`** で、かつ `manifest.json`（番号→衣装/向き）があるときだけ、そのバッチを出す。それ以外は「選択待ちのバッチはありません」。

## 運用手順（ホスト側ファイル操作。実装変更ではない）
### 空表示の切り分け
「選択待ちなし」= PENDINGバッチが無い（未生成 or 既に選択完了で DONE）。多くは異常でない。確認: `cat latest_ref_batch.txt` → その `status.txt`。`DONE` なら選択済み。

### DONE済みバッチを選び直す（再アーム）— UIに再オープン導線は無い
1. `latest_ref_batch.txt` が対象バッチを指すことを確認。
2. `<batch>/status.txt` を `PENDING_REF_SELECTION` に書き換え。
3. **`<batch>/swipe_state.json` を削除**（★必須。`done:true` のままだと `/api/vote` が 409 を返し、UIが即「全枚数チェック済み」に飛んで再選択できない）。
4. iPhoneでアプリを再読み込み。

### 到達できない時
`ss -tlnp | grep 8710`（Tailscale IPでListenか）/ `systemctl --user is-active nsfw-swipe` / `tailscale status`（iPhoneがtailnetにいるか）。ufw/firewalld は無効前提。

## 設計判断（なぜこの形か）
- **Tailscale限定Webアプリ（Telegram不採用）**: NSFW画像を第三者サーバ（Telegram/imgur/クラウドUI）に載せない。tailnet内に留め暗号化直結でiPhoneに配信。**Telegramは画像をTelegramサーバへアップロードするので不採用**。Cloudflare公開トンネルも画像がCloudflareを経由するため次点。
- **セッション非依存**: systemd --user + `loginctl enable-linger kita`（誰もログインしていない朝でも常駐）。起動時に **Tailscale IPを自動採用**（IP変化に自己修復。unitにIPを固定しない）。
- **人間チェックポイント**: 自動生成 → 人間が○/✕で選ぶ。loop-engineeringの「実行はループ、決定は人間」を担保する要。
- **status.txt で排他**: swipe確定=DONE / phase2b(番号返信)=PENDING時のみ動作 → 先に確定した方が勝ちで**二重保存しない**（TOCTOU回避のため書き手は swipe に一本化推奨）。
- **ペルソナ名は一意**: phase1が姓×名プール + `used_names.json` + 既存pCloudフォルダ走査で重複回避（フォルダ衝突＝上書き防止）。
- **元画像 `1_frame_nude.png` がマスター**: z-imageの1枚から Qwen-Edit で参照18枚も動画も派生。**削除・上書き厳禁**（persona.txt にも明記される）。

## 落とし穴
- **2GPU並列は `{ }` で囲む**: `cd && source && ( leg0 ) & ( leg1 ) & wait` はシェル優先順位で leg1 が cd/source されず環境喪失で全滅。`{ ... }` で包む（phase1実装済）。`wait` は exit 0 を返すので**成果物の個数で成否判定**する。
- **`latest_run.txt` と `latest_ref_batch.txt` は別物**: swipe は後者のみ参照。前者は旧フローの名残。
- **状態ファイル**: 投票は `<batch>/swipe_state.json`（`{votes,done}`）。書き込みはロック + 一意tmp名 + atomic replace。
