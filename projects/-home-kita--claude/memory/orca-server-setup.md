---
name: orca-server-setup
description: Orca(コーディングエージェント統合IDE)をakitakenにヘッドレスRemote Orca Serverとして導入。orca serveはxvfb必須・0.0.0.0:6768バインド
metadata: 
  node_type: memory
  type: project
  originSessionId: fbbcbf0f-93a9-5abf-b581-c03dc52bf915
  modified: 2026-09-02T01:37:40.803Z
---

Orca(stablyai/orca・Claude Code/Codex/Cursor CLIを worktree/タブ/diffで束ねるElectron製IDE・⭐59k)を
akitakenに**Remote Orca Server(ヘッドレス)**として2026-09-02導入。akitaken=常時稼働サーバ、
手元のデスクトップ版がクライアントとしてTailscaleで接続する構成。

## 構成(実機確認済み)
- 実体: `/data/kita/orca/`。AppImage(v1.4.194・208MB)を `--appimage-extract` で展開(FUSE不要)→
  `squashfs-root/`。deb版(要root)は使わず
- CLIの正体: `squashfs-root/resources/bin/orca-ide`(launcher) が **ELECTRON_RUN_AS_NODE=1** で
  `app.asar.unpacked/out/cli/index.js` をNodeとして実行。GUIは起動しない。★GUI本体(orca-ide直叩き)は
  ヘッドレスでcore dump。必ずlauncher経由
- 常駐: systemd --user `orca-serve`(enabled/Linger=yes=再起動後も起動)。ラッパー
  `/data/kita/orca/orca-serve.sh`
- ★**orca serve は内蔵ブラウザ用にXディスプレイを要求**する。自前Xvfb起動に失敗しSIGSEGVするので
  **xvfb-runで包む**のが必須。かつanaconda汚染回避で **env -i**(HOME/PATHのみ)。両方揃って
  「Orca server ready」。ラッパーは `env -i ... xvfb-run -a <launcher> serve --pairing-address 100.65.90.52 --port 6768`
- 待受: `ws://0.0.0.0:6768`(advertised=`ws://100.65.90.52:6768` tailnet)。ペアリングは端末トークンで保護

## ★残り=ユーザーの作業(認証・クライアント)
1. akitakenで管理アカウント登録(OAuth・claude/codex login走る): `orca account add --agent claude` /
   `--agent codex`。導入直後は `No managed accounts`(未登録)。launcherはenv -i経由で叩く
2. ペアリングURL(秘密・端末トークン入り)は `journalctl --user -u orca-serve | grep "Pairing URL"`
   で取得。★チャットに貼らない。手元のデスクトップOrcaで 100.65.90.52:6768 へ接続
3. ★クライアント機の制約: Mac Studioは他PC非接触ルール([[cookie-sync-setup]])。Orcaクライアントを
   どの機にするかはユーザー判断(Windows desktop-5c4jvob 等)

## ★セキュリティ注意
- serve は **0.0.0.0:6768 バインド**(全インタフェース)。orca serveにbind-host指定は無い(--pairing-addressは
  advertised専用)。アクセスは端末ペアリングトークンで一応ゲートされるが、ポート自体はLAN等に開く。
  tailnet限定にしたいならファイアウォール(6768をtailscale0/100.64.0.0/10のみ許可・要root)を別途。未実施
- [[cookie-sync-setup]]で判明した通り akitakenのTailscale Funnelが現在ON=露出面に注意


## モバイル(スマホ)アクセス(2026-09-02 追加)
- サービスに **--mobile-pairing** を追加済み(ラッパー orca-serve.sh)。起動時に「Mobile pairing QR」
  (ASCII QR 38行)+「Pairing URL: orca://pair?code=...」を journal に出す。★モバイル限定スコープ
  (フルaccessの既定runtimeリンクより安全=スマホ紛失リスク対策)。★この変更でデスクトップ用runtimeリンクは
  出なくなる(両方要るなら別途)
- iOSアプリ: App Store「Orca IDE」 https://apps.apple.com/us/app/orca-ide/id6766130217
  Android: APK https://github.com/stablyai/orca/releases (mobile-android-v0.0.47/app-release.apk)
- ★スマホは **Tailscale必須**(同tailnetにサインイン)。akitakenを 100.65.90.52:6768 で掴む。リモート
  (外出先)でもTailscaleが繋がっていれば可
- ペアリング取得(秘密・チャットに出さない): akitakenで
  `journalctl --user -u orca-serve | grep -A40 "Mobile pairing QR"` → QRをスキャン、または
  「Pairing URL」(orca://pair?code=...)をスマホで開く。再起動で再ペアリングが要る場合あり
- 残り=ユーザー: iOSアプリ導入・iPhoneにTailscale・orca account add(OAuth)