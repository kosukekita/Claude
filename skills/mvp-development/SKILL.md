---
name: mvp-development
description: "MVP・個人プロジェクトのWebアプリ開発スタック。Next.js + Supabase + Polar.sh + Vercel構成。新規プロジェクト立ち上げ、技術スタック選定、MVP開発時に参照。"
---

# MVP Development Skill

## 技術スタック

```
フレームワーク:  Next.js (App Router)
UI:             Tailwind CSS + shadcn/ui
状態管理:        Zustand
API:            tRPC + Server Actions
認証:           Supabase Auth
DB:             Supabase (PostgreSQL)
課金:           Polar.sh
デプロイ:        Vercel
エラー監視:      Sentry
分析:           PostHog
```

---

## 認証: Supabase Auth

自前実装しない。Supabase Authを使う。

```bash
npm install @supabase/supabase-js @supabase/ssr
```

```typescript
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        },
      },
    }
  )
}
```

- OAuthはSupabase Dashboardから有効化
- Row Level Security (RLS) で認可をDB層に定義

---

## UI: Tailwind CSS + shadcn/ui

```bash
npx shadcn@latest init
npx shadcn@latest add button card dialog input label
```

- Raw CSSは書かない。Tailwindのみ

---

## 状態管理: Zustand

```typescript
import { create } from 'zustand'

interface AppState {
  count: number
  increment: () => void
}

export const useAppStore = create<AppState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))
```

- Reduxは使わない
- サーバー側データ取得はReact Server Componentsで完結

---

## API: tRPC

- end-to-endの型安全。REST APIをゼロから書かない
- Server Actionsとの併用可

---

## DB: Supabase (PostgreSQL)

Supabase Clientで操作する。ORMは使わない。

```typescript
// データ取得
const { data, error } = await supabase
  .from('posts')
  .select('*')
  .eq('user_id', userId)

// データ挿入
const { data, error } = await supabase
  .from('posts')
  .insert({ title: 'Hello', user_id: userId })
```

- スキーマ管理はSupabase Dashboard or SQL migrations
- RLSで認証ユーザーに基づくアクセス制御を定義
- マイグレーションは `supabase db diff` → `supabase db push`

---

## 課金: Polar.sh

1. Polar.shでプロダクト・プランを作成
2. Checkout URLを生成してユーザーに提供
3. Webhookでサブスクリプション状態をSupabaseに同期

```typescript
// app/api/polar/webhook/route.ts
import { Webhooks } from "@polar-sh/nextjs"

export const POST = Webhooks({
  webhookSecret: process.env.POLAR_WEBHOOK_SECRET!,
  onPayload: async (payload) => {
    switch (payload.type) {
      case "subscription.created":
      case "subscription.updated":
        // ユーザーのサブスクリプション状態を更新
        break
      case "subscription.canceled":
        // アクセス権を無効化
        break
    }
  },
})
```

---

## デプロイ: Vercel

```bash
vercel deploy --prod
```

- 環境変数はVercel Dashboardで管理

---

## 監視・分析（初日から入れる）

```bash
npm install @sentry/nextjs && npx @sentry/wizard@latest -i nextjs
npm install posthog-js
```

---

## 環境変数

```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
POLAR_WEBHOOK_SECRET
POLAR_ACCESS_TOKEN
SENTRY_DSN
NEXT_PUBLIC_POSTHOG_KEY
```

---

## CLAUDE.md テンプレート

```markdown
## Tech Stack
- Next.js 15 (App Router)
- Supabase (Auth + PostgreSQL)
- Tailwind CSS + shadcn/ui
- tRPC + Zustand
- Polar.sh for billing
- Vercel for deployment
- Sentry + PostHog

## Commands
- `npm run dev` — 開発サーバー
- `supabase db push` — マイグレーション適用
- `vercel deploy --prod` — 本番デプロイ

## Rules
- 認証はSupabase Auth。自前実装しない
- DBはSupabase Client。ORMは使わない
- UIはshadcn/ui。Raw CSS書かない
- 状態管理はZustand。Redux使わない
- 課金はPolar.sh
- Sentry・PostHogは初日から入れる
```
