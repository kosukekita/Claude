---
name: fugu-ultra-llm-reasoning-mandatory
description: sakana/fugu-ultra(OpenRouter)をLLM/日本語校正で使う際の必須運用 — reasoning無効化不可・max_tokensを大きく取る・1回約$0.6/数分
metadata:
  node_type: memory
  type: reference
---

`sakana/fugu-ultra`（OpenRouter, 実体ID `sakana/fugu-ultra-20260615`, Provider: Sakana AI）を **テキストLLM/日本語校正・推敲** に使うときの実地知見（2026-06-28、推薦書の日本語校正で実証）。キーは `~/.config/openrouter.key`、呼び出しは `cloud_openrouter.py llm --model sakana/fugu-ultra` か `curl .../chat/completions`。日本語は非常に強く、「到達点を示した」のような終止感の強い慣用句・口語的比喩・機械的漢語まで的確に指摘する。校閲の質は高い。

## ★最大の落とし穴: reasoning が必須で無効化できない
- `"reasoning":{"enabled":false}` を送ると **HTTP 400 "Reasoning is mandatory for this endpoint and cannot be disabled."**。
- reasoning が thinking トークンを大量に消費する。`max_tokens` を小さく（例 2000〜4000）すると、思考だけで上限に達し **`finish_reason:"length"` かつ `content:null`（最終出力が空）** で返る。しかも **reasoningフィールドも null** で中身が取れず、課金（37,811 tokens ≈ $0.6）だけ発生する → 完全な無駄打ち。
- **対策: `max_tokens` を大きく取る（12000〜14000）**。これで reasoning + 最終 content が両方収まり `finish_reason:"stop"`・content が返る。校閲1回でも 35,000〜38,000 tokens / 約 **$0.6** / **数分**（curl `--max-time` は 480〜560 秒、foregroundだと2分でタイムアウトするので **必ず run_in_background**）。

## 使い方の実務
- プロンプトは「**最後に必ず本文/JSONを出力すること**」「長い思考は不要、要点のみ簡潔に」と明示すると最終出力に到達しやすい。
- 出力JSONを期待するなら `{"findings":[{quote,problem,suggestion}],...}` 形式で指示すれば素直に返す（reasoning経由でも最終contentにJSONを置く）。
- 一時的に **HTTP 500 "Internal Server Error"** を返すことがある（インフラ障害、拒否ではない）→ そのままリトライで通る。
- コスト高・低速なので **Workflowで多数並列するのは非効率**。1〜2回の単発呼び出しに留め、字数調整や反映は手元(python)でやるのが効率的。

## 校正用途の所見（推薦書で実証）
- Claude自身の校正サブエージェント2体 + fugu の3者で見ると、fuguは「終止感」「比喩の幼さ」「漢語の機械性」など**日本語ネイティブの語感**に強い指摘を出す。技術的事実チェックはClaude側、語感の最終仕上げはfugu、と役割分担すると良い。
- 注意: fuguは「平易化」より「学術的厳密さ」に寄せる傾向（例「お手本」→「教師データ」を推す）。読み手が非専門家なら、fugu案を鵜呑みにせず平易さとのトレードオフを人/Claude側で判断する。

関連: [[openrouter-image-gen-quirks]]（fuguを画像プロンプト英訳の前段に使う話）, [[grok-prompt-keep-japanese]]
