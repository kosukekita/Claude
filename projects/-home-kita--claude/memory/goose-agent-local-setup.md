---
name: goose-agent-local-setup
description: Goose CLI(AAIF/旧Block・OSSエージェント)をakitakenに試験導入 — Ollama gpt-oss:120b接続で完全無料構成・インストール/設定/起動コマンド(2026-08-05)
metadata: 
  node_type: memory
  type: project
  originSessionId: 245c97d8-2c23-431f-91a9-69ed68025f10
  modified: 2026-08-05T04:49:22.555Z
---

Goose CLI v1.45.0（[aaif-goose/goose](https://github.com/aaif-goose/goose)・Apache-2.0・Claude Code/Codex と同カテゴリの自律エージェント）を試験導入（2026-08-05・ユーザー依頼「antigravity cli と使って試しに作ってみたい」）。

- **導入**: 公式スクリプト（`download_cli.sh` を `CONFIGURE=false bash`）→ `~/.local/bin/goose`
- **LLM 接続 = ローカル Ollama で完全無料**: `~/.config/goose/config.yaml` に `GOOSE_PROVIDER: ollama / GOOSE_MODEL: gpt-oss:120b / OLLAMA_HOST: localhost`。★Claude/ChatGPT のサブスク定額は Goose に流用不可（API キー接続だと従量課金になる）ので、無料はローカル一択
- **使い方**: 対話 `goose session` / ヘッドレス `goose run -t "..."`（cwd がワークスペース）。モデル切替は config の GOOSE_MODEL（軽速=qwen3:30b）。gpt-oss:120b は初回ロード重い（~60GB を両GPUへ・アイドルで自動アンロード）
- **実行時は `env -u LD_LIBRARY_PATH -u LD_PRELOAD` 前置**（anaconda 汚染回避・この機の常套）
- スモーク実測: `goose run -t "1+1は？"` → 正答。セッションは cwd 単位で `20260805_1` 形式
- 位置づけ: 本命の役割分担（プラン=Fable5/実装=Codex+/goal）は不変。Goose は試験・比較用の第4エージェント枠（相棒は agy=Antigravity CLI 1.1.9）

**Qwen3.5-122B 増強と実測比較（2026-08-05）**:
- ユーザー指示「gpt-oss:120bより高精度のakitaken最高品質モデルで」→ 調査結果: Qwen3.8-Max(2.4T)・GLM-5.2(744B)は96GB VRAM不可。**96GBクラス最強= qwen3.5:122b-a10b（81GB・256K ctx）**を採用
- ルート残88GBのため **/data 保存の第2 Ollamaインスタンス**（unit `ollama-data2`・port 11435・`OLLAMA_MODELS=/data/kita/models/ollama`・**`OLLAMA_LOAD_TIMEOUT=30m` + `OLLAMA_KEEP_ALIVE=2h` 必須**）。goose config は `OLLAMA_HOST: localhost:11435 / GOOSE_MODEL: qwen3.5:122b`
- **★罠: HDDコールドロード~14分 > クライアント既定タイムアウト** → goose の初回リクエストが timeout で context canceled されランナーごと殺される。**先に curl --max-time 1800 で /api/generate を叩いて事前ウォームアップしてから goose を走らせる**のが正解
- **比較結果（同一お題: Claude Code用ファイルアップローダー）**: agy(Gemini 3.6 Flash)=完動・多機能（Web UI+CLI+Ctrl+Vペースト+クリップボード3段+自己E2Eテスト）で圧勝。goose+qwen3.5:122b=コードは書けたが **FastAPI の `app.mount("/", StaticFiles)` をルート定義より先に置く古典バグで API が全部飲まれ405＝動作せず**、占有済みポート衝突も未解決。goose+gpt-oss:120b=READMEだけ書いて終了。**ローカルLLMエージェントはまだ実装品質でクラウド勢に届かない**（成果物: ~/agent-compare-uploader/）

関連: [[local-llm-roster-ollama]] [[claude-code-nonclaude-gateway-akitaken]] [[plan-fable-implement-codex-goal]]
