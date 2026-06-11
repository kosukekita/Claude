---
name: feedback-u8792-path-unicode-escape
description: バックスラッシュパス C:\\Users\\u8792 はツール引数中で \\u8792 がUnicodeエスケープ解釈され C:\Users螒 に化ける。ツールのpathは常にフォワードスラッシュで書く
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 213c11d7-5066-46e7-968c-ac34498cfd29
---

このPCのユーザー名は `u8792`。バックスラッシュ区切りの絶対パス（C:バックスラッシュUsersバックスラッシュu8792…）をツール（Read/Write/Edit/Grep/Glob/Bash/PowerShell の path・command 引数）に渡すと、「バックスラッシュ+u8792」の部分が **JSON の Unicodeエスケープとして解釈され `螒`（U+8792）に化け**、実在しない別の場所 `C:\Users螒\...` を読み書きしてしまう。この説明文自体も被害に遭った（書いたエスケープ表記が全部 `螒` に化けた）ため、あえてカタカナで表記している。

**Why:** ツール引数は JSON 文字列として渡るため、「バックスラッシュ+u+16進4桁」のパターンがエスケープシーケンスとして成立してしまう。ユーザー名がたまたまこのパターンに一致する。化けた書き込みは**エラーにならず静かに成功**するため、メモリファイル24件＋プラン8件が `C:\Users螒\.claude\` に蓄積していた（2026-06-11 に全件を本来の場所へ救出し、化けディレクトリは `~/.claude/backups/mojibake-rescue-2026-06-11/` に隔離済み）。

**How to apply:**
- ツールに渡すパスは**常にフォワードスラッシュ**で書く: `C:/Users/u8792/.claude/...`（全ツールで動作確認済み）
- PowerShell コマンド内では `$env:USERPROFILE` でパスを組み立てる（コマンド文字列にバックスラッシュ+u8792 を直書きしない）
- 化けパスを調査・操作する必要があるときは `[char]0x8792` で構築し `-LiteralPath` を使う
- Read の内容やサイズが期待と食い違ったら、まずパス化けを疑う（`Get-Item` の `.Length` と比較）
- ファイル内容として「バックスラッシュ+u8792」を書きたいときはバックスラッシュを二重化するかカタカナ等で回避する
- 関連: [[project-mcp-path-portability]]（.mcp.json は `${USERPROFILE}` を使う）。Osteoporosis プロジェクトに症状ベースの旧メモリ `tool-path-mojibake-use-powershell` あり（本メモリが根本原因版）
