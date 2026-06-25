# 統計的整合性レッドフラグ＋名前付きフォールシー自己スキャン

> 投稿前に、自分の原稿を「査読者の目」でスキャンするための自己監査チェックリスト。再現性・QRP（Questionable Research Practices）・推論デザインのレベルで「攻撃されうる箇所」を先回りで潰す。over/under-claim ref は「結果文の言い回し」、表記ルール ref は「書式」を扱うが、本 ref はそれらとは別レイヤー — **デザインと推論そのものの健全性**を見る。

各項目について自分の原稿を **CLEAR（問題なし）/ SUSPECTED（疑いあり・要確認）/ 該当（修正必須）** の3段階でマークしながら通す。SUSPECTED 以上が付いた箇所は、本文・図表・補遺のどこで対処するかをメモしてから投稿する。

---

## A. 統計的整合性レッドフラグ（severity 付き）

査読者がここに引っかかると、リジェクトまたは major revision に直結する。severity（HIGH / MEDIUM / LOW）は「査読での重大度」。自原稿で同じパターンが出ていないか、表の Red Flag 列を1行ずつ照合する。

### A-1. P-hacking Indicators

| Red Flag | 中身（何を疑うか） | Severity |
|----------|------------------|----------|
| Many *p* near .05 | 複数の結果で *p* が **.04–.05 の範囲に集積**している | **HIGH** |
| Selective reporting | 有意な結果だけ報告され、非有意な結果が消えている（disappeared） | **HIGH** |
| Vague analysis strategy | 解析戦略が事前に述べられておらず、後から見ると探索的（exploratory in hindsight）に見える | MEDIUM |
| Unexpected subgroups | 有意を見つけるための事後サブグループ分解（post-hoc subgroup decomposition） | MEDIUM |
| Flexible sample size | 事前に定めた停止規則がない（逐次検定を無補正で実施: sequential testing without correction） | **HIGH** |
| "Excluding outliers" | 不明確な基準で大量の外れ値を除外している | MEDIUM |

> 自己チェックの観点: 「この *p* 値群を見て査読者が p-curve を描いたら、.05 直下に山ができないか？」「Methods に書いた解析計画と、実際に Results で報告した解析は完全に一致しているか？」

### A-2. HARKing（Hypothesizing After the Results are Known）

| Red Flag | 中身 | Severity |
|----------|------|----------|
| Perfect hypothesis-result match | 全仮説が**例外なく支持**されている（all hypotheses supported without exception） | MEDIUM |
| Exploratory packaged as confirmatory | 探索的解析を確証的に包装。文献レビューが明らかに**事後構築**（constructed post-hoc）されている | **HIGH** |
| Hypothesis directionality change | 当初は正方向を予測していたのに結果が負方向、それを「**予想どおり（as expected）**」と再枠付けしている | **HIGH** |
| No pre-registration | OSF / AsPredicted の事前登録リンクがない（必須ではないが推奨） | LOW |

> 自己チェックの観点: 「Introduction の仮説は、データを見る前に本当にこの形だったか？」「全部当たっている論文は、査読者には HARKing を疑わせる」という点を忘れない。事前登録があるなら必ずリンクを張る。

### A-3. その他のレッドフラグ

| Red Flag | 中身 | Severity |
|----------|------|----------|
| *p* = .000 | 統計ソフトの生出力。**正しくは *p* < .001** と書く | LOW |
| df inconsistent with *N* | 自由度（df）から逆算した *N* と、報告した *N* が一致しない | **HIGH** |
| Inconsistent table numbers | 本文の語り（text narrative）が表の値と矛盾している | **HIGH** |
| Causal language | 非実験デザイン（correlational / survey）で因果推論の言葉を使っている | MEDIUM |

> HIGH の3つ（df 不整合・本文と表の矛盾・p=.000 以外の数値矛盾）は、査読者が電卓を叩けば一発で露見し「ずさん」の印象を決定づける。投稿前に**自分で df から N を逆算**し、**本文に書いた全数値を表と1個ずつ突き合わせる**こと。
> 因果語チェック: 横断・観察デザインなら "caused / led to / increased（他動詞的因果）/ effect of X on Y" を "was associated with / predicted / correlated with" に置き換えたか確認する。

---

## B. 名前付きフォールシー（検出 tell 付き）

デザイン・推論レベルの典型的な誤り。各フォールシーには **How to Identify（検出 tell）** が付いている。自原稿の Discussion・結論・解析設計が、どれか1つでも踏んでいないか照合する。

### B-1. デザイン／集計レベル

| Fallacy | 中身 | 検出 tell（How to Identify） |
|---------|------|---------------------------|
| **Ecological fallacy** | 群レベルのデータから個人レベルの結論を推論する | 分析単位（unit of analysis）が推論レベルと不一致。「群で○○な国／集団は…だから個人も…」 |
| **Simpson's paradox** | サブグループに存在する傾向が、群をまとめると逆転する | サブグループの結果を確認していない。→ **分解（disaggregated）と集計（aggregate）を必ず併置**して両方見る |
| **Survivorship bias** | 「生き残った／成功した」ケースだけを分析する | 失敗・脱落（failed / withdrawn）ケースが欠けている。tell の問い: **"What about the failures?"** |
| **Reverse causation** | 因果の向きが逆（cause と effect が逆） | 横断データ（cross-sectional）で因果推論している。時間的前後関係と代替的な因果方向を検討する |
| **Overfitting** | モデルが訓練データに過適合している | **交差検証（cross-validation）またはホールドアウト（holdout）がない** |
| **Endogeneity / omitted-variable** | 脱落変数による推定バイアス | 潜在的な脱落変数（potential omitted variables）が議論されていない |
| **Multicollinearity** | 独立変数同士が強く相関している | **VIF が未報告、または VIF > 10** |
| **Regression to the mean** | 極端な測定値は次の測定で平均へ戻る性質 | 対照群があったか？ 初期測定値は極端だったか？「最低層の成績が改善した」は介入なしでも起きうる |

### B-2. 統計的推論／指標レベル

| Fallacy | 中身 | 検出 tell（How to Identify） |
|---------|------|---------------------------|
| **Base-rate neglect** | 全体確率（base rate）を無視し個別情報を優先 | 関連する base rate と比較していない。「満足度 90%」も全プログラムの base rate が 88% なら大した値ではない。tell の問い: **"What's the base rate?"** |
| **Texas sharpshooter** | ランダムなデータの中でクラスタに注目し、外れを無視してパターンを見つける | 20 個検定して有意だった 1 個だけ報告。tell の問い: **仮説は事前登録されたか？ 多重検定は補正されたか？** |
| **McNamara fallacy** | 定量指標だけで判断し、測りにくい定性要因を無視 | 重要だが測定困難な要因（teaching quality, community impact 等）が除外されていないか |
| **Goodhart's law** | 「指標が目標になると、それは良い指標でなくなる」 | 指標が目標化していないか。指標操作（metric manipulation / gaming）の兆候はあるか |

> 自己チェックの観点: B-1 は「データの構造と因果」、B-2 は「数字の解釈」。Discussion で結論を述べる各文に対し、「この主張は上の12個のどれかに該当しないか」を1パスかける。特に**横断データで因果を語る文**（Reverse causation / Endogeneity）と、**サブグループ解析の解釈**（Simpson's paradox）は踏みやすい。

---

## C. Quick reference: 検出質問 → 捕捉フォールシー

自原稿を読みながら、左の質問を声に出して問う。答えに詰まったら右のフォールシーを SUSPECTED でマークする。

| この質問を投げる（Ask This） | 捕捉するフォールシー（Detects） |
|------------------------------|--------------------------------|
| "What's the base rate?"（base rate は？） | **base-rate neglect** |
| "What about the failures?"（失敗例は？脱落例は？） | **survivorship bias** |
| "Were criteria defined before results?"（基準は結果の前に定義されたか？） | **Texas sharpshooter** / moving goalposts |
| "Does B have other possible causes?"（B に他の原因は？） | post hoc / false cause |
| "Is this sample representative?"（標本は代表性があるか？） | hasty generalization |
| "Is the key term used consistently?"（鍵となる用語は一貫して使われているか？） | equivocation |
| "What evidence was left out?"（除外した証拠は？） | cherry-picking / confirmation bias |
| "Is this the actual argument being made?"（これは実際の主張か？） | straw man |
| "Can we distinguish correlation from causation?"（相関と因果を区別できるか？） | cum hoc / ecological fallacy |
| "Are individual and group levels being mixed?"（個人レベルと群レベルが混ざっていないか？） | ecological fallacy / Simpson's paradox |

---

## D. Severity classification（自己トリアージ用）

見つけた問題を投稿前にどう扱うか。Devil's Advocate の severity 区分を自己監査に転用する。**Minor を Critical に水増しせず、逆に Critical を見逃さない**よう正確にトリアージする。

| Severity | 定義 | 投稿前のアクション |
|----------|------|------------------|
| **Critical** | 致命的欠陥 — 中心的主張または方法論を無効化する | **投稿をブロック。** 解析やデザインの修正、または主張の撤回が必要 |
| **Major** | 重大な弱点 — 信頼性を損なうが修正可能 | 投稿前のリビジョンで必ず対処（感度分析の追加・限界の明記など） |
| **Minor** | 小さな問題 — 中心的妥当性には影響しない | 改善メモとして記録、可能なら直す |
| **Observation** | 興味深い点 — 欠陥ではないが言及の価値あり | アクション不要 |

### 自己ストレステスト（投稿前に4問）

Devil's Advocate の Stress Test を自分の原稿に当てる。1つでも No なら、その箇所を Major 以上として扱う。

| テスト | 自問 | 通過？ |
|--------|------|--------|
| Remove strongest source | 最強の根拠（最大の効果・主要な引用）を外しても、主張は持つか？ | Yes / No |
| Flip the research question | 研究問いを反転させたとき、対立する見解にも信憑性があるか？（あるなら自説の論拠が弱い） | Yes / No |
| Apply to different context | 別の文脈・別の集団に当てはめても、知見は一般化するか？ | Yes / No |
| "So what?" | 意義（significance）は正当化されているか？ | Yes / No |

> 仕上げに、Devil's Advocate が問う **"Would a hostile reviewer find fatal flaws?"** を自分に向ける。さらに **steel-man before attack** の原則 — まず自説の最強版を立て、それを自分で崩しにいく。崩せたら、その反論を Discussion の Limitations で先回りして書く。limitations が **genuine（本物）か performative（形だけ）か** も自問する。

---

## E. 投稿前の最終パス（手順）

1. **A の3表をレッドフラグ照合** — HIGH 項目（p≈.05 集積 / 選択的報告 / 無補正逐次検定 / 探索を確証に偽装 / 予想外を予想どおりと再枠付け / df-N 不整合 / 本文と表の矛盾）をゼロにする。
2. **数値の自己再計算** — df から N を逆算し、本文の全統計値を図表と1個ずつ突合（Inconsistent table numbers の予防）。`p = .000` は `p < .001` に。
3. **B の12フォールシーを Discussion に当てる** — 各結論文に対し1パス。横断データの因果語、サブグループ解釈、VIF 未報告、交差検証の有無を特に確認。
4. **C の検出質問を声に出す** — 詰まった質問に対応するフォールシーを SUSPECTED でマーク。
5. **D のストレステスト4問** — No が出た箇所を Limitations で先回りして明記。
6. 各項目に **CLEAR / SUSPECTED / 該当** を付け、SUSPECTED 以上は対処場所（本文・図表・補遺・事前登録リンク）を決めてから投稿する。
