---
name: feedback-agent-toollock-and-registration
description: サブエージェントのツールロックは Bash も外さないと成立しない。~/.claude/agents/ の新規エージェントはセッション再起動まで登録されない（2026-07-26 実測）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9c01edb6-6e97-4fee-940e-32cd813b649c
  modified: 2026-07-26T13:28:27.864Z
---

サブエージェントを「できないことがある存在」として設計するときの実測知見（2026-07-26）。

## ロックは Bash を外して初めてロックになる

`~/.claude/agents/<name>.md` の frontmatter `tools: ["Read", "Edit"]` でツールを制限できる。
ただし **`Bash` が残っていると全部無効**。シェル経由でファイルを書けるので
「このエージェントはレポートを変更できない」という性質が成立しない。

自分で最初に書いた `dr-critic` は `tools: ["Read","Write","Bash","Grep","Glob"]` にしていて、
`Edit` を外したことで満足していたが、`Bash` で書けるので**設計上の主張が嘘になっていた**。
`Grep` / `Glob` / `Read` があれば探索能力は落ちないので、`Bash` は外す。

**Why:** ツールロックの価値は「プロンプトの禁止事項は圧がかかると破られるが、
持っていないツールは使えない」という一点。迂回路が1本でも残っていれば、それはただの願望。

**How to apply:** ロックを設計したら、`tools:` を1行ずつ見て
「この中に任意のファイルを書ける手段が残っていないか」を確認する。
`Bash` / `Write` / `Edit` / `NotebookEdit`、そして **`ToolSearch`**（他のツールを後から読める）に注意。

## 新規エージェントはセッション再起動まで見えない

エージェントの登録はセッション開始時にしか読まれない。
`~/.claude/agents/dr-patcher.md` を書いた直後の同じセッションで呼ぶと
`Agent type 'dr-patcher' not found. Available agents: ...` になる（実測）。

エージェントに依存する仕組みを作ったら、**その場では実地検証できない**ことを前提に段取りする。
frontmatter の妥当性（name とファイル名の一致・YAML パース・tools 配列）だけは
その場で機械的に検証できるので、それはやる。
