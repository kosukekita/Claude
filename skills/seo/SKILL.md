---
name: seo
description: "SEO/GEO統合スキル。テクニカルSEO、オンページ、コンテンツ、構造化データ、CWV、E-E-A-T、GEO（AI検索最適化）、競合比較、hreflang、画像最適化、プログラマティックSEO、GSC分析。Trigger: SEO, 検索順位, キーワード, 構造化データ, JSON-LD, Core Web Vitals, AI Overviews, GEO, Perplexity, comparison page, programmatic SEO, Search Console, GSC, CTR, インプレッション."
---

# SEO / GEO Optimization

> 詳細な実装例は `references/` を参照: `schema-examples.md`, `html-patterns.md`, `gsc-setup.md`, `report-templates.md`, `keyword-research-api.md`

## 監査ワークフロー

1. **サイト分析** — 種別（EC/SaaS/ブログ/ローカル）、目標、現状課題を把握
2. **優先度監査** — クロール・インデックス → テクニカル → オンページ → コンテンツ → オーソリティ
3. **改善提案** — 優先度 × 工数マトリクスでアクションプラン提示

---

## テクニカル SEO

| 項目 | チェック内容 |
|------|-------------|
| robots.txt | 重要ページのブロック有無、Sitemap ディレクティブ |
| XML サイトマップ | 全重要URL網羅、50,000 URL / 50MB以下、lastmod正確 |
| canonical | 正規URLの一貫性（www/non-www、https、末尾スラッシュ） |
| noindex | 意図しないnoindexがないか |
| ステータスコード | 404/410/301/302 の適切な使い分け |
| **ページファイルサイズ** | **2MB未満必須（超過分はGoogleクローラーに認識されない）** |

### ページファイルサイズ検証（必須）

**ページファイル（HTML/テンプレート等）を作成・生成した後、必ずファイルサイズを確認すること。**

```bash
# ファイルサイズ確認
ls -lh <file>          # macOS/Linux
wc -c < <file>         # バイト数（2,097,152 = 2MB）

# 2MB超過チェック（bash）
python3 -c "
import os, sys
size = os.path.getsize('$FILE')
limit = 2 * 1024 * 1024
print(f'File size: {size/1024:.1f} KB ({size/limit*100:.1f}% of 2MB limit)')
if size > limit:
    print('WARNING: Exceeds 2MB! Google will not index content beyond 2MB.')
    sys.exit(1)
else:
    print('OK: Within 2MB limit.')
"
```

**超過時の対処**:
- 不要なコメント・空白を削除
- インラインコンテンツ（画像 base64 等）を外部ファイル化
- 構造化データの重複を排除
- コンテンツを複数ページに分割（ページネーション + canonical）

### Core Web Vitals

| 指標 | 目標値 | 主な改善策 |
|------|--------|-----------|
| LCP | < 2.5s | 画像最適化（WebP/AVIF）、TTFB削減、プリロード |
| INP | < 200ms | 長時間タスク分割、不要JS削減 |
| CLS | < 0.1 | 画像/動画のサイズ指定、動的コンテンツのスペース予約 |

- HTTPS全ページ、モバイル対応（タップ48px+）、3クリック以内、SSR/SSG推奨

---

## オンページ SEO

- **title**: 日本語30-60字 / 英語50-60字、**meta description**: 日本語80-120字 / 英語150-160字
- **H1**: 1ページ1つ、主要KW含む、H1→H2→H3スキップなし
- **内部リンク**: サイロ構造、具体的アンカーテキスト、孤立ページなし、パンくずリスト
- **URL**: 英語ハイフン区切り、小文字、60字以下、最大3階層

---

## コンテンツ SEO

### 検索意図
- **Informational**: ハウツー、FAQ — **Commercial**: レビュー、比較 — **Transactional**: 商品、料金

### E-E-A-T
- Experience: 実体験・事例 — Expertise: 著者プロフィール — Authoritativeness: 被リンク・メディア — Trustworthiness: 正確な情報・HTTPS

### キーワードリサーチ

**手動フロー**: シード収集 → サジェスト/PAA拡張 → 意図分類 → スコアリング → クラスター

**API + AI 大量キーワード選定**（→ 詳細は `references/keyword-research-api.md`）

| API | 用途 | コスト目安 |
|-----|------|-----------|
| Google Ads API (Keyword Planner) | ボリューム・競合度・CPC一括取得 | 無料（Google Ads アカウント + Developer Token 必要） |
| Google Search Console API | 既存サイトの実クエリ・CTR・順位 | 無料 |
| DataForSEO / SerpApi | PAA・Related Searches・SERP Features | $50-500/月（従量課金） |
| Google Trends（pytrends） | トレンド・季節性分析 | 無料（非公式） |

**ワークフロー（1000KW 選定を一括処理）**:
1. シード 10-20語 → Keyword Planner API で候補 2000-5000 取得
2. GSC API で既存ランキングKW取得 → 既知/未知を分類
3. AI（Claude）で意図分類（Info/Commercial/Transactional）+ クラスタリング
4. AI でコンテンツギャップ分析 → 優先度スコア = `volume / (difficulty × 既存順位)`
5. 上位 1000KW をピラー×クラスター構造で出力

**なぜ API 課金すべきか**: 手動ツールは月100-300クエリ制限。API なら1リクエストで数百候補、バッチで数千処理可能。月$50-100の投資で手動数十時間分の作業を数分に短縮

---

## 構造化データ

JSON-LD推奨。主要スキーマ: Article, FAQPage, Product, BreadcrumbList, LocalBusiness, HowTo, VideoObject
→ 実装例は `references/schema-examples.md`

---

## サイト種別ガイダンス

- **SaaS**: 機能×ユースケースページ、比較ページ、インテグレーションページ
- **EC**: カテゴリ最適化、Product Schema、在庫切れ（410 vs noindex）
- **ローカル**: Google ビジネスプロフィール、LocalBusiness Schema + NAP一貫性
- **コンテンツ**: トピッククラスター、定期更新、著者ページ + E-E-A-T

---

## SEO 戦略立案

Discovery → 競合分析（Top 5） → アーキテクチャ設計 → コンテンツ戦略 → テクニカル基盤 → 4フェーズロードマップ

| Phase | Period | Focus |
|-------|--------|-------|
| Foundation | Weeks 1-4 | Technical setup, core pages, schema, analytics |
| Expansion | Weeks 5-12 | Content creation, blog, internal linking |
| Scale | Weeks 13-24 | Advanced content, link building, GEO |
| Authority | Months 7-12 | Thought leadership, PR, advanced schema |

---

## AI 検索最適化（GEO）

### Key Facts (Feb 2026)
- AI Overviews: 1.5B users/month, 50%+クエリカバー
- Brand mentions correlate 3× more than backlinks with AI visibility
- Only 11% of domains cited by both ChatGPT and Google AI Overviews

### GEO 5 Criteria
1. **Citability (25%)** — 134-167語の自己完結ブロック、最初の40-60語で直接回答
2. **Structural Readability (20%)** — H1→H2→H3、質問ベース見出し、短段落、テーブル/リスト
3. **Multi-Modal (15%)** — テキスト+画像/動画/インフォグラフィック（156%高選択率）
4. **Authority & Brand (20%)** — 著者バイライン、公開日、引用元、Wikipedia/Reddit/YouTube存在
5. **Technical Accessibility (20%)** — SSR必須（AIクローラーはJS非実行）、robots.txt、llms.txt

### AI Crawler
Allow: GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot. Block CCBot/training crawlers if desired.

### Platform別
- Google AIO: Top-10ランキング+パッセージ最適化
- ChatGPT: Wikipedia(47.9%), Reddit(11.3%)
- Perplexity: Reddit(46.7%), Wikipedia

### Quick Wins
"What is [topic]?" 定義（60語内）、134-167語ブロック、質問H2/H3、統計+出典、Person schema、llms.txt作成

---

## 競合比較ページ

### Page Types
- **X vs Y**: 直接比較、feature-by-feature → `[A] vs [B]: [差別化点] ([Year])`
- **Alternatives**: pros/cons、best-for → `[N] Best [A] Alternatives in [Year]`
- **Roundup**: ランキング基準明示 → `[N] Best [Category] Tools in [Year]`

### Schema: Product/SoftwareApplication/ItemList → `references/schema-examples.md`
### Fairness: accurate data, cite sources, disclose affiliation, balanced presentation

---

## Hreflang & 国際 SEO

### 必須チェック
- Self-referencing tag（必須）、Return tags（双方向A↔B）、x-default
- Language: ISO 639-1（`ja` NOT `jp`）、Region: ISO 3166-1 Alpha-2（`en-GB` NOT `en-uk`）
- Hreflang only on canonical URLs、Protocol一致

### 方法
- HTML link tags: <50 variants — XML sitemap: 大規模/cross-domain（推奨）
→ 実装例は `references/html-patterns.md`

---

## 画像最適化

- **Format**: WebP（97%+）> AVIF（92%+）> JPEG/PNG（fallback）→ `<picture>`要素で段階フォールバック
- **Size**: Thumbnail <50KB / Content <100KB / Hero <200KB
- **Alt**: 10-125字、記述的、KW自然に含む
- **Loading**: below-fold → `loading="lazy"` + `decoding="async"` / LCP → `fetchpriority="high"`（lazy禁止）
- **CLS**: width/height必須

---

## プログラマティック SEO

- Data品質: 一意性、freshness、>80%重複はフラグ
- Template: 各ページが standalone value、mad-libs禁止
- URL: lowercase hyphen、<100字、unique slugs

### Thin Content Safeguards
- 100+ページ（review未）→ WARNING、500+（justification無）→ HARD STOP
- Unique content <40% → thin risk、<300 words → review
- **Scaled Content Abuse (2025-2026)**: ≥30-40%差異、50-100ページずつ progressive rollout

### Index Bloat Prevention
- noindex low-value/paginated、faceted navigation canonical、>10k → crawl stats監視

---

## GSC 分析

### タスク → ツール対応
- パフォーマンス概要: `get_performance_overview`
- クエリ分析: `get_search_analytics`, `get_advanced_search_analytics`
- ページ分析: `get_search_by_page_query`
- 期間比較: `compare_search_periods`
- インデックス診断: `inspect_url_enhanced`, `batch_url_inspection`
- サイトマップ: `list_sitemaps_enhanced`, `submit_sitemap`

### 分析パターン
- **順位改善**: 11-20位 → タイトル/メタ最適化で10位内、高impression低CTR → タイトル改善
- **デバイス**: モバイル順位低い → モバイル最適化、モバイルCTR低い → タップしやすいタイトル
- **期間比較**: 急落 → 競合/アルゴリズム、急上昇 → 成功要因を横展開
- **インデックス**: "Crawled not indexed" → 品質改善、"Discovered not indexed" → 内部リンク追加

→ セットアップ・ツール一覧・トラブルシューティングは `references/gsc-setup.md`

---

## Troubleshooting

- **インデックスされない**: robots.txt → noindex → canonical → URL検査 → サイトマップ
- **CWV改善しない**: LCP=最大要素特定+preload、CLS=width/height+font-display、INP=タスク分割
- **リッチリザルト非表示**: Rich Results Test → 必須フィールド → JSON-LD構文 → インデックス確認
- **順位急落**: アルゴ更新 → 手動対策 → 技術問題 → コンテンツ → 被リンク
