---
name: code-review-graph-setup
description: code-review-graph(コード知識グラフMCP・トークン削減)をakitakenに導入した構成 — uv tool・Claude Codeユーザースコープ・Codexグローバル・installコマンドのcwd焼き込み罠(2026-08-05)
metadata: 
  node_type: memory
  type: project
  originSessionId: 245c97d8-2c23-431f-91a9-69ed68025f10
  modified: 2026-08-04T22:45:32.710Z
---

[tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph)（Tree-sitter でコードベースをグラフ化し、AI が必要箇所だけ読むことでトークンを中央値65倍削減・MIT）を akitaken に導入（2026-08-05・v2.3.7）。

**導入構成**:
- CLI: `uv tool install code-review-graph` → `~/.local/bin/{code-review-graph,crg-daemon}`
- Claude Code: **ユーザースコープ MCP** `claude mcp add --scope user code-review-graph -- /home/kita/.local/bin/code-review-graph serve`（全プロジェクトでツール群が見える・✔ Connected 確認済み）
- Codex: `~/.codex/config.toml` の `[mcp_servers.code-review-graph]`（command=導入済みバイナリ・args=["serve"]）

**使い方**: 各リポジトリで初回 `code-review-graph build`（以後 `update`/`watch`・データは `<repo>/.code-review-graph/`）。MCP ツール: `get_impact_radius_tool`（変更のブラスト半径）/ `get_review_context_tool` / `query_graph_tool` / `semantic_search_nodes_tool`（要 `[embeddings]` extra・未導入）等30種。

**罠（実測）**:
- 公式の `code-review-graph install` は**リポジトリ単位**の統合で、cwd に instruction ファイル9種（CLAUDE.md 追記・AGENTS.md・GEMINI.md・.cursorrules 等）と `.mcp.json` を撒く。**~/.claude で実行すると グローバル CLAUDE.md に追記されリポジトリが汚れる**ので使わなかった（--dry-run で要確認）
- `--platform codex` はグローバル `~/.codex/config.toml` に**実行時 cwd を `cwd =` として焼き込む** → 手で cwd 行を削除してセッション cwd 継承にした
- ユーザースコープ MCP の serve が「セッションの cwd のリポジトリ」を正しく掴むかは実プロジェクトでの初回使用時に要確認（公式のリポジトリ内 .mcp.json は cwd を明示ピンする設計）。ダメなら該当リポジトリで `install --platform claude-code --no-instructions` に切替
