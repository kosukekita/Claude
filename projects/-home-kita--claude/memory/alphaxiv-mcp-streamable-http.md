---
name: alphaxiv-mcp-streamable-http
description: "alphaXiv MCP in .mcp.json must be type \"http\" (Streamable HTTP), not \"sse\" — sse hangs 30s and times out"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5abc3f9a-6807-4887-a828-d7f17f8a2012
---

The alphaXiv MCP server (`https://api.alphaxiv.org/mcp/v1`) in `~/.claude/.mcp.json` must use `"type": "http"` (Streamable HTTP), **NOT** `"type": "sse"`. With `sse`, OAuth succeeds and the token is saved fine, but the client opens a GET long-poll that the server never feeds, so it hangs and Claude reports `connection timed out after 30000ms`. Fixed 2026-06-12 by changing `sse` → `http`.

**Diagnostic that nailed it** (token pulled from `~/.claude/.credentials.json` at `mcpOAuth["alphaxiv|<hash>"].accessToken`):
- GET + `Accept: text/event-stream` (old SSE) → HTTP 200 but 0 bytes, times out.
- POST `initialize` + `Accept: application/json, text/event-stream` (Streamable HTTP) → 200 in <1s, returns serverInfo `alphaxiv-assistant v1.0.0`, then `tools/list` yields 4 tools.

**Gotcha — auth vs transport:** the symptom looked like an auth failure (`✘ Failed to connect`, "MCP error"), but auth was complete. `/mcp` printed "Got new credentials, but reconnecting … timed out" — that "Got new credentials" is the tell that OAuth worked and the problem is downstream (transport). Don't keep re-running the OAuth flow; check the transport type. The OAuth `complete_authentication` tool can disappear mid-flow if the MCP server disconnects — but if `/mcp` already saved credentials, the code-exchange is done and re-auth is unnecessary.

**Remote SSH note:** OAuth callback redirects to `http://localhost:3118/callback?code=...&state=...` which won't load over SSH (shows "Authentication Successful" / connection error) — that's expected; the address-bar URL is still valid. But `/mcp`'s built-in reconnect handles the whole exchange itself, so the manual callback-URL paste is usually unnecessary.

alphaXiv tools (4): `discover_papers`, `get_paper_content`, `answer_pdf_queries`, `read_files_from_github_repository`. Scope: arXiv CS/math/physics/stats/EE/quant-bio/quant-fin — NOT biomedical/PubMed. See [[mcp-cross-pc-and-claude-json-race]] for how `.mcp.json` is shared across PCs and the approval-race gotcha.
