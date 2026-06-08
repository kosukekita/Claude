---
name: feedback_ps1_hook_ascii_only
description: ~/.claude/hooks の .ps1 に日本語メッセージを直書きすると文字化けで構文破壊しフック全体が死ぬ。ASCII限定にする
metadata:
  type: feedback
---

`~/.claude/hooks/` 配下の PowerShell フック（.ps1）に**日本語（マルチバイト）メッセージを直書きしてはいけない**。ASCII（英語）のみにする。

**Why:** 2026-06-08、block-dangerous.ps1 に pip ブロックを追記した際、`Write-Error "...グローバル pip install は禁止です..."` と日本語を入れたところ、ファイルの保存エンコーディングと不一致で文字化けし、PowerShellパーサが文字列終端を見失って**フック全体が構文エラーで起動即死**した。結果、追加したpipブロックだけでなく、既存の rm -rf / git push --force ブロックまで全て無効化されていた（テストで `rm -rf` すら exit 1 になり発覚）。

**How to apply:**
- フック内のメッセージ・コメントは**英語（ASCII）で書く**。
- 編集後は必ず検証する: (1) `[System.Management.Automation.PSParser]::Tokenize()` で構文チェック、(2) 置換文字 U+FFFD の混入チェック、(3) 代表コマンドで実挙動テスト（ブロック対象=exit 2、許可対象=exit 0、無関係コマンドで誤発火しないこと）。
- フックのstdin/exit規約: stdinからJSONを受け `tool_input.command` 等を取得。exit 2=ブロック（stderrがClaudeへ）、exit 0=通過。
- **警告のみ（ブロックしない）フック**では `Write-Error` は `$ErrorActionPreference="SilentlyContinue"` で握りつぶされ stderr に出ない。`[Console]::Error.WriteLine(...)` で直接 stderr に書く。
- 新規フックは性質ごとに別ファイルにする（ブロック専用=block-dangerous、警告のみ=warn-*、ログ=log-commands）。

関連: [[feedback_hook_vs_prose_audit]]
