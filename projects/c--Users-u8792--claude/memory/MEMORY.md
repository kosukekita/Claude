# Memory Index

- [feedback_slide_icon_approach.md](feedback_slide_icon_approach.md) — slide-makingでSVGアイコン手書きは失敗する。リファレンスPNGクロップ→base64埋め込みが唯一の確実な方法
- [project_skill_consolidation.md](project_skill_consolidation.md) — ~/.claude/skills統合（05-31,06-08）。現36スキル。code-reviewer/codex-review/gemini-review削除、skill-creator統合、codex-consult新設。codex連携は会話文脈を自動で渡さない→Claudeが要約して/codex:rescueに渡す。PowerShell表示化けに騙されない
- [project_totalsegmentator_license.md](project_totalsegmentator_license.md) — TotalSegmentatorアカデミックライセンス取得済＋全15ライセンスタスクのモデルDL。ローカルはGPU無しで中断（5/15完了）、リモートGPU PCで再開予定。番号はconfig.jsonに平文・メモリ非保存

- [project_mcp_path_portability.md](project_mcp_path_portability.md) — .mcp.jsonのstdioサーバーは相対パス禁止、${USERPROFILE}を使う（HOMEはPowerShellで空）
- [feedback_where_to_place_tips.md](feedback_where_to_place_tips.md) — tips/機能をCLAUDE.md・スキル・どこにも置かないのどれにするかは「実際に発火する文脈」で決める。標準ツールと重複するスキル機能は削る（削除前にgrep確認）
- [feedback_hook_vs_prose_audit.md](feedback_hook_vs_prose_audit.md) — ルールをHook（機械強制）にするか文章のまま残すかの判断原則。main編集ブロックや整形のグローバルHookは害になる。迷ったら文章寄り
- [feedback_ps1_hook_ascii_only.md](feedback_ps1_hook_ascii_only.md) — ~/.claudeのフック.ps1に日本語直書きは文字化けで構文破壊→フック全体が死ぬ。ASCII限定＋編集後は構文/挙動テスト必須
- [feedback_u8792_path_unicode_escape.md](feedback_u8792_path_unicode_escape.md) — パス中の螒がUnicodeエスケープ解釈されC:\Users螒に化けて静かに誤書き込み。ツールのpathは常にフォワードスラッシュ（C:/Users/u8792/...）で書く
