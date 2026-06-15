---
name: project-matt-pocock-skills-import
description: mattpocock/skills から caveman/diagnose/handoff の3本を移植導入（2026-06-15）。全19本を精査し、残り16本は redundant or 環境不一致で見送り
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb3f955-1e55-4f42-836a-465b6f37acda
---

mattpocock/skills（github.com/mattpocock/skills、全19本）を1本ずつ精読し、既存 ~/.claude 設定（33スキル＋11フック＋CLAUDE.md）と突き合わせた結果、**3本を移植導入**（2026-06-15）。

**導入した3本**（`~/.claude/skills/` に SKILL.md として手動作成、専用CLI `npx skills` は不使用）:
- **caveman** — 唯一未カバーだった「簡潔出力モード」を補完。原版の英語電文体を CLAUDE.md「常に日本語」と整合させ**日本語の冗長表現を削る**方向に翻案。コード・エラー文・**絶対パス**は load-bearing として保護。破壊的操作の確認では自動解除（Auto-Clarity Exception → block-dangerous.ps1/protect-files.ps1 と連動）。
- **diagnose** — systematic-debugging（根本原因ゲート）と debugging-wizard（ツール）の「あいだ」=フィードバックループ工学を補完。例を pytest/seeded torch/メトリクススナップショット diff に寄せた。HITL テンプレを **bash版＋PowerShell版の両方**同梱しクロスOS化（`scripts/hitl-loop.template.{sh,ps1}`）。
- **handoff** — cross-agent-memory（恒久保存）と別物の「一時引き継ぎ文書」。OS の temp に書く（リポに置かない）。墨消し対象に本環境の既知機密（TotalSegmentator ライセンス番号・APIキー）とサロゲート/文字化けハザードを具体化。

**見送り16本**: tdd（test-driven-development と重複・例がTS）、git-guardrails-claude-code（block-dangerous.ps1 で既出＋bash hook で Windows非対応＝ダウングレード）、teach（CLAUDE.md 理解度クイズと役割重複・重量級）、setup-pre-commit/migrate-to-shoehorn/scaffold-exercises/setup-matt-pocock-skills（Node/TS/pnpm/Husky/私物CLI前提で Python・Next.js MVP・医療AI のスタックに不一致）、grill-with-docs/zoom-out（DDD/glossary 前提）他。アイデアだけ既存に注入候補: grill-me の質問規律→brainstorming、grill-with-docs の記録3条件→cross-agent-memory 保存ゲート、to-issues の縦割り＋AFK/HITLタグ→writing-plans（未実施・任意）。

**ポイント**: 既存設定が厚い（プロセス系・安全フックとも）ため丸ごと導入価値は少数。判断軸は「①真のギャップを埋めるか ②Windows/PowerShell＋日本語規則と整合するか ③スタック一致するか」。
