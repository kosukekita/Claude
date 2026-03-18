---
name: alphaxiv
description: >
  alphaXiv MCPサーバーを使ったarXiv論文の高度な検索・取得・Q&Aスキル。
  Use when user searches for academic papers, asks "arXivで検索", "論文を探して",
  "alphaxiv", "arxiv search", requests paper content retrieval ("この論文の内容を",
  "論文を読んで"), asks questions about papers ("論文にQ&A"), or needs related
  GitHub code from papers. Also triggers for literature review, systematic review,
  先行研究調査, 文献調査 when combined with arXiv/ML/CS topics.
  Do NOT trigger for PubMed/医学論文 searches (use research-toolkit instead).
metadata:
  mcp-server: alphaxiv
  version: 1.0.0
---

# alphaXiv — arXiv 論文検索・取得スキル

alphaXiv MCP (`https://api.alphaxiv.org/mcp/v1`) を使って arXiv 論文を検索・取得・Q&A する。

## ツール一覧

| ツール | 用途 |
|--------|------|
| `embedding_similarity_search` | 意味的類似度検索（自然言語クエリ）最大25件 |
| `full_text_papers_search` | キーワードベースのフルテキスト検索 |
| `agentic_paper_retrieval` | 自律的マルチターン検索（ベータ） |
| `get_paper_content` | 論文全文取得（AI構造化レポートまたはraw） |
| `answer_pdf_queries` | 論文PDFへの自然言語Q&A |
| `read_files_from_github_repository` | 論文に紐づくGitHubリポジトリのコード取得 |

## 使い方ガイド

### 1. 論文検索

**意味的検索（推奨）** — 自然言語で概念を説明する場合:
```
embedding_similarity_search(query="transformer architecture for time series forecasting")
```

**フルテキスト検索** — 著者名・手法名・ベンチマーク名が明確な場合:
```
full_text_papers_search(query="BERT pre-training language model")
```
- クォーテーションマーク（""）は使用しない
- 著者名検索にも使える

**広範な検索が必要な場合**: 両方を組み合わせて再現率を最大化する

### 2. 論文内容の取得

arXiv または alphaXiv の URL を使用:
```
get_paper_content(url="https://arxiv.org/abs/2301.07041")
```
rawテキストが必要な場合: `fullText=true` オプション追加

### 3. 論文へのQ&A

```
answer_pdf_queries(
  url="https://arxiv.org/abs/2301.07041",
  query="この論文のメイン手法は何か？"
)
```
- arXiv・alphaXiv・Semantic Scholar・直接PDFのURLに対応

### 4. GitHub コード取得

```
read_files_from_github_repository(
  repoUrl="https://github.com/author/repo",
  path="/"
)
```
`/` 指定でファイルツリー全体を取得

## ワークフロー例

### 文献調査（Literature Review）
1. `embedding_similarity_search` でトピックを幅広く検索
2. `full_text_papers_search` で特定の手法名・著者名を補完
3. 関連論文に `get_paper_content` で詳細取得
4. 比較・まとめをユーザーに提示

### 特定論文の深読み
1. URLまたはタイトルから論文を特定
2. `get_paper_content` で構造化サマリーを取得
3. 詳細質問は `answer_pdf_queries` で対応
4. コードが必要なら `read_files_from_github_repository`

## 注意事項

- `full_text_papers_search`: クォーテーションマーク（""）不使用
- `agentic_paper_retrieval`: ベータ段階のため安定性に注意
- `get_paper_content`: デフォルトはAI生成構造化レポート（LLM向け最適化）
