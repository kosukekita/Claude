---
name: plan-fable-implement-codex-goal
description: ★恒久ルール(2026-07-17) プラン=Fable5/実装=Codex+GPT-5.6 Sol+/goal/相談=agmsg/検証=Fable5。実機検証済みの実測値とPATHシャドウイングの罠
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2794230-5b57-41fe-9266-054958a3de72
---

★ユーザー恒久方針（2026-07-17指示）: **Claudeに実装させると穴だらけになるのは昔からそう**なので、
実装はCodexに任せ、Fable5は「要件を満たしてるか・ブレてないか」をチェックする側に回る。
GPT-5.6 Solになってからブレること自体は減った、というのがユーザーの実感。

**Why:** 委譲の理由は速さではなく**独立性**。Claudeが実装すると生成器＝評価者になり穴が穴のまま通る。
「Fable5に壁打ち→完成プランをCodex+/goalで自走実装→その間agmsgでFable5に相談」が
一番意図からブレずに自動で品質が上がる、というのがユーザーの実感。

**How to apply:**
- 実装に着手しそうになったら `delegating-implementation-to-codex` スキル（+ `runbook.md`）を読む。CLAUDE.mdに恒久ルールあり
- プランは `.agent-plan.md` にディスク書き出し（Codexは会話を見られない）
- 「3行だけ」「急ぎ」は例外にならない。撤回はユーザーが「自分で書いて」と明示したときだけ
- 検証は「tests pass」で終わらせない。プランと突き合わせ、逸脱は自分で直さず agmsg で Codex に差し戻す
- バイオ系でFable5が使えない場合はプランもCodex(GPT-5.6 Sol)で作るが、計画と実装のセッションは分ける

**実機検証済み（2026-07-17 akitaken/Linux）:**
- Codex TUI起動 ≈15秒 / 単純 `/goal` 完走 10秒 / **agmsg相談を挟んだ /goal 完走 50秒**（「3行にCodexは過剰」は成立しない）
- Codexは `$agmsg` スキルを自発的に読み、send→20秒間隔ポーリング→回答反映まで自走した
- `/goal` は `codex features enable goals`（stable）+ CLI 0.144.5 で有効。TUIに `Goal active`→`Pursuing goal`→`Goal achieved` と出る
- agmsgの `join.sh`/`send.sh`/`inbox.sh` は**位置引数**（`--team` 等のフラグを渡すと `team '--team' has no registered agents` という紛らわしいエラー）
- agmsg `spawn.sh codex <name> --model gpt-5.6-sol --boot-prompt '/goal ...'` で起動＋タスク投入が1コマンド。**codexはMonitor非対応(`monitor=no`)なので--boot-promptが必須級**（spawn後に送ったメッセージはアイドルのCodexに届かない）
- tmuxの `send-keys "text" Enter` は未送信で止まることがある→**Enterは別コマンドで送る**

**★PATHシャドウイングの罠（この環境で実際に踏んだ）:**
`~/.local/bin/codex`(0.132.0) が npm prefix(`~/.npm-global`) 外の孤児インストールで、
`codex update` が永久に届かないままログインシェル/tmuxのPATH先頭に居座り、
`The 'gpt-5.6-sol' model requires a newer version of Codex`(400) を出していた。
agmsg spawn は `cli=codex` をPATH解決するのでこれを踏む。
`~/.claude/bin/setup-codex-latest-model.sh` に**影を検出して現行版へ貼り替える処理**を追加済み（各PCで実行）。

**スキルのTDD検証結果（skill-writing の RED→GREEN→REFACTOR を実施）:**
- RED(スキル無し): **時間＋「3行だけ」の圧力でワークフローが崩壊**。「ユーザー本人が例外を宣言している」等の合理化を8個生成。他は表面上遵守でも「agmsg相談経路に触れない」「検証がtests pass止まり」「失敗を自分で直す」穴
- GREEN(初版): 敵対的judgeで **0/5**。新たな抜け穴=インフラ不可用エスケープ/緊急度エスカレーション/透明性ロンダリング(宣言すれば誠実)/テスト・フィクスチャは実装じゃない/リファクタ指摘の適用は安全/リバートは実装じゃない/N往復ルール/完全理解ライセンス/プランを事後に書き換えて辻褄合わせ/コスト論による遵守
- REFACTOR後: **5/5 正しい挙動**。ユーザー明示オーバーライド（「君が書いて」）も「1回だけ指摘して従う」で正しく通過
- ★judgeが1件を過剰判定（「この関数だけ君が直して」＝明示的撤回そのもの）。**ユーザーの権限を奪う方向に締めるのは誤り**なので採用しない。唯一の出口＝ユーザーが明示指示したときで、その依頼1回限り
- 最終版で追加で塞いだ穴: **プランにコード片/フィクスチャ中身を貼る密輸**（Codexが書き写し役に落ち独立性ゼロ）・**出口の勧誘**（「私が書きましょうか」を選択肢に添える）・承認の推測・コスト論による遵守（「速いから委譲」＝遅ければ自分で書くと認めたのと同じ）

関連: [[external-ai-consult-fallback]] [[feedback-codex-refactor-per-stage]]
