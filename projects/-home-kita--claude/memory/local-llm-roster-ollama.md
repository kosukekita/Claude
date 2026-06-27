---
name: local-llm-roster-ollama
description: akitaken(A6000x2/96GB)のOllama導入済みテキスト生成LLMと、用途別の使い分け・VRAM実測
metadata: 
  node_type: memory
  type: reference
  originSessionId: 334a4bc2-dc89-4710-8306-4d2948e8f76a
---

akitaken (NVIDIA RTX A6000 48GB × 2 = 96GB VRAM, Ollama 0.17.6) の導入済みテキスト生成ローカルLLM。

**導入済みモデル（2026-06時点）**:
- **gpt-oss:120b**（65GB, OpenAIオープンウェイト, 117B-MoE/活性5.1B, Apache 2.0）= **メイン・最高品質**。o4-mini級の推論。日本語も実用十分(Swallow派生が120B以下で日本語最高評価)。実測: ロード時71GB・**100% GPU**(オフロード無し)で2枚に33+34GB分散、CONTEXT 131072(128K)有効、各カード約14GB空き。`ollama run gpt-oss:120b`。
- **qwen3:30b**（18GB, Qwen3 30B-A3B MoE/活性3B）= 旧メイン。併存させて残す。軽め用途。
- **qwen3.5:latest**（6.6GB, 小型）= 要約・Web取得情報整理の高速用。[[grok-cli-fetch-tools-ratelimit]] でGrok代替の要約に使用中。残す。

**使い分け**: 高品質な推論・分析・長文 = gpt-oss:120b / 軽量高速な要約・整理 = qwen3.5 or qwen3:30b。

**検討して見送ったもの（96GB超で快適不可、CPUオフロード激遅）**: qwen3:235b(q4で142GB)、glm-4.6(355B MoE, q4で135GB+)。llama3.3:70b(43GBで動くが世代古く日本語・推論で見劣り、Metaライセンス)。第2候補だったqwen3:32b(dense, 35GB@q8)とglm-4.7-flash(32GB@q8)は将来の追加候補。

**How to apply**: 「A6000×2で動く最高品質のローカルLLM」を問われたら gpt-oss:120b。96GBで全量GPU・快適の上限は量子化込み概ね70GB前後(KV/コンテキスト余裕込み)。それ超はオフロードで激遅になるので避ける。Ollamaタグの実在は ollama.com/library/<model>/tags で必ず確認(存在しないタグを書かない)。
