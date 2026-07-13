---
name: okf-markdown-frontmatter
description: 新規ナレッジ系Markdownに付けるOKF(Open Knowledge Format)フロントマターの形式・対象/対象外・設計思想
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7f792248-9bef-40fb-8283-33d15119eae9
---

CLAUDE.md「Markdown作成時はOKFを付ける」の形式詳細（行動ルールの核はCLAUDE.md本文＝人が読む/AIに渡すナレッジ系.mdを新規作成時にOKF frontmatterを付ける・最小必須は `type` のみ・対象外には付けない）。

OKF = Open Knowledge Format(Google Cloud提案 2026-06)。複数md横断検索のメタデータになり検索性・段階的関連たどりが向上。

## 形式（最小ルール=必須は `type` のみ。他は任意）
```yaml
---
type: spec            # 必須。種別(例: spec/design/research/readme/runbook/minutes/note)
title: ○○の設計メモ    # 任意
description: 一行要約   # 任意
tags: [okf, watcher]  # 任意
timestamp: 2026-06-29 # 任意。相対でなく絶対日付
owner: ○○            # 任意(担当・部門)
---

# 以下は通常の Markdown 本文
```
迷ったら `type` だけでよい。

## 対象/対象外
- **対象**: 設計メモ・仕様書・調査メモ・議事録・README類・手順書など、自分で新規に作る `.md`。
- **対象外(付けない)**: 記憶ファイル(`memory/*.md`・`./.claude-memory/*.md`＝既にname/description/metadata有)、`SKILL.md`・`CLAUDE.md`・`MEMORY.md` 等の運用ファイル、他者が定めた既存フォーマットのmd。

設計思想=「ルール最小化(必須type)／作成と利用の分離(特定サービス非依存)／どのツールでも実装可能」。出典: https://zenn.dev/knowledgesense/articles/14a874a9f423bb
