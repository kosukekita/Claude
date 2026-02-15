---
name: academic-writing
description: "医学・学術論文の執筆支援。構成（IMRAD）、文体、引用形式、AI 生成テキストパターン（18種）の検出・除去を含む。AI 研究時は TRIPOD+AI（27項目）に準拠した報告を支援。Use when user writes, edits, or reviews academic manuscripts, or requests humanization of AI-generated text. Trigger phrases: 論文, 原稿, manuscript, abstract, humanize, AI文体, 学術英語, IMRAD, 投稿, 論文執筆, アカデミックライティング, 論文校正, academic writing, medical writing, TRIPOD, prediction model."
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

### Step 2: 原稿分析（校正の場合）

1. IMRAD 構造に従っているか確認
2. AI 文体パターン（18種）をスキャン
3. 統計表記・引用形式をチェック

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

### 各セクションの注意点

- **Introduction**: 広い文脈 → 狭い焦点（funnel 構造）。最終段落で目的・仮説を明示
- **Methods**: 再現可能な詳細度。倫理委員会承認・同意取得を明記
- **Results**: データを先に、解釈は Discussion で。表・図を効果的に使用。**Study flow diagram（participant flow / CONSORT / STROBE diagram）は Results セクションに配置する**（Lancet 系列の標準）。N数・除外数は Methods の段階では未知の情報であり、Methods には配置しない
- **Discussion**: 主要な発見を最初に述べる。限界は正直に、しかし過度に卑下しない
- **Outcome / Endpoint の用語**: 「Primary outcome/endpoint」は Secondary outcome が存在する場合にのみ使用する。アウトカムが1つしかない研究では単に「outcome」「endpoint」と記載する。「Primary」と書くと Secondary outcome の記述を読者が期待するため不自然

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

---

## AI 文体除去（Humanizer）

AI 生成テキストに共通する 18 パターンを 4 カテゴリに分類。
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

共著者の名前・所属情報は `references/authors.csv` に格納されている。
論文作成・投稿時にユーザーが著者名（Last Name）を指示したら、CSV から該当著者を抽出して整形出力する。

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

新しい共著者を追加する場合は `references/authors.csv` に行を追加する。

---

## 投稿前チェックリスト

- [ ] IMRAD 構成に従っている
- [ ] Abstract が構造化されている（Objective / Methods / Results / Conclusions）
- [ ] 略語は全て初出時にフルスペルで定義
- [ ] Abstract 内の略語は3回以上使用されるもののみ定義（1-2回はフルスペルのまま）
- [ ] 統計値に 95% CI と P 値が付記されている
- [ ] 引用は具体的（曖昧な "Studies show" がない）
- [ ] AI 文体パターン（18種）が除去されている
- [ ] 見出しがセンテンスケースになっている
- [ ] ストレート引用符を使用している
- [ ] 能動態/受動態がセクションに応じて適切に使用されている
- [ ] フィラー表現・過度なヘッジングが除去されている
- [ ] Target journal の投稿規定（word count、reference style 等）に準拠
- [ ] **AI 研究の場合**: TRIPOD+AI 27 項目チェックリストに準拠している
- [ ] **AI 研究の場合**: Abstract が TRIPOD+AI for Abstracts 13 項目に準拠している
- [ ] **LLM 研究の場合**: TRIPOD-LLM チェックリストにも準拠している

---

## References

- `references/tenses.md` — セクション別の時制使い分けガイド（IMRaD）
- `references/humanizer-patterns.md` — 18 パターンの詳細な検出・修正リファレンス
- `references/authors.csv` — 共著者リスト（名前・所属）
- [TRIPOD+AI statement (BMJ 2024)](https://pubmed.ncbi.nlm.nih.gov/38626948/) — AI 予測モデル研究の報告ガイドライン（27 項目）
- [TRIPOD+AI Expanded Checklist & Supplement](https://www.tripod-statement.org/) — 各項目の詳細な説明と記入例
- [TRIPOD-LLM (Nature Medicine 2024)](https://www.nature.com/articles/s41591-024-03425-5) — LLM を用いた生物医学研究の報告ガイドライン
