---
name: goose-agent-local-setup
description: Goose CLI(AAIF/旧Block・OSSエージェント)をakitakenに試験導入 — Ollama gpt-oss:120b接続で完全無料構成・インストール/設定/起動コマンド(2026-08-05)
metadata: 
  node_type: memory
  type: project
  originSessionId: 245c97d8-2c23-431f-91a9-69ed68025f10
  modified: 2026-08-05T03:04:09.483Z
---

Goose CLI v1.45.0（[aaif-goose/goose](https://github.com/aaif-goose/goose)・Apache-2.0・Claude Code/Codex と同カテゴリの自律エージェント）を試験導入（2026-08-05・ユーザー依頼「antigravity cli と使って試しに作ってみたい」）。

- **導入**: 公式スクリプト（`download_cli.sh` を `CONFIGURE=false bash`）→ `~/.local/bin/goose`
- **LLM 接続 = ローカル Ollama で完全無料**: `~/.config/goose/config.yaml` に `GOOSE_PROVIDER: ollama / GOOSE_MODEL: gpt-oss:120b / OLLAMA_HOST: localhost`。★Claude/ChatGPT のサブスク定額は Goose に流用不可（API キー接続だと従量課金になる）ので、無料はローカル一択
- **使い方**: 対話 `goose session` / ヘッドレス `goose run -t "..."`（cwd がワークスペース）。モデル切替は config の GOOSE_MODEL（軽速=qwen3:30b）。gpt-oss:120b は初回ロード重い（~60GB を両GPUへ・アイドルで自動アンロード）
- **実行時は `env -u LD_LIBRARY_PATH -u LD_PRELOAD` 前置**（anaconda 汚染回避・この機の常套）
- スモーク実測: `goose run -t "1+1は？"` → 正答。セッションは cwd 単位で `20260805_1` 形式
- 位置づけ: 本命の役割分担（プラン=Fable5/実装=Codex+/goal）は不変。Goose は試験・比較用の第4エージェント枠（相棒は agy=Antigravity CLI 1.1.9）

関連: [[local-llm-roster-ollama]] [[claude-code-nonclaude-gateway-akitaken]] [[plan-fable-implement-codex-goal]]
