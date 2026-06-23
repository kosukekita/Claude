---
name: feedback_protect_files_hook_secrets_path_block
description: protect-files.ps1フックは中身でなくパス名(secrets/等)だけでWrite/Editをブロックする。無害なREADMEでも止まるので、そのファイルが本当に機密かを見極めユーザーに方針を確認する
metadata:
  type: feedback
---

PreToolUse フック `~/.claude/hooks/protect-files.ps1` は **ファイルの中身ではなくパス名（正規表現）だけ**で Write/Edit をブロックする。パターン: `.env` / `.env.` / `.pem` / `.key` / `.p12` / `.pfx` / `credentials.json` / `secrets/` / `secret/` / `.ssh/` / `id_rsa` / `id_ed25519`（区切りを `\`→`/` 正規化後にマッチ、`exit 2` でブロック）。

そのため `_secrets/README.md` のように **中身が機密でない運用ドキュメントでも、パスに `secrets/` を含むだけで Write が止まる**ことがある（誤検知）。

**Why:** これは機密漏洩防止の正しい安全機構であり、尊重すべき。安易な無効化・自動回避はしない。`dangerouslyDisableSandbox` は PreToolUse フックには効かない（別レイヤー）。なお、フックを回避する具体的手順を**記憶に書こうとすると auto-mode 分類器が Instruction Poisoning として拒否する**（=セキュリティ制御の迂回を将来セッションに刷り込むのを防ぐ正しい挙動）。だから手順ではなく「事実と判断の置き場所」を残す。

**How to apply:**
1. ブロックされたら、まず **そのファイルが本当に機密かを自分で見極める**。実機密（.env/.pem/トークン等）なら作成自体を見送る or 置き場所を変える。
2. 無害だと判断しても **勝手に回避せず、ユーザーに作成方針を確認する**（AskUserQuestion）。判断と承認をユーザーに委ねる。
3. フック設定そのものを変えたい場合は update-config / settings.json の permission 追加でユーザー主導で行う。

関連: 日本語入り .ps1 は [[feedback_ps1_needs_utf8_bom_on_windows]] でBOM付き保存が必要。フックのstdout文字化けは [[feedback_powershell_hook_utf8_stdout]]。
