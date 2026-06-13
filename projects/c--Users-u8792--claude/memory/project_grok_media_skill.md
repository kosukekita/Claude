---
name: project_grok_media_skill
description: grok-mediaスキル作成（2026-06-13）。xAI公式Grok Build CLIにX Premium+ OAuthで委譲し画像/動画生成。Web情報と違う実機事実が多数
metadata:
  type: project
---

`skills/grok-media/` スキルを作成した経緯と、実機検証で判明した「Web情報と食い違う事実」。

## 結論（採用した土台）
xAI **公式 Grok Build CLI**（`~/.grok/bin/grok.exe`, v0.2.51）に委譲。**X Premium+ の OAuth ログインだけで画像・動画とも生成成功**（API キー従量課金は不要）。codex-consult 型の外部CLI委譲スキル。`grok -p` ヘッドレスで自然言語指示→内蔵メディアツールが発火。

## Web情報が間違っていた点（実機で訂正）
- **メディアツールの実名**（grok本人が回答）: `image_gen` / `image_edit` / `image_to_video` / `reference_to_video`。Web が言う `generate_image`/`generate_video` は誤り。
- **text-to-video 専用ツールは存在しない** → 「テキストから動画」は image_gen で画像→ image_to_video で動かす **2段**。
- **出力先は cwd 直下ではない**。`~/.grok/sessions/<URLエンコードしたcwd>/<session-id>/{images,videos}/N.{jpg,mp4}`。Web の `.grok/generated-media/` は誤り。
- **"$0.05/秒" は別経路（xAI Imagine API・APIキー課金）の価格**で、本スキル（サブスク枠CLI）には無関係。

## ハマりどころ（実機）
- **login は手元の実ターミナルで** `grok login --device-auth`。Claude Code の `!`プレフィックスや非対話実行では OAuth が完走せず auth.json が作られない。
- **生成は mktemp の空ディレクトリで**。既存プロジェクト直下だと grok が周辺探索して `Auth(AuthorizationRequired)` で生成手前で落ちる。
- `Auth(AuthorizationRequired)` の ERROR 行は**毎回出るが致命的ではないノイズ**。ファイルが出ていれば成功。
- **`-p` の応答テキストが空でもファイルは生成済み**のことがある。回収は `grok -r -p "absolute path of the media you just generated?"` で grok 自身に絶対パスを聞くのが確実。
- 所要時間: image_to_video で約50秒（非同期）。run_in_background 推奨。

## 誤って入れて撤去したもの
最初 superagent 製 `grok-dev`（npm/bun, コマンド名 `grok` が公式と衝突, APIキー課金型）を入れたが、X サブスクで動かないため `bun remove -g grok-dev` ＋孤立シム削除で撤去。bun 1.3.14 は導入済みのまま。

## 関連
- スキルが使う Claude 側モデルは Fable5、不可なら最新（現在 Opus 4.8）と SKILL に明記。
- 同型: codex-consult。パス化け対策は [[feedback_u8792_path_unicode_escape]]。
