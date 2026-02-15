---
name: research-toolkit
description: >
  ToolUniverse MCP を活用した科学的データ解析・医学研究ワークフロー。
  600+ の研究ツール（文献検索・創薬・ゲノミクス・構造生物学等）を統合。
  Use when user performs literature search, drug discovery, genomics analysis,
  protein structure prediction, clinical trial search, or biomedical research.
  Trigger phrases: "論文検索", "PubMed", "文献", "タンパク質", "創薬",
  "ゲノム", "臨床試験", "UniProt", "ChEMBL", "AlphaFold",
  "ToolUniverse", "MCP", "研究ツール".
  NOT for application development (web/mobile/desktop apps).
---

# ToolUniverse Connector

> このルールは科学的データ解析・研究タスクを行う際に適用する。
> アプリケーション開発（Web/モバイル/デスクトップアプリ等）では使用しない。

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

### Step 2: ツール選択

`Tool_Finder_LLM` または `Tool_Finder_Keyword` で最適なツールを特定:

```
「タンパク質構造予測に使えるツールを探して」
→ Tool_Finder_LLM が AlphaFold, Boltz 等を推薦
```

### Step 3: データ取得

選択したツールでデータを取得。複数ツールの連携が必要な場合は順序を考慮:

```
例: 創薬ターゲット探索
1. OpenTargets_get_associated_targets_by_disease_efoId（疾患→ターゲット）
2. UniProt_get_protein_info（ターゲットの詳細情報）
3. ChEMBL_search_similar_molecules（既存薬の検索）
```

### Step 4: 結果の統合・解釈

取得データを統合し、ユーザーに分かりやすく提示:
- 主要な発見を要約
- データソースを明記
- 次のステップを提案

---

## 概要

ToolUniverse は Harvard Medical School Zitnik Lab が開発した、600+ の科学ツールを統合した
MCP（Model Context Protocol）サーバー。Claude Code から直接、文献検索・創薬・ゲノミクス・
構造生物学などの研究ツールを呼び出せる。

ドキュメント: https://zitniklab.hms.harvard.edu/ToolUniverse/
GitHub: https://github.com/mims-harvard/ToolUniverse

## セットアップ手順

### 前提条件
- Claude Code がインストール済み
- Python 3.10+
- uv パッケージマネージャー

### Step 1: uv と ToolUniverse のインストール

```bash
# uv のインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# ToolUniverse 専用環境を作成
mkdir -p /path/to/tooluniverse-env

# ToolUniverse をインストール
uv --directory /path/to/tooluniverse-env pip install tooluniverse

# 確認
uv --directory /path/to/tooluniverse-env run python -c "import tooluniverse; print('OK')"
```

### Step 2: Claude Code に MCP サーバーを登録

```bash
# 基本セットアップ（APIキー不要の最小構成）
claude mcp add tooluniverse --scope user -- \
  uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio

# 研究向け推奨構成（SummarizationHook付き）
claude mcp add tooluniverse --scope user \
  --env AZURE_OPENAI_API_KEY=your-key \
  --env AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com \
  -- uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio \
  --exclude-tool-types PackageTool \
  --hook-type SummarizationHook
```

**スコープの選択:**
- `--scope user`: 全プロジェクトで利用可能（推奨）
- `--scope local`: 現在のプロジェクトのみ
- `--scope project`: チーム共有（.claude/.mcp.json に保存）

### Step 3: 確認

```bash
claude mcp list              # 登録済みサーバー一覧
claude mcp get tooluniverse  # 設定詳細
claude doctor                # 診断
```

Claude Code 内で `/mcp` コマンドを実行してサーバー接続を確認。

## 使い方

### ツール検索・実行の基本フロー

Claude Code 内で自然言語で指示するだけでツールが呼び出される:

```
# ツール検索
「タンパク質構造予測ツールを探して」
「PubMedで骨粗鬆症とテリパラチドの論文を検索して」

# データベースクエリ
「UniProtでP05067の機能情報を取得して」
「ChEMBLでEGFR阻害剤を検索して」

# 多段ワークフロー
「アルツハイマー病の創薬ターゲットを特定し、それらのターゲットに作用する既存薬を検索して」
```

### 特定ツールだけをロードする場合

600+ ツール全部をロードするとコンテキスト消費が大きいため、
用途に応じてフィルタリングする:

```bash
# 文献検索に特化
claude mcp add tooluniverse-lit --scope local -- \
  uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio \
  --include-tools EuropePMC_search_articles,openalex_literature_search,PubMed_search_articles,semantic_scholar_search

# 創薬に特化
claude mcp add tooluniverse-drug --scope local -- \
  uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio \
  --include-tools ChEMBL_search_similar_molecules,search_clinical_trials,OpenTargets_get_associated_targets_by_disease_efoId

# ツール名をファイルで指定
claude mcp add tooluniverse --scope local -- \
  uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio \
  --tools-file /path/to/tools.txt
```

### 複数インスタンスの同時運用

```bash
# 文献検索用
claude mcp add tooluniverse-research --scope local -- \
  uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio \
  --include-tools EuropePMC_search_articles,openalex_literature_search

# 分子解析用
claude mcp add tooluniverse-analysis --scope local -- \
  uv --directory /path/to/tooluniverse-env run tooluniverse-smcp-stdio \
  --include-tools ChEMBL_search_similar_molecules,search_clinical_trials

# 不要になったら削除
claude mcp remove tooluniverse-research
```

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
- `Python_Executor` — Pythonコード実行
- `URL_Fetch` — Webページ取得

## トラブルシューティング

```bash
# サーバーが接続できない
claude mcp list                    # 登録状況確認
claude mcp get tooluniverse        # 設定詳細
claude doctor                      # 全体診断

# パスは絶対パスを使用（相対パスは解決エラーの原因になる）
# /path/to/tooluniverse-env は実際の絶対パスに置き換えること

# ツールが見つからない場合
# --include-tools のフィルタが厳しすぎないか確認
# uv --directory ... run tooluniverse-smcp-stdio --help で利用可能なオプションを確認
```

## コンテキストウィンドウの節約

600+ ツール全てをロードすると大量のトークンを消費する。対策:
1. `--include-tools` で必要なツールだけロード
2. `--exclude-tool-types PackageTool` で不要カテゴリを除外
3. `--compact-mode` でコンパクトモード有効化（コアツールのみ公開）
4. 用途別に複数のMCPインスタンスを使い分ける
