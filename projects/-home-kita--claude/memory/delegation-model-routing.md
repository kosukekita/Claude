---
name: delegation-model-routing
description: 委譲先のモデル使い分け。診断・分析=Fable 5.1、実装=Codex（不可時はSonnet 5）（ユーザー指示 2026-09-05）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8766f041-3971-53bb-a375-4b41305dacaa
  modified: 2026-09-05T05:19:55.847Z
---

**委譲先の使い分け（ユーザー指示 2026-09-05）**:

| 用途 | 委譲先 |
|---|---|
| **診断・分析・原因究明** | **Fable 5.1**（`Agent` の `model: "fable"`） |
| 実装（コード・デッキ生成・スクリプト） | Codex（`codex:codex-rescue`）。不可なら Sonnet 5 |

**Why:** 2026-09-05、細分化ラン異常の診断を Sonnet 5 に委譲したところ、ユーザーから
「診断を委譲する場合は fable5.1 にしてください」と指示があった。診断は根拠の精度が結果を左右するため。

**How to apply:**
- 「原因を特定して」「判別して」「なぜこうなったか」系は Fable 5.1
- 「作って」「直して」「デッキを生成して」系は Codex → 不可なら Sonnet 5（[[codex-unavailable-sonnet5-fallback]]）
- Codex はジョブ登録に失敗することがある（ログファイルが生成されない）。タスクIDを返してきても
  `codex-companion.mjs status` に現れなければ未登録なので、切り替える
- 関連: [[plan-fable-implement-codex-goal]]（実装=Codex の恒久ルール）、[[codex-broker-stall-cleanup]]
