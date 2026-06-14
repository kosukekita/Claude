---
name: search-optimization
description: "SEO/LLMO/GEO/AIO 統合スキル（検索最適化の全体）。SEO=Google上位表示の土台、LLMO/GEO=対話型AI（ChatGPT/Claude/Gemini/Perplexity）に引用される積み増し、AIO=Google AI概要対策。テクニカルSEO、オンページ、コンテンツ、構造化データ、CWV、E-E-A-T、サイテーション（言及）、競合比較、hreflang、画像最適化、プログラマティックSEO、GSC分析。Trigger: SEO, LLMO, GEO, AIO, 検索順位, キーワード, 構造化データ, JSON-LD, Core Web Vitals, AI Overviews, AI検索, 生成エンジン最適化, ChatGPT, Perplexity, Gemini, サイテーション, 引用される, comparison page, programmatic SEO, Search Console, GSC, CTR, インプレッション, E-E-A-T, llms.txt."
---

# Search Optimization — SEO / LLMO / GEO / AIO

> 詳細な実装例は `references/` を参照: `schema-examples.md`, `html-patterns.md`, `gsc-setup.md`, `report-templates.md`, `keyword-research-api.md`, `llmo-geo-aio.md`

## 4つの用語の整理（最初にここを揃える）

SEO・LLMO・GEO・AIO はゴール（顧客に選ばれる）は同じだが、選ばれる経路と打ち手が違う。混同すると AI 時代のサイト運用で遠回りになる。

| 用語 | 何の最適化か | 役割 | 主な対象 |
|------|------------|------|---------|
| **SEO** | Google 検索で上位表示 | **土台**（必須・今も有効） | Google 検索結果 |
| **LLMO** | 対話型 AI に社名/サービスを引用させる | SEO の上に**積み増す** | ChatGPT, Claude, Gemini, Perplexity, Felo |
| **GEO** | 生成エンジン最適化。**LLMO とほぼ同義**（用語としては GEO が主流化） | LLMO と同じ | 生成 AI 全般 |
| **AIO** | Google 検索上部の「AI による概要」に入る | **SEO と強く関連・LLMO とは別物** | Google AI Overviews / AI Mode |

**核心の関係**: `SEO（土台）→ その上に LLMO/GEO を積む → 業種で強弱をつける`。

- **SEO ができていないと LLMO も積み上がらない**。AI（ChatGPT/Perplexity 等）は結局ネット上の文章を読みに来るので、Google に見つけてもらえないサイトは AI にもほぼ見つからない。
- **「SEO はもう古い、これからは LLMO だけ」は誤り**。SEO はすべての基礎。
- ただし **「SEO で上位＝AI に引用される」とは限らない**（→ 下の「LLMO/GEO」セクションの海外データ参照）。それぞれの引用ロジックを意識した追加施策が要る。
- 海外の最先端を一言でいうと「**言及されること＝サイテーション**」。アナログ/デジタル問わず社名・サービス・商品名が各所で言及される状態を作るのが今の最重要ポイント。

> たとえ話: **SEO は食べログの評価を取りに行く作業**、**LLMO はミシュランガイドに掲載される作業**。ChatGPT/Perplexity は「独自基準で選別し、ニーズに合う2〜3店を推薦するミシュランの調査員」のように振る舞う。

→ LLMO/GEO/AIO の詳細（海外データ・3施策・Google 公式見解・業種別優先順位・よくある勘違い）は `references/llmo-geo-aio.md`

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

**ページファイル（HTML）を作成・生成した後、必ずサイズを確認すること。**  
Googleがインデックスするのは**最初の2MB（2,097,152バイト）のみ**。超過コンテンツは認識されない（クロール自体は15MBまで可）。

> **SSR・動的サイト**: テンプレートファイルではなく**実際に配信されるHTMLレスポンス**のサイズを確認する。
> ```bash
> curl -s https://example.com/page | wc -c
> ```

```bash
# 静的HTMLファイルのサイズ確認
ls -lh page.html
wc -c page.html          # バイト数（2,097,152 bytes = 2MB）

# Python で確認（page.html を対象ファイルに置き換えて使用）
python3 -c "
import os, sys
path = 'page.html'
size = os.path.getsize(path)
limit = 2 * 1024 * 1024
print('File size: %.1f KB (%.1f%% of 2MB limit)' % (size/1024, size/limit*100))
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

## LLMO / GEO（AI に引用される最適化）

> LLMO＝大規模言語モデル最適化、GEO＝生成エンジン最適化。両者はほぼ同義。SEO の上に積み増す施策。詳細・出典は `references/llmo-geo-aio.md`

### なぜ必要か（消費者行動の変化）
- Gartner 予測: **2026年までに従来型検索エンジンのトラフィックが 25% 減少**（出典: Gartner プレスリリース 2024-02-19）。代わりに ChatGPT/Perplexity 等の AI 検索が急増。

### 「SEO で上位＝AI に引用される」とは限らない（海外データ 3つ）
1. **Google 内の AI 機能同士でも引用元の重複は 13.7%** — AI Overviews と AI Mode で引用ドメインの 8割超が異なる（Position Digital, 2026-04）。
2. **AI ごとに最大引用源が違う** — ChatGPT=Wikipedia(7.8%)、Google AI Overviews=Reddit(2.2%)、Perplexity=Reddit(6.6%)。ChatGPT は「整理された百科事典型」、AIO/Perplexity は「人の口コミ」を重視。
3. **Google AI Mode の引用元の 88% はオーガニック検索の上位圏外**（Position Digital, 2026-04）。Google 1位＝AI Mode 引用 ではない。

→ つまり SEO で上位でも ChatGPT/Perplexity に引用されないことは普通にある。引用ロジックを意識した追加施策が要る。

### LLMO で必要な3つ（SEO を土台に積む）
1. **「質問と答え」をはっきり書く** — 「料金は？」「他社と何が違う？」「対応エリアは？」への回答を見出し＋本文で **1〜3行で完結**させる（AI が答えを抜き出せる形に）。
2. **「誰が書いたか」を明確に（E-E-A-T）** — 代表者・顔写真・経歴・資格。スカスカだと AI は信用できない情報源と判断。Person schema で構造化。
3. **サイト外で「言及される」場所を作る（サイテーション）** — Google ビジネスプロフィール口コミ、業界ポータル紹介、SNS 言及。第三者言及が引用の近道。自サイトで自賛するだけでは不可。

### GEO 5 Criteria（採点フレーム）
1. **Citability (25%)** — 134-167語の自己完結ブロック、最初の40-60語で直接回答
2. **Structural Readability (20%)** — H1→H2→H3、質問ベース見出し、短段落、テーブル/リスト
3. **Multi-Modal (15%)** — テキスト+画像/動画/インフォグラフィック（156%高選択率）
4. **Authority & Brand (20%)** — 著者バイライン、公開日、引用元、Wikipedia/Reddit/YouTube存在
5. **Technical Accessibility (20%)** — SSR必須（AIクローラーはJS非実行）、robots.txt、llms.txt

### Key Facts (Feb 2026)
- AI Overviews: 1.5B users/month, 50%+クエリカバー
- Brand mentions correlate 3× more than backlinks with AI visibility
- Only 11% of domains cited by both ChatGPT and Google AI Overviews

### AI Crawler
Allow: GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot. Block CCBot/training crawlers if desired.

### Platform別
- Google AIO: Top-10ランキング+パッセージ最適化
- ChatGPT: Wikipedia(47.9%), Reddit(11.3%)
- Perplexity: Reddit(46.7%), Wikipedia

### Quick Wins
"What is [topic]?" 定義（60語内）、134-167語ブロック、質問H2/H3、統計+出典、Person schema、llms.txt作成

### 業種別の優先順位（実務）
- **地方スモールビジネス（整体・士業・飲食・美容など）**: まず **SEO + MEO**（Google ビジネスプロフィール＋質問形コンテンツ）。LLMO は後。
- **全国商圏の SaaS・コンサル**: 「業界×悩み」の質問形コンテンツ＋E-E-A-T。LLMO の恩恵が最大の層（競合も強い）。
- **医療・士業など信頼が命**: **E-E-A-T 最優先**（代表者・有資格者情報を厚く）。
- ※全業種が LLMO をやるべきとは限らない。SEO/MEO で取れる売上が残る業種も多い。

### AIO（Google AI Overview Optimization）
- Google 検索上部の「AI による概要」に入る工夫。**SEO と強く関連、LLMO とは別物**。
- **Google 公式見解（2026-05）**: 「AEO/GEO 向けの特別な最適化はない。生成AI検索向け最適化＝検索体験全体への最適化＝SEO」と宣言。
- **ただし注意**: この宣言は **Google の AIO/AI Mode に限定**。ChatGPT/Perplexity/Claude は Google とは別ルートでサイトを読むため、それらに引用されるには別の打ち手（LLMO）が必要。Google 公式見解に振り回されて施策を欠落させない。

### よくある勘違い 3つ
1. **「AI で作ったサイトだから LLMO は効いている」** — 作り方と LLMO 対策は別物。中身が整っていなければ効かない。
2. **「LLMO のためにキーワードを詰め込めばいい」** — 詰め込みは逆効果。AI は「人が読んで自然な文章」を評価する。
3. **「LLMO をやれば SEO はいらない」** — SEO はすべての基礎。

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
