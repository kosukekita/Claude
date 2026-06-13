---
name: project_tooluniverse_mcp_wsl_fix
description: tooluniverse-osteo MCP起動失敗の恒久修正。Nodeランチャーがvenvバイナリを直接spawn。bash/.sh完全排除
metadata:
  type: project
---

`~/.claude/.mcp.json` の `tooluniverse-osteo` MCP サーバーが Windows で起動失敗する問題の修正履歴。

## 症状
`claude mcp list` で `tooluniverse-osteo: ✗ Failed to connect`。

## 真因（2段階）
1. **WSL罠**: `.mcp.json` で `"command": "bash"` が System32 の WSL スタブ(`C:\Windows\System32\bash.exe`)に解決され、登録 WSL ディストロに `/bin/bash` が無く即死。
2. **commit 081a23b の不整合（要注意の教訓）**: 081a23b は「`.js` が venv バイナリを直接 spawn、`.sh` は削除」とコミットメッセージに書いたが、**実際にコミットされた `.js` は旧設計のまま**で、削除済みの `tooluniverse-osteo.sh` を bash 経由で呼ぼうとしていた。→ `tooluniverse-osteo.sh: No such file or directory` で落ちる。**メッセージと実体が食い違ったコミット**だった（「Verified on Windows 11」も実態に反していた）。

## 恒久修正（commit 53e5674）
`bin/tooluniverse-osteo.js` を**自己完結 Node ランチャー**に書き直し:
- `$TOOLUNIVERSE_HOME`(既定 `~/tooluniverse-env`)配下の `.venv/Scripts/tooluniverse-smcp-stdio.exe`(Win)／`.venv/bin/tooluniverse-smcp-stdio`(POSIX)を `fs.existsSync` で per-OS 解決し、`spawn` で**直接起動**。
- **bash も `.sh` もチェーンから完全排除** → WSL 罠と Git Bash 依存を原理的に消した。`__dirname` 非依存でどの cwd からでも動く。
- `--include-tools`: PubMed_search_articles / EuropePMC_search_articles / search_clinical_trials / Tool_Finder_Keyword の4つを埋め込み。`semantic_scholar_search` は build v2.14.5 に無くツールロードを中断させるので**除外**。
- venv 実体: `C:/Users/u8792/tooluniverse-env/.venv/Scripts/`（`.claude/.venv` ではない）。サーバーは `ToolUniverse SMCP Server v2.14.5`。

## 検証方法（再発時に使う）
JSON-RPC を逐次 stdin に流す（initialize → notifications/initialized → tools/list、各間に sleep）。一括 pipe は stdin 早期 EOF で TaskGroup エラーになるので逐次送る。`node bin/tooluniverse-osteo.js` 単体起動で4ツール+`find_tools` がロードされれば OK。最終確認は `claude mcp list`。

**Why:** コミットメッセージを信じて「修正済み」と思い込むと再ハマりする。081a23b のように*メッセージと実体が食い違う*ことが実際に起きた。MCP 起動不調時はコミットメッセージではなく `.js` の実体と venv パスを直接検証する。

**How to apply:** `tooluniverse-osteo ✗ Failed to connect` を見たら、まず `node bin/tooluniverse-osteo.js` を手動起動してエラー文を読む。`.venv/Scripts/tooluniverse-smcp-stdio.exe` の存在と `TOOLUNIVERSE_HOME` を確認する。
