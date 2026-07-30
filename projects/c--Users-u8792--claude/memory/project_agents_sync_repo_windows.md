---
name: agents-sync-repo-windows
description: スキル正本github.com/kosukekita/agentsの3OS対応完了(2026-07-30)。Windows修復済み・同期タスク無音化済み・~/.claudeのskills/追跡除外済み。Mac到着時はclone+install.shのみ(launchd実機検証TODO)
metadata: 
  node_type: memory
  type: project
  originSessionId: dfa0f49a-e019-46aa-bec2-d0f781950a94
  modified: 2026-07-30T08:30:45.050Z
---

スキル正本は **github.com/kosukekita/agents**（agents-sync-repo）。Claude Code と Codex が同一ファイルを共有し、各機2分毎に自動 commit/rebase/push 同期。2026-07-30 に3OS対応が完了した状態:

- **Windows（u8792）**: 修復済み。ジャンクション53本＋AgentSkillsSync タスク稼働。タスクは **wscript.exe + scripts/run-sync-hidden.vbs 経由の完全無音実行**（素の powershell.exe 起動だと2分毎にコンソールが出る。LogonType は cmdlet では `Interactive`。`InteractiveToken` は XML 側の表現で New-ScheduledTaskPrincipal に渡すと実機エラー）。検査は `tests/windows-hidden-task.ps1 [-Live]`
- **macOS**: `launchd/com.kosukekita.agent-skills-sync.plist`＋install.sh の Darwin 分岐を実装済み（clone → install.sh の2手）。**launchd 部分は実機未検証**（Mac 近々導入予定・2026-07-30時点）。到着時に `launchctl print gui/$(id -u)/com.kosukekita.agent-skills-sync` と sync.log で確認する
- **sync.sh のロック**: flock 非依存（macOS に flock コマンドが無い）。`scripts/portable-lock.sh`（mkdir＋pid＋stale の mv 原子奪取）。テストは `tests/lock.sh`（flock 不可視 PATH で並列・stale を実測）
- **~/.claude リポの skills/ は追跡除外済み**（コミット 78392c6）。リンクは各 OS の installer が生成する機械生成物で git に載せない（Linux絶対パスsymlinkの同期が2026-07-29にWindows全スキルを壊した再発防止）。**この削除コミットを pull した他の同期機（akitaken・Spine 等）はスキルリンクが消えるので installer を1回再実行する**
- akitaken の ~/.claude は未コミットのローカル編集（MEMORY.md 等）で同期停止中の債務あり（2026-07-30時点・手つかず。解消はakitaken上のセッションで）
- install.ps1 の既知のクセ: 再実行時にジャンクションの同一性判定が誤って全件バックアップ→同一ターゲットへ再作成する（結果は無害・毎回 backups/ が増える。将来直すなら Add-SkillJunction の ExistingTarget 計算）
- スキル編集は `%LOCALAPPDATA%\agents-sync-repo`（Win）/ `~/.local/share/agents-sync-repo`（Linux/Mac）で行い、~/.claude/skills 側は触らない。関連 [[claude-sync-windows-linux]]
