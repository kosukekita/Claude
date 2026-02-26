---
name: seo
description: "SEO/GEO統合スキル。テクニカルSEO、オンページ、コンテンツ、構造化データ、CWV、E-E-A-T、GEO（AI検索最適化）、競合比較、hreflang、画像最適化、プログラマティックSEO、GSC分析。Trigger: SEO, 検索順位, キーワード, 構造化データ, JSON-LD, Core Web Vitals, AI Overviews, GEO, Perplexity, comparison page, programmatic SEO, Search Console, GSC, CTR, インプレッション."
---

# SEO / GEO Optimization

> サイトの検索パフォーマンスを体系的に分析・改善する統合スキル。

---

# Part 1: SEO 監査・最適化

## ワークフロー

### Step 1: サイト分析
- **サイト種別**: コーポレート、EC、ブログ、SaaS、ローカルビジネス等
- **目標**: トラフィック増加、CV改善、ブランド認知、ローカル集客等
- **現状の課題**: インデックス問題、順位低下、速度、コンテンツ不足等

### Step 2: 優先度に基づく監査
1. **クロール・インデックス** — 最優先（検索に表示されなければ他は無意味）
2. **テクニカル基盤** — サイト速度・Core Web Vitals・モバイル対応
3. **オンページ最適化** — タイトル・メタ・見出し・内部リンク
4. **コンテンツ品質** — E-E-A-T・検索意図・独自性
5. **オーソリティ** — 被リンク・ブランドシグナル

### Step 3: 改善提案
優先度 × 工数のマトリクスで施策を整理し、アクションプランを提示。

---

## テクニカル SEO

### クロール・インデックス

| 項目 | チェック内容 |
|------|-------------|
| **robots.txt** | 重要ページのブロック有無、Sitemap ディレクティブ |
| **XML サイトマップ** | 全重要 URL を網羅、50,000 URL / 50MB 以下、lastmod 正確 |
| **canonical** | 正規 URL の一貫性（www/non-www、https、末尾スラッシュ） |
| **noindex** | 意図しない noindex がないか |
| **hreflang** | 多言語サイトの双方向リンク、x-default 設定 |
| **ステータスコード** | 404/410/301/302 の適切な使い分け |

### Core Web Vitals

| 指標 | 目標値 | 主な改善策 |
|------|--------|-----------|
| **LCP** | < 2.5s | 画像最適化（WebP/AVIF）、TTFB 削減、リソースプリロード |
| **INP** | < 200ms | 長時間タスクの分割、不要な JS 削減 |
| **CLS** | < 0.1 | 画像/動画のサイズ指定、動的コンテンツのスペース予約、font-display |

### その他テクニカル
- **HTTPS**: 全ページ SSL 対応、混合コンテンツなし
- **モバイル対応**: レスポンシブ、タップターゲット 48px 以上
- **サイト構造**: 重要ページまで 3 クリック以内
- **JavaScript SEO**: SSR/SSG 推奨、レンダリングブロッキング回避

---

## オンページ SEO

### メタタグ最適化

| 要素 | 日本語サイト | 英語サイト |
|------|-------------|-----------|
| **title** | 30〜60 文字 | 50〜60 文字 |
| **meta description** | 80〜120 文字 | 150〜160 文字 |
| **OGP 画像** | 1200×630px | 1200×630px |

### 見出し構造
- H1 は 1 ページに 1 つ、主要キーワードを含む
- 階層をスキップしない（H1 → H2 → H3）
- 見出しだけで記事の構造が把握できること

### 内部リンク
- サイロ構造で関連コンテンツをクラスタリング
- アンカーテキストは具体的に（「こちら」を避ける）
- 孤立ページ（内部リンクのないページ）を作らない
- パンくずリストの実装

### URL 設計
- 短く、意味のある英語（60 文字以下推奨）
- ハイフン区切り、小文字統一
- パラメータよりパスベース
- 最大 3 階層を推奨

---

## コンテンツ SEO

### 検索意図の 4 タイプ

| タイプ | 説明 | コンテンツ例 |
|--------|------|-------------|
| **Informational** | 知識・情報を求める | ハウツー記事、解説、FAQ |
| **Navigational** | 特定サイト・ページを探す | ブランドページ、ログインページ |
| **Commercial** | 購入前に比較・検討する | レビュー、比較記事、ランキング |
| **Transactional** | 購入・申込をしたい | 商品ページ、料金ページ、申込フォーム |

### E-E-A-T フレームワーク

| 要素 | 施策 |
|------|------|
| **Experience（経験）** | 実体験に基づくコンテンツ、事例、スクリーンショット |
| **Expertise（専門性）** | 著者プロフィール、資格・実績の明示 |
| **Authoritativeness（権威性）** | 信頼できるソースからの被リンク、メディア掲載 |
| **Trustworthiness（信頼性）** | 正確な情報、運営者情報、プライバシーポリシー、HTTPS |

### キーワードリサーチ手順
1. **シード収集** — ターゲット顧客の課題・用語を洗い出し
2. **拡張** — サジェスト、関連検索、競合分析、PAA（People Also Ask）
3. **分類** — 検索意図 × ファネルステージでマッピング
4. **優先度付け** — ボリューム × 意図適合度 ÷ 競合難易度でスコアリング
5. **クラスタリング** — 1 ピラーページに 4〜6 クラスター記事

---

## 構造化データ（JSON-LD）

JSON-LD を推奨。主要スキーマ:

### Article / BlogPosting
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "記事タイトル",
  "author": { "@type": "Person", "name": "著者名" },
  "datePublished": "2025-01-01",
  "dateModified": "2025-06-01",
  "image": "https://example.com/image.jpg"
}
```

### FAQPage
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "質問文",
    "acceptedAnswer": { "@type": "Answer", "text": "回答文" }
  }]
}
```

### その他の主要スキーマ
- **BreadcrumbList** — パンくずリスト
- **Product** — 商品（価格、在庫、レビュー）
- **LocalBusiness** — 店舗情報（住所、営業時間、電話番号）
- **HowTo** — 手順記事
- **VideoObject** — 動画コンテンツ

**検証**: Google Rich Results Test で必ずテストする。

---

## サイト種別ガイダンス

### SaaS / プロダクト
- 機能ページ × ユースケースページで検索意図を網羅
- 比較ページ（vs 競合）、インテグレーションページ
- プログラマティック SEO でテンプレート大量生成時は薄いコンテンツに注意

### EC サイト
- カテゴリページの最適化（ファセットナビゲーションのクロール制御）
- 商品 Schema（Product + Offer + AggregateRating）
- 在庫切れページの取り扱い（410 vs noindex）

### ローカルビジネス
- Google ビジネスプロフィールの最適化
- LocalBusiness Schema + NAP（名前・住所・電話番号）一貫性
- 地域キーワード + サービスページ

### コンテンツ / ブログ
- トピッククラスターモデル（ピラー＋クラスター）
- 定期的なコンテンツ更新・リフレッシュ
- 著者ページと E-E-A-T シグナル強化

---

## SEO 監査レポート出力フォーマット

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEO AUDIT REPORT: [サイト名]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY: [全体評価 / 主要な発見]

CRITICAL (即時対応):
  - [問題と改善策]

HIGH (1週間以内):
  - [問題と改善策]

MEDIUM (1ヶ月以内):
  - [問題と改善策]

LOW (余裕があれば):
  - [問題と改善策]

ACTION PLAN:
  1. [施策 / 期待効果 / 工数目安]
  2. ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ツール・監査スケジュール

- **無料**: Google Search Console, PageSpeed Insights, Rich Results Test, Lighthouse
- **有料**: Screaming Frog, Ahrefs, Semrush, Sitebulb

| 頻度 | 内容 |
|------|------|
| **週次** | Search Console エラー監視、インデックス状況 |
| **月次** | Core Web Vitals、順位変動、コンテンツ更新 |
| **四半期** | フル SEO 監査、競合分析 |
| **年次** | SEO 戦略レビュー、キーワードマップ更新 |

---

## Troubleshooting

### ページがインデックスされない
1. `robots.txt` で Disallow されていないか確認
2. `noindex` タグがないか確認
3. canonical が自己参照になっているか確認
4. Search Console で「URL検査」を実行
5. サイトマップに含まれているか確認

### Core Web Vitals が改善しない
- **LCP**: 最大要素を特定 → 画像なら WebP/AVIF + preload、TTFB が遅いならサーバー/CDN
- **CLS**: 画像/動画に width/height 明示、font-display: swap + fallback、動的コンテンツにスペース予約
- **INP**: 長時間タスクを 50ms 以下に分割、不要な JS を削除または遅延読み込み

### 構造化データがリッチリザルトに表示されない
1. Rich Results Test でエラー確認
2. 必須フィールドの確認
3. JSON-LD 構文エラーチェック
4. ページのインデックス確認

### 順位が急落した
1. **アルゴリズム更新**: Google 公式ブログで確認
2. **手動対策**: Search Console のセキュリティと手動対策を確認
3. **技術的問題**: クロールエラー、サーバーダウン、robots.txt 変更
4. **コンテンツ問題**: 薄いコンテンツ、重複コンテンツ
5. **被リンク問題**: スパムリンク、重要リンクの喪失

---

# Part 2: SEO 戦略立案

## Process

### 1. Discovery
- Business type, target audience, competitors, goals
- Current site assessment (if exists)
- Budget and timeline constraints, KPIs

### 2. Competitive Analysis
- Top 5 competitors の content strategy, schema, technical setup 分析
- Keyword gaps and content opportunities
- E-E-A-T signals, domain authority 推定

### 3. Architecture Design
- URL hierarchy and content pillars
- Internal linking strategy
- Sitemap structure with quality gates

### 4. Content Strategy
- Content gaps vs competitors
- Page types and estimated counts
- Blog/resource topics and publishing cadence
- E-E-A-T building plan, content calendar

### 5. Technical Foundation
- Hosting/performance requirements
- Schema markup plan per page type
- Core Web Vitals baseline, AI search readiness, mobile-first

### 6. Implementation Roadmap (4 phases)

| Phase | Period | Focus |
|-------|--------|-------|
| **Foundation** | Weeks 1-4 | Technical setup, core pages, essential schema, analytics |
| **Expansion** | Weeks 5-12 | Content creation, blog launch, internal linking, local SEO |
| **Scale** | Weeks 13-24 | Advanced content, link building, GEO optimization |
| **Authority** | Months 7-12 | Thought leadership, PR, advanced schema |

### Output Deliverables
- `SEO-STRATEGY.md`, `COMPETITOR-ANALYSIS.md`, `CONTENT-CALENDAR.md`, `IMPLEMENTATION-ROADMAP.md`, `SITE-STRUCTURE.md`

---

# Part 3: AI 検索最適化（GEO）

## Key Statistics (February 2026)

| Metric | Value |
|--------|-------|
| AI Overviews reach | 1.5B users/month, 200+ countries |
| AI Overviews query coverage | 50%+ of all queries |
| AI-referred sessions growth | 527% (Jan-May 2025) |
| ChatGPT weekly active users | 900M |
| Perplexity monthly queries | 500M+ |

## Critical Insight: Brand Mentions > Backlinks

**Brand mentions correlate 3× more strongly with AI visibility than backlinks.**
(Ahrefs December 2025 study of 75,000 brands)

| Signal | Correlation |
|--------|------------|
| YouTube mentions | ~0.737 (strongest) |
| Reddit mentions | High |
| Wikipedia presence | High |
| Domain Rating (backlinks) | ~0.266 (weak) |

**Only 11%** of domains are cited by both ChatGPT and Google AI Overviews for the same query.

## GEO Analysis Criteria

### 1. Citability Score (25%)
- **Optimal passage length: 134-167 words** for AI citation
- Clear, quotable sentences with specific facts/statistics
- Self-contained answer blocks, direct answer in first 40-60 words
- Definitions following "X is..." patterns

### 2. Structural Readability (20%)
- 92% of AI Overview citations come from top-10 ranking pages
- Clean H1→H2→H3 hierarchy, question-based headings
- Short paragraphs (2-4 sentences), tables, lists, FAQ sections

### 3. Multi-Modal Content (15%)
- 156% higher selection rates with multi-modal elements
- Text + images, video, infographics, interactive elements

### 4. Authority & Brand Signals (20%)
- Author byline with credentials, publication/update dates
- Citations to primary sources, entity presence (Wikipedia, Reddit, YouTube)

### 5. Technical Accessibility (20%)
- **AI crawlers do NOT execute JavaScript** — SSR is critical
- AI crawler access in robots.txt, llms.txt presence

## AI Crawler Detection

Check `robots.txt` for:

| Crawler | Owner | Purpose |
|---------|-------|---------|
| GPTBot | OpenAI | ChatGPT web search |
| OAI-SearchBot | OpenAI | OpenAI search features |
| ChatGPT-User | OpenAI | ChatGPT browsing |
| ClaudeBot | Anthropic | Claude web features |
| PerplexityBot | Perplexity | Perplexity AI search |

**Recommendation:** Allow GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot. Block CCBot and training crawlers if desired.

## llms.txt Standard

Location: `/llms.txt` (root of domain)

```
# Title of site
> Brief description

## Main sections
- [Page title](url): Description

## Optional: Key facts
- Fact 1
```

## Platform-Specific Optimization

| Platform | Key Citation Sources | Optimization Focus |
|----------|---------------------|-------------------|
| **Google AI Overviews** | Top-10 ranking pages (92%) | Traditional SEO + passage optimization |
| **ChatGPT** | Wikipedia (47.9%), Reddit (11.3%) | Entity presence, authoritative sources |
| **Perplexity** | Reddit (46.7%), Wikipedia | Community validation, discussions |
| **Bing Copilot** | Bing index, authoritative sites | Bing SEO, IndexNow |

## GEO Quick Wins
1. Add "What is [topic]?" definition in first 60 words
2. Create 134-167 word self-contained answer blocks
3. Add question-based H2/H3 headings
4. Include specific statistics with sources
5. Add publication/update dates
6. Implement Person schema for authors
7. Allow key AI crawlers in robots.txt
8. Create `/llms.txt` file

## GEO High Impact
1. Create original research/surveys (unique citability)
2. Build Wikipedia presence for brand/key people
3. Establish YouTube channel with content mentions
4. Implement comprehensive entity linking (sameAs across platforms)

---

# Part 4: 競合比較ページ

## Page Types

### 1. "X vs Y" Comparison Pages
- Direct head-to-head comparison
- Balanced feature-by-feature analysis, clear verdict
- Target: `[Product A] vs [Product B]`

### 2. "Alternatives to X" Pages
- List of alternatives with pros/cons, best-for use case
- Target: `[Product] alternatives`, `best alternatives to [Product]`

### 3. "Best [Category] Tools" Roundup
- Curated list with ranking criteria
- Target: `best [category] tools [year]`

### 4. Comparison Table Pages
- Feature matrix, sortable/filterable
- Target: `[category] comparison chart`

## Feature Matrix Layout
```
| Feature          | Your Product | Competitor A | Competitor B |
|------------------|:------------:|:------------:|:------------:|
| Feature 1        | ✅           | ✅           | ❌           |
| Feature 2        | ✅           | ⚠️ Partial   | ✅           |
| Pricing (from)   | $X/mo        | $Y/mo        | $Z/mo        |
```

## Schema for Comparison Pages

- **Product** with AggregateRating — 個別商品比較
- **SoftwareApplication** — ソフトウェア比較
- **ItemList** — ランキング・まとめ記事

## Keyword Targeting

| Pattern | Example |
|---------|---------|
| `[A] vs [B]` | "Slack vs Teams" |
| `[A] alternative` | "Figma alternatives" |
| `best [category] tools` | "best project management tools" |
| `[A] vs [B] for [use case]` | "AWS vs Azure for startups" |

### Title Formulas
- X vs Y: `[A] vs [B]: [Key Differentiator] ([Year])`
- Alternatives: `[N] Best [A] Alternatives in [Year] (Free & Paid)`
- Roundup: `[N] Best [Category] Tools in [Year] — Compared & Ranked`

## Conversion & Fairness
- CTA: above fold, after comparison table, bottom of page
- Social proof, pricing highlights, trust signals
- **Fairness**: accurate data, no defamation, cite sources, disclose affiliation, balanced presentation

---

# Part 5: Hreflang & 国際 SEO

## Validation Checks

| Check | Description |
|-------|------------|
| **Self-Referencing** | Every page must hreflang to itself |
| **Return Tags** | Bidirectional: A→B AND B→A |
| **x-default** | Fallback for unmatched languages |
| **Language Codes** | ISO 639-1 (`en`, `ja`, NOT `eng`, `jp`) |
| **Region Codes** | ISO 3166-1 Alpha-2 (`en-US`, `en-GB`, NOT `en-uk`) |
| **Canonical Alignment** | Hreflang only on canonical URLs |
| **Protocol Consistency** | All URLs same protocol (HTTPS) |
| **Cross-Domain** | Works across domains, requires return tags on both |

## Common Mistakes

| Issue | Severity | Fix |
|-------|----------|-----|
| Missing self-referencing tag | Critical | Add hreflang pointing to same page URL |
| Missing return tags | Critical | Add matching return tags on all alternates |
| Missing x-default | High | Add x-default pointing to fallback page |
| Invalid language code (`eng`) | High | Use ISO 639-1 two-letter codes |
| Invalid region code (`en-uk`) | High | Use ISO 3166-1 Alpha-2 (`en-GB`) |
| Hreflang on non-canonical URL | High | Move to canonical URL only |

## Implementation Methods

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| HTML link tags | Small sites (<50 variants) | Easy to implement | Bloats `<head>` |
| HTTP headers | Non-HTML files (PDFs) | Works for any file | Complex server config |
| XML sitemap | Large sites, cross-domain | Scalable, centralized | Requires sitemap maintenance |

### HTML Example
```html
<link rel="alternate" hreflang="en-US" href="https://example.com/page" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

### Sitemap Example
```xml
<url>
  <loc>https://example.com/page</loc>
  <xhtml:link rel="alternate" hreflang="en-US" href="https://example.com/page" />
  <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
  <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/page" />
</url>
```

---

# Part 6: 画像最適化

## Checks

### Alt Text
- Present on all `<img>` (except decorative: `role="presentation"`)
- Descriptive, 10-125 characters, natural keyword inclusion

### File Size

| Image Category | Target | Warning | Critical |
|----------------|--------|---------|----------|
| Thumbnails | < 50KB | > 100KB | > 200KB |
| Content images | < 100KB | > 200KB | > 500KB |
| Hero/banner | < 200KB | > 300KB | > 700KB |

### Format

| Format | Support | Use Case |
|--------|---------|----------|
| WebP | 97%+ | Default recommendation |
| AVIF | 92%+ | Best compression, newer |
| JPEG | 100% | Fallback for photos |
| PNG | 100% | Graphics with transparency |
| SVG | 100% | Icons, logos, illustrations |

### Recommended `<picture>` Pattern
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" width="800" height="600" loading="lazy" decoding="async">
</picture>
```

### Responsive Images
```html
<img src="image-800.jpg"
  srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="Description">
```

### Loading & Priority
- `loading="lazy"` on below-fold images only
- `fetchpriority="high"` on LCP/hero images
- `decoding="async"` on non-LCP images
- **Never** lazy-load LCP images

### CLS Prevention
- `width` and `height` attributes on all `<img>`
- `aspect-ratio` CSS as alternative

### File Names
- Descriptive: `blue-running-shoes.webp` not `IMG_1234.jpg`
- Hyphenated, lowercase

---

# Part 7: プログラマティック SEO

## Data Source Assessment
- Row count, column uniqueness, missing values
- Data freshness, duplicate detection (>80% overlap = flag)

## Template Engine Planning
- **Variable injection**: Title, H1, body, meta description, schema
- **Content blocks**: Static (shared) vs dynamic (unique per page)
- **Conditional logic**: Show/hide based on data availability
- Each page must read as standalone valuable resource
- No "mad-libs" patterns (just swapping names in identical text)

## URL Pattern Strategy
- `/tools/[tool-name]`, `/[city]/[service]`, `/integrations/[platform]`
- Lowercase, hyphenated, < 100 characters, unique slugs

## Internal Linking Automation
- Hub/spoke model, related items (3-5), breadcrumbs, cross-linking
- 3-5 internal links per 1000 words

## Thin Content Safeguards

| Metric | Threshold | Action |
|--------|-----------|--------|
| Pages without content review | 100+ | ⚠️ WARNING |
| Pages without justification | 500+ | 🛑 HARD STOP |
| Unique content per page | <40% | ❌ Thin content risk |
| Word count per page | <300 | ⚠️ Review |

### Scaled Content Abuse (2025-2026)
- Google June 2025: wave of manual actions on AI-generated content at scale
- August 2025: SpamBrain enhanced pattern detection
- **Content differentiation**: ≥30-40% genuinely unique between pages
- **Progressive rollout**: Batches of 50-100 pages, monitor 2-4 weeks before expanding

### Safe vs Risky Patterns
✅ Integration pages (real docs, API details), template/tool pages, glossary (200+ words), product pages (unique specs), data-driven pages

❌ Location pages with only city name swapped, "[tool] for [industry]" without real value, AI-generated without human review

## Index Bloat Prevention
- Noindex low-value pages, noindex paginated results beyond page 1
- Faceted navigation: noindex filtered views, canonical to base
- >10k pages: monitor crawl stats in GSC
- Monthly: indexed count vs intended count

---

# Part 8: GSC 分析

## Workflow

### Step 1: タスク分類

| タスク種別 | 主要ツール |
|-----------|-----------|
| パフォーマンス概要 | `get_performance_overview` |
| クエリ分析 | `get_search_analytics`, `get_advanced_search_analytics` |
| ページ分析 | `get_search_by_page_query` |
| 期間比較 | `compare_search_periods` |
| インデックス診断 | `inspect_url_enhanced`, `batch_url_inspection` |
| サイトマップ管理 | `list_sitemaps_enhanced`, `submit_sitemap` |

### Step 2: プロパティ確認
```
list_properties → 利用可能なサイト一覧を取得
```

### Step 3: データ取得・分析 → Step 4: 洞察・提案

## 利用可能なツール（19種）

### プロパティ管理
`list_properties`, `get_site_details`, `add_site`, `delete_site`

### 検索アナリティクス
`get_search_analytics`, `get_performance_overview`, `get_advanced_search_analytics`, `compare_search_periods`, `get_search_by_page_query`

### URL・インデックス管理
`check_indexing_issues`, `inspect_url_enhanced`, `batch_url_inspection`

### サイトマップ
`get_sitemaps`, `list_sitemaps_enhanced`, `submit_sitemap`, `get_sitemap_details`

## 分析パターン

### パフォーマンス概要
1. `get_performance_overview` → クリック、インプレッション、CTR、平均順位
2. `get_search_analytics` (dimensions: query, device) → 上位クエリ、デバイス別

### 順位改善の機会
- 11-20位のクエリ → タイトル/メタ最適化で10位以内を狙う
- 高インプレッション・低CTR → タイトル改善の余地

### モバイル vs デスクトップ
- モバイルの順位がデスクトップより低い → モバイル最適化が必要
- モバイルの CTR が低い → タップしやすいタイトルに改善

### 期間比較
- 急落クエリ → 競合の台頭、アルゴリズム変更
- 急上昇クエリ → 成功要因を横展開

### インデックス診断
- "Crawled - currently not indexed" → コンテンツ品質改善
- "Discovered - currently not indexed" → 内部リンク追加
- "Blocked by robots.txt" → robots.txt 修正

## GSC レポート出力フォーマット

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GSC PERFORMANCE REPORT: [サイト名]
期間: [開始日] 〜 [終了日]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY:
  クリック数: [数値] ([前期比 +/-%)
  インプレッション: [数値] ([前期比 +/-%)
  平均CTR: [数値]%
  平均順位: [数値]

TOP QUERIES:
  1. [クエリ] — クリック: [数値], 順位: [数値]

OPPORTUNITIES:
  - [クエリ]: 順位 [数値] → 10位以内を狙える
  - [クエリ]: CTR [数値]% → タイトル改善推奨

ISSUES:
  - [問題の説明と対応策]

NEXT ACTIONS:
  1. [推奨アクション]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## GSC セットアップ

### 認証方法

#### OAuth（推奨 - 個人利用）
1. Google Cloud Console で OAuth 2.0 クライアント ID を作成
2. `client_secrets.json` をダウンロード
3. `export GSC_OAUTH_CLIENT_SECRETS_FILE=/path/to/client_secrets.json`

#### サービスアカウント（自動化・チーム利用）
1. サービスアカウント作成 → JSON キーダウンロード
2. Search Console でアクセス権付与
3. `export GSC_CREDENTIALS_PATH=/path/to/service-account.json` + `export GSC_SKIP_OAUTH=true`

### Claude Code への登録
```bash
claude mcp add gsc --scope user -- \
  /path/to/mcp-gsc/.venv/bin/python /path/to/mcp-gsc/gsc_server.py
```

## GSC Troubleshooting

- **認証エラー**: 環境変数パス確認、トークンリフレッシュ
- **プロパティ非表示**: GSC でアカウントにプロパティ登録確認、サービスアカウントのアクセス権確認
- **データ取得失敗**: 期間にデータ存在するか、日付フォーマット（YYYY-MM-DD）、プロパティURL形式確認
- **MCP 起動失敗**: `claude mcp list` で確認、手動起動テスト

## References
- [mcp-gsc GitHub](https://github.com/AminForou/mcp-gsc)
- [Google Search Console API](https://developers.google.com/webmaster-tools/v1/api_reference_index)
- [Search Console ヘルプ](https://support.google.com/webmasters/)
