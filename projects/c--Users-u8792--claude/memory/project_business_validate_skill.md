---
name: project_business_validate_skill
description: business-validate-before-buildingスキルを作成（2026-07-07）。新規アプリ/SaaS相談時に実装より先に「売れる証拠」の検証を課すdiscipline-enforcing型
metadata: 
  node_type: memory
  type: project
  originSessionId: f36ae5d5-7df5-4f3e-84d1-4b15a5fdeb37
---

ユーザー提供の画像（個人開発の4原則: ①作る前に売れる証拠を確認 ②1%だけ良くするポジショニング ③試してから伸ばす ④広告依存から脱却）を skill-writing の TDD 手順でスキル化した（2026-07-07）。

**成果物**: `~/.claude/skills/business-validate-before-building/SKILL.md`（320語）。ユーザー要望で名前を `business` 始まりにし、新規アプリ/SaaS/事業を「作りたい」と言った瞬間に発動、mvp-development の手前の意思決定ゲートとして機能。

**RED/GREEN/REFACTOR 実測**（skill-writing の Iron Law 遵守）:
- RED（スキルなし）: サブエージェント3体中2体が需要検証を飛ばして実装計画・`create-next-app`へ直行。4原則を体系カバーしたものは0件 → 「エンジニアの自然な傾向＝作る前に売れる証拠を飛ばす」を実証
- GREEN（スキルあり）: 全件が原則1〜3を明示通過、実装を意図的に保留
- REFACTOR: ユーザーが検証を明示拒否＋「時間がない」「絶対いける」の3重圧力でも折れず、合理化テーブルの反論で撃退（bulletproof確認、追加穴埋め不要）

**設計判断**: discipline-enforcing型として Iron Law・Red Flags・合理化テーブルを装備。descriptionは「いつ使うか」トリガーのみ（ワークフロー要約を書かない [[project_skill_consolidation]] の方針）。「学習目的なら検証省略」の抜け道は"推測せず本人確認"で塞いだ。

関連: [[project_skill_consolidation]]（skills統合の方針・履歴）
