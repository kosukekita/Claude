---
name: publishing-security-skill
description: publishing-security-reviewスキル作成(2026-07-30)。RED実測=検出は元々できるが「既に露出中だから」で公開強行が真の失敗。codex-securityは$23.40/25分・Windows不可・git履歴を見ない
metadata: 
  node_type: memory
  type: project
  originSessionId: dfa0f49a-e019-46aa-bec2-d0f781950a94
  modified: 2026-07-30T12:03:09.734Z
---

**publishing-security-review** スキルを作成（2026-07-30・agents リポ `0c20aac`）。openai/codex-security を参考にしたが、チェックリストは上流 README ではなく**自前の RED 実測**から作った。

**最大の学び: RED が1回目に「合格」したこと。** 平文 `sk_live_` や `process.env` 丸出しエンドポイントを仕込んでも、エージェントは元々検知して公開を止める。**検出能力を教えるスキルは無駄**だった。テストを難しく作り直し（既に稼働中のサイト・小改修依頼・git履歴に埋めた鍵・依存CVE・認可漏れ）、そこで初めて本命の失敗が出た: **critical 2件を検知しながら公開実行**、理由は「既に本番で露出中だからリスクは減らない」。→ **止める目的はリスク削減ではなくユーザーに決定機会を渡すこと**、という反論をスキルの筆頭に置いた。GREEN/REFACTOR とも 3/3 合格。

**codex-security の実測（2026-07-30・小規模Next.js 10ファイル）**:
- **$23.40 USD / 25分36秒 / 1回**。カバレッジ表示は `partial`
- **Windows では実行不可**（上流バグ: `samePluginFile()` が `lstat().dev=0` と `fstat().dev` を比較し必ず不一致 → `Invalid Codex plugin directory`）。バージョンを変えても再現。整合性チェックの改変は検査の無効化なのでしない
- **git 履歴を見ない**（レポートに `Excluded .git/**` と明記）。手動観点2が見つける critical を構造的に取りこぼす。逆に手動に無い指摘（無制限読み出しによる資源枯渇）は出す。**上位互換ではなく併用前提**
- Linux 実行には Node 22.13+ が要る（Ubuntu 24.04 の既定 v20 では不足 → `~/.local/node22` にユーザー領域展開）。SSH 経由は切断で SIGTERM されるので `setsid nohup` で分離
- **ユーザー確定**: 観点7は「重大公開のみ必須」（初回ローンチ／認証・決済・PII 経路の追加変更／権限変更）。小改修は任意。観点1〜6は毎回必須

**同時に実施**: `~/.claude/CLAUDE.md` 冒頭に「ルールの優先順位」節を追加（ユーザー指示が最上位、セキュリティは提示必須だが決定はユーザー、プロジェクト固有ルールは下位）。詳細は [[codex-global-rules-wiring]]。
