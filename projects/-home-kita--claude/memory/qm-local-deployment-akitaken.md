---
name: qm-local-deployment-akitaken
description: QM(yc-software/qm)を akitaken に完全ローカル構築した構成の要点。ソース直起動+署名付きcore+web-uiテストシームcookie認証、Claudeサブスク OAuth、Tailscale Serve限定公開、経理スキル+月次cron
metadata: 
  node_type: memory
  type: project
  originSessionId: c11c2fb1-5cac-4e75-80f8-a532b6a5aa80
  modified: 2026-08-03T07:13:59.554Z
---

# QM 完全ローカル構築（akitaken・2026-08-03 稼働開始）

「会社まるごと管理」用のマルチプレイヤーエージェント基盤 [yc-software/qm](https://github.com/yc-software/qm) を akitaken に構築。個人事業の経理・メール・書類管理の土台。

## 構成（この選択には理由がある。変える前に読むこと）

- **ソース直起動**（`/data/kita/qm/qm`、ブランチ `local-deploy`）。**qm CLI の docker target は使えない** — sandbox が Fly.io 必須で完全ローカル不可（core イメージに docker CLI/socket が無い）
- **core は署名付き必須**（CORE_SIGNING_SECRET あり）。無署名にすると keychain のターン注入・capability・cron ツールが `signingSecret && apiBaseUrl` ゲート（src/core/orchestrator.ts:1027,1380,1437）で全滅し **Google 連携が成立しない**。加えて `x-admin-actor` 生ヘッダで admin 全権が取れる穴が開く（sandbox からも到達可能）
- **認証は「候補B」**: web-ui に CORE_SIGNING_SECRET を渡しつつ `NODE_ENV=test` + `ALLOW_UNSIGNED_TEST_IDENTITY=1` で cookie サインインを維持（plugins/web-ui/server/index.ts:34-36 のテストシーム）。**git pull 後は必ず `grep ALLOW_UNSIGNED_TEST_IDENTITY plugins/web-ui/server/index.ts` で存続確認** → 消えていたら portal+auth 4プロセス構成（アネックス）へ移行
- **HARNESS=claude + CLAUDE_CODE_OAUTH_TOKEN**（`claude setup-token`・1年有効・`/data/kita/qm/.secrets/`）。MODEL_PROVIDER 宣言と ANTHROPIC_API_KEY 設置は禁止（宣言すると API キーが必須化）。**この経路は未文書だが実証済み**（HOME 隔離＋APIキー無しで応答確認）
- ポート: core 8788（全IF ← sandbox が host-gateway 経由で到達するため 127.0.0.1 にすると壊れる）/ web-ui 8789（127.0.0.1）/ Postgres 55433（127.0.0.1）
- 二重 URL: `PUBLIC_API_URL=http://host.docker.internal:8788`（sandbox→core）と `PUBLIC_WEB_URL=https://akitaken.tail7c9257.ts.net`（ブラウザ）は**別物**
- 公開は **tailscale serve（tailnet限定）**。**Funnel は絶対に有効化しない** — cookie 認証は「誰として入るか」しか制限せず「誰が入るか」は制限しないので、公開＝全世界に乗っ取り許可

## 運用

- systemd --user: `qm-core` / `qm-web` / `qm-pgdump.timer`（毎日04:30 pg_dump→`/data/kita/qm/backups`・30日保持）
- 秘密は `/data/kita/qm/.secrets/`（mode600）と `.env` 2ファイル。**pg_dump に含まれないので別途バックアップ必須**。CONNECTOR_SECRET_KEY を失うと keychain 全滅
- 経理: `keiri-ledger` スキル（`/data/kita/qm/skills/`、`PLUGIN_SKILLS_DIRS` で読込。SKILLS_SEED_DIR 上書きは標準18スキルを消すので禁止）＋ 月次 cron `0 9 1 * *` Asia/Tokyo。**会計SaaS連携は存在しない**ので Sheets台帳＋Gmail＋publish内製ダッシュボードで組む
- **Google OAuth は publishing status = In production 済み（2026-08-03）→ 7日失効は解消**。7日失効は Testing 限定の仕様で、審査(verification)の有無とは無関係。「Publish app」ボタンだけで解除でき、Personal Use 例外（100ユーザー未満）で審査不要（[公式](https://support.google.com/cloud/answer/13464323)）。**審査申請は不可能かつ不要** — ts.net は Public Suffix List 収載で top private domain が `tail7c9257.ts.net`＝Tailscale 所有、Search Console の DNS ドメイン所有権を証明できない。加えて Gmail は restricted scope で CASA（年次・第三者評価）が必要になり個人利用には過剰
- 残る失効要因: **Googleアカウントのパスワード変更**（Gmailスコープ含むため）／6か月未使用／同一クライアントで refresh token 100本超過。再接続は `POST /api/connectors/google/start` の authorizeUrl を発行して開く（Testing 時代に発行したトークンは古い期限が残るので、公開ステータス変更後は必ず取り直す）
- publishing status の変更・審査申請は **Console UI 専用**（API/gcloud に該当サーフェスが存在しない。IAP oauth-brands は 2026-03-19 に停止済み）
- git pull 前に pg_dump。pull 後は npm ci → typecheck → sandbox:local:build → web-ui build

## 踏んだ罠

- **Codex を `-s workspace-write` で起動するとネットワーク/docker/systemd/$HOME が全部塞がれて何もできない** → ユーザー既定（config.toml の danger-full-access）で起動する＝ `-s` フラグを付けない
- iOS/Windows でサインインループ: ①入力欄が自動大文字化＋許可リストが大小区別（修正済み commit 1d3b809）②**web-ui 再ビルド後はブラウザの強制リロード（Ctrl+Shift+R）が要る**
- `tailscale cert` は **cwd に秘密鍵を書き出す** → `~/.claude`（自動push される公開リポ）で実行してはいけない
- `tailscale serve` は要 root。`sudo tailscale set --operator=$USER` を一度だけ人手で実行（sudo パスワードは代行不可）
- Playwright は anaconda 汚染で起動不可 → `env -u LD_LIBRARY_PATH -u LD_PRELOAD`

関連: [[codex-token-invalidation-stale-daemons]]
