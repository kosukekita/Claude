---
name: academic-writing
description: "医学・学術論文の執筆支援。構成（IMRAD）、文体、引用形式、AI 生成テキストパターン（18種）の検出・除去を含む。AI 研究時は TRIPOD+AI（27項目）に準拠した報告を支援。投稿先ジャーナルの推薦（JCR IF ベース）にも対応。Use when user writes, edits, or reviews academic manuscripts, or requests humanization of AI-generated text, or asks for journal recommendation. Trigger phrases: 論文, 原稿, manuscript, abstract, humanize, AI文体, 学術英語, IMRAD, 投稿, 論文執筆, アカデミックライティング, 論文校正, academic writing, medical writing, TRIPOD, prediction model, ジャーナル, journal, IF, インパクトファクター, 投稿先, submission. Do NOT trigger for モデル構築・欠損値補完・SHAP 等の解析の実装そのもの（use ai-prediction-model）— 本スキルは予測モデル研究の『執筆・報告』のみを担当する。"
---

# Academic Writing

> 医学・学術論文の執筆・校正・AI 文体除去を支援するスキル。

## Workflow

論文執筆・校正タスクを受けたら、以下のステップで進める:

### Step 1: タスク分類

| タスク種別 | 内容 | 主な参照セクション |
|-----------|------|-------------------|
| **新規執筆** | 論文のドラフト作成 | 論文構成（IMRAD）、文体ルール |
| **校正・編集** | 既存原稿の改善 | 文体ルール、引用・参考文献 |
| **AI文体除去** | AI生成テキストの humanize | AI文体除去（18パターン） |
| **AI研究報告** | 予測モデル研究の執筆 | TRIPOD+AI チェックリスト |
| **報告ガイドライン選択** | RCT/観察/SR/質的/診断精度等で正しいチェックリストを選ぶ | `references/equator-guideline-selector.md`（予測モデルは TRIPOD+AI） |
| **システマティックレビュー/メタ解析** | SR/MA の執筆・査読 | `references/systematic-review-meta-analysis-toolkit.md` |
| **引用の検証** | 引用が実在し、かつ主張を支持しているか監査 | `references/citation-existence-verification.md`（実在）／`references/citation-claim-faithfulness.md`（支持） |
| **投稿前セルフレビュー** | 致命傷・統計的整合性・論証・図を投稿前に自己点検 | `references/adversarial-self-review.md`、`references/integrity-fallacy-self-audit.md`、`references/argument-frameworks-claim-calibration.md`、`references/figure-design-self-check.md` |
| **著者・貢献** | CRediT/ICMJE での著者資格・貢献記述・AI開示 | `references/authorship-credit-icmje.md` |
| **投稿先選定** | ジャーナル推薦・捕食的ジャーナル回避 | 投稿先ジャーナルの推薦（捕食的ジャーナルのスクリーニング含む） |

### Step 2: 原稿分析（校正の場合）

1. IMRAD 構造に従っているか確認
2. AI 文体パターン（18種）をスキャン
3. 統計表記・引用形式をチェック
4. Results は一文ずつ over/under-claim チェックリストを適用（下記「Results 特有の over/under-claim 検出チェックリスト」）
5. 必要に応じて拡張リファレンスを併用: 引用は実在＋忠実性を監査（`citation-existence-verification.md` / `citation-claim-faithfulness.md`）、統計・デザインは整合性レッドフラグとフォールシーを自己スキャン（`integrity-fallacy-self-audit.md`）、図は `figure-design-self-check.md`、論証は `argument-frameworks-claim-calibration.md`

### Step 3: 執筆・修正

タスク種別に応じて:
- **新規執筆**: IMRAD 構造に従ってセクションを作成
- **校正**: 問題箇所を特定し修正案を提示
- **AI文体除去**: 18パターンに基づいて書き換え

### Step 4: 最終チェック

投稿前チェックリスト（下部参照）を実行。

---

## 論文構成（IMRAD）

医学論文の標準構成:

| セクション | 目的 |
|-----------|------|
| **Title** | 主要な発見を簡潔に要約 |
| **Abstract** | 研究全体の構造化要約（目的・方法・結果・結論） |
| **Introduction** | 背景・先行研究・研究目的 |
| **Methods** | 研究デザイン・対象・手法・統計解析 |
| **Results** | データ・統計結果を客観的に提示 |
| **Discussion** | 結果の解釈・先行研究との比較・限界・結論 |

セクション別の時制使い分けは `references/tenses.md` を参照。

### セクション間の境界ルール

| セクション | 書くべき内容 | 書かない内容 |
|-----------|------------|------------|
| Introduction | 背景、先行研究、研究の目的 | 自データの結果 |
| Methods | 基準、定義、手法、解析計画 | 具体的な数値・結果 |
| Results | データの記述、解析結果、数値 | 手法の正当化、考察、臨床的意義づけ、探索的所見の確証化、因果的言い換え |
| Discussion | 結果の解釈、先行研究との比較、限界 | 新たな結果の提示 |

### Methods–Results の対応（手法なしの結果は御法度）

**Results に登場する解析・アウトカム・感度分析・サブグループ・代替定義は、すべて Methods で事前に設計・定義する**。Methods に対応記述のない解析の結果を Results に突然出すのは御法度（読者は「いつ・なぜその解析をしたか」を追えない）。逆に、Methods で述べた解析は Results で必ず結果を報告する（書きっぱなしにしない）。投稿前に **Methods と Results の解析項目を 1:1 で突き合わせる**。

- NG: Results に「感度分析①②③」「definition 3（定義③）」「サブグループ X」が初出だが、Methods に該当する設計・定義がない。
- OK: Methods「頑健性確認のため感度分析 A・B・C を行った」→ Results「A・B・C の結果は…」。
- 対象: 主解析／補足解析／感度分析／サブグループ解析／代替アウトカム・代替定義／追加モデル など、Results で言及する全解析。

### 各セクションの注意点

- **Introduction**: 広い文脈 → 狭い焦点（funnel 構造）。最終段落で目的・仮説を明示
- **Methods**: 再現可能な詳細度。倫理委員会承認・同意取得を明記。**基準・定義・手法のみ記載し、具体的な数値・結果は Results に記載する**
  - Methods に書く: 試験デザイン、適格/除外基準、アウトカムの定義、統計手法、モデル構成、分割基準、感度分析の設計
  - Methods に書かない（→ Results）: 具体的なサンプルサイズ（n=448 等）、群ごとの人数（BP 259名, PTH 189名 等）、施設数・施設ごとの登録数、欠測の理由・割合の具体的数値、解析結果から判明した事実
  - NG（Methods に結果が混在）: "有効解析対象: n=448（BP 259, PTH 189）。欠測は主にBMD未測定施設による。"
  - OK: Methods に "12ヶ月時点BMDが未測定の患者は解析から除外した。" → Results に "448名（BP群259名、PTH群189名）が有効解析対象となった。"
  - **除外「基準」は Methods、除外「件数・残存 n」は Results**（同じ除外を1文に混ぜない）。除外基準は事前計画なので Methods、実際に何例除外され何例残ったかは特定データに適用した帰結なので Results（CONSORT/STROBE の participant flow と同じ理屈）。
    - NG（基準と件数が Methods に同居）: "For E1, 22 patients without a recorded observation period were excluded, yielding 2,586."
    - OK: Methods に "E1 was analyzed in patients with an available vertebral-fracture observation period."（基準）→ Results の analysis-set 段落に "For E1, 22 patients without a recorded observation period were excluded, leaving 2,586; E2 and E3 retained all 2,608."（件数・残存 n）
    - 特にアウトカムごとに分母 n が異なる場合（例: E1=2,586 / E2・E3=2,608）、その差は Results の表に出るので、Results 本文の analysis-set 段落で件数差の理由を1文添えると表が自己説明的になる。
  - **ソフトウェア名は専用パラグラフに一度だけ／関数名は論文に書かない**: 使用パッケージ・ソフトウェア名（version 付き）は「統計解析ソフトウェア（再現性）」の専用パラグラフに一度だけ記載し、各手法パラグラフでは繰り返さない。**具体的な関数名（例: regression_forest(), causal_survival_forest()）は論文本文に一切書かない**。手法は概念で記述し（例: "a regression forest"・"a causal survival forest"）、関数名は共有する解析コード／補遺（supplement）に置く。
- **Results**: データを先に、解釈は Discussion で。表・図を効果的に使用。**Study flow diagram（participant flow / CONSORT / STROBE diagram）は Results セクションに配置する**（Lancet 系列の標準）。N数・除外数は Methods の段階では未知の情報であり、Methods には配置しない
- **Discussion**: 主要な発見を最初に述べる。限界は正直に、しかし過度に卑下しない
- **Outcome / Endpoint の用語**: 「Primary outcome/endpoint」は Secondary outcome が存在する場合にのみ使用する。アウトカムが1つしかない研究では単に「outcome」「endpoint」と記載する。「Primary」と書くと Secondary outcome の記述を読者が期待するため不自然

### Results 特有の over/under-claim 検出チェックリスト

Results は結果を淡々と記述し、過大主張（over-claim）も過小評価（under-claim）も排除する。**各文について、対応する統計出力を 1 つ特定できない文、または Discussion に属する評価語（clinical importance / negligible / determinant / demonstrated など）を含む文は書き換える**。境界ルール表・AI 文体 18 パターンは文体・レトリックを扱うが、ここは統計用語の意味論（推定量 → 言語表現の対応）を扱う。Results を一文ずつ次の基準で点検する。

- **探索的に選ばれた最良群の効果を確証的に書かない（winner's curse）**
  - NG: `The top CATE quartile demonstrated a statistically significant extension in fracture-free survival.`
  - OK: `In the quartile with the largest estimated CATE, the observed difference was ...; this subgroup was identified exploratorily from the same data.`
- **variable importance / SHAP / feature ranking を effect modifier・determinant と言い換えない**（予測寄与は効果修飾の証明ではない）
  - NG: `... were important determinants of HTE and acted as patient-classifying factors.`
  - OK: `... ranked highly in variable importance; this ranking alone does not establish effect modification.`
- **非有意な相互作用・群差を「効果あり」「より有効」と書かない**
  - NG: `PTH was more effective in patients without hypertension.`（交互作用が非有意なのに）
  - OK: `The interaction term was not significant; the data did not show that the effect differed by hypertension status.`
- **回帰係数・相互作用係数を因果的に言い換えない**
  - NG: `The coefficient indicated that hypertension reduced the benefit of PTH.`
  - OK: `The fitted interaction coefficient was negative, corresponding to a lower estimated treatment effect under the model.`
- **非有意・不精確を「no effect」「random error の範囲」「clinically negligible」と断定しない**
  - NG: `The effect was clinically negligible and within the range of random error.`
  - OK: `The estimate was ... (95% CI ...); clinical importance is not assessed in Results.`
- **統計的有意を臨床的意義・真の効果の証明に昇格させない**
  - NG: `A statistically significant benefit was demonstrated.`
  - OK: `A difference was estimated, with a 95% CI excluding the null.`
- **association / estimate / rank と effect modification / mechanism / causation を分ける**（後者は Discussion）

---

## 学術英語の文体ルール

### 基本原則

1. **簡潔性** — 一文一意。不要な語を削除する
2. **正確性** — 曖昧な表現を避け、具体的なデータで裏付ける
3. **客観性** — 中立的なトーン。プロモーション的表現を排除
4. **一貫性** — 用語・略語・表記を統一する

### 能動態 vs 受動態

- **Methods**: 受動態が標準（"Blood samples were collected..."）
- **Results/Discussion**: 能動態を推奨（"We found that...", "The results show..."）
- 主語が重要でない場合のみ受動態を使用

### 避けるべき表現

| 避ける | 使う |
|--------|------|
| In order to | To |
| Due to the fact that | Because |
| A total of N patients | N patients |
| It is important to note that | （削除して直接述べる） |
| The study has the ability to | The study can |
| With respect to | For / Regarding |
| At the present time | Currently |
| In the majority of cases | Usually / In most cases |

### 数値・統計の表記

- ハザード比・オッズ比には 95% CI を必ず付記: `(HR 0.65; 95% CI 0.50-0.85; P = 0.002)`
- P 値: `P = 0.002`（大文字 P、イタリック推奨）。`P < 0.001` は具体値が不明な場合のみ
- パーセンテージ: 小数点以下1桁に統一
- 略語: 初出時にフルスペル `sodium-glucose cotransporter 2 (SGLT2)`
- **Abstract 内の略語ルール**: Abstract 内で **3回以上** 使用される略語のみ定義する。1-2回しか使わない略語はフルスペルのまま記載し、略語定義しない。Abstract は独立した文章であり、本文の略語定義とは別に判断する
- **Figure Legends 内の略語ルール**: Figure Legends は本文とは独立したユニットであり、**略語は再定義が必要**。Legend テキスト内では本文と同じルール（2回まではフルスペル、3回以上で略語を使用）を適用する。**Figure 内に表示される略語**は、Legend の初出時から「略語（フルスペル）」で定義する。Legend テキストで説明されなかった Figure 内の略語は、Legend 末尾に `Abbreviations:` として一覧記載する
  - 例: `Figure 1. Changes in BMD from baseline to 12 months.` → 末尾に `Abbreviations: BMD, bone mineral density; BP, bisphosphonate; PTH, parathyroid hormone.`

---

## 引用・参考文献

### バンクーバー方式（医学論文標準）

- 本文中: 番号順に上付き数字 `...mortality was reduced.¹`
- 引用リスト: 出現順に番号付け
- 著者6名まで全員記載、7名以上は最初の6名 + "et al."

### 引用の原則

- **具体的に引用**: "Studies show..." ではなく "In the EMPA-REG OUTCOME trial,¹..."
- **一次文献を優先**: レビュー論文よりオリジナル研究を引用
- **引用の配置**: 文末ピリオドの前に配置
- **引用なき一般化の禁止**: 「よく知られている（it is well known）」「報告されている（it has been reported）」と書く場合は必ず引用文献を付ける。自データから得た知見を一般的事実のように記述してはならない — 自データの結果は Results セクションで報告する

---

## AI 文体除去（Humanizer）

AI 生成テキストに共通する 18 パターンを 4 カテゴリに分類。
（18 パターンは文体の問題を扱う。Results の統計的 over/under-claim は別掲「Results 特有の over/under-claim 検出チェックリスト」で判定する。）
詳細な検出キーワード・Before/After 例は `references/humanizer-patterns.md` を参照。

### パターン概要

| # | カテゴリ | パターン | 修正方針 |
|---|---------|---------|---------|
| 1 | Content | 過度な重要性強調 | 具体的データに置換 |
| 2 | Content | 注目度・メディア強調 | 検証可能な事実のみ |
| 3 | Content | 表面的な -ing 分析 | 動名詞削除、明示的解釈 |
| 4 | Content | プロモーション言語 | 中立・測定可能な表現 |
| 5 | Content | 曖昧な引用 | 具体的試験名・著者名 |
| 6 | Content | 型にはまった課題セクション | 実際の限界・方法論 |
| 7 | Language | AI 多用語 | 単純で多様な語彙 |
| 8 | Language | コピュラ回避 | 直接的な is/are |
| 9 | Language | 否定的並列 | 直接的な文 |
| 10 | Language | 3つセット過度使用 | 意味のある項目のみ |
| 11 | Language | 同義語循環 | 一貫した用語 |
| 12 | Language | 偽の範囲表現 | 正確なメトリック |
| 13 | Style | エムダッシュ過度使用 | 括弧・文構造再構築 |
| 14 | Style | タイトルケース見出し | センテンスケース |
| 15 | Style | カーリークォート | ストレート引用符 |
| 16 | Filler | フィラー表現 | 簡潔化 |
| 17 | Filler | 過度なヘッジング | データに基づく直接表現 |
| 18 | Filler | 一般的ポジティブ結論 | 具体的次ステップ・限界 |

### Humanizer 実行手順

1. 入力テキストを通読
2. 18 パターン全てを走査して該当箇所を特定
3. 各パターンの修正方針に従って書き換え
4. 科学的データ（数値・統計・発見）は変更しない
5. 修正版テキストと変更点サマリーを出力

---

## AI 研究の報告ガイドライン（TRIPOD+AI）

> AI/機械学習を用いた臨床予測モデルの開発・評価研究では **TRIPOD+AI** に準拠して報告する。
> TRIPOD+AI は 2024 年に BMJ で公開された 27 項目のチェックリストであり、旧 TRIPOD 2015 を置換する。

### 適用範囲

TRIPOD+AI は以下に該当する研究に適用:
- 回帰モデル・機械学習・深層学習による **予測モデルの開発**
- 既存予測モデルの **外的検証（validation）**
- 予測モデルの **更新（updating）**
- 診断・予後・モニタリング・スクリーニング目的を問わない

> **LLM を用いた研究** の場合は TRIPOD-LLM（Nature Medicine, 2024）も併せて参照すること。

### TRIPOD+AI チェックリスト（27 項目）

#### Title & Abstract

| Item | 報告内容 |
|------|---------|
| **1** | タイトルに予測モデルの開発/評価であること、対象集団、アウトカムを明示 |
| **2** | Abstract は TRIPOD+AI for Abstracts（13 項目）に準拠 |

#### Introduction

| Item | 報告内容 |
|------|---------|
| **3a** | ヘルスケアの文脈と研究の根拠を説明 |
| **3b** | 対象集団とケアパスウェイにおけるモデルの使用目的を記述 |
| **3c** | グループ間の既知の健康格差を記述 |
| **4** | 研究目的を明示（開発・検証・更新のいずれか） |

#### Methods

| Item | 報告内容 |
|------|---------|
| **5a-b** | データソース・データ取得期間を記述 |
| **6a-c** | 研究セッティング・適格基準・治療内容を記述 |
| **7** | データの前処理・品質チェック方法を記述 |
| **8a-c** | アウトカムの定義・評価方法・評価者の盲検化を記述 |
| **9a-c** | 予測因子の選択・測定方法を記述 |
| **10** | サンプルサイズの根拠を説明 |
| **11** | 欠測データの取り扱い方法を記述 |
| **12a-g** | 分析方法（モデル構築・検証・性能評価の手法）を記述 |
| **13** | クラス不均衡への対処方法を記述（該当する場合） |
| **14** | 公平性（fairness）に関するアプローチを記述 |
| **15** | モデル出力の形式を明示 |
| **16** | 開発データと評価データの差異を特定 |
| **17** | 倫理委員会承認を明記 |

#### Open Science

| Item | 報告内容 |
|------|---------|
| **18a** | 資金源を記載 |
| **18b** | 利益相反を開示 |
| **18c** | プロトコルへのアクセス方法を記載 |
| **18d** | 事前登録情報を記載 |
| **18e** | データの利用可能性を記載 |
| **18f** | コードの利用可能性を記載 |

#### Patient & Public Involvement

| Item | 報告内容 |
|------|---------|
| **19** | 患者・市民参画（PPI）の詳細を記載 |

#### Results

| Item | 報告内容 |
|------|---------|
| **20a-c** | 参加者のフロー・特性を記述 |
| **21** | 各分析における参加者数を明示 |
| **22** | 再現可能なモデルの完全な詳細を提供 |
| **23a-b** | 性能指標を信頼区間とともに報告 |
| **24** | モデル更新の結果を報告（該当する場合） |

#### Discussion

| Item | 報告内容 |
|------|---------|
| **25** | 公平性への考慮を含む全体的な解釈 |
| **26** | 研究の限界を議論 |
| **27a-c** | モデルの実用性・ユーザー要件・今後の研究を議論 |

### TRIPOD+AI for Abstracts チェックリスト（13 項目）

1. 予測モデルの開発/評価であること、対象集団、アウトカムを明示
2. ヘルスケアの文脈と研究の根拠を簡潔に記述
3. 研究目的を明示（開発・検証・両方）
4. データソースを記述
5. 適格基準とセッティングを記述
6. アウトカムと時間軸を明示
7. モデルの種類・構築手順・検証方法を明示
8. 性能評価指標を明示
9. 参加者数とアウトカムイベント数を報告
10. 最終モデルの予測因子を要約
11. 性能推定値を信頼区間とともに報告
12. 結果の全体的な解釈を提示
13. 事前登録番号とレジストリ名を記載

### TRIPOD+AI における重要ポイント

- **再現性**: コード・データの公開を積極的に行い、モデルの再現を可能にする（Item 18e-f）
- **公平性**: サブグループ間での性能差・バイアスを評価し報告する（Item 14, 25）
- **前処理の透明性**: 特徴量エンジニアリング・正規化・欠測処理を全て記述する（Item 7, 11）
- **検証**: 内的検証と外的検証を区別し、方法論を明確に報告する（Item 12）
- **性能指標**: Discrimination（AUROC 等）と Calibration の両方を報告し、CI を付記する（Item 23）

---

## 著者リスト管理

共著者の名前・所属情報は `references/authors.md` に格納されている。
論文作成・投稿時にユーザーが著者名（Last Name）を指示したら、リストから該当著者を抽出して整形出力する。

### 重要な注意事項

- **`authors.md` の順番は原稿の著者順序と無関係**。著者順はユーザーが指示する順番に従うこと
- **必要な著者のみ抽出して使用する**。リスト全員を自動的に含めず、ユーザーが指定した著者だけを記載すること

### 使い方

ユーザーの指示例:
- 「Kita, Ebina, Etani を著者に入れて」
- 「全員を著者リストに」
- 「Kita を first author、Hori を last author にして」

### 出力フォーマット

**タイトルページ用（著者名 + 上付き所属番号）:**

```
Kosuke Kita¹², Kosuke Ebina¹, Yuki Etani¹

¹ Department of Orthopaedic Surgery, Osaka University Graduate School of Medicine
² Department of Artificial Intelligence in Diagnostic Radiology, Osaka University Graduate School of Medicine
```

- 所属番号は出現順に重複排除して自動割り当て
- 同じ所属の著者は同じ番号を共有

**投稿フォーム用（個別フィールド）:**

```
Author 1: First Name: Kosuke | Last Name: Kita
  Affiliation 1: Department of Orthopaedic Surgery, Osaka University Graduate School of Medicine
  Affiliation 2: Department of Artificial Intelligence in Diagnostic Radiology, Osaka University Graduate School of Medicine

Author 2: First Name: Kosuke | Last Name: Ebina
  Affiliation: Department of Orthopaedic Surgery, Osaka University Graduate School of Medicine
```

### 著者リストの更新

新しい共著者を追加する場合は `references/authors.md` に行を追加する。

---

## 投稿先ジャーナルの推薦

ユーザーから投稿先ジャーナルの相談を受けた場合、`references/translational_journals_analysis.md` のジャーナルリスト（Clarivate JCR IF 順）を参照して推薦する。

### 推薦の原則

1. **研究テーマとの適合性**: ジャーナルの Scope・Aims に研究内容が合致するか最優先で判断
2. **インパクトファクター**: リストの IF を参考に、研究の新規性・エビデンスレベルに見合うジャーナルを提案
3. **OA 要件**: 助成金や所属機関の OA ポリシーを考慮
4. **段階的提案**: 第一候補（挑戦的）・第二候補（妥当）・第三候補（確実）の 3 段階で提案する
5. **リスト外のジャーナル**: 研究分野がリストの対象（Translational Medical AI）と異なる場合は、その旨を伝えた上で分野固有のジャーナルを提案する

### 捕食的ジャーナルのスクリーニング

投稿先・引用先のジャーナルが捕食的（predatory）でないかを投稿前に確認する。以下のレッドフラグが複数該当する場合は要警戒。

**レッドフラグ・チェックリスト:**

- [ ] 攻撃的なメール勧誘（submit を促す spam 的メール）
- [ ] 投稿から **72時間以内**での受理（査読が機能していない）
- [ ] 編集委員会が不明、または偽名・無関係な研究者を無断掲載
- [ ] Scopus / Web of Science / PubMed のいずれにも索引されていない
- [ ] **COPE**（Committee on Publication Ethics）非加盟
- [ ] **DOAJ**（Directory of Open Access Journals）未収載（OA誌の場合）
- [ ] 過度に広いスコープ（"International Journal of Everything" 的）
- [ ] 偽・水増しの impact metric（独自指標を IF と詐称等）
- [ ] サイトの英文が粗悪（文法・スペルミス多数）
- [ ] APC が異常に低い（full OA で **< $200**）／逆に不透明
- [ ] 編集部の所在地が表記された国と相違
- [ ] 撤回（retraction）方針・倫理方針の欠如

**正当性の確認リソース:**

- **DOAJ** — 正当な OA 誌のホワイトリスト
- **COPE member directory** — 出版倫理団体の加盟確認
- **Scopus Source List** / **Journal Citation Reports (Clarivate)** — 索引・指標の正本
- **Cabell's Predatory Reports** — 捕食的誌のブラックリスト（購読制）
- **Beall's List** — 非公式だが出発点として有用
- **Think. Check. Submit.**（thinkchecksubmit.org） — 投稿前の総合チェックツール

---

## 投稿規定の数値ルールは実掲載論文で実態を確認してから守る

投稿規定（Author Instructions）に書かれた **数値の制約**（抄録の語数上限、本文 word count、参考文献数、図表数の上限など）は、額面どおりに機械適用する前に、**その雑誌の実掲載論文を実測して実態を確認する**。規定の数値は編集・査読の過程で柔軟に運用されることが多く、規定を超えていてもアクセプトされている論文が珍しくない。規定値ぎりぎりまで削って情報密度を不必要に落とす前に、まず実態を調べる。

### 手順

1. **規定値を把握する**: まず Author Instructions の数値（例: 抄録 250–300語）を確認する。
2. **実掲載論文を実測する**: 同じ雑誌・同じ article type（Original Article 等）の実際の掲載論文を **10〜40 本**集め、対象の数値（抄録語数など）を**実測**する。
   - 取得元: PubMed E-utilities（`esearch`/`efetch`、認証不要・公開）。ジャーナル名タグ `"<ISO略名>"[jour]`、`[pt]` で article type を絞る。efetch の XML（`<AbstractText>`）が構造化抄録のラベルを保持する。語数は本文トークンを実測する（ラベル語は不算入で統一）。出版社サイトが bot 保護（Cloudflare 等）で取れなくても PubMed/PMC からは取得できることが多い。
3. **要約統計を出す**: 最小・中央値・最大・平均、および「規定値を超えている論文の割合」を算出する。
4. **判断する**:
   - 自分の原稿が **実掲載の中央値前後かそれ以下**なら、規定値を多少超えていても **そのまま採用してよい**（不要な削減をしない）。
   - 実掲載でも稀にしか超えない数値を**大きく**超えている場合のみ、削減を検討する。
   - 削減する場合も、報告すべき数値（CI・P値）や非 directive のフレーミングは落とさず、冗長語・フィラーから削る。
5. **ユーザーに実態を示す**: 「規定は X だが実掲載は中央値 Y・最大 Z で N% が規定超。よって…」と根拠を添えて判断を提示する。

> この原則は語数だけでなく、参考文献数・図表数・著者数など投稿規定中の全ての「数値上限」に適用する。ただし **構造（見出しの種類と順序）・必須要素（試験登録番号・資金源の記載・報告ガイドライン準拠）・倫理要件は数値ルールではなく、実態に関わらず厳守する**。

## Figure 作成ルール

- **フォントサイズ**: Figure 内の全てのテキスト（軸ラベル、凡例、注釈等）は **20pt 以上** とする
- **略語**: Figure 内で使用した略語は、全て **Figure Legend（図の説明文）に定義を記載** する

## Table キャプション・脚注ルール

表のキャプションは「**1文の表題＋表下の脚注（Note/legend）**」に分離する。ICMJE は明文で *"Place explanatory matter in footnotes, not in the heading."*（説明事項は見出しではなく脚注へ）と規定し、AMA Manual of Style（11th ed.）・NEJM ファミリーの実掲載論文も同じ構造（タイトル＝1文の名詞句、補足は全て脚注）。複数文を表題位置に連結した「物語的キャプション」は非標準。

- **表題（1文）**: 「この表が何を示すか」だけを書く。例: `Baseline characteristics of the pooled analysis set, by initial treatment.` / `Overall average treatment effect, expressed as the difference in restricted mean survival time.`
- **脚注（Note）に置く**: 統計表記の慣例（mean (SD), n (%)）/ 略語キー（表は本文と独立に読まれるため、本文既出でも各表の脚注に再掲）/ 記号（✓ 等）の意味 / 群・分類の定義（例 Q1=greatest predicted benefit）/ 行の収載基準（どの行を載せたか）/ 効果量の向き（positive = …）/ 欠測 n。
- **表のキャプション・脚注に「結果」を書かない**（最重要）。結果＝具体的な所見の数値・有意性の判定文・効果の解釈。これらは Results 本文のみに置く。
  - 排除する例: "All point estimates were slightly negative and all 95% CIs crossed 0, with no significant difference"（=結果文。しばしば直前の本文と重複）/ "(statistically significant)"（=判定ラベル）。
  - 「結果」と「定義/凡例」の線引き: **判定ラベル**（significant / present / no modifier 等、実データへの評価）は本文へ。**判定規則そのものの定義**（"HTE was classified as present when both AUTOC and Cochran's Q met P<0.05" のように、何をもってそのカテゴリとするかの機械的ルール）は脚注に置いてよい。✓ 等の記号は「statistically significant」と書かず "95% CI lower bound exceeded 0" のような機械的条件で定義する。
- **収載基準と表内容の整合**: 「有意な変数のみ掲載」と脚注に書くなら、非該当アウトカムに min P 値の行を載せている等の矛盾を残さない。「該当が無い場合は最小 P 値を示す」まで脚注で明示して整合させる。

---

## 投稿前チェックリスト

- [ ] IMRAD 構成に従っている
- [ ] Abstract が構造化されている（Objective / Methods / Results / Conclusions）
- [ ] 略語は全て初出時にフルスペルで定義
- [ ] Abstract 内の略語は3回以上使用されるもののみ定義（1-2回はフルスペルのまま）
- [ ] Figure Legends 内の略語は本文とは独立して再定義されている（Figure 内の略語は Legend 末尾に Abbreviations として一覧記載）
- [ ] 統計値に 95% CI と P 値が付記されている
- [ ] 引用は具体的（曖昧な "Studies show" がない）。引用なき一般化がない
- [ ] Methods に具体的な数値・結果が混在していない（N数、群ごとの人数等は Results に記載）
- [ ] 除外「基準」は Methods、除外「件数・残存 n」は Results に分けて記載（同じ除外を1文に混ぜていない）。アウトカム別に分母 n が異なる場合は Results の analysis-set 段落で件数差の理由を明記
- [ ] Methods と Results の解析項目が 1:1 対応している（Results の全解析・感度分析・代替定義が Methods に設計記述あり。手法なしの結果がない）
- [ ] Results の各文が over/under-claim チェックリストを通過している（探索的最良群の確証化、variable importance の effect modifier 化、非有意の効果あり化、係数の因果的言い換えがない）
- [ ] AI 文体パターン（18種）が除去されている
- [ ] 見出しがセンテンスケースになっている
- [ ] ストレート引用符を使用している
- [ ] 能動態/受動態がセクションに応じて適切に使用されている
- [ ] フィラー表現・過度なヘッジングが除去されている
- [ ] Figure 内のフォントサイズが 20pt 以上である
- [ ] Figure 内の略語が全て Figure Legend に定義されている
- [ ] **Table のキャプションが「1文の表題＋表下の脚注」に分離されている**（ICMJE: 説明事項は見出しでなく脚注へ。物語的な複数文キャプションがない）
- [ ] **Table のキャプション・脚注に「結果」（所見の数値・有意性の判定文・効果の解釈）が書かれていない**（結果は Results 本文のみ。判定規則の定義は脚注可、判定ラベルは本文へ）
- [ ] Table の略語が各表の脚注に再定義され、記号（✓ 等）が機械的条件で定義されている。脚注の収載基準が表内容と矛盾していない
- [ ] Target journal の投稿規定（word count、reference style 等）に準拠
- [ ] **投稿規定の数値ルール（抄録語数・本文word count・文献数・図表数）は、厳守して削る前にその雑誌の実掲載論文を実測し実態を確認した**（規定超でもアクセプトされている例が多い。見出し構造・必須要素・倫理要件は数値ルールではなく厳守）
- [ ] **AI 研究の場合**: TRIPOD+AI 27 項目チェックリストに準拠している
- [ ] **AI 研究の場合**: Abstract が TRIPOD+AI for Abstracts 13 項目に準拠している
- [ ] **LLM 研究の場合**: TRIPOD-LLM チェックリストにも準拠している
- [ ] ソフトウェア・パッケージ名は専用パラグラフ（統計解析ソフトウェア・再現性）に一度だけ記載。関数名は論文本文に書いていない（手法は概念で記述し、関数名はコード／補遺に置く）
- [ ] **報告ガイドライン**: 研究デザインに対応する EQUATOR チェックリストに準拠（RCT=CONSORT／観察研究=STROBE／SR・MA=PRISMA／質的=COREQ／診断精度=STARD／症例報告=CARE 等。`references/equator-guideline-selector.md`）
- [ ] **引用検証**: 全参照が実在し（捏造・ハルシネーション参照なし）、各引用がその主張を実際に支持している（集団・指標・結論強度の歪曲なし。`references/citation-existence-verification.md` / `citation-claim-faithfulness.md`）
- [ ] **整合性・フォールシー**: P-hacking/HARKing 等の整合性レッドフラグと名前付きフォールシー（Simpson/ecological/RTM/Texas sharpshooter 等）を自己スキャン済み（`references/integrity-fallacy-self-audit.md`）
- [ ] **敵対的セルフレビュー**: CRITICAL 4類型（Foundation Collapse／Logic-Chain Break／Data-Conclusion Mismatch／Stronger Counter-Narrative）を投稿前に自己点検済み（`references/adversarial-self-review.md`）
- [ ] **著者・貢献**: CRediT 役割と ICMJE 著者4要件を満たし、AI 利用を開示している（`references/authorship-credit-icmje.md`）
- [ ] **投稿先**: 捕食的ジャーナルのレッドフラグを確認済み（投稿先・引用先とも）

---

## References

### 既存リファレンス

- `references/tenses.md` — セクション別の時制使い分けガイド（IMRaD）
- `references/humanizer-patterns.md` — 18 パターンの詳細な検出・修正リファレンス
- `references/authors.md` — 共著者リスト（名前・所属）
- `references/translational_journals_analysis.md` — Translational Medical AI ジャーナルの JCR IF 順リスト（投稿先推薦用）

### 拡張リファレンス（執筆・自己査読・文献調査の質を高める）

- `references/citation-claim-faithfulness.md` — 引用‑主張の忠実性監査（存在≠支持）。6次元照合・5段階 verdict ladder・defect stage 語彙・Pass 規則・サンプリング・安全な書き換え例
- `references/citation-existence-verification.md` — 引用の実在検証。S2/Crossref/OpenAlex/arXiv（+PubMed）へ多重照会しタイトル類似度0.70と DOI/ID クロスチェックで捏造参照を摘発（単一インデックスの欠落≠捏造）
- `references/equator-guideline-selector.md` — 研究デザイン→EQUATOR 報告ガイドライン選択表（PRISMA/CONSORT/STROBE/COREQ/SQUIRE 等の凝縮チェックリスト＋フロー図。TRIPOD 以外の全ファミリ）
- `references/integrity-fallacy-self-audit.md` — 統計的整合性レッドフラグ（P-hacking/HARKing 等、severity 付き）と名前付きフォールシー（検出 tell 付き）で投稿前に自原稿を自己監査
- `references/figure-design-self-check.md` — Figure 設計の自己チェック（チャート種選択・禁則と修正・色覚/コントラスト配慮・VLM 描画検証・キャプション過大主張）
- `references/adversarial-self-review.md` — 投稿前の敵対的セルフレビュー（3レンズ精読・devil's-advocate ストレステスト・CRITICAL 4類型・severity 較正2ゲート）
- `references/authorship-credit-icmje.md` — CRediT 14役割・ICMJE 著者4要件・著者/謝辞境界・Author×Role マトリクス・AI 著者方針と AI 引用例
- `references/systematic-review-meta-analysis-toolkit.md` — SR/MA 報告ツールキット（PRISMA 2020・RoB 2/ROBINS-I・I²/GRADE・効果量と抽出階層・出版バイアス検定ゲート・SWiM・PROSPERO/OSF）
- `references/argument-frameworks-claim-calibration.md` — 原稿の論証検査と主張言語の較正（Toulmin/Bradford Hill/IBE/エピステミック・ステータス梯子）

### 外部リンク

- [TRIPOD+AI statement (BMJ 2024)](https://pubmed.ncbi.nlm.nih.gov/38626948/) — AI 予測モデル研究の報告ガイドライン（27 項目）
- [TRIPOD+AI Expanded Checklist & Supplement](https://www.tripod-statement.org/) — 各項目の詳細な説明と記入例
- [TRIPOD-LLM (Nature Medicine 2024)](https://www.nature.com/articles/s41591-024-03425-5) — LLM を用いた生物医学研究の報告ガイドライン
