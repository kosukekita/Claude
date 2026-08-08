---
name: mf-cloud-api-qm-integration
description: マネーフォワード クラウド会計API/MCPをQMの経理へ統合する調査結果と確定事項。QMはリモートMCP不可→API直叩き+新スキル keiri-mf-journal で合意。プラン別の実質制約つき
metadata: 
  node_type: memory
  type: project
  originSessionId: c169736f-6a34-4c21-91cd-ba6543a125cc
  modified: 2026-08-08T23:39:35.342Z
---

# マネーフォワード クラウド × QM 経理統合（2026-08-09 調査・設計合意／**MF契約は保留中**）

きっかけは [Zenn記事](https://zenn.dev/yuichirominato/articles/dc8cf3915f1c6f)（2026-08-08・"idea"記事＝**コードもSKILL.mdも無い運用思想の紹介**）。領収書写真をClaudeに投げる→Vision抽出→インボイス検証→MCP経由でMF APIに仕訳登録＋証憑添付、という構成。

## 確定した設計（ユーザー決定 2026-08-09）

- **経路は「MF会計APIを直叩きするスクリプト」**。MCP経由ではない
- **統合先は新スキル `keiri-mf-journal`**（`/data/kita/qm/skills/` 配下。`PLUGIN_SKILLS_DIRS` に既に含まれるので配置だけで読まれる）。既存 `keiri-ledger` には**混ぜない**
  - 理由: ①現SKILL.mdが「Gmail・payout・経費・ダッシュボードは対象外」とスコープ宣言済みで書込先もSheets限定 ②冪等キーが二重化する（Sheets出典ID vs MF仕訳ID。*Sheets成功・MF失敗*の中間状態が壊れやすい）③keiri-ledgerは本番稼働中（月次cron＋PENDING人間チェックポイント）
- 責務2系統: **(A) 収入**=Sheets`収入`行→MF複式仕訳 ／ **(B) 経費**=領収書画像→Vision＋インボイス登録番号検証→MF仕訳＋証憑添付
- 二層構成は [[keiri-bookkeeping-threshold]] のとおり: **Sheets=一次記録／MF=会計帳簿**（複式仕訳・決算書・e-Tax）

## ★QMはリモートMCPに繋げない（調べ直し防止）

`qm/src/harness/claude-harness.ts:436-437` が **`strictMcpConfig: true` ＋ `mcpServers: { qm: server }`（in-process SDK MCP固定）**。外部リモートMCPを足すにはharness改修が要る。一方QMには `POLAR_TOKEN_MEDAI` をkeychain→env注入してAPI直叩きする `keiri-ledger` の型が既にあり、MF会計APIも同じ型に乗る＝**API直叩きが素直**。

## MF側の一次情報（2026-08時点）

- **公式リモートMCPサーバー**（2026-03-26 全プラン開放。Claude Code対応）
  - beta（4/1〜・認証延長＋自動再認証。Gemini CLI非対応）: `https://beta.mcp.developers.biz.moneyforward.com/mcp/ca/v3`
  - alpha（1時間ごと再認証）: `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3`
  - ツール: 仕訳一覧/新規作成/更新、入出金明細、勘定科目・補助科目・取引先・部門・税区分、残高試算表、推移表。**証憑アップロードはツール一覧に無い**（API仕様書での確認が未了）
- **API/MCPは追加料金ゼロ**。アプリポータルの登録・利用も無料。**プラン別のAPI可否は公式に記載なし**。ただし「登録可能な仕訳の件数等は有償プランの制限と同様」＝**APIは上限を回避しない**
- 事前準備: 管理コンソールの「全権管理」でアプリポータル利用開始 → ユーザーに「アプリ連携」＋「クラウド会計・確定申告」権限付与。権限は3種（システム管理者／アプリ開発／アプリ連携）
- 認可は **OAuth 2.0 のみ**（APIキー不可）。Bearerトークンで叩く

## プラン別の実質制約（確定申告・料金表 更新2026-06-18）

| | 無料 | パーソナルミニ 年10,800円 | パーソナル 年15,360円 |
|---|---|---|---|
| 仕訳登録/会計年度 | **50件** | 10万件 | 10万件 |
| 確定申告書 PDF/xtx出力(e-Tax) | ×（雑所得・控除のみなら可） | ○ | ○ |
| 証憑添付 | × | 1,000件 | 無制限 |
| ストレージ | 100MB | 100MB | 10GB |
| 仕訳帳・総勘定元帳・残高試算表のCSV出力 | × | **×** | ○ |

- **65万控除の最低ラインはミニ**（複式簿記10万件＋xtx出力で要件は満たす）。**推奨はパーソナル**＝ミニだと帳簿CSV出力が×で、Sheets台帳とMF帳簿の**突合による独立検証**ができない（自走ループの検証性が落ちる）。100MBは領収書PDFで即枯渇。差額は年4,560円
- **罠**: 料金表の「外部サービス ×」は**MAP経営社「MAP3」向けCSV出力**のことで、API/OAuthとは無関係。ミニでAPIが塞がれるわけではない
- **ユーザー報告(2026-08-09): 今は無料プランが無い** → 無料PoCは不可。再開時は1ヶ月無料トライアルでのPoCを検討（ただし注記※3「トライアル利用状態では確定申告書出力は使えない」）

## 状態

**MFの本格設定はユーザー判断で保留（2026-08-09）**。`keiri-ledger` は無変更で稼働継続。再開時は上記の設計合意から着手すればよい（プラン選定→アプリポータル→OAuth→`keiri-mf-journal`）。実装は規約どおりCodexへ委譲する。

関連: [[qm-local-deployment-akitaken]] / [[keiri-bookkeeping-threshold]]
