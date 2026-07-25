---
name: claude-code-nonclaude-gateway-akitaken
description: claude-gw で Claude Code から非Claudeモデル（ローカルollama/AtlasCloud/サブスクブリッジ）を /model 切替で使う LiteLLM ゲートウェイ構成（akitaken・2026-07-25 構築）
metadata:
  type: reference
---

akitaken に LiteLLM ゲートウェイ（127.0.0.1:4000, systemd user `litellm.service`）を構築済み。
**入口は `claude-gw`**（通常の `claude` はサブスク Claude のまま共存。環境変数はプロセス単位）。
正本 runbook: `~/.config/litellm/README.md`（構成図・全ファイル・罠・出典）。

- モデル一覧は `litellm-models`。セッション中は `/model <名前>`（ゲートウェイ配下では任意文字列が無検証パススルー — 公式仕様）。命名: 素の名前=サブスク枠 / atlas-*=従量 / local-*=ローカル無料。
- 全17モデル稼働・全経路検証済み(2026-07-25): サブスク枠=gpt-5.6-sol(既定)/terra/luna/gpt-5.5/gpt-5.4-mini/grok-4.5/grok-4.3/grok-3-mini、従量=atlas-gpt-5.6-sol/atlas-gpt-5.5/atlas-grok-4.5/atlas-glm-5.2/atlas-kimi-k3/atlas-deepseek-v4、ローカル=local-gptoss/local-qwen3/local-qwen3-unc（num_ctx は litellm の extra_body.options.num_ctx で拡張済み・検証済み）。
- サブスク枠ブリッジ = CLIProxyAPI（127.0.0.1:8317, `cliproxyapi.service`）。codex+xai OAuth ログイン済み（トークン `~/.cli-proxy-api/`・自動リフレッシュ）。再ログイン（-codex-login / -xai-login）は**エージェント実行不可（権限クラシファイアが遮断）**、ユーザー本人が実行する。
- 罠: AtlasCloud は models 掲載≠routable（必ず極小プローブ）。claude-gw セッションでは claude.ai コネクタ MCP が無効（AUTH_TOKEN 優先の仕様）。背景タスクは ANTHROPIC_DEFAULT_HAIKU_MODEL=local-qwen3 で課金ゼロ化済み。
- これにより CLAUDE.md の「Claude Code 本体は Claude 系のみ・変更不可」は**ゲートウェイ経由なら例外**（公式サポート外構成）。委譲台帳（[[external-ai-consult-fallback]]）と使い分ける: 会話まるごと別モデル＝claude-gw、単発相談＝従来の ask-*/codex/grok。
