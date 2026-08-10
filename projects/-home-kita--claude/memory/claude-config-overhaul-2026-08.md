---
name: claude-config-overhaul-2026-08
description: 2026-08-10のグローバル設定刷新。CLAUDE.md 29.5KB→8.7KB、スキル10本をskills-archive/へ退避。復元手順と根拠データ
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-10T04:03:58.112Z
---

2026-08-10、Boris tips 記事（訂正OS）に基づきユーザー指示でグローバル設定を刷新した。

**CLAUDE.md**: 194行/29.5KB → 72行/8.7KB。★ユーザー確定の恒久ルールは全て保持（圧縮＋記憶ポインタ化）。
完全削除したのは「Workflow Best Practices」節（汎用アドバイス）のみ。詳細（LLMルーティング台帳の
コマンド・ask-local等の直接入口）は [[external-ai-consult-fallback]] へ退避してから削った。
旧版はスクラッチパッドと ~/.claude の git 履歴に残存。

**スキル退避**: 938セッションの呼び出し実績を集計し、10本を
`~/.local/share/agents-sync-repo/skills-archive/` へ git mv（54→44本）。復元手順は同所の README.md。
退避: caveman / google-workspace-cli / search-optimization / dispatching-parallel-agents /
receiving-code-review / requesting-code-review / subagent-driven-development / using-git-worktrees /
executing-plans / finishing-a-development-branch（後半6本は superpowers 実行系クラスタ＝
役割分担ルール「実装はCodex」で陳腐化）。

**ゼロ使用でも残した理由**: h3-prompt-writing・mf-cli=作成直後／zotero=academic-writingの必須依存／
browser-automation=settings.json許可リスト掲載／research-toolkit・ai-prediction-model・
medical-image-landmark-detection=医療研究クラスタ／infographic・make-poster=slide-makingからのルーティング先。
★計測はLinux機の履歴のみで **Windows機の使用実績は不可視**。誤退避なら即復元してよい。

**未処理**: `~/.codex/AGENTS.md`（84KB・別構造）は今回触っていない。CLAUDE.md と自動同期される
仕組みかは未確認。Codex側の規律が旧版のままの可能性があるので、次に Codex を使うとき確認する。
