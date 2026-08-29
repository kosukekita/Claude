---
name: cookie-sync-setup
description: Chromeログイン時にcookieを自動でakitakenへ集約する仕組み(拡張→Tailscale Serve→受信サーバ)。stealth-browser-mcpの手動エクスポート撤廃
metadata: 
  node_type: memory
  type: project
  originSessionId: fbbcbf0f-93a9-5abf-b581-c03dc52bf915
  modified: 2026-08-29T07:00:20.563Z
---

人が使うPCのChromeでログインしたら、その cookie を自動で akitaken の
`~/.config/stealth-browser-cookies/<site>.json` に集約する仕組み。2026-08-29 構築・実機疎通済み。
[[stealth-browser-mcp-setup]] の cookie 注入ログイン(案1)の「手動エクスポート」を撤廃するもの。

## 構成(Codex実装・fable検証)
拡張(MV3・各PC) → Tailscale Serve:8443(tailnet限定) → akitaken 127.0.0.1:8787 受信サーバ →
`<site>.json`(600・cookie配列トップレベル=Cookie-Editor互換)。実体 `/data/kita/stealth-cookie-sync/`。

- 受信: `server/receiver.py`(stdlib)。systemd --user `cookie-receiver`(enabled/Linger=yes=再起動後も起動)。
  env=`~/.config/stealth-browser-cookies/receiver.env`(TOKEN・600・git外)
- 公開: `tailscale serve --bg --https=8443 http://127.0.0.1:8787`。★**tailnet only**(Funnelでない)。--bgで永続
- 拡張: `chrome.cookies.onChanged`→eTLD+1ごと5秒debounce→`getAll({domain})`→POST。
  送信先URL/トークンは options で各PC設定(ハードコードなし)。任意のデバイスラベル欄あり

## ★セキュリティ制約(ユーザー指示)
- **Mac Studio(ais-mac-studio)は完全除外**。拡張を入れない・Macから他PCへ経路を作らない
  (AI完全操作機なので踏み台にしない)。送信元はWindows等の人が使うPCだけ
- ハブ型=各PC→akitakenの一方向のみ。PC同士は触れない。受信口はakitakenだけ・127.0.0.1バインド
- 受信はBearerトークン認証(hmac定数時間)・site無害化で `../` 拒否・512KB上限・cookie値をログに出さない

## ★別件の要確認(調査中に発見)
akitaken の Tailscale **Funnel が現在ON**(`https://akitaken.tail7c9257.ts.net` root:443→127.0.0.1:8799
が公開)。記憶[[qm-local-deployment-akitaken]]の「QMはFunnel厳禁・Serve限定」と食い違う。8799が何かと
公開の是非は別途要確認。今回の8443はこれと分離しtailnet onlyにしてある(触っていない)。

## 使い方(新規PCを足すとき)
1. 送信先URL(非秘密): `https://akitaken.tail7c9257.ts.net:8443/push`
2. トークン(秘密): `~/.config/stealth-browser-cookies/receiver.env` の TOKEN 値。**チャットに貼らない**
3. そのPC(Windows等)のChromeで `/data/kita/stealth-cookie-sync/extension/` を「パッケージ化されていない
   拡張機能を読み込む」→ options に URL とトークンを入力。★Mac Studioには入れない
4. 以後そのPCでログインすると自動で akitaken に cookie が届く→新セッションで注入ログインに使える
