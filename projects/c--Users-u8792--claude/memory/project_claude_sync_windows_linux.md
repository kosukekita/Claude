---
name: project_claude_sync_windows_linux
description: ~/.claude をGitHubで同期しているPCはWindowsとLinuxの2種。フック・設定はWin/Linux両対応必須
metadata:
  node_type: memory
  type: project
---

ユーザーの `~/.claude`（グローバル設定リポジトリ、GitHub同期）を共有しているマシンは **Windows と Linux の2種**（ユーザー明言, 2026-07-03）。

**含意（設定・フックを触るとき常にこの前提で判断する）:**
- フックは必ず **Win版(.ps1) と Linux版(.sh) の両方**を用意し、ロジックを lockstep で揃える（片方だけ直すと、もう片方のOSで動くときに古い挙動が残り不整合になる。実際 auto-pull/push の .sh が .ps1 より古い旧ロジックのまま取り残されていた → [[feedback_autosync_hook_divergence_deadlock]]）。
- settings.json の hooks 起動コマンドは `if command -v powershell` で .ps1、else で .sh を呼ぶ分岐になっている。
- グローバル記憶スラグは2つ存在: `c--Users-u8792--claude`（Windows）と `-home-kita--claude`（Linux, ホームは /home/kita）。両者は同じ GitHub リポジトリ経由で同期される（.gitignore が `projects/*--claude/memory/**` だけ un-ignore）。
- シェルスクリプト(.sh)は **必ず LF 改行**。core.autocrlf=true の Windows で CRLF 化すると Linux で `bad interpreter: ...^M` で即死する。`.gitattributes` に `*.sh text eol=lf` を入れて保護済み。
- .ps1 に日本語を入れるなら BOM付きUTF-8必須（cp932誤読でパースエラー）。ただし ASCII-only の .ps1 は BOM不要 → [[feedback_ps1_needs_utf8_bom_on_windows]]。
- ツール引数のパスは常にフォワードスラッシュで書く（`C:/Users/u8792/...`）。バックスラッシュだと u8792 が化け漢字 U+8792 に化ける → [[feedback_u8792_path_unicode_escape]]。

関連: [[feedback_autosync_hook_divergence_deadlock]] [[project_mcp_path_portability]]
