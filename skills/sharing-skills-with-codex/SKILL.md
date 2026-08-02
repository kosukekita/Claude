---
name: sharing-skills-with-codex
description: Claude Code のスキル・設定を Codex CLI など他エージェントでも使えるようにしたい時に使う。トリガー例=「Codexでもスキルを使いたい」「スキルをCodexと共有して」「~/.agents/skills に登録して」「Codexに同じ設定を入れたい」「新しいPCでCodex側のスキルが無い」。Use when the user wants Codex (or another agent reading ~/.agents/skills) to share the same skills or settings as Claude Code, or when a skill works in Claude Code but is missing in Codex. Do NOT use for: スキルの新規作成・改善（skill-writing）、Codexへの実装委譲の進め方（delegating-implementation-to-codex）。
---

# Sharing Skills with Codex（~/.claude/skills を Codex と共有する）

## 核心原則

**コピーではなくシンボリックリンクで共有する。** Codex は `~/.agents/skills/` を読む。ここへ `~/.claude/skills/*` をリンクすれば、`~/.claude` を git pull するだけで Codex 側も自動で最新になる（コピー方式は必ず乖離する）。ただし **Codex 専用に実体インストールされたスキル（agmsg 等）を上書きしてはならない**。

## 手順（各PCで1回＋スキル追加/削除時）

```bash
bash ~/.claude/bin/sync-skills-to-codex.sh --dry-run   # まず確認
bash ~/.claude/bin/sync-skills-to-codex.sh             # 同期実行
```

- スクリプトが正本（仕様・保護規則はスクリプト内コメント参照）。挙動: 全スキルをリンク／実体ディレクトリは保護スキップ／ソース削除済みのぶら下がりリンクは自動掃除／冪等
- リンク方式なので**内容の更新は pull だけで反映**される。再実行が必要なのは**スキルを追加・削除した時だけ**
- 新しいPCのセットアップ順: `~/.claude` を clone → `setup-codex-latest-model.sh`（Codex 本体と agmsg）→ 本スクリプト

## 設定（CLAUDE.md）の共有

- Codex の設定正本は `~/.codex/config.toml` と **AGENTS.md**（グローバル `~/.codex/AGENTS.md`・プロジェクト直下 `AGENTS.md`）
- **CLAUDE.md を丸ごと AGENTS.md にリンクしない**こと。CLAUDE.md には Claude 固有の規定（Skill ツール・フック・役割分担で「実装は Codex」等）が含まれ、Codex に読ませると矛盾する（Codex が「実装は Codex に委譲」を読む等）
- 共有したい規範（品質優先・revert防止・記憶の置き場等）は AGENTS.md に**要点だけ転記**する。プロジェクト固有の共有事項はプロジェクト直下の AGENTS.md へ

## 検証済み事項（2026-08-02・テスト6件PASS）

初回同期／冪等性（再実行で変化なし）／実体保護（agmsg 無傷）／ソース削除→リンク掃除／dry-run 無変更／リンク経由の SKILL.md 読取。※Codex 本体での発火確認はローカルPCで行う（`codex` 起動→スキル一覧または簡単な依頼で発動確認）

## 注意・限界

- スキル本文が Claude 固有機能（Skill ツール・Claude 専用ツール名・フック）に依存している場合、Codex では該当部分が動かない。共有前提のスキルは手順を汎用コマンドで書く
- 発火判定は SKILL.md の `name`/`description` に依存（形式は両者互換）。Codex で発火しない時は description のトリガー語を具体化する（skill-writing の CSO と同じ）
- このリポジトリのリモート実行環境（Claude Code on the web）には Codex も `~/.agents/` も無い。共有はローカルPC上の作業

## よくある失敗

| 失敗 | 対策 |
|---|---|
| cp で複製して以後乖離 | リンク方式（スクリプト）を使う |
| agmsg 等の実体を上書き | スクリプトの protect が防ぐ。手動で `ln -sfn` しない |
| スキル削除後もリンクが残り Codex がエラー | スクリプトが自動掃除。手動削除しない |
| CLAUDE.md を AGENTS.md に丸ごとリンクして矛盾 | 要点だけ AGENTS.md に転記 |

## 関連スキル

- **skill-writing**: スキル自体の作成・改善・発火チューニング
- **delegating-implementation-to-codex**: Codex への実装委譲の運用（agmsg・/goal）
