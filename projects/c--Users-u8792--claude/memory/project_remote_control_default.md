---
name: project_remote_control_default
description: Remote Control を Claude Code 起動時にデフォルト有効化。公式の永続フラグは無いので PowerShell profile のラッパー関数で実現。脱出口は claude-plain
metadata:
  type: project
---

Claude Code の Remote Control（リモート操作）を**毎回の起動でデフォルト有効**にするための設定。

## 背景・制約
- Remote Control は `claude --remote-control` で有効になるが、**「常に有効」にする公式の永続設定キーは存在しない**（`settings.json` にフラグが無い）。`~/.claude/settings.json` の `remote` 等は接続情報であって自動有効化はしない。
- そのため、起動コマンド自体にフラグを毎回付与する形で永続化する。

## 解決（PowerShell profile のラッパー）
PowerShell の profile に `claude` を上書きするラッパー関数を定義し、`claude.cmd` を `--remote-control` 付きで呼ぶ:

```powershell
function claude { claude.cmd --remote-control @args }
```

- これで `claude` と打つだけで常に Remote Control 有効で起動する。`@args` でユーザーが付けた追加引数はそのまま透過される。
- **実体の .cmd を直接呼ぶ**点が重要（関数名 `claude` と実体 `claude.cmd` を区別しないと自己再帰になる）。

## 脱出口（無効で起動したいとき）
Remote Control を**付けずに**起動したい場合のために `claude-plain` を別途用意する（素の `claude.cmd` をそのまま呼ぶエイリアス／関数）。デバッグや Remote Control が邪魔なときに使う。

**Why:** 公式に永続フラグが無いため、起動経路（PowerShell profile）でフラグを注入するのが唯一の安定手段。GUI 設定や settings.json では実現できない。

**How to apply:** Remote Control がいつの間にか無効になっている／毎回手で付けているなら、PowerShell profile（`$PROFILE`）にラッパー関数があるか確認する。新規 PC セットアップ時はこのラッパー関数と `claude-plain` 脱出口を profile に追加する。関連: [[feedback_ps1_hook_ascii_only]]（profile/フック .ps1 は ASCII 限定、日本語直書きは文字化けで構文破壊）。
