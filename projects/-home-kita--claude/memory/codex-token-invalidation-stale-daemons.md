---
name: codex-token-invalidation-stale-daemons
description: "codex \"token_invalidated/別アカウントでサインイン\" の真因は残留codex常駐の旧トークンrefresh。再ログイン前に全codexプロセス停止が必須。ヘッドレスloginはcurl配送+/success取得で完遂"
metadata: 
  node_type: memory
  type: project
  originSessionId: c11c2fb1-5cac-4e75-80f8-a532b6a5aa80
  modified: 2026-08-03T02:54:33.951Z
---

# Codex トークン即時無効化の真因と復旧手順（2026-08-03 akitaken 実測）

**症状**: codex TUI が `token_invalidated` / "Your access token could not be refreshed because you have since logged out or signed in to another account"。`codex login` で再ログインしても**数分以内に新トークンも無効化**され、/goal が Goal blocked のまま。`codex login status` は "Logged in" を返すので当てにならない（ローカル auth.json の存在確認のみ）。

**真因**: 数日〜数週間前から残留した codex 常駐プロセス群（Claude Code プラグインの app-server-broker.mjs + `codex app-server`、`codex-code-mode-host`、放置 tmux 内の古い TUI、`--remote-control` app-server）が**旧リフレッシュトークンで更新を続け**、サーバ側のセッション排他/リユース検知で最新ログインを無効化し合う。放置された未完了 `codex login`（ポート1455占有）も併発していた。

**復旧手順（この順で機械的に）**:
1. `ps -eo pid,lstart,cmd | grep -i codex | grep -v shell-snapshots` で全列挙（lstart で古さを見る）
2. 古い TUI は tmux 経由で `/quit`（セッション状態を保存）、デーモン類（app-server/broker/code-mode-host）は kill。**全滅させてから**次へ
3. `lsof -iTCP:1455 -sTCP:LISTEN` で放置 login を検出→kill
4. `codex login` をバックグラウンド起動→出力から auth URL 抽出→ユーザーに渡す→戻りURLを `curl 'http://127.0.0.1:1455/auth/callback?...'` で配送（[[headless-oauth-localhost-callback]] スキル準拠）→ **`curl http://127.0.0.1:1455/success` を取得しないと login プロセスが終了しない**
5. auth.json の mtime 更新を確認してから TUI を**新規起動**（既存 TUI はメモリ上の旧トークンを使い続けるため再起動必須）

**予防**: codex を使い終わったセッション/プラグインの常駐が数日残ると再発する。トークン異常を見たら最初に残留プロセス列挙。Windows 機など他PCの codex 同時利用も同種の相互無効化を起こしうる。

**関連**: tmux 3.4 ではペイン指定 `-t "=name"` が "can't find pane" になる（`=name:` コロン付きなら OK）。codex TUI は起動時に Update available メニューで停止することがある（"2" Skip を送る）。
