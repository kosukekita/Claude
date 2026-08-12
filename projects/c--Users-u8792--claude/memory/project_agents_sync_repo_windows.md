---
name: agents-sync-repo-windows
description: スキル正本github.com/kosukekita/agentsの3OS対応(2026-07-30)。Win(u8792)は2026-08-03にskills/消失が発覚しinstall.ps1再実行で復旧済み。~/.claudeのskills/追跡除外済み。Mac到着時はclone+install.shのみ(launchd実機検証TODO)
metadata: 
  node_type: memory
  type: project
  originSessionId: dfa0f49a-e019-46aa-bec2-d0f781950a94
  modified: 2026-08-12T04:31:16.251Z
---

スキル正本は **github.com/kosukekita/agents**（agents-sync-repo）。Claude Code と Codex が同一ファイルを共有し、各機2分毎に自動 commit/rebase/push 同期。2026-07-30 に3OS対応が完了した状態:

- **Windows（u8792）**: 【2026-08-03 実測】7/30の「修復済み」は実機で保持されていなかった。8/3時点で ~/.claude/skills・~/.agents/skills・AgentSkillsSync タスク・%LOCALAPPDATA%\agents-sync（状態dir）が**すべて不在**（skills/ 消失の直接原因は 7/31 09:01 の auto-pull が untrack コミット 78392c6 を rebase 取り込みし、git が追跡ファイル削除として働き木の skills/ を除去したこと。repo 内ファイルが全て 7/31 09:25 刻印＝その直後に repo 側も git で復元された形跡あり）。install.ps1 再実行で復旧: junction 54本(claude)/52本(codex)・タスク登録・sync.log「Synchronization completed」まで検証済み。**教訓: 「設置済み」はタスク登録(Get-ScheduledTask)・junction実在・state dir の3点で検証してから記録する**。タスクは **wscript.exe + scripts/run-sync-hidden.vbs 経由の完全無音実行**（素の powershell.exe 起動だと2分毎にコンソールが出る。LogonType は cmdlet では `Interactive`。`InteractiveToken` は XML 側の表現で New-ScheduledTaskPrincipal に渡すと実機エラー）。検査は `tests/windows-hidden-task.ps1 [-Live]`
- **Windows で同期が「静かに」止まる第一容疑者＝git identity 未設定**【2026-08-12 実測・修正済み】: DESKTOP-5C4JVOB の agents-sync-repo は user.name/user.email が local にも global にも無く、`git commit` が `Author identity unknown` で失敗 → sync.ps1 が exit 1。**症状が出るのは「コミットすべき変更が発生した時だけ」**で、無変更時は fetch/push が no-op で成功するため sync.log は "Synchronization completed" が並び、正常に見える（＝スキルを編集するまで気付けない）。作業木は `git add -A` 済みの staged のまま放置され、GitHub には何も上がらない。切り分けは `%LOCALAPPDATA%\agents-sync\sync.log` の `ERROR: git commit ... failed` と `Get-ScheduledTaskInfo AgentSkillsSync` の LastTaskResult=1。修正は `git -C %LOCALAPPDATA%\agents-sync-repo config --local user.name kosukekita` / `user.email kosukekita@users.noreply.github.com`（~/.claude リポは local に同じ identity を持っていたので、この repo だけ欠けていた）。**スキル/記憶ファイルを編集したら、~/.claude の git status だけ見て済ませない**（skills/ はジャンクションで別リポジトリ = 実体は agents-sync-repo 側）
- **macOS**: `launchd/com.kosukekita.agent-skills-sync.plist`＋install.sh の Darwin 分岐を実装済み（clone → install.sh の2手）。**launchd 部分は実機未検証**（Mac 近々導入予定・2026-07-30時点）。到着時に `launchctl print gui/$(id -u)/com.kosukekita.agent-skills-sync` と sync.log で確認する
- **sync.sh のロック**: flock 非依存（macOS に flock コマンドが無い）。`scripts/portable-lock.sh`（mkdir＋pid＋stale の mv 原子奪取）。テストは `tests/lock.sh`（flock 不可視 PATH で並列・stale を実測）
- **~/.claude リポの skills/ は追跡除外済み**（コミット 78392c6）。リンクは各 OS の installer が生成する機械生成物で git に載せない（Linux絶対パスsymlinkの同期が2026-07-29にWindows全スキルを壊した再発防止）。**この削除コミットを pull した他の同期機（akitaken・Spine 等）はスキルリンクが消えるので installer を1回再実行する**
- akitaken の ~/.claude は未コミットのローカル編集（MEMORY.md 等）で同期停止中の債務あり（2026-07-30時点・手つかず。解消はakitaken上のセッションで）
- install.ps1 の既知のクセ: 再実行時にジャンクションの同一性判定が誤って全件バックアップ→同一ターゲットへ再作成する（結果は無害・毎回 backups/ が増える。将来直すなら Add-SkillJunction の ExistingTarget 計算）
- スキル編集は `%LOCALAPPDATA%\agents-sync-repo`（Win）/ `~/.local/share/agents-sync-repo`（Linux/Mac）で行い、~/.claude/skills 側は触らない。関連 [[claude-sync-windows-linux]]
