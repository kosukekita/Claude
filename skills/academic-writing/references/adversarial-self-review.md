# 投稿前の敵対的セルフレビュー

> 自分の原稿を「敵対的査読者」として読み、致命傷（fatal flaw）を投稿前に自分で見つける統合セルフレビュー。3 レンズ精読 → devil's-advocate ストレステスト → CRITICAL の操作的定義 → severity 較正ゲートの順で回す。「20 個の些細な指摘より、最も重要な単一の問題を最初に述べる」が全体の規律。

このファイルは、IMRAD 構成・文体 18 パターン・TRIPOD+AI・Vancouver 引用・over/under-claim・Figure font ≥20pt といった既存の執筆チェックとは独立した「査読眼での自己点検」の手順を扱う。文章の体裁ではなく**論証が壊れていないか**を見る。

---

## 0. 全体の規律 — fatal flaw を最初に

一番やってはいけないのは **"Missing forest for trees"**（木を見て森を見ず）。瑣末な 20 個の指摘を並べて、唯一の致命傷を見逃すこと。

> **規律: Always state the single most important issue first.**
> 自原稿に最大 1 つの致命傷があるとしたら何か、を最初に言語化する。残りの細かい指摘はその後でよい。

関連する査読者の罠（self-review でも同じ罠にはまる）:

| Trap | 内容 | 回避策 |
|------|------|--------|
| **Methodological tunnel vision** | 手法だけ批判し、「問いが重要か」を見ない | 先に Lens 3（貢献）から始める |
| **Novelty bias** | 再現研究・漸進的研究を不当に減点 | 再現は価値がある。実行の質で評価する |
| **Expertise projection** | 自分の好む手法を使っていないことを欠点扱い | 選ばれた手法を、その手法自身の土俵で評価する |
| **Positivity-severity oscillation** | コメントは甘く、スコアは辛い（不整合） | 先に verdict（重大度）を決め、後から根拠を書く |
| **Missing forest for trees** | 20 個の些細な指摘で唯一の致命傷を見逃す | 常に最重要の単一問題を最初に述べる |

---

## 1. 3 レンズ精読 — 同時に 3 つの目で読む

自原稿は、以下の 3 レンズで**同時に**評価する。各レンズは「順番に問う質問」と「判定ヒューリスティック」を持つ。

### Lens 1: Internal Validity — "Does the evidence support the claims?"

順に問う:

1. 中心となる主張（central claim）は何か？
2. どんなエビデンスが提示されているか？
3. エビデンスから主張への論理の鎖（warrant）は通っているか？
4. 著者（=自分）が検討していない**代替説明（alternative explanations）**はないか？
5. **どれか 1 つのエビデンスを外したら論証は崩れるか？**

> **判定: #5 が Yes なら、論証は単一の linchpin（要石）に依存している。** フラグを立てる。原稿の貢献は、その 1 つのエビデンスの強さ以上にはなれない。

### Lens 2: External Validity — "Does this matter beyond this study?"

順に問う:

1. 関心の対象となる集団（population of interest）は誰か？
2. 標本（sample）はその集団を代表しているか？
3. 条件は再現可能（replicable）か？
4. 別の文脈・文化・時代でも所見は成り立つか？
5. 著者が言及していない**境界条件（boundary conditions）**は何か？

> **判定ヒューリスティック: 多くの著者は一般化可能性を過大に語る。** 標本が「1 つの大学・1 つの国」由来なら、限定（qualification）なしに「一般に（generally）当てはまる」と主張することはできない。

### Lens 3: Contribution — "So what?"

順に問う:

1. この論文の前に、我々は何を知っていたか？
2. この論文の後で、何を知ったか？
3. その差分（delta）は**意味があるか**（統計的有意 statistically significant とは別物）？
4. これを知って誰が利益を得るか？
5. どんな新しい問いが開かれるか？

> **判定ヒューリスティック: delta を 1 文で言えなければ、貢献が弱いか、伝わっていないかのどちらか。** どちらも査読で指摘される。執筆者として始める順序は Lens 3 → Lens 1（tunnel vision を避けるため、まず「問いが重要か」を確かめてから手法を見る）。

---

## 2. Devil's-Advocate ストレステスト — 自原稿への最強の反論

自分が**反対の立場の学者**だったら、この原稿をどう叩き潰すかを書く。バランスよく長所短所を述べるのではなく、**叩くことだけ**に徹する（"only challenge")。

### 必須成果物: Strongest Counter-Argument（200–300 語）

> もしあなたが反対意見を持つ学者なら、この論文をどう反証するか？ **これがレビュー全体で最も重要な部分**であり、省略不可。
>
> 公平性のため、最強の反論を書く**直前に 1–2 文で原稿の長所を肯定**してから攻撃に入る（acknowledge strengths）。

### Stress Test バッテリ（各項目 Yes/No で答える）

| Test | 問い | 通過条件 |
|------|------|----------|
| Remove strongest source | 最強のソース／エビデンスを外しても論証は持つか？ | Yes なら頑健（No=linchpin 依存） |
| Flip the research question | research question を反転したら、反対派の見解は信用できるか？ | No なら自説が頑健 |
| Apply to different context | 別の文脈に当てはめたら所見は一般化するか？ | Yes なら external validity 高い |
| "So what?" | 重要性（significance）は正当化されているか？ | Yes なら貢献が立つ |
| Hostile reviewer | 敵対的な査読者なら致命傷（fatal flaw）を見つけるか？ | No が望ましい |
| Limitations genuine? | limitations は本物か、体裁（performative）だけか？ | genuine であること |

これらに加えて、攻撃の角度として 8 つの challenge dimension を使う:

1. **Core Thesis Challenge** — 核心の主張は何か。最強の反論は何か。核心が崩れても残る価値はあるか。著者の説明より**倹約的（parsimonious）な代替説明**はないか。
2. **Cherry-Picking Detection** — 引用が自説支持に偏っていないか。重要な反証エビデンスを落としていないか。「代表的」引用 vs「選択的」引用の比率。survivorship bias はないか。
3. **Confirmation Bias Detection** — 文献レビュー前に結論が決まっていなかったか。research question の枠組みが特定の答えを誘導していないか。手法選択が期待結果に有利でないか。
4. **Logic Chain Validation** — 前提→結論の各ステップは妥当か。隠れた前提（hidden assumptions）はないか。因果推論は十分なエビデンスで支えられているか。論理の飛躍（logical leaps）はないか。
5. **Overgeneralization Check** — 結果からの推論の射程がデータの支える範囲を超えていないか。文脈固有の所見を一般状況に不当に一般化していないか。
6. **Alternative Paths Analysis** — 提案する解／政策／理論に見落とされた代替（B, C, D）はないか。なぜ A を選んで B/C/D を選ばなかったのか。より成熟・経済的・実現可能な代替はないか。
7. **Stakeholder Blind Spots** — 重要なステークホルダーの声が欠けていないか（誰が欠けているかの特定のみ。何を言うかの詳述は別役割）。
8. **"So What?" Test** — 実際のインパクトは何か。結論が正しければ世界はどう変わるか。この分野に本当にこの論文が必要か。漸進的貢献で十分か。

### Frame-Lock Detection（精読後に 1 回）

レビューを終えたら自問する: **「8 つの challenge dimension のどれも捉えなかった、論文全体を支える"未言明の前提（unexamined premise）"はないか？」** あれば独立の所見として書き出す。

---

## 3. CRITICAL（致命傷）の操作的定義 — この 4 類型だけ

「CRITICAL = 改訂では救えない核心論証・方法論の致命傷」。**自原稿の指摘が CRITICAL を名乗れるのは、次の 4 類型の少なくとも 1 つに当てはまるときだけ**。それ以外は MAJOR か MINOR に落とす。

| 類型 | 定義 | 例 |
|------|------|----|
| **Foundation Collapse** | 論証の核心仮定が証明可能に誤り／裏付け不足 | 「X と Y の線形関係を仮定しているが、著者自身の Table 2 が U 字カーブを示している」 |
| **Logic-Chain Break** | エビデンスが妥当でも、主結論がそこから follow しない | 「相関しか示していないのに、交絡 A, B, C を扱わずに因果を主張している」 |
| **Data-Conclusion Mismatch** | データが結論を能動的に否定している | 「『有意な改善』と結論しているが、Table 4 の primary outcome は p=0.12」 |
| **Stronger Counter-Narrative** | より倹約的な代替説明がデータによりよく適合する | 「標本の選択バイアス（自発参加 voluntary participation）の方が、提案する介入メカニズムより観測効果をうまく説明する」 |

**CRITICAL に該当しない（= MAJOR か MINOR にすべき）例:**
- 関連はするが中心でない参考文献の欠落
- 核心でない主張のやや不正確な言い回し
- 体裁（formatting）の不整合
- 論じられていない些細な limitation

severity の段階は次の通り:

| Severity | 定義 | 扱い |
|----------|------|------|
| **CRITICAL** | 改訂では救えない核心論証・方法論の致命傷 | 最終判断に必ず反映 |
| **MAJOR** | 信頼性を著しく損なうが、実質的な改訂で改善可能 | Required Revisions に列挙 |
| **MINOR** | 核心論証には影響しないが記す価値あり | Suggested Revisions に列挙 |
| **OBSERVATION** | 欠点ではないが別視点を提供 | レポート末尾に付記 |

---

## 4. Severity 較正ゲート — 過大評価を防ぐ 2 つのフィルタ

CRITICAL / MAJOR を確定する前に、次の 2 ゲートを通す。**自分の指摘を、自分で疑う**段階。

### (a) Field-Norm ゲート

CRITICAL / MAJOR の重大度が「**この分野は X すべき**」という分野規範への依拠で成り立っている場合、その指摘は次の 2 フィールドを**必ず**持たねばならない:

- `field_norm_boundary` — その分野の**実際の**accepted-practice の境界。外部で検証可能な根拠（reference、venue/data policy、community standard、reporting guideline、文書化された専門家慣行）に基づく。「自分の理解では（in my understanding）」は不可。
- `evidence_crossing_rationale` — なぜ**この原稿のエビデンス**がその境界を越えるのか。サブ分野が適用しない一般基準に単に未達なだけ、ではない理由。

> **両方を根拠付けられないなら、その規範を根拠に CRITICAL/MAJOR を付けてはならない。** advisory に格下げし `[FIELD-NORM UNVERIFIED]` とラベルする。
>
> これは「一般には正しい要求（例: CERN 流の再現性アーティファクト要求）が、その規範を共有しない分野で fatal-flaw 扱いされる」失敗を防ぐためのゲート。敵対的な強度ほど、モデル知識から主張した規範を CRITICAL に増幅しやすい。

自問:
- 自分の CRITICAL/MAJOR のうち、重大度が「分野は X すべき」（再現性・報告・エビデンス完全性・データ公開の期待）に依拠するものについて、その分野の**実際の**境界を、自分の prior ではなく外部の検証可能なソースから名指しできるか？
- この原稿のエビデンスは本当にその境界を越えているか、それとも別サブ分野の reference class（CERN 再現性／観察生態学の R²）を当てはめているだけか？
- 「これに対処すれば核心結果は変わるか？」の推論が、方法論的厳密さ・射程・臨床的妥当性を**過小評価**し、専門用語で飾った提示上の問題を**過大評価**していないか？

### (b) Surface-Form Parity ゲート

verdict を確定する前に、**流暢さ・専門用語っぽさ**でなく**実質**で判断しているかを確認する。AI 査読者の典型的失敗は「prose style で 2 つの異なる基準を使い分ける」こと: 砕けた／曖昧な表現には文字通りの精密さを要求して過剰に却下し、精密な表現には技術的具体性を信用して過剰に受容する。根は「specificity（具体性）は correctness（正しさ）と相関する」という学習済み prior で、両方向に誤射する。

verdict 確定前に通すパリティゲート:

- **Extract the checkable substance first** — その懸念の根底にある事実主張・射程・エビデンス基盤を、それが届いた言い回しから切り離して取り出す。
- **Judge the claim against the paper, not against the polish** — verdict は、原稿のエビデンスがその実質的主張を支持／反証するかで決まる。文章がどれだけ流暢・形式的・技術的かでは決まらない。
- **Do not down-rate informal/vague wording** as if it were a factual defect — ただし曖昧さが**実際に**真偽条件を変える／評価不能にする場合は別。口語的表現（"no really", "feels off"）はそれ自体では正しい懸念を却下する理由にならない。
- **Do not credit technical specificity** as if it were evidence — 名前付き概念・コード要素・データセットアーティファクト・数式フレームワーク（"the identifiability problem inherent in compositional data", "Git LFS pointer files" のような）でも、原稿に照らして確かめるまで受容しない。
- **Run the opposite-style counterfactual** — 同じ実質的主張を**反対のスタイル**（精緻 ↔ 砕けた）に書き換えても verdict が変わるか自問する。変わるなら verdict は実質でなく surface form を拾っている → verdict を修正するか、言い回しのせいで安定判断ができないなら「ambiguous」と印を付ける。

> 懸念の**出自（人間か AI か）は判断入力にしない**。バイアスは prose style に反応するもので、著者ラベルには反応しないから。ゲートは対称: 砕けた表現にも技術的に精密な表現にも同じ基準を適用する。

---

## 5. 自己点検の出力フォーマット（テンプレート）

```markdown
## Devil's Advocate Self-Review

### Strongest Counter-Argument
[200-300 words. 反対の立場の学者ならどう反証するか。レビュー全体で最重要。
直前に 1-2 文で原稿の長所を肯定してから攻撃に入る。]

### Issue List

#### CRITICAL
| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|----------|---------------------|-----------------------------|
（最後の 2 列は、重大度が field norm に依拠するとき必須。根拠付けできなければ
 `[FIELD-NORM UNVERIFIED]` を書き advisory に格下げ。norm 非依存なら空欄可。）

#### MAJOR
| # | Dimension | Issue Description | Location | Field-Norm Boundary | Evidence-Crossing Rationale |

#### MINOR
| # | Dimension | Issue Description | Location |

### Ignored Alternative Explanations / Paths
1. [代替説明 A: なぜ著者の説明より良いか]

### Unexamined Premise（Frame-Lock Detection で検出した場合のみ）
[8 dimension が捉えなかった、論文全体を支える未言明の前提]

### Observations (Non-Defects)
- [別視点の所見]
```

### レビュー規律（self-review でも守る）

1. **No personal attacks** — 著者でなく論証を攻撃する（自分相手でも同じ）。
2. **No nitpicking** — 各 CRITICAL/MAJOR は核心論証に実質的影響を持つこと。
3. **Must propose the strongest counter-argument** — 最重要部分、省略不可。
4. **Acknowledge strengths** — 最強の反論の前に 1–2 文で長所を肯定。
5. **Specific citations** — 各指摘は原稿の具体的箇所・ページ番号を引く。

---

## 6. アンチ追従（Anti-Sycophancy）— 自分の指摘を安易に取り下げない

self-review で自分の指摘に反論（rebuttal）したくなったとき、**安易に concede しない**。これは「執筆モデルが会話の調和を最適化するため、攻撃を立ち上げるより速く取り下げる」傾向への対策。

### rebuttal を 1–5 でスコアし、行動を決める

| Score | 定義 | 行動 |
|-------|------|------|
| **5** | 攻撃の核心を新エビデンス／隙のない論理で直接解体 | Withdraw（取り下げ） |
| **4** | 攻撃を実質的に弱める（小さな隙は残る） | Downgrade severity（例 CRITICAL→MAJOR） |
| **3** | 部分的に対処するが核心は残る | Maintain（維持。部分対応は認める） |
| **2** | 接線的／論点ずらし | Restate（攻撃を言い直し、欠けを説明） |
| **1** | エビデンスなしの断言 | Strengthen（角度を足して攻撃を強化） |

決定は必ずログする:

```
[DA-REBUTTAL: Finding #X | Rebuttal Score: Y/5 | Action: Withdraw/Downgrade/Maintain/Restate/Strengthen | Reason: ...]
```

ルール:
- **Do not soften after pushback.** CRITICAL だった指摘は、rebuttal が ≥4 でない限り CRITICAL のまま。
- **No consecutive concessions.** Withdraw（5）も Downgrade（4）も concession。直前で concede したら、次の concession のバーは 5/5 に上がる（前回 concede 済みで score-4 の rebuttal が来たら Downgrade せず Maintain）。
- **Persistent pushback ≠ valid rebuttal.** 同じ論拠で 3 回押しても score は上がらない。**Pressure is not evidence.**
- **Track concession rate.** re-review で指摘の 50% 超を取り下げ／格下げしたらフラグ: 「自分の元の指摘のかなりの割合を譲った。これが本当の改善なのか、自分の追従傾向なのか、人間の査読者が検証すべき」。
