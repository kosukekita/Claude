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
