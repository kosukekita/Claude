# Memory Index

- [feedback_slide_icon_approach.md](feedback_slide_icon_approach.md) — slide-makingでSVGアイコン手書きは失敗する。リファレンスPNGクロップ→base64埋め込みが唯一の確実な方法
- [project_skill_consolidation.md](project_skill_consolidation.md) — ~/.claude/skills統合履歴（〜2026-06-14）。achievement+career→cv-profile、Swiss-modernism→ui-ux-design、writing-skills→skill-writingリネーム。方針: 重複は同一ツールのみマージ、別レイヤー/依存関係（例 subagent-driven⊃TDD）は統合せず「依存契約の明示＋RED/GREEN実測」で締める、descriptionにworkflow要約を書かない
- [project_totalsegmentator_license.md](project_totalsegmentator_license.md) — TotalSegmentatorアカデミックライセンス取得済＋全15ライセンスタスクのモデルDL。ローカルはGPU無しで中断（5/15完了）、リモートGPU PCで再開予定。番号はconfig.jsonに平文・メモリ非保存

- [project_tooluniverse_mcp_wsl_fix.md](project_tooluniverse_mcp_wsl_fix.md) — tooluniverse-osteo MCP起動失敗。081a23bはメッセージと実体が食い違い未修正→Nodeランチャーがvenvバイナリを直接spawn(bash/.sh完全排除)で恒久修正。commit 53e5674
- [project_remote_control_default.md](project_remote_control_default.md) — Remote Control起動時デフォルト有効化。公式永続キー無し→PowerShell profileで `function claude {claude.cmd --remote-control @args}`。脱出口claude-plain
- [project_grok_media_skill.md](project_grok_media_skill.md) — grok-mediaスキル作成。公式Grok Build CLIにX Premium+ OAuthで委譲し画像/動画生成（サブスク枠・APIキー不要）。実機事実: ツール名image_gen/image_to_video、t2v専用無し、出力は~/.grok/sessions配下、loginは実ターミナルで
- [feedback_powershell_hook_utf8_stdout.md](feedback_powershell_hook_utf8_stdout.md) — WindowsのPowerShellフックが日本語をstdoutに返すと文字化け（u8792→螒、記憶→龍L���）。原因はACP=932でWrite-OutputがShift_JIS出力。UTF-8バイト直書き(OpenStandardOutput)で解決。memory-inject.ps1のみ該当、commit a044da7でpush済
