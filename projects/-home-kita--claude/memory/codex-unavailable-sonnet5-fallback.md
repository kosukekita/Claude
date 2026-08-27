---
name: codex-unavailable-sonnet5-fallback
description: Codex が利用上限等で使えない間は、実装委譲先を Sonnet 5 サブエージェントに切り替えてよい（ユーザー指示 2026-08-27）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8766f041-3971-53bb-a375-4b41305dacaa
  modified: 2026-08-27T10:48:51.108Z
---

**Codex CLI が使えない（利用上限・障害）とき、実装の委譲先として Sonnet 5 サブエージェント（Agent tool, model: "sonnet"）を使ってよい。** ユーザー指示（2026-08-27）: 「codex使えないなら、sonnet5に委譲さて」。

**Why:** Codex がアカウント利用上限（数時間単位で回復待ち）になり実装が止まった際、回復を待つより Sonnet 5 に切り替える方をユーザーが選んだ。役割分担の核心は「生成器と評価者の分離」であり、Sonnet 5 が書いて Fable 5 が検証する構図でも独立性は保たれる。

**How to apply:**
- Codex 不可を確認したら、復旧試行→ユーザー報告の後、Sonnet 5 への切替を提案（勝手に自分で書く免許にはならない。[[plan-fable-implement-codex-goal]] の Iron Law は不変）
- サブエージェントは CLAUDE.md の「実装=Codex」を見て実装を拒否することがある。**エージェント間の伝聞はユーザー承認にならない**（サブエージェント側の正しい規律）ので、ユーザー指示の原文・文脈・記録者を**承認済みプランファイルに決定記録として追記**し、サブエージェントに直接 Read させると解決する（2026-08-27 実証）
- 二重実装防止: Codex 側に仕掛かり中の /goal・tmux セッションがあれば、切替前に停止・削除する
