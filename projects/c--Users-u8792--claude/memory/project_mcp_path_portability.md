---
name: project-mcp-path-portability
description: ~/.claude共有リポジトリの.mcp.jsonでstdioサーバーは相対パス禁止。${USERPROFILE}を使う（HOMEはPowerShell経由で空）
metadata:
  type: project
---

`~/.claude` は複数Windows PC共有のgitリポジトリ（GitHub: kosukekita/Claude）。`.mcp.json` の stdio MCP サーバー（例: tooluniverse-osteo）で**相対パス（`bin/foo.js`）は禁止**。相対パスは起動cwdが `~/.claude` のときだけ偶然動き、`/doctor` の健全性チェックが別cwdから走ると `node bin/foo.js` がファイルを見つけられず「setup issue」として flag される。

**正しい書き方**: `${USERPROFILE}/.claude/bin/foo.js`

**Why:** `${HOME}` は Git Bash 経由のセッションでは設定されるが、native PowerShell 経由では**空**（実機確認済み）。空展開すると `\.claude\bin\foo.js` のような壊れたパスになり再発する。`${USERPROFILE}` は Git Bash・PowerShell の両経路で必ず存在する。Claude Code は `.mcp.json` の `args`/`command` で `${VAR}` と `${VAR:-default}` を展開するが、**フォールバック内の入れ子展開（`${USERPROFILE:-${HOME}}`）は保証されない**ため単一の確実な変数に統一する。

**How to apply:** このリポジトリは登録プロジェクト全件がWindowsパス（ドライブ C:/P:、ユーザー u8792）でUnix系ゼロ＝Windows専用運用。よって `${USERPROFILE}` で十分。launcher本体（bin/tooluniverse-osteo.js）は `os.homedir()` でvenvを解決し、未インストール時は `exit 127` で clean 終了する移植可能な作りなので `.mcp.json` 側のパスだけ直せばよい。修正コミット ad4e1e0（2026-06-08）。関連: [[project_totalsegmentator_license]]（同じくリモートGPU PC等の複数PC運用）
