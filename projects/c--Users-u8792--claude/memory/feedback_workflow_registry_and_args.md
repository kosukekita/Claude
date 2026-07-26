---
name: feedback-workflow-registry-and-args
description: Claude Code の Workflow ツールは組み込みしか名前解決せず ~/.claude/workflows/ は無視される。カスタムは scriptPath 経由・args は文字列で届く（2026-07-26 実測）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9c01edb6-6e97-4fee-940e-32cd813b649c
  modified: 2026-07-26T13:28:14.346Z
---

Workflow ツールの登録と引数まわりの実測（2026-07-26・Windows・claude-code 経由）。
公式ドキュメントに書かれていない挙動なので、毎回試さずここを見る。

## 名前で解決できるのは組み込みだけ

`Workflow({name: "..."})` が解決するのは **組み込みの `deep-research` と `code-review` のみ**。
`~/.claude/workflows/*.js` を置いても**無視される**（`Workflow "x" not found. Available: deep-research, code-review`）。
プロジェクト側 `.claude/workflows/` も未確認だが、ユーザーレベルは効かない。

**カスタムワークフローの配布は `Workflow({scriptPath: "<絶対パス>"})`**。任意のディスクパスから読める（実測OK）。
スキルに同梱して SKILL.md からパスで呼ぶのが現実的な形。

## args は文字列で届く

ツール引数に JSON オブジェクトを渡しても、スクリプト側には**文字列**として入る。
`typeof args === "string"` なら `JSON.parse` を試みる必要がある。
組み込み `deep-research` が `args` を素の質問文字列として扱うのもこのため。

## スクリプト realm の制約

素の ECMAScript realm。`URL` グローバル無し（ホスト解析は正規表現でやる）。
`Date.now()` / `Math.random()` / 引数なし `new Date()` は**例外を投げる**（resume 再現性のため）。
時刻・乱数が要るなら `args` 経由で渡すか Bash 側で生成する。

## 組み込み deep-research の中身（バイナリから抽出）

5角度 → 最大15ソース取得 → 上位25クレーム × 3票の敵対的反証（2票で棄却）→ 単一エージェント統合 → JSON。
永続化なし・学術API なし・レポート本文なし・出荷ゲートなし。
軽い調査には十分だが、深い調査には足りない（それが [[project-deep-research-pro-skill]] を作った理由）。
抽出方法: `claude.exe` を `// deep-research: Scope` で検索するとスクリプト全文が平文で入っている。
