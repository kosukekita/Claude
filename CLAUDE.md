# Global Rules

- **Language**: Always respond in Japanese (常に日本語で回答してください).

## Skills

以下のスキルが `~/.claude/skills/` に格納されている。タスクに応じて適切なスキルを参照すること:

- **python-rules** — Python コードの記述・実行時に参照。venv 管理、PEP 8、PyTorch CUDA 選択などのルール。
- **research-toolkit** — 科学的データ解析・医学研究タスク（文献検索、創薬、ゲノミクス、ToolUniverse MCP 操作）で参照。アプリケーション開発には使用しない。
- **ui-ux-design** — UI/UX デザイン・フロントエンド実装（ランディングページ、ダッシュボード、Webアプリ等）で参照。67スタイル・カラーパレット・フォントペアリングの知識を含む。
- **academic-writing** — 医学・学術論文の執筆支援（構成・文体・引用形式・AI文体除去18パターン）。論文執筆・原稿改善タスクで参照。
- **skill-creator** — Claude用スキルの設計・構築・テスト・改善を支援。ユースケース定義、YAMLフロントマター生成、インストラクション作成、トリガーテスト、イテレーション改善をガイド。
- **playwright-cli** — Playwright MCP を活用したブラウザ自動化・E2Eテスト。セッション管理、ストレージ状態、リクエストモック、トレース、動画録画をカバー。
- **seo** — SEO監査・最適化スキル。テクニカルSEO、オンページ最適化、構造化データ、Core Web Vitals、キーワードリサーチ、E-E-A-Tを体系的にガイド。
- **seo-competitor-pages** — 競合比較ページ（X vs Y）・代替製品ページの生成。機能比較マトリックス、スキーママークアップ、コンバージョン最適化。
- **seo-geo** — AI検索最適化（GEO）。AI Overviews、ChatGPT、Perplexity対応。llms.txt、AIクローラー管理、引用可能性スコアリング。
- **seo-hreflang** — 多言語・多地域サイトのhreflang監査・検証・生成。言語/地域コード検証、自己参照・リターンタグ。
- **seo-images** — 画像SEO最適化。altテキスト、フォーマット（WebP/AVIF）、遅延読み込み、CLS防止、レスポンシブ画像。
- **seo-plan** — 戦略的SEO計画。業界別テンプレート、競合分析、コンテンツ戦略、4フェーズ実装ロードマップ。
- **seo-programmatic** — プログラマティックSEO。大規模データ駆動ページ、テンプレートエンジン、薄いコンテンツ対策、インデックス肥大防止。
- **gsc-analytics** — Google Search Console MCP を活用した検索パフォーマンス分析。クエリ分析、インデックス状況確認、サイトマップ管理、期間比較、モバイル/デスクトップ分析。
- **google-workspace-cli** — gogcli を活用した Google Workspace CLI 操作。Gmail、Calendar、Drive、Docs、Sheets、Chat、Tasks など 15+ サービスをターミナルから操作。
- **achievement** — 喜多洸介の学術業績（論文・書籍・学会発表・受賞歴・助成金）の管理・参照・出力。CV作成、業績リスト生成、科研費様式など各種フォーマットでの出力に対応。
- **infographic** — AntV Infographic を活用したインフォグラフィック生成。テキストや情報から視覚的なインフォグラフィックを作成。約200種のテンプレート、手書き風・グラデーション等のテーマ、SVG出力対応。
