# Global Rules

- **Language**: Always respond in Japanese (常に日本語で回答してください).
- **Marp 使用禁止**: パワーポイント・スライド作成に Marp は使用しない。python-pptx 等で直接 .pptx を生成すること。
- **PowerPoint デザイン設定** (python-pptx 使用時):
  - 背景: `#F9F9F9`（装飾なし無地白）
  - テキスト: `#1A1A1A`（視認性を確保した黒）
  - アクセント: `#004BB1`（青）、サブアクセント: `#E3F2FD`（淡青）
  - フォント: `Arial, 'Yu Gothic', 'YuGothic', sans-serif`（英数字 Arial 優先、日本語 游ゴシック）
  - フォントサイズ: タイトル 50pt / 見出し 35pt / 本文 25pt
  - スタイル: モノクローム基調、図解・強調のみ青の濃淡使用、コントラスト抑制＋視認性確保、十分な余白

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
- **prompt-engineer** — LLMプロンプト設計・最適化。Chain-of-thought、few-shot learning、構造化出力、評価フレームワーク。
- **rag-architect** — RAGシステム設計・構築。ベクトルDB、セマンティック検索、ドキュメント検索、コンテキスト拡張。
- **debugging-wizard** — 体系的デバッグ手法。エラー調査、スタックトレース分析、根本原因特定、トラブルシューティング。
- **mcp-developer** — MCPサーバー/クライアント開発。JSON-RPC 2.0、TypeScript/Python SDK、リソースプロバイダー、ツール関数。
- **api-designer** — REST/GraphQL API設計。OpenAPI 3.1仕様、リソースモデリング、バージョニング、ページネーション、エラーハンドリング。
- **code-reviewer** — コードレビュー手法。PRレビュー、品質監査、セキュリティ脆弱性検出、リファクタリング提案。
- **zotero** — Zotero ローカル API + REST API 連携。DOI 一括インポート、コレクション管理、アイテム検索・一覧表示、BibTeX インポート。文献登録・文献管理タスクで参照。

### Superpowers（開発ワークフロー）
- **brainstorming** — 創造的作業前の要件・設計探索。機能追加・コンポーネント作成前に必須。
- **writing-plans** — 複数ステップタスクの実装計画作成。コードに触れる前に使用。
- **executing-plans** — 実装計画の実行とレビューチェックポイント管理。
- **subagent-driven-development** — 独立タスクのサブエージェント駆動開発。
- **dispatching-parallel-agents** — 2つ以上の独立タスクの並列実行。
- **test-driven-development** — TDD実践。実装コード記述前に使用。
- **systematic-debugging** — バグ・テスト失敗・予期せぬ動作の体系的調査。修正提案前に使用。
- **verification-before-completion** — 完了主張前の検証必須。証拠なき主張禁止。
- **requesting-code-review** — タスク完了・主要機能実装・マージ前の作業検証。
- **receiving-code-review** — コードレビューフィードバック受領時の技術的検証。
- **finishing-a-development-branch** — 実装完了・テストパス後の統合方法選択ガイド。
- **using-git-worktrees** — 機能作業の分離。実装計画実行前に使用。
- **writing-skills** — スキル作成・編集・デプロイ前検証。TDDをドキュメントに適用。
- **using-superpowers** — 会話開始時のスキル発見・活用方法。

## Skill Security

スキル追加時は必ず `skill-scanner` でセキュリティチェックを実行:
```bash
skill-scanner scan /path/to/skill --use-behavioral
```
- HIGH/CRITICAL 検出時は内容を精査し、誤検知でなければ追加しない
- 誤検知（セキュリティドキュメント内の例文等）は許容

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
