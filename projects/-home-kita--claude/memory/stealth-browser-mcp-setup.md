---
name: stealth-browser-mcp-setup
description: stealth-browser-mcp導入構成。anaconda汚染でChrome起動失敗→env -iラッパー必須。ログイン再現はset_cookie注入が既定
metadata:
  node_type: memory
  type: project
---

anti-bot(Cloudflare等)を回避する実Chrome自動化MCP `stealth-browser-mcp`
(vibheksoni/stealth-browser-mcp・MIT・nodriver+CDP+FastMCP)を2026-08-29に導入。

## 構成
- 実体: `/data/kita/stealth-browser-mcp`(commit d95605a)。venvは `uv venv --python /usr/bin/python3.12`
  (★python3-venvが無くensurepip不可→uvで作る)。依存は `VIRTUAL_ENV=... uv pip install -r requirements.txt`
- 登録: `claude mcp add-json stealth-browser-mcp '{...command: run_clean.sh}'`(userスコープ・stdio)
- ★**env -iラッパー必須**(`/data/kita/stealth-browser-mcp/run_clean.sh`)。素で起動すると
  `google-chrome: libpango: undefined symbol: g_once_init_leave_pointer` でChrome起動失敗
  ＝anacondaのglib汚染。`env -i HOME=... PATH=/usr/bin:/bin` でシェル初期化すると通る
  (tmuxの `env LD_LIBRARY_PATH=` と同系統の汚染回避。[[leaked-toolcall-hook-linux]]参照)
- ヘッドレスサーバなのでDISPLAY無し。nodriverは `headless=True` で起動可(実測 HEADLESS OK)。
  実Chromeはクリーンenvなら `--headless=new --no-sandbox` でDOM取得成功

## ★「ログイン突破」の実際
- anti-botの壁は越えるが、**認証情報を破る機能ではない**。login/password専用ツールは無い
- 認証情報の渡し方は2通り:
  1. **set_cookie()注入(既定・推奨)**: `set_cookie(instance_id,name,value,url=,domain=,path=/,secure=,http_only=,same_site=)`。
     ログイン済みセッションcookieを流し込む＝生PW不要・2FA/CAPTCHA回避。server.py:1052
  2. type_text()でフォーム入力: navigate→type_text→click_element。生PWが会話に載る・2FAで詰まる
- `STEALTH_BROWSER_MCP_AUTH_TOKEN` はサイト認証ではなく**HTTPトランスポートのbearer**(stdioなら不要)
- 運営者の注意(README:245): CDP実行/任意JS/cookie/network傍受をフル権限で握る＝ローカルstdio+信頼できるクライアント前提。cookieも秘密情報として経路を絞る
