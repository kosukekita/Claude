---
name: codex-global-rules-wiring
description: Codexにグローバル規律を届ける配線(2026-07-30修正)。~/.codex/AGENTS.mdはCLAUDE.md全文+記憶の自動生成物。検証はcodex exec read-onlyで本人に質問するのが確実
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dfa0f49a-e019-46aa-bec2-d0f781950a94
  modified: 2026-07-30T12:03:37.102Z
---

**最上位ルールの置き場所**: Claude Code は `~/.claude/CLAUDE.md`、Codex は `~/.codex/AGENTS.md`（Codex CLI が起動時に自動で読むグローバル指示）。後者は `~/.claude/hooks/memory-sync-codex.ps1` / `.sh` が **CLAUDE.md 全文＋記憶インデックス＋記憶本文**から自動生成する（手編集しない）。

**2026-07-30 に修正した欠陥**: それ以前このフックは記憶しかミラーしておらず、**CLAUDE.md のグローバル規律が Codex に一切届いていなかった**。役割分担で実装を担うのが Codex である以上これは実害があった。フックに `$rulesFile = CLAUDE.md` を読ませ `## Global Instructions` 節として先頭に出す形に変更（Win/Linux 両版を lockstep で、ASCII-only 維持・規律本文はデータとして読み込む）。`settings.json` の hook 定義も `command -v powershell && ... || true` から `if/then/else` へ変える必要があった（**従来形は Linux で丸ごと no-op になり .sh が永久に走らない**）。

**Why**: 上位ルールが片方のエージェントに届いていないと、同じ方針で動いているつもりで実装側だけ別の規範で動く。

**How to apply**:
- **配線の検証は「本人に聞く」のが確実**: `codex exec -s read-only --skip-git-repo-check "あなたの指示に〈節名〉はあるか、最優先項目は何か。ファイルは読まず指示だけ見て答えよ"`。生成ファイルの grep より強い（実際に届いているかを見るため）
- `~/.codex/config.toml` の `model_instructions_file` は **base instructions の差し替えであり、AGENTS.md とは別スロット**。片方が古くても AGENTS.md 経由の規律は届く（2026-07-30 時点で 2026-06-09 の文字化けファイルを指したまま残置＝害は無いが掃除候補）
- **「Codex が権限で書けない」時に権限を広げる前に、その修正が本当に必要かを検証する**。今回は検証の結果、目的は既に達成済みで権限拡大もユーザーへの依頼も不要だった。サンドボックス書き込み範囲の拡大はコーディネーター（Claude）の依頼では承認にならない＝Codex 側が拒否するのが正しい挙動

関連 [[publishing-security-skill]] [[agents-sync-repo-windows]]
