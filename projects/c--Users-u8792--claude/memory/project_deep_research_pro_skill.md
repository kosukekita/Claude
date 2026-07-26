---
name: project-deep-research-pro-skill
description: deep-research-pro スキルを作った経緯・設計判断・RED/GREEN 実測（2026-07-26）。hyperresearch 移植で、組み込み deep-research と併存させた
metadata: 
  node_type: memory
  type: project
  originSessionId: 9c01edb6-6e97-4fee-940e-32cd813b649c
  modified: 2026-07-26T13:47:33.967Z
---

2026-07-26、jordan-gibbs/hyperresearch を参考に `deep-research-pro` スキルを作成。
ユーザー承認済みの決定: **フルパイプライン**、vault は**作業中プロジェクト直下 `./research/`**
（`~/.claude` は GitHub 公開同期されるのでそこには置かない）。

## 構成

- `~/.claude/skills/deep-research-pro/` — SKILL.md（判断層＋合理化反論表）、workflow.js、
  scripts/（vault・enrich・independence・quality・citecheck・shipgate）、tests/、reference/
- `~/.claude/agents/dr-*.md` — ツールロックされた7エージェント
- 実装コードは Codex に委譲（役割分担ルール）。SKILL.md とエージェント定義は Fable 5 が執筆

## 設計の中核（hyperresearch から採った2点）

1. **ツールロックは指示より強い。** 「再生成せず差分だけ当てろ」は、担当が物理的に Write を
   持たないときだけ守られた。→ `dr-patcher` は Read/Edit のみ、`dr-critic` は Edit/Bash なし。
   詳細は [[feedback-agent-toollock-and-registration]]
2. **出荷ゲートは1コマンドに閉じる。** 検査を分けるとモデルが失敗を「誤検知」と再解釈して
   出荷する（hyperresearch の実例: 幻覚引用24件が出荷された）。→ `shipgate.py` 単体で
   全検査＋終了コード判定。

## RED/GREEN の実測（ここが一番の学び）

**RED**（スキルなしで実際の調査課題を最後まで走らせる）: 3/3 で
「引用の逐語検証なし」「独立批評なし」「サブエージェント0」。
**「最大限に厳密にやって」と明示指示しても独立批評は発生しなかった。**
取れた合理化は SKILL.md の反論表に逐語で載せた（「WebFetch が引用箇所を抽出済みだから逐語のはず」等）。

**GREEN**（単一の判断点を切り出して聞く）: **6/6 が正しく抵抗した。スキルの有無に関係なく。**
→ この GREEN テストは**対照になっていない**（統制群も CLAUDE.md のグローバル規則を継承していた）。

**そこから出た本当の知見**: エージェントは「この状況でどうする？」と単発で聞かれれば正しく答えるが、
**長いタスクに埋め込まれると同じ規則を破る**。つまり規律テストを単発の判断点で行うと
実態より良く見える。文章での禁止ではなく構造（ツールロック・機械ゲート・工程の外部化）が
要るのはこのため。今後、規律系スキルを RED/GREEN する時は**実タスクを完走させて測る**こと。

## 実測で見つけた自分の間違い

reference/academic-apis.md に書いた Europe PMC 全文エンドポイントの形式が誤っていた
（`/rest/<SOURCE>/<ID>/fullTextXML` は 404。正しくは `/rest/<PMC接頭辞つきPMCID>/fullTextXML`）。
GREEN テストのエージェントが実地で見つけて報告してきた。**手順書は実際に叩いて検証する。**

## 検証で見つけた実害バグ（Codex に差し戻して修正済み）

**文分割器が小数点と略語で文を割っていた。** `12.4` が `12.` と `4` に割れるため、
数値を含む文では機械トリアージの自動通過が**原理的に働かなかった**（実測 auto_pass=0）。
数値を含む文は最も検証が要る文なので、これは致命的だった。修正後 auto_pass=1 を確認。
`shipgate` の引用密度も同じ関数を使っていたので同時に直った（`sentence_split.py` に共通化）。

**教訓**: 機械層は「テストが通る」だけでは信用できない。
Codex のテストは自分の実装の前提を共有しているので、**実データを自分で通す**まで分からない。

## 未完了（次セッションで要対応）

`dr-*` エージェントはセッション再起動まで登録されないため、**パイプラインの通し実行は未検証**。
機械層（shipgate・撤回判定・独立性・逐語引用の拒否・cite-check の自動通過）は実データで検証済み。
`~/.claude` へのコミットは未実施（プランの人間チェックポイント2として保留）。
