---
name: mcp-servers-setup
description: MCP導入状況(2026-07-30)。context7/playwright/githubは接続確認済み、sentry/cloudflare/stripeはOAuth待ち。GitHubはDCR非対応でghトークンをsettings.local.json経由で渡す
metadata: 
  node_type: memory
  type: project
  originSessionId: dfa0f49a-e019-46aa-bec2-d0f781950a94
  modified: 2026-07-30T12:46:53.779Z
---

2026-07-30 に MCP を追加（kimuai08 の記事「ボリスがオススメする最強MCPサーバー8選」を参考。**URLは記事からでなく各公式ドキュメントで確認**）。すべて `--scope user`＝`~/.claude.json`（**このファイルは `~/.claude` リポの外なのでPC間同期されない**。他PCで使うには各PCで再設定が必要）。

**接続確認済み（headless `claude -p` で実データ取得まで検証）**:
- `context7` — `https://mcp.context7.com/mcp`。**認証不要で即動く**（無料キーはレート上限緩和用）。Next.js 公式ドキュメント取得を実測
- `playwright` — `npx -y @playwright/mcp@latest --isolated`。ブラウザは自動DL。example.com の h1 取得を実測
- `github` — `https://api.githubcopilot.com/mcp/`。private リポの最新コミット取得を実測

**OAuth 待ち（ユーザーが `/mcp` で承認する。本人同意が要るので代行不可）**: `sentry`（`https://mcp.sentry.dev/mcp`）・`cloudflare-observability`（`https://observability.mcp.cloudflare.com/mcp`）・`stripe`（`https://mcp.stripe.com/`）

**GitHub MCP の非自明な罠**: 素で追加すると `Incompatible auth server: does not support dynamic client registration` で接続失敗する。解決は **PAT をヘッダで渡す**こと。`gh` CLI が既に認証済みなら `gh auth token`（scopes: gist/read:org/repo）がそのまま通る（エンドポイントへ initialize を投げて HTTP 200 を実測）。設定は `--header "Authorization: Bearer \${GITHUB_MCP_TOKEN}"` とし、**トークン実体は `~/.claude/settings.local.json` の env ブロック**に置く（`.gitignore:2` で除外済み・auto-push の add 対象外＝公開リポに載らない。既存の HTML2PPTX_API_KEY と同じ慣行）。gh のトークンが失効・ローテートしたら同ファイルを更新する。

**入れなかったもの**: Figma・Linear（ユーザーが使っていないサービス。記事の落とし穴1「MCPを増やすほど賢くなるわけではない」に従う）。

**要注意**: 現在の接続数は多め（gsc/context7/playwright/github/sentry/cloudflare/stripe/tooluniverse-osteo/alphaxiv＋chrome-devtools＋claude-in-chrome＋Google系3）。ツール候補が増えると選択ミス・文脈圧迫が起きるので、**プロジェクトごとに必要な3〜5個だけ有効化**する運用が正しい（`settings.json` の `disabledMcpjsonServers`／プロジェクトスコープ）。`alphaxiv` は 2026-07-30 時点で DNS 解決不能（`clerk.alphaxiv.org` ENOTFOUND）。

関連 [[publishing-security-skill]]（MCPが本番に届く前提での読み書き分離）
