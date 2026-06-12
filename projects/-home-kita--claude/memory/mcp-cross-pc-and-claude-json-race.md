---
name: mcp-cross-pc-and-claude-json-race
description: ~/.claude/.mcp.json is shared across Windows+Linux PCs; approval state races between concurrent claude processes
metadata: 
  node_type: memory
  type: project
  originSessionId: dba384f7-bab3-40cc-8bb8-7c2ab17e50ab
---

`~/.claude` is a git repo synced across multiple machines (a Windows PC and a Linux box `akitaken`). The `.mcp.json` `tooluniverse-osteo` server originally hardcoded a Windows path (`C:\Users\kita\tooluniverse-env\.venv\Scripts\tooluniverse-smcp-stdio.exe`), which can't launch on Linux.

Fix applied: `.mcp.json` now runs `bash bin/tooluniverse-osteo.sh` (repo-relative, resolved from project root). That wrapper auto-detects the right binary across machines — checks `$TOOLUNIVERSE_HOME` (default `$HOME/tooluniverse-env`) under `.venv/bin` (Unix) then `.venv/Scripts/*.exe` (Windows), then PATH. The 5 `--include-tools` (PubMed_search_articles, semantic_scholar_search, EuropePMC_search_articles, search_clinical_trials, Tool_Finder_Keyword) live inside the wrapper.

**Committed 2026-06-02** on branch `fix-mcp-cross-pc-setup` (commit `c0ae15d`): the `.mcp.json` change + `bin/tooluniverse-osteo.sh` were previously only in the working tree (uncommitted, `bin/` untracked), so the Linux fix wasn't persisted/synced. Same commit adds `.env.template` (ToolUniverse API keys) and gitignores `.env`/`.env.local` — `.env` was NOT ignored before, a leak risk if real keys were dropped in. Branch not yet pushed to `origin` (github.com/kosukekita/Claude). On Linux the binary lives at `/home/kita/tooluniverse-env/.venv/bin/tooluniverse-smcp-stdio` and the wrapper launches cleanly (verified: prints "🚀 Starting ToolUniverse SMCP Server").

**Why it matters / gotcha:** MCP approval for `.mcp.json` servers is stored in `~/.claude.json` at `projects["/home/kita/.claude"].enabledMcpjsonServers`. Editing that file by hand works (immediate readback confirms), but **multiple concurrent `claude` processes** each hold the whole config in memory and rewrite the entire file on exit — clobbering hand-written approvals with their stale state. So `claude mcp list` keeps showing `⏸ Pending approval` even after a correct edit. To approve reliably, do it through a live Claude session's startup prompt (or kill the other processes first), not by editing the JSON while others run. `claude mcp reset-project-choices` clears the enabled/disabled lists.

The `claude.ai Gmail/Calendar/Drive` "Needs authentication" entries are unrelated OAuth logins, not part of the doctor MCP warning.
