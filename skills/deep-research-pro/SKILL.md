---
name: deep-research-pro
description: >
  調査レポート・文献レビュー・エビデンス要約を「出す前」に機械的に検証するときに使う。
  引用符の中身が本当に出典にあるか、引用がその文を支持しているか、撤回論文を引いていないか、
  同じプレスリリースの転載を独立した複数ソースと数えていないか、を検査する。
  Use when a research report, literature review, or evidence summary is about to be delivered and
  its citations need mechanical verification before it ships. Also use when checking whether a
  cited paper has been retracted, or whether apparent multi-source agreement is actually syndication.
  Trigger phrases: レポートを検証, 引用を検証, 出典を確認, 引用の実在確認, 幻覚引用,
  撤回論文, リトラクション, 出典が正しいか, ファクトチェック（自分の原稿）, 出す前に確認,
  verify citations, check quotes, retraction check, before shipping the report, citation audit.
  Do NOT use for: 調査そのものを行うこと（組み込みの deep-research ワークフローか通常の
  WebSearch/WebFetch を使う）、arXiv 検索（alphaxiv）、PubMed 等のツール実行（research-toolkit）、
  論文執筆の作法や Zotero 引用挿入（academic-writing）。
---

# Deep Research Pro — 出荷前の機械的検証

## これは何か

**調査そのものはしない。書き終えたレポートを検査する。**
モデルの自己申告ではなく、終了コードで通す／止める。

調査は組み込みの `deep-research` ワークフロー（`Workflow({name: "deep-research", args: "<質問>"})`）か、
通常の WebSearch/WebFetch で行う。このスキルはその**後**に掛ける。

> **収集パイプラインは凍結中。** このスキルには16フェーズの自前調査パイプラインもあったが、
> 2026-07-27 の実測で完走しなかったため凍結した（`frozen-pipeline/README.md` に失敗の記録）。
> **`frozen-pipeline/` の中身を実行しないこと。**

## 何を捕まえるか（すべて実データで確認済み）

| 検査 | 捕まえるもの | 実測 |
|---|---|---|
| `verbatim_quotes` | 引用符の中身が、保存した出典本文に**逐語で存在しない** | 幻覚引用を仕込んだレポート → exit 1 |
| `citecheck_unresolved` | どの出典にも解決しない引用（捏造・破損） | 存在しないノートへの引用 → exit 1 |
| `retracted_sources` | 撤回論文を、撤回に触れずに引用している | 撤回ノートを引用 → exit 1 |
| `required_headings` | 必須の見出しが無い／順序が違う | — |
| `word_count` / `citation_density` | 分量・引用密度が範囲外 | — |

補助:
- **撤回判定** — OpenAlex・Crossref・PubMed の3経路を照会し、1つでも陽性なら撤回扱い。
  実在の撤回論文（Wakefield 1998）で OpenAlex と PubMed の2経路が一致することを確認済み。
- **独立性監査** — URL正規化・ワイヤーサービス署名・本文類似度の3経路でクラスタ化し、
  代表以外の重みを下げる。同一ワイヤー記事の4転載 → 独立性の和 **1.75**（4票にならない）。

## 使い方

前提: `PYTHONIOENCODING=utf-8` を前置する（Windows で付け忘れると cp932 で落ちる）。
以下 `$S = C:/Users/u8792/.claude/skills/deep-research-pro/scripts`。

### 1. 引用した出典を vault に入れる

**逐語検証は出典本文が手元にないと原理的にできない。** 引用した出典は本文を保存する。

```bash
python $S/vault.py write-note <note-id> --project <作業ディレクトリ> \
  --body <本文ファイル> --url <URL> --retrieved-at 2026-07-27 \
  --title "<タイトル>" --type <randomized-trial|cohort|government|news|...> \
  --utility-score <0-18>
```

`--body -` で標準入力からも読める。`<作業ディレクトリ>/research/sources/` に保存される。

**`~/.claude` 配下では実行しない**（GitHub 公開同期されるため調査内容が公開される）。

### 2. クレームを抽出する（引用と文の結合を見たいとき）

各クレームに**出典本文からの逐語引用**を付ける。

```bash
python $S/vault.py write-claims <note-id> <claims.json> --project <作業ディレクトリ>
```

**逐語でないクレームは機械的に拒否され、拒否件数が返る**（実測: 2件中1件を拒否）。
つまり抽出する側が引用を捏造しても、ここで落ちる。

この工程を飛ばしても構わない。飛ばした引用は「未検証」として件数が出るだけで、
**出荷は止まらない**（「未検証」と「捏造」は別物として扱う）。

### 3. ゲートを掛ける

```bash
python $S/shipgate.py <レポート.md> --research <作業ディレクトリ>/research \
  --required-heading "<見出し1>" --required-heading "<見出し2>" \
  --min-citation-density 0.2
```

**終了コード 0 でなければ出荷しない。** 結果は JSON で、`failures` に落ちた検査名が入る。

### 補助コマンド

```bash
python $S/enrich.py <DOI>              # 被引用数・撤回判定（OpenAlex→Crossref→PubMed）
python $S/citecheck.py <レポート.md> --research <...>/research   # 文-引用の対応を単体で見る
python $S/independence.py <sources.json>                         # syndication クラスタリング
```

## ゲートの判定は事実であって、評価の対象ではない

落ちたら**レポートを直して**再実行する。

検査を個別に回して「これは誤検知だ」と論じ始めたら、そこが失敗の入口。
参照元（hyperresearch）では、lint が幻覚引用24件を検出したのに
「誤検知」と自分宛のメモを書いてそのまま出荷した事例が記録されている。

直し方は決まっている:

| 落ちた検査 | 直し方 |
|---|---|
| `verbatim_quotes` | 引用符は逐語のときだけ。比喩・強調の引用符は外して普通の文にする。実引用は出典どおりに直すか消す |
| `citecheck_unresolved` | その出典を実際に保存するか、引用を消す。**引用先が存在しないのは捏造** |
| `retracted_sources` | 撤回に言及したうえで論じるか、引用を外す |
| `required_headings` | 依頼された構造に合わせる |

## 調査そのものの規律（実測された抜け道）

以下は**スキルなしで実際の調査課題を最後まで走らせたときに出た言い訳**（2026-07-26 実測・3体）。
検証以前に、集める段階でこれが起きる。思い浮かんだら手を止める。

| 言い訳（実測・逐語） | 現実 |
|---|---|
| 「defensible な立場を取るには十分だ」 | ソース3件で言った台詞。十分だと判定したのは、やめたい側 |
| 「もう強力なシステマティックレビューの証拠がある」 | 最初の2コールで言った。**反証を探す前に構造が固まっている** |
| 「抄録＋業界紙の要約で同じ数字が得られる」 | 得られない。数値と方法は本文にしかない |
| 「WebFetch が引用箇所を抽出済みだから逐語のはず」 | **違う。WebFetch は小型要約モデル経由で逐語保証がない。** 引用符に入れてよいのは自分が本文で見た文字列だけ（この検査が落とすのは、ほぼこれ） |
| 「レポートが自分で限界を開示しているから批評者も同じ指摘しかしない」 | **開示は検証の代用にならない。** 穴を書き添えても穴は埋まらない |
| 「絵が整合したので検索をやめた」 | やめる基準は「整合したとき」ではなく「新しい検索が新情報を返さなくなったとき」 |
| 「自分で立場を書き、自分で反論節を書いた」 | それは自己採点。反論節を書いた本人は、その反論の甘さを見つけられない |
| 「取得しやすい文献ばかり集まったが、結論は変わらないだろう」 | 変わる。安心側が公開で批判側が有料なら、その非対称が結論を作る |

**「最大限に厳密にやって」と明示指示しても、独立した批評パスは発生しなかった**（実測3/3）。
だから文章で頼むのではなく、機械で止める。

## このスキルができないこと

- **事実の正しさは判定しない。** 検査するのは構造と結合だけ。
  「引用符の中身が出典に逐語で存在する」ことは検証できるが、
  **その出典が正しいかは検証できない。** そこは人間の担当。
- 保存していない出典は検証できない（逐語照合には本文が要る）。
- 調査そのものはしない（凍結した理由は `frozen-pipeline/README.md`）。

## 詳細

- 各検査がなぜ存在するのか（設計根拠）: `reference/checks.md`
- 学術APIの実測済みレシピ（撤回判定・全文取得・ペイウォール回避）: `reference/academic-apis.md`
- 凍結したパイプラインと失敗の記録: `frozen-pipeline/README.md`
