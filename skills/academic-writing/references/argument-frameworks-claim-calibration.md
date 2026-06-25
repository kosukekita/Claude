# 原稿論証フレームワーク＋エピステミック・ステータス言語較正

> 原稿の論証を「検査」し、主張言語をエビデンスの強さに「較正」するための 4 ツール集。Toulmin（論証分解）／Bradford Hill（因果検査）／Inference to Best Explanation（競合説明の評定）／Epistemic Status ladder（動詞の較正）。チェックボックスを埋めるためではなく、論証の質そのものを**考えるため**に使う。

---

## 1. Toulmin Model — 論証を 6 要素に分解する

研究上のあらゆる論証は 6 つの構成要素を持つ。原稿をレビューするときは、各要素を一つずつ同定し、欠けているものに赤旗を立てる。

| Component | 何を問うか | 欠けているときの Red Flag |
|-----------|-----------|--------------------------|
| **Claim** | 何を主張しているのか？ | thesis が曖昧／途中で揺れる（vague or shifting thesis） |
| **Data / Evidence** | それを支える証拠は何か？ | 実証的裏付けのない主張（claims without empirical backing） |
| **Warrant** | なぜその証拠がその主張を支えるのか？ | データと結論の間の論理的飛躍（logical gap between data and conclusion） |
| **Backing** | その Warrant 自体を支えるものは何か？ | 方法論の妥当性を無検証で前提にしている（assumed methodology validity） |
| **Qualifier** | その主張はどれくらい確実か？ | 絶対表現（"proves", "always"）の使用 |
| **Rebuttal** | 何があればその主張は崩れるか？ | limitation を一切認めていない |

**Judgment heuristic**: **Warrant を同定できないなら、Data がどれだけ提示されていてもその論証は弱い**と判断してよい。Warrant を欠いた Data はただの情報（information）にすぎず、主張を支えていない。

### 使い方の tell
- Discussion で結論が大きいのに、その結論を結果と繋ぐ「なぜ」（Warrant）が書かれていない → 論証が空洞。
- "proves" / "always" / "definitively" のような絶対語が出たら Qualifier の欠落を疑う。
- limitation 段落が無い、あるいは形式的すぎる → Rebuttal の欠落。

---

## 2. Causal Reasoning — Bradford Hill 9 基準（因果検査）

論文が「X が Y を**引き起こす**（X causes Y）」と主張しているとき、以下の 9 基準で評定する。これは医学・疫学領域の**因果主張（causal claim）に適合する**枠組みで、相関を因果と言い換えていないかを検査する。

1. **Strength of association** — 効果はどれくらい大きいか？
2. **Consistency** — 複数の研究／文脈で再現されているか？
3. **Specificity** — X は特異的に Y をもたらすか（何にでも効くのではなく）？
4. **Temporality** — X は Y に**先行**するか？（**唯一の必須基準 / Only mandatory criterion**）
5. **Biological / theoretical gradient** — X が増えれば Y も増える（用量反応）か？
6. **Plausibility** — 妥当なメカニズムがあるか？
7. **Coherence** — 既存の知識と矛盾しないか？
8. **Experiment** — 実験的証拠はあるか？
9. **Analogy** — 類似の原因が類似の効果を生むか？

**Judgment heuristic**:
- 多くの社会科学系論文は 3〜5 基準を満たす程度。
- **満たすのが 3 未満（fewer than 3）なら、その因果主張は未支持（unsupported）**。
- 厳密に必須なのは **#4 Temporality のみ**。残りの 8 基準は**累積的なエビデンス（cumulative evidence）**であり、満たすほど因果の確からしさが増す。

### 使い方の tell
- 横断研究（cross-sectional）なのに「引き起こす」と書いている → Temporality を満たせていない可能性が高く、因果語は撤回すべき。
- 「相関がある」ことだけを根拠に因果を語っている → Strength 以外の基準がほぼ空欄。

---

## 3. Inference to Best Explanation (IBE) — 競合説明の評定

同一の所見に対して複数の説明が成り立ちうるとき、著者が好む説明だけでなく**ありうる説明をすべて**俎上に載せて比較する。

1. **ありうる説明をすべて列挙する**（著者の preferred explanation だけにしない）
2. 各説明を次の 4 軸で評定する:
   - **Explanatory scope** — どれだけ多くを説明できるか
   - **Simplicity** — アドホックな仮定がより少ないか（fewer ad-hoc assumptions）
   - **Fit** — 既知の事実との整合性
   - **Predictive power** — 新しい観測を予測できるか
3. 4 軸を通じて**最も高得点の説明が best explanation**であって、著者の仮説に最も合う説明ではない。

**Judgment heuristic**: **論文が説明を 1 つしか検討していないなら、それがどれほど巧みに論じられていても confirmation bias である**。最低限、**Discussion セクションは最強の代替説明 2 つ（the two strongest alternative explanations）に言及すべき**。

### 使い方の tell
- Discussion が自説の補強だけで、代替解釈・交絡・逆因果に触れていない → 代替説明 2 つを足すよう要求する。
- 「他に説明のしようがない」式の断定 → 列挙不足のサイン。

---

## 4. Epistemic Status of Claims — エビデンスの強さに動詞を較正する

すべての主張が同じ重みを持つわけではない。主要な主張を一つずつ分類し、**その status に**見合った言語（動詞・テンプレ文）に較正する。

| Status | 意味 | Appropriate Language（テンプレ） |
|--------|------|-------------------------------|
| **Established** | 再現済み・査読済み・高いコンセンサス（replicated, peer-reviewed, high consensus） | `"X is..."` |
| **Supported** | 証拠はあるが未再現（evidence exists but not yet replicated） | `"Evidence suggests X..."` |
| **Preliminary** | 単一研究または小標本（single study or small sample） | `"Preliminary findings indicate..."` |
| **Speculative** | 直接の証拠ではなく推論に基づく（based on reasoning, not direct evidence） | `"We hypothesize that..."` |
| **Contested** | 相反する証拠が存在する（conflicting evidence exists） | `"While some studies find X, others..."` |

**Judgment heuristic**: **Preliminary な所見に Established 言語を使っていれば、それは overclaiming（過大主張）**であり、アカデミックライティングで最も頻出する品質問題の一つ。

### Before / After（status と動詞のミスマッチを直す）

**NG（Preliminary な単一小標本に Established 言語）**
> Our findings demonstrate that the biomarker **is** a determinant of outcome.

**OK（status を Preliminary に較正）**
> **Preliminary findings indicate** that the biomarker may be associated with outcome; replication in larger cohorts is needed.

---

**NG（相反する証拠があるのに断定）**
> The intervention **improves** survival.

**OK（status を Contested に較正）**
> **While some studies find** a survival benefit, **others** report no effect, leaving the question unresolved.

---

**NG（メカニズム推論のみなのに事実として記述）**
> Inflammation **causes** the progression observed here.

**OK（status を Speculative に較正）**
> **We hypothesize that** inflammation contributes to the progression observed here.

---

## レビュー時の統合ワークフロー（チェックリスト）

主要な主張ごとに、順に通す:

1. **Toulmin 分解** — Claim / Data / Warrant / Backing / Qualifier / Rebuttal を同定。Warrant が見つからなければ論証は弱い。
2. **因果主張か？** — Yes なら Bradford Hill 9 基準で評定。Temporality を満たすか、満たす基準が 3 以上あるかを確認。3 未満なら因果語を撤回。
3. **代替説明は尽くされたか？** — IBE で説明を列挙し 4 軸で評定。Discussion が最強の代替 2 つに触れているか。
4. **言語は status に較正されているか？** — Established / Supported / Preliminary / Speculative / Contested のどれかを判定し、動詞・テンプレ文を合わせる。Preliminary に Established 言語なら overclaiming として修正。
