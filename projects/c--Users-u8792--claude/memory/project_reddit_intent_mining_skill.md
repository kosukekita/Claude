---
name: project-reddit-intent-mining-skill
description: reddit-intent-miningスキル作成（2026-07-27）。X宣伝投稿の手法をTDDでスキル化。非自明=ベースラインはコンプラ・Reddit作法を既に自力で守れるので、スキルの価値は外科的プロトコル5点に集中させた
metadata: 
  node_type: memory
  type: project
  originSessionId: f857ea35-fb2b-451e-8562-b3fc34b28f9e
  modified: 2026-07-27T04:26:28.349Z
---

reddit-intent-mining スキルを作成（2026-07-27）。出典はコールドメール代行業者のX宣伝投稿（Redditの買い手挙手投稿を4時間以内に検知して即アウトリーチする手法）。

- **配置判断**: business-validate-before-building への追記ではなく新規スキル。前者は意思決定ゲート（discipline型）、本作は収集技法（technique型）でレイヤーが異なる。新スキル側から原則1（売れる証拠）・原則1.5（相乗り先）への依存契約を一方向で明示し、既存スキルは無編集（Iron Law回避＋lockstep維持）。[[project_business_validate_skill]]
- **RED実測の非自明な学び**: スキル無しのFable 5ベースラインは「コンプラ（特電法/メール収集拒否）・Redditカルマ作法・needs検証」を既に自力で守れる。全滅していたのは①意図フレーズ定型バッテリー ②4時間鮮度ルール（全員「過去1週間」で検索） ③相手の言葉を引用する2行ファーストコンタクト＋30分即応 ④手動実証→RSS/F5Bot→PRAWの自動化階段（圧力下で即ツール実装に走った） ⑤宣伝投稿数値の未検証扱い。スキルはこの差分だけに集中させた。
- **REFACTORで閉じた穴**: モードB用フレーズ（"how do you guys handle"）がモードAの営業検索に混入→一般議論スレへの割り込み営業を誘発／新規0カルマアカウントで翌朝から営業返信→スパムフィルタ死。各1行の明示で再検証6/6 pass。
- **モードA/Bで鮮度が逆**: リード獲得は4時間以内が命、アイデア発掘は逆に期間を広げ反復性（複数スレ・複数サブの蓄積）を見る。初稿はここが矛盾しており自己レビューで修正。
