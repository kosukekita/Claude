---
name: claude-subagent-cheap-model-routing
description: Claude Codeのサブエージェントだけを安価モデル(AtlasCloud等)に流す方法と実測結果。codex-routerはCodex専用で流用不可
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-09T01:52:50.693Z
---

2026-08-09 実機検証。「codex-router(duolahypercho)でClaudeのサブエージェントを安価モデルにできるか」の結論。

**codex-router は使えない**: あれは Codex CLI/App 側のルータ（Codex の `config.toml` に managed block を追記し、Responses API を LiteLLM で各社形式に変換、`model_catalog_json` で Codex のモデルピッカーに載せる）。設定項目にある「subagent」も Codex のサブエージェント。Claude Code は Anthropic Messages API を叩くので接点がない。

**Claude Code でやるなら既存の claude-gw（LiteLLM ゲートウェイ）で足りる**（[[claude-code-nonclaude-gateway-akitaken]]）。新ソフト（claude-code-router 等）は不要。実測で成立を確認:
- メイン `claude-atlas-deepseek-v4` / サブエージェント `claude-atlas-glm-5.2` で `modelUsage` に両方が別々に計上され、サブエージェントの Bash も実行された。
- サブエージェントのモデル解決順（公式 docs）: ①`CLAUDE_CODE_SUBAGENT_MODEL` 環境変数 → ②Agent ツールの per-invocation `model` パラメータ → ③frontmatter `model:` → ④メイン会話のモデル。**frontmatter に固定してもモデルが `model:"haiku"` を渡すと上書きされる**ので、確実に固定したいなら環境変数を使う。
- frontmatter `model:` はフルモデルID可（`--model` と同じ値を受ける）＝ゲートウェイ配下なら任意文字列が通る。
- AtlasCloud の deepseek-v4 / glm-5.2 / kimi-k3 は Anthropic Messages 形式の tool_use が正しく返る（curl プローブ済み）＝サブエージェントの道具使いに耐える。
- **注意**: `modelUsage.costUSD` は Anthropic 価格表で計算されるので非Claudeモデルでは無意味な数字（DeepSeek 132k tok で $0.67 と表示された）。実費は AtlasCloud 側で見る。
- メインだけ本物の Claude サブスクに残したい場合は、LiteLLM に `claude-opus-5` → CLIProxyAPI(`-claude-login`) のルートを足す必要がある（`cli-proxy-api --help` に claude-login あり・未設定）。BANリスクの自衛は既存方針どおり。

**同時に見つかった claude-gw の実バグ（未修正）**: `~/.claude/settings.json` の `fallbackModel` が**配列** `["opus[1m]"]` なのに、`~/.local/bin/claude-gw` は `--settings` で**文字列**を渡している。v2.1.226 では文字列側が効かず `claude-opus-5` がゲートウェイに流れ、**全リクエストが 400 Invalid model name で即死**する（`claude-gw -p "hi"` すら通らない）。`--settings` の fallbackModel を配列 `["claude-atlas-gpt-5.6-sol"]` にすると復旧するのを実測。
併せて、AtlasCloud 側で `atlas-gpt-5.4-mini`(=not found) と `atlas-gpt-5.6-sol`(=bad request) が upstream エラーを返す（config.yaml のモデルID が陳腐化）。
