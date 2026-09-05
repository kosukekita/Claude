---
name: delegation-model-routing
description: 委譲先のモデル使い分け。プラン・診断=最新モデル(GPT-6 Astra / Fable 5.1)、実装=GPT-6 Astra、不可ならSonnet 5（ユーザー指示 2026-09-05）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8766f041-3971-53bb-a375-4b41305dacaa
  modified: 2026-09-05T05:25:04.570Z
---

**委譲先の使い分け（ユーザー指示 2026-09-05）**:

| 用途 | 委譲先 |
|---|---|
| **プラン・診断・原因究明**（大事な元になるもの） | **最新モデル**: GPT-6 Astra（Codex）または **Fable 5.1**（`Agent` の `model: "fable"`） |
| **与えられたプランの実装** | **GPT-6 Astra**（Codex）。不可なら **Sonnet 5** |

ユーザー原文: 「どちらかというと、プランや診断などの大事な元は gpt6astra や fable5.1 のような最新モデル。
与えられたプランを実装するときは、gpt6astra か無理なら sonnet5 にして」

**Why:** プラン・診断は後段すべての精度上限を決めるため、最新モデルの推論力を使う。実装は与えられた
仕様に従う作業なので、Astra が使えないときは Sonnet 5 で代替できる。

**How to apply:**
- Codex の既定モデルは `~/.codex/config.toml` の `model` で決まる。**2026-09-05 時点で `gpt-6-astra`**
  （それ以前の記憶にある `gpt-5.6-sol` は古い。委譲前に config を確認する）
- **モデル名は `gpt-6-astra`**。`astra` / `gpt-5.7-astra` / `astra-preview` は `not supported` で弾かれる
- Codex が利用上限に達したら（`You've hit your usage limit ... try again at <日時>`）その時刻まで使えない。
  **実装は Sonnet 5 へ、診断は Fable 5.1 へ**振り分ける
- Codex はジョブ登録に失敗することがある（タスクIDを返すのに `codex-companion.mjs status` に現れない）。
  その場合も切り替える
- 関連: [[codex-unavailable-sonnet5-fallback]]、[[codex-broker-stall-cleanup]]、[[plan-fable-implement-codex-goal]]
