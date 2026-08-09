---
name: workflow-model-tiering
description: Workflowを書くときのモデル層別け規約（finder=安い/verify・judge=強い）と、環境変数が上書きしてしまう罠
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0ed7d245-95b1-436b-8b15-d958d57a966b
  modified: 2026-08-09T02:25:08.437Z
---

★ユーザー指示（2026-08-09）: **Workflow スクリプトを書くときは、必ずステージごとにモデルを層別けする。**

- **finder / sweep / 収集ステージ** → `opts.model` に安いモデルを**明示的に指定**（既定 `'sonnet'`）
  ＋ `opts.effort: 'low'`。幅を稼ぐ層。見落としは本数と多様な lens で埋める。
- **verify / judge / synthesize ステージ** → ★**`opts.model` を書かない（省略＝セッションモデルを継承）**
  ＋ 高い effort。ここは判断であり、生成器と評価者を分ける意味そのものなので絶対に下げない。

★**強い層に `'opus'` 等をハードコードしない**（ユーザー指摘 2026-08-09）。ハードコードすると
セッションを Fable 5 など最新モデルに切り替えても判断層だけ古いモデルに固定され、新モデルが出るたび
スクリプトが腐る。省略すれば**ユーザーが `/model` で選んだモデル＝そのとき最良と判断したもの**が
自動的に判断層に載り、障害時は Claude Code 側の `fallbackModel` が次点へ落とす。
Workflow ツール自身のガイダンスも「既定は省略。メインループのモデル継承がほぼ常に正しい」。
下げる側だけ明示する、が原則（**明示するのは格下げのときだけ**）。
- 迷ったら「間違いが検出可能か」で決める。**「見つかりませんでした」が結論になりうる作業を安価にしない**
  （偽陰性が沈黙し、親がそれを事実として続きを組み立てるため）。読み取り専用かどうかは判断軸ではない。

**Why**: ultracode の目的は「高いモデルを使うこと」ではなく「最も正確な答えを出すこと」。安価モデルで
幅、強いモデルで判断、という配分は網羅性とコストを同時に満たし、ultracode の趣旨に反しない。

**How to apply**: `agent(prompt, {model: 'sonnet', effort: 'low', phase: 'Find'})` /
`agent(prompt, {model: 'opus', phase: 'Verify'})` のように **stage ごとに明示**する。省略すると
全エージェントがセッションのメインモデルを継承する（既定は層別けなし）。

★**罠**: `CLAUDE_CODE_SUBAGENT_MODEL` を設定すると、**スクリプトの `opts.model` ごと上書きされる**
（公式 docs 明記: "which overrides both"）。サブエージェント固定のためにこの環境変数を常設すると、
ワークフローの層別けが黙って無効化される。→ **常設しない。** サブエージェントを固定したいときだけ
そのコマンドの前置きで一時的に付ける。

関連: [[claude-subagent-cheap-model-routing]]（素の claude では BASE_URL がプロセス全体に効くため、
非 Claude の安価モデルは nested プロセス経由でしか使えない）
