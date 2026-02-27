---
name: mvp-development
description: "MVP・個人プロジェクトのWebアプリ開発スタック。Next.js + Supabase + Polar.sh + Vercel構成。新規プロジェクト立ち上げ、技術スタック選定、MVP開発時に参照。Trigger: MVP, 新規プロジェクト, アプリ開発, LP作成, SaaS, Webアプリ, Next.js, Supabase, Vercel, Polar."
---

# MVP Development

> コード例・テンプレートは `references/code-examples.md` を参照

## Workflow

MVP開発タスクを受けたら、以下のステップで進める:

### Step 1: 要件確認
- サイト種別（SaaS / LP / ダッシュボード / ツール）
- 認証要否、課金要否
- 主要機能の特定

### Step 2: プロジェクト初期化
- Next.js (App Router) + Tailwind CSS + shadcn/ui
- Supabase プロジェクト作成・環境変数設定
- 必要に応じて tRPC, Zustand, Sentry, PostHog 追加

### Step 3: 実装
- 以下の技術スタックルールに従って実装

### Step 4: デプロイ
- Vercel にデプロイ、環境変数設定

---

## 技術スタック（厳守）

| レイヤー | 採用技術 | 禁止事項 |
|---------|---------|---------|
| フレームワーク | Next.js (App Router) | Pages Router |
| UI | Tailwind CSS + shadcn/ui | Raw CSS, CSS Modules |
| 状態管理 | Zustand | Redux, Recoil |
| API | tRPC + Server Actions | REST APIをゼロから構築 |
| 認証 | Supabase Auth | 自前実装, NextAuth |
| DB | Supabase (PostgreSQL) | ORM (Prisma等) |
| 課金 | Polar.sh | Stripe直接実装 |
| デプロイ | Vercel | 他のホスティング |
| エラー監視 | Sentry | 初日から導入 |
| 分析 | PostHog | 初日から導入 |

## 重要ルール

- **認証**: Supabase Auth のみ。OAuth は Dashboard から有効化。RLS で認可を DB 層に定義
- **DB**: Supabase Client で操作。スキーマは Dashboard or SQL migrations。`supabase db diff` → `supabase db push`
- **UI**: shadcn/ui コンポーネント優先。Raw CSS は書かない
- **サーバーデータ**: React Server Components で取得。クライアント状態のみ Zustand
- **課金**: Polar.sh でプラン作成 → Checkout URL → Webhook で Supabase に同期
- **監視**: Sentry + PostHog は初日から入れる（後回しにしない）
- **環境変数**: Vercel Dashboard で管理。`.env.local` はローカルのみ

---

## Troubleshooting

### Supabase Auth が動かない
- `NEXT_PUBLIC_SUPABASE_URL` と `NEXT_PUBLIC_SUPABASE_ANON_KEY` を確認
- Supabase Dashboard で OAuth プロバイダーの Callback URL を確認

### RLS でデータが取得できない
- RLS ポリシーが有効か確認（`auth.uid()` の条件）
- Service Role Key はサーバー側のみで使用

### Polar.sh Webhook が届かない
- Webhook Secret が一致しているか確認
- ローカル開発では ngrok 等でトンネリング

### Vercel デプロイ失敗
- 環境変数が全て設定されているか確認
- `next build` がローカルで通るか確認
