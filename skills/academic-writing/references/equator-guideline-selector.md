# 研究デザイン→EQUATOR 報告ガイドライン選択表

> 執筆を始める前に「自分の研究デザインに正しい報告チェックリスト（reporting guideline）を当てる」ための対応表。EQUATOR Network（Enhancing the QUAlity and Transparency Of health Research）が集約する各ガイドラインを design → guideline で引けるようにし、主要 5 種（PRISMA / CONSORT / STROBE / COREQ / SQUIRE）の中核項目を凝縮して併載する。予後・予測モデルの **TRIPOD** は本スキルの TRIPOD+AI reference が深く扱うため、ここでは選択表の 1 行として触れるに留める。

報告ガイドラインは「どう報告するか（reporting）」の最低基準であり、研究デザインそのものや解析実装（欠損補完・SHAP 等）の指示書ではない。Methods/Results の文章化の直前にここで guideline を確定し、該当チェックリストの全文を [EQUATOR Network](https://www.equator-network.org/) からダウンロードして突き合わせる。

---

## 1. 研究デザイン → 報告ガイドライン 対応表

| 研究デザイン | 主たる報告ガイドライン | 適用シーン |
|---|---|---|
| Systematic review / Meta-analysis | **PRISMA**（PRISMA 2020 が最新） | 複数研究を統合する文献レビュー |
| ├─ Scoping review | **PRISMA-ScR** | システマティックレビューより緩いスコーピングレビュー |
| └─ Network meta-analysis | **PRISMA-NMA** | 多重比較メタアナリシス |
| Randomized controlled trial（RCT） | **CONSORT**（CONSORT 2010 + extensions） | ランダム割付を伴う介入実験 |
| ├─ クラスター（学級/施設単位）割付 | **CONSORT-Cluster** | 個人単位の完全ランダム化が困難なとき |
| └─ 社会的/心理的介入 | **CONSORT-SPI**（Social and Psychological Interventions extension） | 盲検化が難しい/教育・行動介入 |
| Observational study（cohort / case-control / cross-sectional） | **STROBE** | 介入を伴わない量的観察研究 |
| Qualitative research（インタビュー・フォーカスグループ・観察） | **COREQ**（32 項目・3 ドメイン） | 質的研究。民族誌は **SRQR** を代替として検討 |
| Quality improvement study | **SQUIRE 2.0** | 系統的な質改善プロジェクトの報告 |
| Diagnostic accuracy study | **STARD** | 診断ツール（検査）の精度評価 |
| Prognostic / prediction model study | **TRIPOD** | 予測モデルの開発・検証（→ 本スキルの TRIPOD+AI reference で詳述） |
| Case report | **CARE** | 単一または少数例の詳細症例報告 |
| Economic evaluation | **CHEERS** | 費用対効果分析 |
| Mixed methods research | **GRAMMS** | 質的・量的を組み合わせたデザイン |
| Animal study | **ARRIVE** | 動物実験 |

> 報告ガイドラインは最低基準であって質の上限ではない。チェックリストを満たしても研究の質の高さは保証されないが、満たせていない場合は報告の質に欠陥があることを通常は示す。

---

## 2. PRISMA — Systematic Review / Meta-analysis 凝縮チェックリスト

**Full Name**: Preferred Reporting Items for Systematic Reviews and Meta-Analyses ／ **Version**: PRISMA 2020（最新）

| # | Item | 内容 | 必要度 |
|---|---|---|---|
| 1 | **Title** | systematic review（meta-analysis の有無も）と明示 | Required |
| 2 | **Abstract** | 構造化抄録（background, purpose, methods, results, conclusions） | Required |
| 3 | **Registration** | 登録番号とプラットフォーム（例: PROSPERO） | Strongly recommended |
| 4 | **Eligibility criteria** | 選択・除外基準を PICOS または PEO 形式で | Required |
| 5 | **Information sources** | 検索したデータベースと日付 | Required |
| 6 | **Search strategy** | 少なくとも 1 つの DB の完全な検索式 | Required |
| 7 | **Selection process** | スクリーニング過程（レビュアー数、不一致の解消法） | Required |
| 8 | **Data extraction** | データ抽出方法 | Required |
| 9 | **Risk of bias** | バイアスリスク評価ツールと結果 | Required |
| 10 | **Synthesis methods** | 統合方法（narrative / meta-analytic） | Required |
| 11 | **PRISMA flow diagram** | 文献スクリーニングのフロー図 | Required |
| 12 | **Results** | 各研究の特性、バイアス評価、統合結果 | Required |
| 13 | **Discussion** | エビデンスの確実性、限界、既知見との関係 | Required |
| 14 | **Funding** | 資金源と利益相反 | Required |

### PRISMA フロー図テンプレート

```
Records identified (n = )
├── Database searching (n = )
└── Other sources (n = )
         ↓
Duplicates removed (n = )
         ↓
Records screened (n = )
├── Excluded (n = )
         ↓
Reports sought for retrieval (n = )
├── Not retrieved (n = )
         ↓
Reports assessed for eligibility (n = )
├── Excluded, with reasons (n = )
│   ├── Reason 1 (n = )
│   ├── Reason 2 (n = )
│   └── Reason 3 (n = )
         ↓
Studies included in review (n = )
├── In qualitative synthesis (n = )
└── In quantitative synthesis (meta-analysis) (n = )
```

---

## 3. CONSORT — Randomized Controlled Trial 凝縮チェックリスト

**Full Name**: Consolidated Standards of Reporting Trials ／ **Version**: CONSORT 2010 + extensions

| # | Item | 内容 |
|---|---|---|
| 1 | **Title & Abstract** | RCT と明示、構造化抄録 |
| 2 | **Background** | 科学的背景と試験の根拠 |
| 3 | **Objectives** | 具体的目的または仮説 |
| 4 | **Trial design** | デザイン型（parallel, crossover, factorial 等）と割付比 |
| 5 | **Participants** | 適格基準、セッティング、データ収集場所 |
| 6 | **Interventions** | 各群の介入の具体的記述（投与方法・タイミングを含む） |
| 7 | **Outcomes** | 主要・副次アウトカム指標（定義と時点を含む） |
| 8 | **Sample size** | サンプルサイズ計算法（power analysis） |
| 9 | **Randomisation** | ランダム系列生成法、割付の隠蔽（allocation concealment）機構 |
| 10 | **Blinding** | 盲検化の実施（誰を、どう盲検したか） |
| 11 | **Statistical methods** | 統計解析法、ITT/PP 解析 |
| 12 | **Flow diagram** | 参加者フロー図（recruitment → allocation → follow-up → analysis） |
| 13 | **Results** | 群別結果、効果量と精度（CI） |
| 14 | **Harms** | 有害事象または副作用 |
| 15 | **Limitations** | バイアス源、不精確さ、多重比較 |
| 16 | **Registration** | 試験登録番号 |

**拡張の選び方**: 個人単位ランダム化なら CONSORT 2010、学級/施設など群単位なら **CONSORT-Cluster**、教育・行動・心理など盲検化困難な介入なら **CONSORT-SPI**。教育分野の RCT は完全ランダム化ができずクラスターランダム化になりがち、かつ教員/学生が群を知ってしまい盲検化が難しい、という典型課題がある。

---

## 4. STROBE — Observational Study 凝縮チェックリスト

**Full Name**: Strengthening the Reporting of Observational Studies in Epidemiology ／ **適用**: cohort・case-control・cross-sectional

| # | Item | 内容 |
|---|---|---|
| 1 | **Title & Abstract** | 研究デザイン型を示す |
| 2 | **Background** | 科学的背景、研究の根拠 |
| 3 | **Objectives** | 具体的目的、事前指定の仮説 |
| 4 | **Study design** | デザイン（cohort / case-control / cross-sectional）を明示 |
| 5 | **Setting** | セッティング・場所・関連する日付（recruitment, exposure, follow-up） |
| 6 | **Participants** | 適格基準、データソース、サンプリング法 |
| 7 | **Variables** | アウトカム変数、曝露変数、潜在的交絡因子、効果修飾因子 |
| 8 | **Data sources** | 各変数のデータソースと測定法 |
| 9 | **Bias** | 潜在的バイアス源への対処法 |
| 10 | **Study size** | サンプルサイズの決定法 |
| 11 | **Statistical methods** | 統計手法（交絡の扱い、欠損データの扱いを含む） |
| 12 | **Results** | 記述統計、主要結果（効果量・CI・p値を含む） |
| 13 | **Discussion** | 主要知見、限界、一般化可能性、他研究との整合性 |
| 14 | **Funding** | 資金源 |

**サブタイプの対応**: 横断調査 → **STROBE-CS**（cross-sectional）、追跡研究 → **STROBE-Cohort**、後ろ向き比較 → **STROBE-CC**（case-control）。例: 学習成果の横断調査=cross-sectional、卒業後就職の追跡=cohort、退学リスク因子分析=case-control。

---

## 5. COREQ — Qualitative Research 凝縮チェックリスト（32 項目・3 ドメイン）

**Full Name**: Consolidated Criteria for Reporting Qualitative Research ／ **適用**: インタビュー、フォーカスグループ

### Domain 1: Research Team and Reflexivity（研究チームと再帰性）

| # | Item | 内容 |
|---|---|---|
| 1 | **Interviewer/facilitator** | 誰がインタビュー/FG を実施・進行したか |
| 2 | **Credentials** | 研究者の資格 |
| 3 | **Occupation** | 研究者の職業的アイデンティティ |
| 4 | **Gender** | 研究者の性別 |
| 5 | **Experience & training** | 質的研究の経験・訓練 |
| 6 | **Relationship with participants** | 研究者と参加者の関係 |
| 7 | **Participant knowledge** | 参加者の研究についての知識レベル |

### Domain 2: Study Design（研究デザイン）

| # | Item | 内容 |
|---|---|---|
| 8 | **Methodological orientation** | 理論的枠組み（例: grounded theory, phenomenology） |
| 9 | **Sampling** | サンプリング戦略・方法 |
| 10 | **Method of approach** | 参加者への接触方法 |
| 11 | **Sample size** | 参加者数 |
| 12 | **Non-participation** | 不参加の人数と理由 |
| 13 | **Setting** | インタビュー場所 |
| 14 | **Presence of non-participants** | インタビュー中の非参加者の同席有無 |
| 15 | **Description of sample** | 参加者の人口統計学的特性 |
| 16 | **Interview guide** | インタビューガイドの使用有無とパイロット検証の有無 |
| 17 | **Repeat interviews** | 反復インタビューの実施有無 |
| 18 | **Audio/visual recording** | 音声/映像記録の有無 |
| 19 | **Field notes** | フィールドノートの作成有無 |
| 20 | **Duration** | インタビュー時間 |
| 21 | **Data saturation** | データ飽和の議論の有無 |
| 22 | **Transcripts returned** | 逐語録を参加者へ返却しフィードバックを得たか |

### Domain 3: Analysis and Findings（分析と知見）

| # | Item | 内容 |
|---|---|---|
| 23 | **Data analysis** | 分析手法（例: thematic analysis, IPA） |
| 24 | **Software** | 使用した分析ソフトウェア |
| 25 | **Participant checking** | 参加者が知見を確認したか |
| 26 | **Quotations** | テーマを支持する引用を提示しているか |
| 27 | **Data and findings consistency** | データと知見の整合性 |
| 28 | **Clarity of major themes** | 主要テーマが明確に提示されているか |
| 29 | **Clarity of minor themes** | 副次テーマが明確に提示されているか |

> 原典は「32 項目・3 ドメイン」と明記しつつ凝縮表は #1–#29 を掲げている。提出前は EQUATOR の COREQ 全 32 項目チェックリストで最終突合すること。

---

## 6. SQUIRE — Quality Improvement Study 凝縮チェックリスト

**Full Name**: Standards for QUality Improvement Reporting Excellence ／ **Version**: SQUIRE 2.0 ／ **適用**: 質改善プロジェクト、系統的質改善、高等教育の質保証（QA）研究

| # | Item | 内容 |
|---|---|---|
| 1 | **Title** | 質改善研究と明示 |
| 2 | **Abstract** | 構造化抄録 |
| 3 | **Problem description** | 質問題の性質と重大性 |
| 4 | **Available knowledge** | 既知の関連エビデンス |
| 5 | **Rationale** | 改善施策の理論的根拠 |
| 6 | **Specific aims** | 具体的（定量可能な）改善目標 |
| 7 | **Context** | 改善の環境的コンテキスト |
| 8 | **Intervention(s)** | 改善施策の具体的記述 |
| 9 | **Study of the intervention(s)** | 改善効果をどう評価したか |
| 10 | **Measures** | アウトカム指標・プロセス指標・バランス指標（balancing measures） |
| 11 | **Analysis** | 量的/質的分析手法 |
| 12 | **Ethical considerations** | 倫理審査（該当する場合） |
| 13 | **Results** | 改善結果（時系列データを含む） |
| 14 | **Discussion** | 主要知見、コンテキストとの関係、一般化可能性 |
| 15 | **Limitations** | 研究の限界 |

SQUIRE 2.0 は PDSA サイクルや QA/認証対応の改善（teaching quality improvement, curriculum reform, 学生支援サービス改善, 認証指摘への自己改善, IR 駆動の改善サイクル）の報告に特に有用。

---

## 7. 研究タイプ早見フロー

```
研究タイプは？
│
├── 既存研究の統合 → PRISMA
│   ├── Systematic review → PRISMA 2020
│   ├── Scoping review → PRISMA-ScR
│   └── Meta-analysis → PRISMA + MOOSE
│
├── 介入実験 → CONSORT
│   ├── 個人単位ランダム化 → CONSORT 2010
│   ├── 学級/施設単位ランダム化 → CONSORT-Cluster
│   └── 社会的/心理的介入 → CONSORT-SPI
│
├── 観察調査 → STROBE
│   ├── 横断調査 → STROBE-CS
│   ├── 追跡研究 → STROBE-Cohort
│   └── 後ろ向き比較 → STROBE-CC
│
├── 質的研究 → COREQ
│   ├── インタビュー → COREQ
│   ├── フォーカスグループ → COREQ
│   └── 民族誌 → SRQR（代替）
│
└── 質改善 → SQUIRE
    ├── PDSA サイクル → SQUIRE 2.0
    └── QA/認証改善 → SQUIRE 2.0
```

---

## 8. ガイドライン選択の 3 ステップ

1. **研究デザインを特定する**: 自分の研究はどの型のデザインか。
2. **対応表で引く**: 上の対応表で該当する報告ガイドラインを見つける。
3. **チェックリストを入手する**: [EQUATOR Network](https://www.equator-network.org/) で全文チェックリストをダウンロードして突き合わせる。

---

## References

- EQUATOR Network — https://www.equator-network.org/
