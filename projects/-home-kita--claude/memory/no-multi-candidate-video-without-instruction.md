---
name: no-multi-candidate-video-without-instruction
description: 動画/画像はユーザー指示が無い限り同目的で複数候補を勝手に生成しない。submit済みクラウドジョブはkillしても課金は戻らない
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

★恒久ルール（2026-07-15 ユーザー明確指示）: **私が指示しない限り、同じ目的の動画（や画像）を勝手に複数生成しない。既定は1本。**

違反例: Ryosukeドラゴン動画の現実オチ尾を、Ultracode/Codexの「複数候補を出して最良を選ぶ」を根拠に**勝手に3候補（4k）を並列生成**した→ユーザーに「なぜ勝手に3候補？1つでいい」と指摘。

**Why:** クラウド生成は1本ごとに実費が発生する。品質担保のつもりの多候補生成でも、ユーザーが望んでいない限り課金と時間のムダ。判断の主導権はユーザーにある（cognitive checkpoint を奪わない）。

**How to apply:**
- 動画・画像の本番生成は**既定1本**。複数候補/バリエーション/seed振りは**ユーザーが明示的に頼んだ時だけ**。
- 「品質のため候補を複数出しましょうか？」と**提案して承認を得てから**なら可。黙って複数走らせない。
- Ultracode有効でも、これは適用外にしない（Ultracodeは"探索の網羅"を推すが、課金を伴う同目的の重複生成はユーザー同意が要る）。[[quality-over-speed-media-gen]] は品質のために時間はかけてよいが、それは「1本を高品質に」であって「勝手に複数本」ではない。

**★submit済みクラウドジョブをkillしても課金は戻らない（2026-07-15 同時に学習）:** AtlasCloud等はsubmit時点でサーバ側生成が走り課金される。ローカルのpollプロセスをkillしても返金されず、むしろ払った成果物を捨てるだけ。誤って複数走らせたら**killせず、prediction id（ログの `prediction id=...`）を再ポーリングして回収**する方が損失が小さい。回収は `_poll_prediction(key, f"{MEDIA_BASE}/model/prediction/{id}", {}, ...)` → `_first_output` → `_download`。関連 [[atlascloud-nsfw-image-and-pipeline]]。
