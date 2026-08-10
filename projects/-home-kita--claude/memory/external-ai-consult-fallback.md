---
name: external-ai-consult-fallback
description: Codex/Grokが使えない時の外部AI相談の具体手順(or-consult.mjs→OpenRouter→AtlasCloud)。コマンド・モデルID・落とし穴
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
  modified: 2026-08-10T04:00:28.340Z
---

CLAUDE.md「外部AI相談のフォールバック」の実装詳細（本文はCLAUDE.mdに要点＋このポインタ）。大前提=Claude系の知見で足りる相談は自セッションが答える／OpenRouter・AtlasCloudで `anthropic/claude-*` を呼ばない(二重課金)／外部AIはCodex/Grok障害時かつClaude以外の独立視点が要る時だけ／キーの中身は表示しない／PIIは送らない。

## 第一候補: OpenRouter (`~/.claude/bin/or-consult.mjs`, Node・CLI非依存)
```bash
node ~/.claude/bin/or-consult.mjs "<相談プロンプト>"                              # 既定=openai/gpt-5.5(Codex系代替・空応答少)
echo "<長文>" | node ~/.claude/bin/or-consult.mjs --stdin --model x-ai/grok-4.3
node ~/.claude/bin/or-consult.mjs "<プロンプト>" --model openai/o3-pro --max-tokens 12000  # 重reasoningはmax大
node ~/.claude/bin/or-consult.mjs --list
```
- APIキー=`~/.config/openrouter.key`(chmod600・ラッパーが読む)。既定 `--max-tokens 4000`。
- **anthropic/claude-* は指定しない**。使うのは gpt/grok/gemini/o3 等。
- ⚠️ 重reasoning(gpt-5.5-pro/o3-pro)はmax-tokens小だと推論で使い切りcontent空(課金だけ)→`--max-tokens 12000+`。
- 従量課金。残高不足=HTTP402→max下げるか残高追加。医学データはPII無し前提(大腿骨FE等は可)。
- 代替モデル目安: Codex代替=`openai/gpt-5.5`/`openai/o3-pro`(重), Grok=`x-ai/grok-4.3`, Gemini=`google/gemini-2.5-pro`。
- 手動フォールバック(Claudeが判断して使う)。`codex:rescue`自動切替は未実装。

## 二次: AtlasCloud (OpenRouterが402/429で使えない時)
階段は `Codex/Grok → OpenRouter → AtlasCloud`。ここでも `anthropic/claude-*` は呼ばない。
- キー=`~/.config/atlascloud.key`(1行・末尾改行なし・chmod600)。無ければ `$ATLASCLOUD_API_KEY`。読み出したら `.strip()`。
- LLM相談の入口=video-media-studioスキル `scripts/cloud_atlascloud.py llm`(`/v1` OpenAI互換・同期)。画像/動画は `/api/v1` 非同期で形が違う。
- id例: `deepseek-ai/DeepSeek-V3.1`, `openai/gpt-5.5`, `openai/o3-pro`, `xai/grok-4.5`, `google/gemini-3.1-pro-preview`。★OpenRouterの`x-ai`はAtlasCloudでは`xai`(ハイフン無)。
- ⚠️ 落とし穴: エラー封筒は `{"code":N,"msg":"..."}`。**不正キーは401でなくHTTP404**(不正modelは400)→404を「エンドポイント無し」と即断せず認証失敗も疑う。
- ⚠️ **残高切れのHTTPステータスは未文書＝未確定。402と決め打ちしない。** 非2xxは `{code,msg}` をそのまま人間に見せて落とす。

## 全体ルーティング台帳（CLAUDE.md 2026-08-10 刷新時にここへ退避・ユーザー確定 2026-07-25）

Claudeが拒否したら止めず、この台帳で外部LLMに発注して統合するのが標準動作。
指名トリガー（「Codexで」「Grokで」「ローカルLLMで」）はフォールバックを待たず直行。

- **A. 通常（SFW・文章/分析/コード）**: Claude（無料・最優先）→ Codex `codex exec --skip-git-repo-check "…"` → Grok `grok -p "…"` → ローカル `ask-local "…"` → OpenRouter or-consult.mjs／AtlasCloud llm（従量・最後）
- **B. NSFW・際どい創作**: Grok（サブスク・寛容）→ `ask-local-unc "…"`（huihui_ai/qwen3-abliterated:30b）→ OpenRouterの無検閲系。**GPT系はBでは使わない**（拒否傾向）
- **C. 医療・研究の過剰拒否**: Codex（GPT-5.6・医療推論強）→ `ask-local "…" gpt-oss:120b`（高品質・初回ロード重）/ `qwen3:30b`（軽速）→ それでも断られる内容のみ `ask-local-unc`
- **ユーザー直接入口（このLinux機のみ・他PCは再設置要）**: `ask-gpt` / `ask-grok` / `ask-local "…" [model]` / `ask-local-unc`（~/.local/bin）。セッション内なら `!ask-grok "…"`。セッション丸ごと別モデル= `claude-gw`（[[claude-code-nonclaude-gateway-akitaken]]・※fallbackModelバグ未修正で現在起動不能 [[claude-subagent-cheap-model-routing]]）、または `codex` / `grok` を直接起動（フルエージェントTUI）

関連: [[atlascloud-nsfw-image-and-pipeline]] [[optimal-gen-models-table-and-new-model-eval]]
