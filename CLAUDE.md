# Global Rules

- **Language**: Always respond in Japanese (常に日本語で回答してください).
- **Slides/Presentation Workflow**:
  1. まず **marp** スキルで Markdown スライドを作成
  2. 図解が必要な箇所は **infographic** スキルで SVG を生成し、Markdown に埋め込む
  3. 完成後 `marp --pptx` で PowerPoint に変換

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
- **career** — 喜多洸介の経歴（学歴・職歴）の管理・参照・出力。CV作成、経歴照会、履歴書フォーマットでの出力に対応。
- **infographic** — AntV Infographic を活用したインフォグラフィック生成。テキストや情報から視覚的なインフォグラフィックを作成。約200種のテンプレート、手書き風・グラデーション等のテーマ、SVG出力対応。
- **marp** — Marp CLI を活用した Markdown → PowerPoint/PDF/HTML スライド生成。Infographic で生成した SVG を埋め込み可能。

## Workflow Best Practices

### 開発フロー
- **Plan Mode 優先**: 複雑なタスクは Plan Mode でアーキテクチャを固めてから実装
- **1機能 = 1会話**: 大規模開発では機能単位で会話を分割（個人開発規模なら1スレッドでも可）
- **セッション間共有**: `SCRATCHPAD.md` や `plan.md` に進捗・計画を書き出し、次のセッションで参照

### CLAUDE.md の原則
- **簡潔さが命**: Claude が従える指示は約150-200個。システムプロンプトで約50消費されるため、残り100-150が上限
- **理由を書く**: 「何を」だけでなく「なぜ」を伝えることで判断力が向上
- **随時更新**: 作業中・作業後に Claude 自身に編集させてアップデート

### トラブル対応
- **ループ時の対処**: 指示を重ねるのではなく、会話をクリアするかアプローチを根本から変える
- **Hooks 活用**: ファイル変更時に Prettier・型チェックを自動実行して技術的負債を防ぐ
