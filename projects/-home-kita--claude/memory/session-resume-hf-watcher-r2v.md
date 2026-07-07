---
name: session-resume-hf-watcher-r2v
description: 【再開用】2026-07-07〜08セッションの続き。hf-watcher勾配ゲート改修+NSFW限定Top1動画生成、Wan-VACE真r2v成立まで完了。次アクションと未了点
metadata: 
  node_type: memory
  type: project
  originSessionId: 962c799f-34d9-461f-8ff7-8e2af5af1210
---

# セッション再開ポイント（2026-07-08時点）

前回セッションのテーマ: hf-watcher(週次HF新着監視)の改修と、Wan-VACE r2v動画の一気通貫検証。**大半完了、下記が続き**。

## 完了済み（触る必要なし）
1. **ビジネス/Xダイジェスト停止**: `biz-insights.timer`/`x-digest.timer`を`systemctl --user disable --now`済。復帰は`enable --now`。hf-watcher.timerのみ稼働(月9:00)。
2. **hf-watcher勾配ゲートv2**: 絶対数→速度(trend/Δ♥週/若齢♥日、30日窓フル再走査、near-missログ)。詳細[[hf-weekly-model-watcher]]。
3. **NSFW限定・Top1配信**: `HFW_NSFW_ONLY`(既定ON)+`HFW_MAX_REPORT=1`。動画は`eval-video.mjs`(Z-Image静止画→LTX-2.3+LoRA i2v→pCloudリンク)、GGUF/非LTXは「生成サンプルなし+理由」明記。実写NSFW動画1本pCloudリンク送信実証済。
4. **r2v監視語追加**: hf-watcherに`reference-to-video`タグ+`vace`/`bernini`検索追加済。
5. **ペルソナ「三井彩香」**(29歳UXデザイナー/顔75点/Fカップ): `~/media-out/persona-ayaka/persona.md`。
6. **SFW/NSFWキャラシート**: `sheet_sfw.png`(Codex)/`sheet_nsfw_final.png`(表情パネル削除・顔アップ/顔パーツ保持・全身3面各1枚、ffmpeg合成)。テンプレ恒久ルール追記済。
7. **★真のr2v成立(2026-07-08)**: 別人モーション動画→OpenPose骨格化→Wan-VACEで三井彩香に転写。`r2v_pose.mp4`+`r2v_proof.png`。詳細[[wan-vace-r2v-local-setup]]。

## 主要ファイル
- hf-watcher本体: `~/media-out/hf-watcher/hf-watcher.mjs`、動画生成: `~/media-out/hf-watcher/eval-video.mjs`
- r2vスクリプト: `~/.claude/skills/video-media-studio/scripts/gen_wan_vace.py`(--control-mode pose、matplotlib/scipy依存追加済)
- 成果物: `~/media-out/persona-ayaka/`(ref_body.png=三井彩香ヌード参照、motion_drive.mp4=別人モーション、r2v_pose.mp4=真r2v)

## 次アクション候補（ユーザー選択待ち・未着手）
- **(A) HunyuanCustom導入**: Codexが「1枚→全身identity転写はVACEでなくHunyuanCustom(video-driven customization)が本命」と指摘。r2vの顔忠実度を上げたいなら乗り換え検討(未導入)。
- **(B) r2vのconditioning_scale調整**: 参照が動きに負ける場合0.6-0.8。今回1.0で成功済み。
- **(C) hf-watcher定常運転の見守り**: 次回実行7/13(月)9:00。Δ♥週ゲートはスナップショット1週分たまって実効化。件数見て閾値(HFW_MIN_TREND等env)調整。
- **(D) gen_wan_vace.pyの未コミット変更**: Codex改修分(control-mode等)は`~/.claude`のgit未コミット。必要ならコミット。

## 重要な教訓（繰り返さない）
- **真r2vはreference_imagesだけでは不可**(i2v化)。pose/depth control video+全白mask+refの3点必須。生RGB動画は全白maskで素通り。
- **検証をサボらない**: i2v/r2vをSSIM測定せず「新規レンダ」と3回誤断言しユーザーに2回指摘された。フレーム0 vs 参照のSSIMを必ず測る(i2v≈0.91 / 真r2v≈0.85で別構図)。

関連: [[hf-weekly-model-watcher]], [[wan-vace-r2v-local-setup]], [[r2v-reference-to-video-models]], [[optimal-gen-models-table-and-new-model-eval]], [[person-image-6elements-confirm-before-fill]]
