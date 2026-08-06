---
name: feedback_hooks_crossshell_dispatch
description: settings.json のフック起動は Bash 構文だと PowerShell セッションで全滅する。node dispatch.js 経由のクロスシェル起動に統一済み（2026-08-06）
metadata:
  node_type: memory
  type: feedback
---

`~/.claude/settings.json` の hooks 起動コマンドを **Bash 構文（`if command -v X >/dev/null 2>&1; then ...; fi`）で書いてはいけない。** Claude Code の Windows セッションはシェルが **PowerShell** のことがあり、その場合コマンド文字列は PowerShell にそのまま渡され、`MissingOpenParenthesisInIfStatement` のパースエラーで **1行も実行されない**（ExitCode 1・副作用ゼロ。無害プローブで実測確認）。

**Why:** 症状が「Stop hook error の文字化け」としてしか見えないため、**安全ガードと記憶注入が全部死んでいても気づけない**。2026-08-06 の実害では block-dangerous / protect-files / guard-file-revert / memory-inject / auto-pull / auto-push など**15本すべてが無効**だった。文字化けは PowerShell の日本語エラーが CP932 のまま UTF-8 として読まれた二次症状にすぎない。

**How to apply:** 起動コマンドは条件分岐を持たせず、両シェルで同一に解釈される単一形式にする。現行の正解は

```
node "$HOME/.claude/hooks/dispatch.js" <hook-name>
```

- PowerShell にも `$HOME` 自動変数があるので、この1行が bash / PowerShell / Git Bash すべてで通る。
- OS 判定・スクリプト選択（`.mjs` → `.ps1`/`.sh` → `.py`）・stdin/stdout/終了コードの素通しは `hooks/dispatch.js` が担う。**終了コードは丸めない**（PreToolUse の 2 = ブロックが死ぬ）。
- 対象スクリプトが無い OS では黙って exit 0（Linux で `.ps1` しか無いフックは静かにスキップ。akitaken に pwsh は無い）。

**同一マシンにシェルの違う複数セッションが同時に存在しうる**（このWindows機では PowerShell セッションと Git Bash セッションが並走していた。bash は PATH 上に無く `%LOCALAPPDATA%\Programs\Git\bin\bash.exe`）。「片方で動いているから直っている」は誤り。**両方で検証する。**

**未解決の別穴（2026-08-06 時点）**: PreToolUse の `matcher: "Bash"` は **PowerShell ツールでは発火しない**（`~/.claude/command-log.txt` が PowerShell セッションの呼び出しで一切伸びないことで実測）。つまり修正後も block-dangerous / log-commands / warn-tu-encoding / warn-bash-overwrite / guard-destructive-and-resolution は PowerShell セッションでは無効のまま。matcher を `Bash|PowerShell` に広げる必要がある。

関連: [[project_claude_sync_windows_linux]] [[feedback_autosync_hook_divergence_deadlock]] [[feedback_ps1_hook_ascii_only]]
