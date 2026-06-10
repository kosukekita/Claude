---
name: mobile-preview-tailscale
description: Use when the user wants to preview a local site/app on their phone (実機確認), asks for a phone URL for a localhost project, or wants to share a locally-served page across their own devices over Tailscale. Covers starting a LAN-bound dev server and building the phone-reachable URL.
---

# Mobile Preview over Tailscale

ローカルで配信中のサイト/アプリを、同一 tailnet のスマホ（や別PC）から実機確認するための手順。
IP はハードコードせず**毎回コマンドで動的取得**する（別マシンにこのスキルをコピーしてもそのまま動く）。

## When to Use
- 「スマホで確認したい」「実機で見たい」「URLは？」（localhost のプロジェクトに対して）
- 自分の別デバイス（スマホ・別PC）に、ローカル配信中のページを見せたい
- **NOT for**: 第三者への公開（それは本番デプロイ）。Tailscale は自分の tailnet 内だけ。

## 前提（最初に1回だけ確認）
- 配信元PC・閲覧側デバイスの**両方に Tailscale が入り、同じアカウントでログイン**していること（同一 tailnet）。
- 入っていなければこのスキルは使えない。ユーザーにスマホへ Tailscale アプリを入れて同じアカウントでログインするよう案内する。

## 手順

### 1. 配信元PCの Tailscale IP を取得（ハードコードしない）
```bash
tailscale ip -4
```
PATH に無ければフルパス:
- Windows: `& "C:\Program Files\Tailscale\tailscale.exe" ip -4`
- macOS:   `/Applications/Tailscale.app/Contents/MacOS/Tailscale ip -4`
返る `100.x.y.z` が tailnet 内アドレス。これを URL のホストに使う。
（接続先デバイス一覧・状態は `tailscale status` で確認できる。）

### 2. dev サーバーを *全インターフェース* にバインドして起動
`localhost`/`127.0.0.1` バインドだと他デバイスから届かない。必ず `0.0.0.0`（全IF）で待受ける。
- 静的HTML（Python）: `python -m http.server <PORT> --bind 0.0.0.0`（Win で python 無ければ `py -m ...`）
- Vite:   `vite --host 0.0.0.0`（または package.json に `--host`）
- Next:   `next dev -H 0.0.0.0`
- 既存の開発サーバーがあるならそれを `0.0.0.0` 公開オプション付きで起動する。
ポートは慣例で 8765/5173/3000 等。長時間動かすならバックグラウンド実行。

### 3. スマホで開く URL を組み立てて渡す
```
http://<手順1のIP>:<PORT>/<パス>
```
例: `http://100.68.192.19:8765/bedding/2026-06-11-mattress-lower-back/`
複数ページあるなら主要URLを併記して渡す。

## つながらない時のチェック（順に）
1. **同一 tailnet か** — スマホ側 Tailscale が同じアカウントでログイン＆オン。`tailscale status` に相手デバイスが出るか。
2. **サーバーが生きているか** — `curl -s -o /dev/null -w "%{http_code}" http://localhost:<PORT>/<パス>` が 200 か。
3. **バインドが 0.0.0.0 か** — `localhost`/`127.0.0.1` で起動していると他デバイスから不可。再起動して `--bind 0.0.0.0`。
4. **ポート/ファイアウォール** — OS のファイアウォールがそのポートの受信を許可しているか（初回は許可ダイアログが出ることがある）。
5. **HTTPS 必須機能** — カメラ等 HTTPS が要る機能を試すなら `tailscale serve`（TLS 終端付き）を検討。単なる閲覧は http で十分。

## メモ
- Tailscale を使う理由: 同一 Wi-Fi 不要・LAN IP 変動に強く、自分のデバイス間だけに閉じた安全な経路。
- 自分のデバイス間限定。tailnet 外への共有は別途（`tailscale funnel` 等）で、機密ページには使わない。
