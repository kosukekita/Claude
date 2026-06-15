---
name: codex-consult
description: >
  Codex（GPT 系・別ベンダー AI）に会話の文脈ごと相談・委譲して、第二の視点や続きの実装を得るスキル。
  Claude（自分）が行き詰まったときのレスキュー、設計・判断のセカンドオピニオン、作業の続きの実装委譲に使う。
  Use when the user wants Codex's independent opinion, a second opinion on a design/decision, a rescue when Claude is stuck, or to hand off continued implementation to Codex.
  Trigger phrases: Codexに相談, Codexの意見, Codexに聞いて, Codexならどうする, Codexにレスキュー,
  Codexに続きを, Codexに任せる, セカンドオピニオン（Codex）, 行き詰まったのでCodex, ask Codex, consult Codex, second opinion from Codex, rescue with Codex.
  Do NOT trigger for: コード差分のワンショットレビュー（標準 /code-review か `codex review` CLI を使う）、
  論文・文章の第三者チェック（gemini CLI を Bash で直叩き）。本スキルは『会話の文脈を踏まえて Codex に相談/委譲する』場合のみ。
allowed-tools: SlashCommand, Bash, Read, Glob
---

# Codex Consult

Codex（別ベンダー AI）に、**いま進行中の会話の文脈ごと**相談・委譲するスキル。

## なぜこのスキルが要るか（重要な前提）

`/codex:rescue` も `codex` CLI も、**Claude とユーザーの会話履歴を自動では読まない**。
Codex に届くのは「渡したプロンプト文字列1本」＋作業ディレクトリ（Codex はそこから repo を自力で読む）だけ。

→ つまり「会話の文脈を踏まえた相談」を成立させるには、**Claude（自分）が会話の意図・前提・
詰まった点を要約してプロンプトに明示的に埋め込んでから渡す**必要がある。本スキルはその要約と委譲の手順。

## Instructions

### Step 1: 相談タイプを判断

| タイプ | 状況 | プロンプトの力点 |
|--------|------|------------------|
| **rescue** | Claude がバグ・設計で行き詰まった | 試したことと失敗、別解を求める |
| **second-opinion** | 設計・判断の妥当性を別AIに問う | 採用案とトレードオフ、反論を求める |
| **handoff** | 作業の続きを Codex に実装させる | 現状の到達点と残タスク、完成条件 |

### Step 2: 会話文脈を構造化テンプレートに要約

Codex は会話を知らないので、次のテンプレートを **Claude が埋めて** 1つのプロンプト文字列にする。
該当しない項目は省略してよい。日本語で書く（Codex も日本語で返すよう最後に指示）。

```
【これまでの議論】今ユーザーと何をしようとしているか（1-3文）
【目標】達成したいこと
【私(Claude)が試したこと】アプローチと、なぜそれではダメだったか
【詰まっている点 / 論点】具体的な問題。second-opinion ならば「採用案とその理由」
【対象】関連ファイル（例: src/foo.ts の bar 関数）。Codex は cwd から自力で読める
【Codexに求めること】rescue=別の原因と修正案 / second-opinion=独立した評価と反論 / handoff=残りの実装
日本語で回答してください。
```

### Step 3: `/codex:rescue` に渡して委譲

要約したプロンプトを `/codex:rescue` の引数にして実行する。`/codex:rescue` が
運搬・セッション継続（--resume/--fresh）・モデル選択を担う。

**プロンプトは必ず `/codex:rescue` の引数として全文渡す（stdin 依存にしない）。**
ランナー（codex-companion.mjs）の `readStdinIfPiped()` は `fs.readFileSync(0)` で stdin を
同期ブロッキング読みするため、引数を空にして stdin から入力を期待すると**無限ハング**する。
Step 2 の構造化プロンプトは長くても1本の引数文字列に収め、空委譲はしない。

```
/codex:rescue <Step 2 で組んだ構造化プロンプト>
```

- 同じ相談を続ける（前の Codex の回答を踏まえる）場合は `--resume` を付ける。
- 別の独立した相談を始める場合は `--fresh`。
- 重い設計批判なら `--effort high`、素早い一次見解なら無指定（既定）。
- 結果は Codex の出力をそのまま提示し、必要なら Claude が会話の文脈に統合・補足する。

#### 重い委譲は最初から background で（120秒タイムアウト回避）

`--effort high` や、レビュー／実装委譲のように Codex が**数分かかる**見込みのものは、
**foreground で投げない**。foreground 実行は親 Bash ツールの既定 120 秒タイムアウトに当たり、
途中切れ（不完全な出力）や「no output」になる（実体はセッションに残るが回収に手間がかかる）。

→ 重い委譲は計画的に **background 実行**にし、`/codex:status` で進捗、`/codex:result` で最終結果を回収する。
素早い一次見解（短い second-opinion 等）だけ foreground でよい。目安: 「3 分以内で返ると確信できるか？
否なら background」。

> 代替: `/codex:rescue` を使わず Claude が直接 `codex exec` で渡すこともできる（rescue が使えない環境）。
> その場合も**プロンプトは引数で渡す**。stdin に流すなら必ずヒアドキュメント等で実体を与え、
> 空 stdin にしない（同上のハング回避）。

## Examples

### Example 1: 行き詰まりのレスキュー
User: 「このバグ、3回直そうとしたけどダメ。Codexに相談して」

Actions:
1. タイプ=rescue
2. テンプレートを埋める（議論=○○の実装中 / 試したこと=A,Bを試したが△△で失敗 / 詰まり=□□ / 対象=src/x.ts / 求める=別の原因と修正案）
3. `/codex:rescue <埋めたプロンプト>` を実行、結果を提示

### Example 2: 設計のセカンドオピニオン
User: 「このアーキテクチャでいいか、Codexの意見も聞きたい」

Actions:
1. タイプ=second-opinion
2. テンプレートを埋める（採用案とトレードオフを明記し「最も強い反論は何か」を求める）
3. `/codex:rescue --effort high <埋めたプロンプト>` を実行、Claude の見解と並べて提示

### Example 3: 実装の続きを委譲
User: 「ここまで実装した。残りはCodexに任せたい」

Actions:
1. タイプ=handoff
2. テンプレートを埋める（現状の到達点・残タスク・完成条件・テスト方法を明記）
3. `/codex:rescue <埋めたプロンプト>` を実行

## Troubleshooting

### Codex が未インストール / 未認証
`/codex:setup` を実行するようユーザーに案内する。

### 会話の文脈が Codex に伝わっていない出力が返る
Step 2 のテンプレートの記入が薄い。議論・試したこと・詰まり・求めることを具体的に書き直して再実行する。

### 委譲が途中で切れる / ハングする / no output で返る
原因はほぼ**ランナーの呼び出し方**で、Codex が生成したコマンド（`rg | Select-Object` 等。Codex の
サンドボックスは Windows では PowerShell/cmd で動くので混成でも動く）ではない。確認順:

1. **foreground で重い委譲を投げていないか** → 親 Bash の 120 秒で切れる。`--effort high`/長尺は background へ（Step 3）。
2. **プロンプトを引数で渡したか** → 空委譲＋stdin 待ちで `readStdinIfPiped()` が無限ハング。必ず引数で全文渡す。
3. **`--background` と stdin を同時に使っていないか** → detached（stdio:"ignore"）で stdin が無いのに読むと確実にハング。

「no output」でも Codex 本文は残っていることが多い:
`~/.codex/sessions/<年>/<月>/<日>/rollout-*.jsonl` を新しい順に数本見て、`role=assistant` の
**最長メッセージ**を拾う（短い断片は思考/ツール段階）。抽出結果は**コンソールに print せず**
UTF-8 でファイルに書き出して Read で開く（cp932 化け回避）。詳細 → [[feedback_codex_review_output_via_session_jsonl]]。

### コマンドが「クォート未閉」でハングする（全角クォート混入）
貼り付け／転記したコマンドに全角ダブルクォート `“ ”`（U+201C/U+201D）が混じると、bash も PowerShell も
クォートとして認識せず**未閉扱いで入力待ちハング**になる。Codex 自身はこれを生成しない（実コマンドは
ASCII クォート）。**コマンドは必ず ASCII の `"` / `'` に正規化**してから実行・転記する。日本語パスやログを
扱う際は cp932 化けと併発しやすい → [[feedback_u8792_path_unicode_escape]]。

### 機密を含む情報を渡してよいか
Codex への委譲は**外部送信**。機密・個人情報・要ログインのデータを含む場合は、渡す前にユーザーへ確認する。
