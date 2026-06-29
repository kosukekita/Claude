---
name: feedback_autosync_hook_divergence_deadlock
description: ~/.claude のauto-pull/auto-pushフックがff-onlyとpush握り潰しで乖離からデッドロックする問題と恒久修正
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f0bd5198-80e9-4600-a3b2-c4a01583f314
---

~/.claude を複数PC(Win/Linux)でgit同期する auto-pull.ps1(SessionStart)/auto-push.ps1(Stop) は、放置すると ahead/behind が無限拡大しデッドロックする設計欠陥があった(実際 behind 111まで膨張)。2026-06-29 に恒久修正し全同期完了。

**Why(根本原因):**
- auto-push: `git push 2>$null` が rejected(リモート先行)でも握り潰し正常終了 → ローカルにコミットだけ残り ahead 増加。
- auto-pull: `git pull --ff-only origin main` のみ → ローカル先行コミットが1つでもあると ff 不可で黙って no-op → behind 解消されず。
- 両者が噛み合い、一度 push 失敗すると双方とも自動回復できず乖離が単調増加。`$ErrorActionPreference=SilentlyContinue`＋`2>$null`＋`exit 0` で全失敗が無言化し誰も気づかない。
- 隠れた罠: auto-pull の stash 判定 `git status --porcelain` が真でも、未追跡ファイル(chrome/・paste-cache/)だけだと `git stash push` は未追跡を stash しないため `$stashed=$true` のまま既存の別 stash を誤って pop する。

**How to apply(修正の要点):**
1. auto-pull: `--ff-only` を `git -c core.editor=true rebase --no-autostash --no-rerere-autoupdate origin/main` に置換。直後に `.git\rebase-merge`/`.git\rebase-apply` の存在で競合検知→`git rebase --abort` でクリーンに中断(非対話hookで競合一時停止して30sタイムアウト即死を防ぐ)。
2. auto-push: push後 `if ($LASTEXITCODE -ne 0)` で fetch+rebase してから1回だけ再push。競合時はabortしてコミットはローカルに残し次回リトライ。
3. stash判定は `git status --porcelain --untracked-files=no`(未追跡除外)。復元は `pop` でなく `apply`成功時のみ`drop`。
4. `--force` は絶対不使用(未pushのローカルコミットのrebaseは公開履歴を書き換えない)。`$LASTEXITCODE`はnative exe(git)なのでSilentlyContinue下でも有効。ASCII-only維持。

**乖離が既に起きた時の解消(検証済み・安全):**
`git fetch origin` → `git tag backup/pre-rebase-<date> HEAD` → `git rebase origin/main`(競合しないことをmerge-treeや使い捨てworktreeで事前確認可) → `git push origin main`(--force不要) → 確認後 `git tag -d`。

検証はCodexセカンドオピニオン＋マルチエージェントワークフロー(使い捨てworktreeで実rebase試走しexit0確認)の2系統が一致。修正は ParseFile構文チェック＋実機実行(stash誤爆なし)でパス済み。関連: [[feedback_ps1_needs_utf8_bom_on_windows]] [[feedback_u8792_path_unicode_escape]]
