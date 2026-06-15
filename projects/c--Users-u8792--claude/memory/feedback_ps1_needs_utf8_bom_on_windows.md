---
name: feedback-ps1-needs-utf8-bom-on-windows
description: 日本語を含む.ps1はBOMなしUTF-8だとWindows PowerShell 5.1がcp932で読みパースエラーで実行失敗する。BOM付きUTF-8で保存する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4fb3f955-1e55-4f42-836a-465b6f37acda
---

日本語のコメント／文字列を含む `.ps1` スクリプトを **BOMなし UTF-8** で保存すると、Windows PowerShell 5.1 は既定でシステムコードページ（このPCは cp932）として読むため、日本語バイト列が壊れて文字列終端（`"`）を見失い、**`powershell -File` 実行時にパースエラーで落ちる**。`#!/usr/bin/env bash` の sh 版は BOM 不可なのでそのまま、**ps1 版だけ BOM 付き UTF-8 で保存する**。

**Why:** 2026-06-15、diagnose スキルの HITL テンプレ `hitl-loop.template.ps1`（Write ツールが BOMなし UTF-8 で作成）が、`[Parser]::ParseFile` で「Unexpected token '}'」「string is missing the terminator」を出した。真因は構文ではなくエンコーディング: UTF-8 として明示デコードすれば `ParseInput` はエラー0だが、`ParseFile`（＝実 `powershell -File` と同じ読み取り経路）は cp932 読みで壊れる。BOM があれば PowerShell はコードページに関わらず UTF-8 と判定する。Codex レビューはこの実機固有の罠を見逃した（コード論理しか見ないため）。関連: [[feedback_powershell_hook_utf8_stdout]]（PowerShell の stdout 側 cp932 問題）。

**How to apply:**
- 日本語入り `.ps1` を新規作成したら、`[System.IO.File]::WriteAllText($p,$text,(New-Object System.Text.UTF8Encoding($true)))` で BOM 付き保存し直す。
- 検証は `[Parser]::ParseFile`（BOM無しだと cp932 で読むので実行時と同じ失敗を再現できる）。`ParseInput` に UTF-8 デコード済み文字列を渡すだけだとこの罠を見逃す。
- `.sh` / `.py` / JSON 等には BOM を付けない（別の不具合を生む）。ps1 限定の対処。
