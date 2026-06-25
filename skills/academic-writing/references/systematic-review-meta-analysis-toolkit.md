# システマティックレビュー/メタ解析の報告ツールキット

> SR/MA を執筆・査読するための具体リファレンス。PRISMA 2020（27項目＋フロー図）、RoB 2 / ROBINS-I、I²・GRADE の判定アルゴリズム、効果量の選択と抽出階層、出版バイアス検定の研究数ゲート、登録先を、原典の数値・ドメイン名・閾値そのままで日本語化したもの。Cochrane Handbook v6.4 準拠。

このファイルは「SR/MA の執筆・報告・査読」に特化する。IMRAD・文体18パターン・TRIPOD+AI・Vancouver 引用・over/under-claim・Figure font≥20pt などは本スキルの他セクションでカバー済みなのでここでは繰り返さない。SR/MA 固有の報告要件だけを扱う。

判定の用語（Low / Some Concerns / High、ドメイン名 D1–D7、effect measure の略号 RR/OR/SMD など）、チェックリスト項目名、テンプレート英文、検定名（Egger's / Peters / trim-and-fill / p-curve など）は**英語のまま**残す。書き換えると元の instrument・guideline と対応が取れなくなるため。

---

## 0. 進め方（Cochrane の8段階と a priori 原則）

SR を受けたら、Cochrane Handbook v6.4 の段階に沿って進める。各段で「事前に決めたこと」を逸脱していないか確認する。

| 段階 | Cochrane 章 | 必須要件 |
|------|------------|---------|
| Planning | Ch 1–3 | プロトコル登録、明確な objective、PICOS |
| Searching | Ch 4 | 包括的検索（**≥ 2 databases**）、検索式を文書化 |
| Selecting | Ch 4 | **独立した dual screening**、事前定義の基準 |
| Data extraction | Ch 5 | 標準化フォーム、pilot testing、dual extraction |
| Risk of bias | Ch 8 (RoB 2), Ch 25 (ROBINS-I) | ドメインベース評価、signaling questions |
| Synthesis | Ch 10–12 | 適切な統計手法、異質性評価 |
| GRADE | Ch 14 | アウトカムごとの確信度 |
| Reporting | Ch 15 | PRISMA 2020 準拠 |

基本原則（fundamental principles）として、(1) a priori protocol（検索前に PROSPERO / OSF に登録）、(2) 複数 DB を検索し単一ソースに頼らない、(3) screening・extraction・risk of bias は最低でも一部を二者独立で、(4) 結果を見る前に解析計画を確定、(5) 別チームが追試できるレベルで全てを文書化、を守る。

決定フロー（要約）: 登録 → PRISMA-P でプロトコル → ≥2 DB で系統的検索＋PRISMA flow → dual screening → RoB（RCT=RoB 2 / 非ランダム化=ROBINS-I）→ 統合（定量データ＋比較可能なら meta-analysis、そうでなければ SWiM の narrative synthesis）→ アウトカムごとに GRADE → PRISMA 2020 で報告。

---

## 1. PRISMA 2020 — 27項目チェックリスト（セクション対応）

正式名称: **Preferred Reporting Items for Systematic Reviews and Meta-Analyses**（Page et al. 2021, BMJ 372:n71）。投稿前に各項目が本文のどこかで満たされているか必ず突き合わせる。13a–13f は synthesis の6サブ項目で、SR/MA 査読で最も漏れやすい。

### Title and Abstract

| # | Item | 報告すべき内容 |
|---|------|---------------|
| 1 | **Title** | systematic review / meta-analysis / both のいずれかを title で明示 |
| 2 | **Abstract** | 構造化要約: background, objectives, data sources, study eligibility criteria, participants, interventions, study appraisal/synthesis methods, results, limitations, conclusions, **registration number** |

### Introduction

| # | Item | 報告すべき内容 |
|---|------|---------------|
| 3 | **Rationale** | 既存知見の文脈でレビューの根拠を述べる |
| 4 | **Objectives** | **PICOS** を参照して問いを明示 |

### Methods

| # | Item | 報告すべき内容 |
|---|------|---------------|
| 5 | **Eligibility criteria** | 包含/除外基準（PICOS 各要素、date range、言語、publication status） |
| 6 | **Information sources** | 検索した全ソース（databases, registers, websites, organizations, reference lists）と日付 |
| 7 | **Search strategy** | **少なくとも1つの DB の完全な検索式**（filter・limit 含む） |
| 8 | **Selection process** | どの研究が適格かを決めた方法（reviewer 数、consensus process） |
| 9 | **Data collection process** | 抽出方法（reviewer 数、独立か、著者からのデータ入手/確認の手順） |
| 10 | **Data items** | 抽出した全アウトカム変数・その他の変数を定義 |
| 11 | **Study risk of bias assessment** | RoB 評価の方法（使用 tool、結果を synthesis にどう使ったか） |
| 12 | **Effect measures** | アウトカムごとの効果指標（例: RR, MD, SMD） |
| 13a | **Synthesis methods** | 各 synthesis にどの研究が適格かを決めるプロセス |
| 13b | | データを synthesis 用に準備する方法（例: multi-arm 研究の扱い） |
| 13c | | 個別研究と synthesis を表/図で示す方法 |
| 13d | | 結果を統合する方法と根拠（meta-analysis: model, software / narrative: **SWiM**） |
| 13e | | 異質性の原因を探る方法（subgroup, meta-regression） |
| 13f | | 実施した sensitivity analyses |
| 14 | **Reporting bias assessment** | 欠測結果に由来するバイアス（publication bias）の評価方法 |
| 15 | **Certainty assessment** | エビデンス体の確信度評価の方法（例: **GRADE**） |

### Results

| # | Item | 報告すべき内容 |
|---|------|---------------|
| 16a | **Study selection** | 検索・選択の結果、理想は **PRISMA flow diagram** |
| 16b | | 包含基準を満たしそうだが除外した研究を引用し理由を説明 |
| 17 | **Study characteristics** | 各包含研究を引用し特性を提示 |
| 18 | **Risk of bias in studies** | 各包含研究の RoB 評価を提示 |
| 19 | **Results of individual studies** | 全アウトカムについて各研究の summary data・効果推定値・CI・synthesis 結果 |
| 20a | **Results of syntheses** | 各 synthesis で寄与研究の特性と RoB を要約 |
| 20b | | 全統計的 synthesis の結果（**CI と異質性指標**を含む） |
| 20c | | 異質性の原因を探った全調査の結果 |
| 20d | | 全 sensitivity analyses の結果 |
| 21 | **Reporting biases** | 欠測結果に由来するバイアスの評価を提示 |
| 22 | **Certainty of evidence** | 評価した各アウトカムの確信度を提示 |

### Discussion

| # | Item | 報告すべき内容 |
|---|------|---------------|
| 23 | **Discussion** | 他エビデンスの文脈での総合解釈、エビデンスとレビュー過程の限界、含意 |
| 24 | **Registration and protocol** | 登録情報（register 名と登録番号）とプロトコルへのリンク |
| 25 | **Support** | 資金的・非資金的支援源と funder の役割 |
| 26 | **Competing interests** | 著者の利益相反 |
| 27 | **Availability of data, code, and other materials** | 公開可能なもの（data collection form 雛形、抽出データ、analysis code、その他）を報告 |

### PRISMA 2020 Flow Diagram（カウントすべき箱）

5段（IDENTIFICATION → 重複除去 → SCREENING → 取得 → 適格性評価 → INCLUDED）。各箱に必ず n を入れる。

```
IDENTIFICATION
  Records identified from databases (n = )
  Records identified from other sources (n = )
        │
Records removed before screening:
  Duplicate records (n = )
  Records marked as ineligible by automation (n = )
  Records removed for other reasons (n = )
        │
SCREENING
  Records screened (n = )
  Records excluded (n = )
        │
  Reports sought for retrieval (n = )
  Reports not retrieved (n = )
        │
  Reports assessed for eligibility (n = )
  Reports excluded, with reasons (n = )
    Reason 1 (n = ) / Reason 2 (n = ) / Reason 3 (n = )
        │
INCLUDED
  Studies included in review (n = )
  Reports of included studies (n = )
  Studies included in quantitative synthesis (n = )
```

**NG**: フロー図に「Excluded (n=120)」とだけ書き、最終段で除外理由の内訳がない（16b と矛盾）。
**OK**: 適格性評価段で除外を理由別に分解（Reason 1 … (n=) 形式）し、INCLUDED で review 包含数と quantitative synthesis 包含数を別々に示す。

---

## 2. Risk of Bias — RoB 2（RCT）と ROBINS-I（非ランダム化）

研究デザインで instrument を機械的に選ぶ。ランダム化試験 → **RoB 2**（個別ランダム化=標準、cluster=cluster extension、crossover=crossover extension）。非ランダム化（cohort / case-control / before-after / interrupted time series）→ **ROBINS-I**。custom 基準を発明せず、instrument のアルゴリズムを厳密に適用する。

評価手順: (1) デザイン分類 → (2) 各ドメインの signaling questions を**順番に**全て回答（Yes / Probably Yes / No / Probably No / **No Information**、根拠と研究の頁/節を記録）→ (3) アルゴリズムでドメイン判定（全体印象で上書きしない）→ (4) 集約規則で総合判定 → (5) traffic-light 可視化。迷ったら "Low" でなく **"Some Concerns"** に倒す（conservatism）。報告不足それ自体がリスク指標で、最低でも Some Concerns に上げる。

### RoB 2 — 5ドメイン（signaling question 数つき）

| Domain | 焦点 | Signaling Q 数 |
|--------|------|---------------|
| **D1: Randomization process** | 配列生成、allocation concealment、ベースライン差が偶然と整合するか | 3 |
| **D2: Deviations from intended interventions** | 割付の認識、trial context 由来の逸脱、解析が適切か（ITT） | 7（effect of assignment）/ 5（effect of adhering） |
| **D3: Missing outcome data** | ほぼ全例でアウトカムが得られたか、欠測が真値に依存しうるか、適切に対処したか | 5 |
| **D4: Measurement of the outcome** | アウトカム測定法が適切か、介入の知識が評価に影響しうるか、assessor が盲検か | 5 |
| **D5: Selection of the reported result** | 事前計画どおりに解析されたか、複数の測定/解析/subgroup があったか、結果が選択された可能性 | 3 |

各ドメイン判定: **Low Risk** / **Some Concerns** / **High Risk**。

**総合 RoB 2 アルゴリズム**（このとおり機械的に）:

| 条件 | Overall |
|------|---------|
| 全ドメイン Low | **Low Risk** |
| 1つ以上で Some Concerns、High なし | **Some Concerns** |
| 1つ以上で High Risk | **High Risk** |

### ROBINS-I — 7ドメイン（3時点）

**Pre-intervention**: D1 Confounding（統制されていないベースライン交絡因子）、D2 Selection of participants（試験参加が介入とアウトカムに関連するか）。
**At intervention**: D3 Classification of interventions（介入が明確に定義・信頼性高く分類されたか）。
**Post-intervention**: D4 Deviations from intended interventions（逸脱、co-intervention のバランス）、D5 Missing data（アウトカムが概ね完全か、除外がアウトカムに関連するか）、D6 Measurement of outcomes（測定が妥当・信頼でき、評価がバイアスを受けないか）、D7 Selection of the reported result（複数解析から選ばれた可能性）。

判定尺度: **Low**（well-performed RCT と同等）/ **Moderate**（非ランダム化として健全だが well-performed RCT には及ばない）/ **Serious**（重要な問題あり）/ **Critical**（有用なエビデンスを提供できないほど問題）/ **No information**（報告不足）。

**総合 ROBINS-I**: 最も重症なドメイン判定がそのまま総合になる。1つでも **Critical Risk** があれば総合は Critical Risk。

### Traffic-light 出力テンプレート

```markdown
| Study | D1 | D2 | D3 | D4 | D5 | D6* | D7* | Overall |
|-------|----|----|----|----|----|----|------|---------|
| Author1 (2023) | 🟢 | 🟡 | 🟢 | 🟢 | 🟡 | — | — | 🟡 |
| Author2 (2024) | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | — | — | 🟢 |
| Author3 (2022) | — | — | — | — | — | 🟡 | 🔴 | 🔴 |
*D6–D7 apply to ROBINS-I only

Distribution: Low Risk X (XX%) / Some Concerns X (XX%) / High Risk X (XX%)
```

🟢 Low / 🟡 Some Concerns / 🔴 High。robvis（R）で traffic-light plot を作るのが定番。

### RoB エッジケース（査読で見落としやすい）

- **Cluster-randomized**: cluster extension を使い、追加ドメイン **D1b**（個別 recruitment とランダム化の timing）を評価。clusters を個別募集前にランダム化すると recruitment bias が起きやすい。
- **教育系など非ランダム化が大半の領域**: 既定で ROBINS-I。D1（confounding）に特に注意（学生の self-selection はほぼ普遍）。propensity score matching は交絡を減らすが消さない。
- **Mixed-methods**: 定量部分を RoB 2 / ROBINS-I、定性部分は別の品質評価（例: CASP qualitative checklist）。両者を別々に報告。
- **報告不足の研究**: signaling question に答えられないこと自体がリスク。"No Information" とし「Insufficient reporting prevents assessment of this domain」と注記。
- **複数アウトカム**: レビューに含めるアウトカムごとに RoB を別評価（objective vs subjective でバイアスプロファイルが異なる）。

---

## 3. 異質性の評価（I² / Q / τ² / prediction interval）

異質性は「無視するもの」ではなく情報。**定量化し、説明し、モデル化する**。statistical tests を4つセットで報告する。

| 指標 | 解釈 | 報告 |
|------|------|------|
| **Q-test（Cochran's Q）** | 観測変動が sampling error を超えるか検定。**p < 0.10** で異質性を示唆（0.05 でなく 0.10 を使う — Q は検出力不足） | p 値を報告 |
| **I²** | 総変動のうち真の異質性（sampling error 以外）の割合 | **95% CI つき**で報告（研究数が少ないと CI は非常に広くなる） |
| **τ²（tau²）** | study 間分散の絶対量 | 値を報告。random-effects model で使用 |
| **Prediction interval** | 新しい研究で期待される真の効果の範囲 | pooled estimate と並べて報告 |

### I² 解釈帯（Cochrane 6.4 §10.10.2、帯は意図的にオーバーラップ）

| I² | Label | 意味 | アクション |
|----|-------|------|-----------|
| 0–40% | Low | 重要でないかもしれない | pooling 続行、I² を報告 |
| 30–60% | Moderate | 中等度の可能性 | pooling 続行、原因を調査 |
| 50–90% | Substantial | 相当の異質性 | 原因調査、subgroup 検討、**prediction interval を報告** |
| 75–100% | Considerable | 顕著な異質性 | pooling が意味を持つか問い直す、narrative synthesis を検討 |

**重要な但し書き**: 帯は意図的に重複する。I² の意味は (a) 効果の大きさ、(b) Q-test の p 値、(c) forest plot の目視、に依存する。**全効果が同方向なら高 I² の懸念は小さく**、逆に効果がゼロをまたいで分かれる中等度 I² の方が懸念は大きい。I² は研究の精度に影響され、精密な研究が多いと絶対差が小さくても高 I² になりうる。研究数が少ないときの I² の 95% CI は非常に広いので必ず併記する。

I² > 40% のときの調査戦略: (1) forest plot で外れ値/subgroup パターンを目視、(2) 事前指定 subgroup 解析、(3) 連続 moderator は **≥ 10 studies** なら meta-regression、(4) leave-one-out・高リスク研究除外などの sensitivity、(5) 明確な subgroup が異質性を説明するなら分割して別々に報告。

### Forest plot 出力テンプレート

```markdown
| Study | Effect (SMD/RR/OR) | 95% CI Lower | 95% CI Upper | Weight (%) | n Tx | n Ctrl |
| Author1 (2023) | 0.45 | 0.12 | 0.78 | 18.3 | 50 | 52 |
| **Pooled** | **0.51** | **0.33** | **0.69** | **100** | — | — |

Model: Random-effects (DerSimonian-Laird / REML)
Heterogeneity: I² = 42%, Q = 12.3 (df = 7, p = 0.09), tau² = 0.03
Prediction interval: [0.05, 0.97]
Test for overall effect: Z = 5.62, p < 0.001
```

---

## 4. GRADE — エビデンスの確信度

正式名称: **Grading of Recommendations, Assessment, Development and Evaluations**（Guyatt et al. 2008）。アウトカムごとに開始点を置き、down / up する。

**開始点**: Randomized trials → **HIGH（⊕⊕⊕⊕）** / Non-randomized（観察研究）→ **LOW（⊕⊕◯◯）**。

### 下げる要因（Rate Down、全デザイン共通）

| 要因 | 下げ幅 | 適用条件 |
|------|--------|---------|
| **Risk of bias** | −1 / −2 | study design/execution の serious / very serious な限界（高リスク研究が多数） |
| **Inconsistency** | −1 / −2 | 説明できない異質性（**I² > 50%**、効果方向がばらつく） |
| **Indirectness** | −1 / −2 | エビデンスがレビュー質問の PICOS を直接扱わない |
| **Imprecision** | −1 / −2 | 広い CI、小標本、CI が臨床判断閾値をまたぐ（total < OIS） |
| **Publication bias** | −1 | funnel plot の非対称、small study effects、未公表試験の存在 |

### 上げる要因（Rate Up、**観察研究のみ**）

| 要因 | 上げ幅 | 適用条件 |
|------|--------|---------|
| **Large effect** | +1 / +2 | **RR > 2 or < 0.5**（large）、RR > 5 or < 0.2（very large）、交絡なし |
| **Dose-response gradient** | +1 | 明確な用量反応関係 |
| **Plausible confounding** | +1 | 想定される全交絡が観測効果を**弱める方向**に働く |

### 確信度レベル

| レベル | 記号 | 意味 |
|--------|------|------|
| High | ⊕⊕⊕⊕ | 真の効果が推定値の近くにあると非常に確信 |
| Moderate | ⊕⊕⊕◯ | そこそこ確信。真の効果は近いが大きく異なる可能性も |
| Low | ⊕⊕◯◯ | 限定的。真の効果は大きく異なるかもしれない |
| Very Low | ⊕◯◯◯ | ほとんど確信なし。真の効果は大きく異なる可能性が高い |

### GRADE Summary of Findings 出力テンプレート

```markdown
| Outcome | Studies (n) | Participants (N) | Effect Estimate (95% CI) | Certainty | Rationale |
| outcome 1 | X | N | SMD 0.45 [0.20, 0.70] | ⊕⊕⊕⊕ High | — |
| outcome 2 | X | N | RR 1.30 [0.90, 1.88] | ⊕⊕◯◯ Low | Downgraded: imprecision (-1), risk of bias (-1) |
```

down/up の根拠を必ず Rationale 列に明記する（「Downgraded: imprecision (-1), risk of bias (-1)」のように要因と幅を書く）。GRADEpro GDT で SoF テーブルを作るのが定番。

---

## 5. 効果量の選択と抽出階層

pooling 前に全結果を共通指標に変換する。「リンゴとオレンジ」を混ぜると無意味なフルーツサラダになる。

### 連続アウトカム

| 指標 | 式 | 使う場面 |
|------|----|---------|
| **SMD**（Standardized Mean Difference） | (M₁ − M₂) / SD_pooled | 同じ構成概念を異なる尺度で測定 |
| **Hedges' g** | SMD × correction factor J | **小標本（n < 20/群）**。Cohen's d より優先 |
| **MD**（Mean Difference） | M₁ − M₂ | 全研究で同一尺度 |
| **Response Ratio** | ln(M₁ / M₂) | 絶対差より比例変化が意味を持つ |

### 二値アウトカム

| 指標 | 式 | 使う場面 |
|------|----|---------|
| **RR**（Risk Ratio） | (a/(a+b)) / (c/(c+d)) | incidence データ、prospective |
| **OR**（Odds Ratio） | (a×d) / (b×c) | case-control、稀なアウトカム |
| **RD**（Risk Difference） | (a/(a+b)) − (c/(c+d)) | 絶対差が重要なとき |
| **NNT**（Number Needed to Treat） | 1 / RD | RD の臨床的解釈 |

### Time-to-event アウトカム

| 指標 | 使う場面 |
|------|---------|
| **HR**（Hazard Ratio） | 打ち切りありの生存/脱落解析 |
| **ln(HR) + SE** | time-to-event メタ解析の標準入力 |

### 効果量の抽出階層（上から優先）

好ましいデータが報告されていなければ、この順で降りる:

1. **Direct**: 群ごとの means, SDs, sample sizes
2. **Derived**: t-statistics, F-statistics, p-values + sample sizes
3. **Estimated**: confidence intervals + point estimates
4. **Approximated**: medians + IQR（**Wan et al. 2014** の方法で変換）
5. **Graphical**: forest plot / bar chart から digitize（**最終手段**）

階層を降りた抽出はデータ抽出表でフラグし、近似した効果量を除いた sensitivity analysis を回す。p 値のみ報告の研究は p + sample size から近似効果量へ変換（Borenstein et al. 2009）。

---

## 6. pooling の可否・出版バイアス検定の研究数ゲート・SWiM

### pooling するか（feasibility）

meta-analysis が適切なのは**全て満たす**とき: PICOS が十分に類似 / アウトカムが比較可能（または標準化可能）/ 使える定量データが **≥ 2 studies**（最低限、5+ が望ましい）/ 臨床・方法論的異質性が誤解を招くほど極端でない / 効果方向が意味をもって結合できる。

**narrative synthesis に切り替える**のは**どれか1つでも**該当: 根本的に異なる構成概念を測定 / 共通効果量に変換不可 / **I² > 90% で moderator が特定できない** / 抽出可能な定量データが 2 studies 未満 / 結合の理論的根拠なく集団・文脈が大きく異なる。

### 出版バイアス検定の研究数ゲート

研究数が足りないのに funnel plot や Egger's を回すと誤検出になる。ゲートを守る:

| 方法 | 用途 | 最小研究数 |
|------|------|-----------|
| **Funnel plot**（視覚） | 常に（定性的） | **≥ 10** |
| **Egger's test** | 連続アウトカム | **≥ 10** |
| **Peters' test** | 二値アウトカム（OR では Egger's より優先） | **≥ 10** |
| **Trim-and-fill** | 「欠けた」研究を補完して調整効果を推定 | **≥ 10** |
| **p-curve analysis** | 有意結果が真の効果を反映するか | **≥ 20** |

PRISMA 14/21 の reporting bias は、研究数がゲートに届かなければ「研究数不足のため定量的 funnel/Egger は実施せず」と明記すること自体が報告になる。

### sensitivity analysis 標準バッテリ

(1) **Leave-one-out**（1研究で結果が駆動されていないか）、(2) 高リスク研究を除いて再 pooling、(3) fixed-effect vs random-effects 比較（大きな乖離=影響力ある異質性）、(4) **trim-and-fill** で出版バイアスの影響、(5) SMD を使ったなら可能な所で MD も計算。事前指定 subgroup（design / 出版年 / 地域 / 標本サイズ中央値上下 / RoB 低高、各 **≥ 2 studies/subgroup**）は**非有意でも全て報告**（null を隠さない）。

### pooling 不適なら SWiM で叙述的統合

meta-analysis が不適なときは **SWiM（Synthesis Without Meta-analysis）** ガイドラインに従う:

- **Grouping of studies**: 介入タイプ・集団・アウトカム等でどう群分けしたか
- **Synthesis method**: vote counting based on **direction of effect** / harvest plot / albatross plot / effect direction plot
- **Summary of findings**（表）: comparison ごとに Studies(n) / Direction of Effect（Favors intervention / Favors control / Mixed）/ Consistency（Consistent / Inconsistent）/ Confidence（High / Moderate / Low）
- **Limitations を明示**: pooled effect size を推定できない / 異質性を正式に評価できない / vote counting は標本サイズ差に影響される / direction of effect は大きさを捉えない

### メタ解析エッジケース

- **< 5 studies**: 技術的に 2+ で可能だが検出力不足。**fixed-effect** を使う（random-effects は少数で τ² を推定できない）。subgroup / meta-regression はしない。強い caveat つきで報告。
- **片群/両群でゼロイベント**: 片群ゼロには continuity correction（0.5）。両群ゼロは標準メタ解析から除外。稀イベントは Peto OR を検討。ゼロイベント研究数を別途報告。
- **混合デザイン（RCT + 観察研究）**: まずデザイン別に pooling。横断 pooling するなら観察=LOW・RCT=HIGH から GRADE 開始。design-stratified と combined の両推定値を報告し結合/分離の根拠を明記。

---

## 7. プロトコル登録

- **いつ**: 公表予定の SR は**常に**、**文献検索を始める前**に登録。outcome reporting bias を防ぎ a priori 計画を示す。
- **どこ**:

| Platform | 対象 | 費用 | URL |
|----------|------|------|-----|
| **PROSPERO** | 健康関連 SR | 無料 | crd.york.ac.uk/prospero |
| **OSF Registries** | 全分野 | 無料 | osf.io/registries |
| **INPLASY** | 全分野 | ~$40 | inplasy.com |
| **Research Registry** | 全分野 | SR は無料 | researchregistry.com |

- **プロトコル内容（PRISMA-P 2015）**: (1) Title・registration・authors・amendments、(2) Rationale・objectives・PICOS、(3) Information sources・search strategy・records management、(4) Data extraction・RoB assessment・data synthesis plan、(5) Meta-bias assessment・confidence in cumulative evidence。
- PRISMA 24（Registration and protocol）は register 名・登録番号・プロトコルへのリンクを本文に書く。

---

## 8. ツール早見

- **解析**: R の `metafor`（包括）/ `meta`（標準・使いやすい）/ `dmetar`（Harrer らの教科書併走）、`RevMan`（Cochrane 必須）、Stata（`metan`, `metareg`, `metabias`）、Python（`statsmodels`, `PythonMeta`）、JASP（GUI）。
- **可視化**: `robvis`（traffic-light plot）、GRADEpro GDT（SoF table）。
- **スクリーニング/管理**: Covidence（Cochrane は無料）、Rayyan（無料・AI 補助）、ASReview（OSS・AI 補助）、EPPI-Reviewer、Zotero/Mendeley。

---

## References

- PRISMA 2020: Page MJ, et al. BMJ. 2021;372:n71. https://doi.org/10.1136/bmj.n71
- RoB 2: Sterne JAC, et al. BMJ. 2019;366:l4898. https://doi.org/10.1136/bmj.l4898
- ROBINS-I: Sterne JAC, et al. BMJ. 2016;355:i4919. https://doi.org/10.1136/bmj.i4919
- GRADE: Guyatt GH, et al. BMJ. 2008;336:924-926.
- Cochrane Handbook for Systematic Reviews of Interventions v6.4 (2023): https://training.cochrane.org/handbook
