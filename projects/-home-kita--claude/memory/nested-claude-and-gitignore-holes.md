---
name: nested-claude-and-gitignore-holes
description: ~/.claude/.claude ネストはgit無視済みでGitHubに漏れない(再生成は正常)／公開リポの本当の穴はgenerated等の未ignore作業生成物
metadata: 
  node_type: memory
  type: project
  originSessionId: f7c667f6-ec8d-4525-83ce-a1aff993d10b
---

`~/.claude` リポ（公開 GitHub `kosukekita/Claude`）の同期に関する確定事実。

**ネスト `~/.claude/.claude/`（`scheduled_tasks.lock` 等）について:**
- GitHub には**一度も漏れていない**。`.gitignore` の `.claude/`（行10）でブロック済み、かつ `hooks/auto-push.sh` は `git add -A` ではなく**ホワイトリスト方式**（`.gitignore .mcp.json CLAUDE.md settings.json skills hooks bin` + `projects/*--claude/memory`）なので拾わない。
- ネストの**再生成は正常動作**。cwd=`~/.claude` で稼働中の別 claude プロセス（scheduled-tasks 機能）が cwd 配下に `scheduled_tasks.lock` を置くため、削除しても生きている限り作り直される（削除4分後の復活を実証済み）。
- 実害ゼロ（GitHub漏れなし・動作正常）。ユーザー判断は**「放置」**。再調査・自動削除フックは不要。

**本当に塞ぐ価値があったのはこちら（2026-06-26 対処済み）:**
- `generated/`（NSFW画像・動画）, `paste-cache/`, `chrome/`, `image-cache/`, `SCRATCHPAD.md` が `.gitignore` 未登録だった＝手動 `git add .` で公開リポに漏れる穴。auto-push は無視するが手動addは別。
- → `.gitignore` の「Local State」直後に追記して恒久封鎖（commit `8429e2d`）。`.gitignore` の**行末コメントは効かない**（パターン扱いになる）ので注意。

関連: [[mcp-cross-pc-and-claude-json-race]]
