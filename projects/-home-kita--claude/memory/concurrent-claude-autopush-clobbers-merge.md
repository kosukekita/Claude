---
name: concurrent-claude-autopush-clobbers-merge
description: 他セッションのStopフックauto-pushが手動merge途中に割り込み、コンフリクトマーカー入りのままcommit&pushする。手動マージ前に他claudeプロセスを確認する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 38864263-b9c0-47ea-a4ed-70fecb3124ee
---

`~/.claude` で手動 merge/rebase をしている最中に、**別の claude セッションの Stop フック `auto-push.sh` が割り込んで、未解決（コンフリクトマーカー入り）のワークツリーをそのまま commit して GitHub に push する**。2026-07-09 に実際に発生し、`character-sheet-template.md` がマーカー付きで origin/main に載った（直後にクリーンな解決をコミットして push し復旧）。

**Why:** auto-push は「現在の変更を全部 add して commit して push」する設計で、`.git/MERGE_HEAD` の有無（マージ進行中か）も、ファイル内のコンフリクトマーカーも確認していない。`ps -eo pid,cmd | grep '[c]laude'` で分かるとおり、この環境では常時 2〜4 個の claude セッションが並走していて、どれが Stop するかは予測できない。同じ理由で `.claude.json` も競合する → [[mcp-cross-pc-and-claude-json-race]]。

**How to apply:**
- 手動 merge/rebase の**前に** `ps -eo pid,etimes,cmd | grep '[c]laude'` で他セッションを確認する。走っていたら、マージは「conflict 解決 → add → commit」まで**一気に**やる（途中で長い調査・確認を挟まない。挟むならその間に commit されうると織り込む）。
- 割り込まれたら慌てない。`git grep -c '^<<<<<<<' HEAD` で被害ファイルを特定し、正しい解決を上書きコミットして push すればよい（`--force` 不要）。ワークツリーの解決内容は残っている。
- 完了確認は `git rev-list --count origin/main..HEAD` と `git rev-list --count HEAD..origin/main` が両方 0、かつ `git grep -c '^<<<<<<<' origin/main` が空であること。
- Win/Linux 分岐の解消手順そのものは [[hf-weekly-model-watcher]] ではなく Windows スラグの `feedback_autosync_hook_divergence_deadlock` が正本（fetch → backup タグ → rebase/merge → push、`--force` は絶対不使用）。33 コミット規模で片側がファイルを新規追加している場合は rebase だと各コミットで add/add 衝突が再発するので **merge の方が安全**（衝突解決 1 回で済む）。
