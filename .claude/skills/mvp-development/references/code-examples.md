# MVP Development コード例

## Supabase Auth

### クライアント側

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

### サーバー側

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

## shadcn/ui 初期化

```bash
npx shadcn@latest init
npx shadcn@latest add button card dialog input label
```

## Zustand ストア

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

## Supabase DB 操作

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

## Polar.sh Webhook

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

## 監視・分析

```bash
npm install @sentry/nextjs && npx @sentry/wizard@latest -i nextjs
npm install posthog-js
```

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

## CLAUDE.md テンプレート

新規プロジェクトの CLAUDE.md に以下を記載:

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
