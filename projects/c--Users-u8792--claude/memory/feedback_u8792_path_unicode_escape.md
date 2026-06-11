---
name: feedback-u8792-path-unicode-escape
description: このPCのパス C:\Users螒 はツール呼び出しで 螒 がUnicodeエスケープ解釈され C:\Users螒 に化ける。ツールのpathは常にフォワードスラッシュで書く
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 213c11d7-5066-46e7-968c-ac34498cfd29
---

このPCのユーザー名は `u8792`。バックスラッシュ区切りの絶対パス `C:\Users螒\...` をツール（Read/Write/Edit/Grep/Glob/Bash/PowerShell の path・command 引数）に渡すと、`螒` が **JSON の Unicode エスケープとして解釈され `螒`（U+8792）に化け**、実在しない/別の場所 `C:\Users螒\...` を読み書きしてしまう。

**Why:** ツール引数は JSON 文字列として渡るため、`\u` + 16進4桁のパターンがエスケープシーケンスとして成立してしまう。ユーザー名がたまたまこのパターンに一致する。化けた書き込みは**エラーにならず静かに成功**するため、メモリファイル24件＋プランが `C:\Users螒\.claude\` に蓄積していた（2026-06-11 に全件を本来の場所へ救出し、化けディレクトリは `~/.claude/backups/mojibake-rescue-2026-06-11/` に隔離済み）。

**How to apply:**
- ツールに渡すパスは**常にフォワードスラッシュ**で書く: `C:/Users/u8792/.claude/...`（全ツールで動作確認済み）
- PowerShell コマンド内では `$env:USERPROFILE` でパスを組み立てる（コマンド文字列にも `螒` を直書きしない）
- 化けパスを調査・操作する必要があるときは `[char]0x8792` で構築し `-LiteralPath` を使う
- Read の内容やサイズが期待と食い違ったら、まずパス化けを疑う（`Get-Item` の `.Length` と比較）
- 関連: [[project-mcp-path-portability]]（.mcp.json は `${USERPROFILE}` を使う）。Osteoporosis プロジェクトに症状ベースの旧メモリ `tool-path-mojibake-use-powershell` あり（本メモリが根本原因版）
