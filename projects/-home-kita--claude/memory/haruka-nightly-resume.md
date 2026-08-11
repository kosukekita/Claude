---
name: haruka-nightly-resume
description: 【再開用】遥の3分動画を毎晩生成しpCloud URLを毎朝6時メールする自走パイプライン。実装完了・GPU争奪で稼働保留中
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-11T03:50:06.144Z
---

2026-08-10〜11 構築。**実装は完了、タイマーは未有効化（disabled）**。研究ジョブ(GPU1)優先のため保留。

## 構成
`~/media-out/haruka-nightly/`（bin/ catalog/ state/ runs/）＋ systemd --user unit 4本
（gen 01:00 / mail 06:00・`~/.config/systemd/user/haruka-nightly-*.{service,timer}`）。
プランは `~/.claude/.agent-plan-haruka-nightly.md`。

- 動画3部: ①日常デート60s ②高級ホテルで下着・ソファ密着・飲ませ合う大人の会話90s ③全裸POV騎乗位30s
  （②③とも**男性の体を映さない**。③は「気持ちいい」「好き」を喘ぎまじりに連呼）
- 設定: 遥と視聴者は**秘密の不倫関係**。①に軽いヤキモチのセリフを1ショット逐語で入れる
- 台帳6冊×各100件（`catalog/`）: daily_scenes / daily_outfits / dialogue_lines / hotel_lingerie /
  hotel_dialogue / cowgirl_actions。**SFW4冊はClaude執筆・explicit系はローカル無検閲LLM産**。
  毎晩ランダム選択＋前夜と同一組合せなら引き直し（自由生成だと同種が繰り返されるためユーザーが台帳方式を指定）
- QCゲート: 尺150-210s / 音声実在 / **顔照合（compare_face_sim・閾値0.45＝良品実測0.5866で較正）** /
  モザイク再検査（NudeNet自動検出→適用後に再スキャンしてcleanでなければ失敗）
- 失敗しても**必ず6:00にメール**（原因1行つき）＝沈黙しない設計。メールはURLのみ（NSFWを本文に載せない）

## 実走で確認できたこと（2026-08-10 夜）
- Run1 26ショット生成完走・失敗時のstate記録・**raw残存時のresume（trim削除後6秒で再組み立て）** は実機OK
- ★**残る唯一の未検証は「3ラン通しの完走」**。実装欠陥ではなく毎回GPU争奪で止まっている

## 再開手順（研究ジョブが GPU1 を解放したら）
1. `~/media-out/haruka-nightly/bin/haruka_nightly.py` を手動実行（フル1サイクル・約2時間）
2. 実物（3分動画・モザイク位置・pCloud URL）をユーザーに提示
3. OKなら `systemctl --user enable --now haruka-nightly-gen.timer haruka-nightly-mail.timer`

## 既知の注意
- プランナーLLMはOllama（explicitは `huihui_ai/qwen3-abliterated:30b`）。**GPUが埋まるとCPUオフロードで7秒/tok**
  になり計画生成がタイムアウトする→起動時プリウォーム実装済み（keep_alive=90m）だがVRAMは要る
- Run1の計画は放置すると①2.3秒の細切れ②第三者の男が登場、になる→`--min-shot-sec 3.5`と
  「男を映さない」固定文で対策済み（実測で判明した欠陥）

関連: [[uncensored-image-pipeline-resume]]（同じくGPU待ち）、[[background-waiter-design]]
