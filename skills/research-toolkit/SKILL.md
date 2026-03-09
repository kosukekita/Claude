---
name: research-toolkit
description: "ToolUniverse CLI (tu) を活用した科学的データ解析・医学研究ワークフロー。2000+ の研究ツール（文献検索・創薬・ゲノミクス・構造生物学等）を統合。Use when user performs literature search, drug discovery, genomics analysis, protein structure prediction, clinical trial search, or biomedical research. Trigger phrases: 論文検索, PubMed, 文献, タンパク質, 創薬, ゲノム, 臨床試験, UniProt, ChEMBL, AlphaFold, ToolUniverse, 研究ツール. NOT for application development (web/mobile/desktop apps)."
---

# ToolUniverse CLI Connector

> このルールは科学的データ解析・研究タスクを行う際に適用する。
> アプリケーション開発（Web/モバイル/デスクトップアプリ等）では使用しない。

## CLI コマンドリファレンス

ToolUniverse は `tu` CLI で操作する。Windows では cp932 エンコーディング問題があるため、
常に `PYTHONIOENCODING=utf-8` を付けて実行すること。

```bash
# 基本形（Windows 必須プレフィックス）
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu <COMMAND>
```

| コマンド | 用途 | 例 |
|---------|------|-----|
| `tu status` | ツール数・カテゴリ・バージョン表示 | `tu status` |
| `tu list` | ツール一覧 | `tu list --categories uniprot` |
| `tu find` | 自然言語でツール検索 | `tu find 'drug safety' --limit 5` |
| `tu grep` | テキスト/正規表現でツール検索 | `tu grep protein --field description` |
| `tu info` | ツール詳細情報 | `tu info UniProt_get_entry_by_accession` |
| `tu run` | ツール実行 | `tu run UniProt_get_entry_by_accession accession=P12345` |
| `tu test` | ツールのテスト実行 | `tu test Dryad_search_datasets` |

### tu run の引数形式

```bash
# key=value 形式
tu run UniProt_get_entry_by_accession accession=P12345

# JSON 形式
tu run UniProt_get_entry_by_accession '{"accession": "P12345"}'
```

## Workflow

研究タスクを受けたら、以下のステップで進める:

### Step 1: タスク分類

ユーザーのリクエストを以下のカテゴリに分類:

| カテゴリ | 主要ツール | 例 |
|---------|-----------|-----|
| **文献検索** | PubMed, EuropePMC, Semantic Scholar | 「〇〇に関する論文を探して」 |
| **創薬・化合物** | ChEMBL, PubChem, ClinicalTrials | 「EGFR阻害剤を検索」 |
| **ゲノミクス** | UniProt, Ensembl, BLAST | 「P05067の情報を取得」 |
| **構造生物学** | AlphaFold, RCSB PDB | 「タンパク質構造を予測」 |
| **臨床・疫学** | ClinVar, DailyMed, WHO GHO | 「臨床試験を検索」 |

### Step 2: ツール検索

`tu find` または `tu grep` で最適なツールを特定:

```bash
# 自然言語検索
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu find 'protein structure prediction' --limit 5

# キーワード検索
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu grep 'AlphaFold' --field name
```

### Step 3: ツール詳細確認

```bash
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu info <tool_name>
```

### Step 4: データ取得

```bash
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu run <tool_name> key=value
```

複数ツールの連携が必要な場合は順序を考慮:

```
例: 創薬ターゲット探索
1. tu run OpenTargets_get_associated_targets_by_disease_efoId efoId=EFO_0000249
2. tu run UniProt_get_protein_info accession=P12345
3. tu run ChEMBL_search_similar_molecules smiles=...
```

### Step 5: 結果の統合・解釈

取得データを統合し、ユーザーに分かりやすく提示:
- 主要な発見を要約
- データソースを明記
- 次のステップを提案

---

## 概要

ToolUniverse は Harvard Medical School Zitnik Lab が開発した、2000+ の科学ツールを統合した
研究プラットフォーム。`tu` CLI から直接、文献検索・創薬・ゲノミクス・構造生物学などの研究ツールを呼び出せる。

ドキュメント: https://aiscientist.tools/
GitHub: https://github.com/mims-harvard/ToolUniverse

## セットアップ

### 前提条件
- uv パッケージマネージャー（`curl -LsSf https://astral.sh/uv/install.sh | sh`）

### 使い方（CLI モード）

```bash
# インストール不要 — uvx で直接実行
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu status
PYTHONIOENCODING=utf-8 uvx --from tooluniverse tu find 'drug safety'
```

### APIキー（任意・推奨）

環境変数に設定:
- `NCBI_API_KEY` — PubMed/NCBI（無料: https://www.ncbi.nlm.nih.gov/account/settings/）
- `NVIDIA_API_KEY` — NVIDIA NIM（構造予測等）
- `BIOGRID_API_KEY` — BioGRID（タンパク質相互作用）
- `FDA_API_KEY` — openFDA（医薬品データ）

## 主要ツールカテゴリと代表的ツール

詳細は `references/tool-catalog.md` を参照。

### 文献検索
- `PubMed_search_articles` — PubMed文献検索
- `EuropePMC_search_articles` — Europe PMC文献検索
- `semantic_scholar_search` — Semantic Scholar検索
- `openalex_literature_search` — OpenAlex文献検索
- `arxiv_search` — arXiv プレプリント検索
- `biorxiv_search` / `medrxiv_search` — bioRxiv/medRxiv検索

### 創薬・化合物
- `ChEMBL_search_similar_molecules` — 類似化合物検索
- `PubChem_search_compounds` — PubChem化合物検索
- `search_clinical_trials` — ClinicalTrials.gov臨床試験検索
- `OpenTargets_get_associated_targets_by_disease_efoId` — 疾患ターゲット検索
- ADMET予測ツール群

### ゲノミクス・バイオインフォマティクス
- `UniProt_get_protein_info` — タンパク質情報取得
- `BLAST_search` — 配列類似性検索
- `Ensembl_get_gene_info` — 遺伝子情報
- `GnomAD` / `GTEx` / `GWAS` — 変異・発現・関連解析
- `Enrichr` — 遺伝子セットエンリッチメント解析
- `KEGG` — パスウェイデータベース

### 構造生物学
- `AlphaFold` — タンパク質構造予測
- `RCSB_PDB` — タンパク質構造データベース
- `Boltz` — 構造予測ツール

### 臨床・疫学
- `search_clinical_trials` — 臨床試験検索
- `ClinVar` — 臨床的変異データベース
- `DailyMed` — 医薬品ラベル情報
- `RxNorm` — 薬剤名標準化
- `NHANES` — 健康栄養調査データ
- `WHO_GHO` — WHO健康統計

### ユーティリティ
- `Tool_Finder_LLM` — AIによるツール推薦（何を使えばいいかわからないとき）
- `Tool_Finder_Keyword` — キーワードでツール検索

## トラブルシューティング

```bash
# Windows で UnicodeEncodeError が出る場合
# → 常に PYTHONIOENCODING=utf-8 を付ける

# ツールが見つからない場合
tu find '<目的を自然言語で記述>'
tu grep '<キーワード>' --field name

# ツールの使い方がわからない場合
tu info <tool_name>

# テスト実行
tu test <tool_name>
```
