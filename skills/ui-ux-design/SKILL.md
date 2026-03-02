---
name: ui-ux-design
description: "UI/UXデザインインテリジェンス。67スタイル、96カラーパレット、57フォントペアリング、13テックスタック、60コンポーネントパターン、95+デザインシステム参照対応。Use when user requests UI/UX work: design, build, create, implement, review, fix, improve web/mobile interfaces or UI components. Trigger phrases: ランディングページ, ダッシュボード, UI設計, フロントエンド, React, Tailwind, デザインシステム, カラーパレット, レスポンシブ, website, landing page, portfolio, SaaS, e-commerce, コンポーネント, accordion, modal, datepicker, drawer, button, tabs, dialog, form, tooltip, card, table, widget. File types: .html, .tsx, .jsx, .vue, .svelte."
---

# UI/UX Design Intelligence

> Source: [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) v2.2 をベースに凝縮。

## WORKFLOW

UI/UX タスクを受けたら、以下のステップで進める:

### Step 1: 要件分析
ユーザーのリクエストから以下を特定:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page 等
- **Style keywords**: minimal, playful, professional, elegant, dark mode 等
- **Industry**: healthcare, fintech, gaming, education 等
- **Stack**: React, Next.js, Vue, HTML+Tailwind（デフォルト）等

### Step 2: デザインシステム生成
以下の5要素を決定して提示:
1. **Pattern** — ランディングページ構造 / レイアウトパターン
2. **Style** — UIスタイル（67種から選択。詳細は `references/styles-catalog.md`）
3. **Colors** — カラーパレット（詳細は `references/color-typography.md`）
4. **Typography** — フォントペアリング（詳細は `references/color-typography.md`）
5. **Key Effects** — アニメーション・インタラクション

### Step 3: コード実装
デザインシステムに基づいてコードを生成。

### Step 4: Pre-delivery チェック
- [ ] 絵文字をアイコン代わりに使っていない（SVG: Heroicons/Lucide を使用）
- [ ] クリッカブル要素に `cursor-pointer` を設定
- [ ] ホバー状態にスムーズなトランジション（150-300ms）
- [ ] テキストコントラスト比 4.5:1 以上
- [ ] キーボードナビゲーション用のフォーカス状態
- [ ] `prefers-reduced-motion` の尊重
- [ ] レスポンシブ: 375px, 768px, 1024px, 1440px

---

## INDUSTRY-SPECIFIC REASONING RULES

業界ごとの推奨設定。ユーザーのプロダクトに合わせて自動選択:

### Tech & SaaS
- **Pattern**: Feature-Rich Showcase + Trust & Authority
- **Style Priority**: Minimalism, Glassmorphism, AI-Native UI
- **Color Mood**: Blue-dominant professional, tech gradients
- **Typography**: Inter / Geist / SF Pro — clean, modern sans-serif
- **Anti-patterns**: 過度な装飾、スキューモーフィズム

### Healthcare / Medical
- **Pattern**: Trust & Authority + Social Proof
- **Style Priority**: Accessible & Ethical, Inclusive Design, Soft UI
- **Color Mood**: Blue/green trust palette, calming tones
- **Typography**: Source Sans Pro / Noto Sans — 高い可読性
- **Anti-patterns**: ダークモード、派手なアニメーション、低コントラスト

### Fintech / Banking
- **Pattern**: Trust & Authority + Data Dashboard
- **Style Priority**: Glassmorphism, Minimalism, Dark Mode
- **Color Mood**: Navy/dark blue trust, green for positive
- **Typography**: Inter / IBM Plex — 数字に強いフォント
- **Anti-patterns**: AI purple/pink gradients、カジュアルすぎるデザイン

### E-commerce
- **Pattern**: Hero-Centric + Conversion-Optimized
- **Style Priority**: Flat Design, 3D Product Preview, Bento Grid
- **Color Mood**: Brand-specific with high-contrast CTA
- **Typography**: DM Sans / Poppins — フレンドリーかつ読みやすい
- **Anti-patterns**: 情報過多、CTA不明確

### Beauty / Wellness / Spa
- **Pattern**: Hero-Centric + Social Proof
- **Style Priority**: Soft UI Evolution, Organic Biophilic, Nature Distilled
- **Color Mood**: Soft pink, sage green, gold accents
- **Typography**: Cormorant Garamond / Montserrat — エレガント
- **Anti-patterns**: ネオン色、ハードなアニメーション、ダークモード

### Portfolio / Creative Agency
- **Pattern**: Storytelling-Driven + Interactive Demo
- **Style Priority**: Motion-Driven, Brutalism, Interactive Cursor
- **Color Mood**: Bold, high contrast, monochrome or accent
- **Typography**: Space Grotesk / Syne — 個性的
- **Anti-patterns**: ジェネリックテンプレート感

### Education
- **Pattern**: Feature-Rich + Social Proof
- **Style Priority**: Claymorphism, Inclusive Design, Flat Design
- **Color Mood**: Warm, friendly, high contrast
- **Typography**: Nunito / Quicksand — 親しみやすい
- **Anti-patterns**: 複雑なナビゲーション、小さいフォント

### Gaming / Entertainment
- **Pattern**: Hero-Centric + Interactive
- **Style Priority**: Cyberpunk, 3D Hyperrealism, HUD/Sci-Fi
- **Color Mood**: Neon, dark backgrounds, vivid accents
- **Typography**: Rajdhani / Orbitron — futuristic
- **Anti-patterns**: 退屈なレイアウト、ミニマルすぎ

---

## STACK-SPECIFIC GUIDELINES

### HTML + Tailwind（デフォルト）
- Semantic HTML5 タグを使用（`<header>`, `<main>`, `<section>`, `<article>`）
- `@apply` は最小限に、utility-first を維持
- Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`

### React / Next.js
- コンポーネント単位で分離
- shadcn/ui を推奨（アクセシビリティ内蔵）
- `use client` / `use server` の適切な使い分け（Next.js App Router）
- コンポーネント実装時は `references/design-systems.md` のヘッドレスライブラリを参照

### Vue / Nuxt
- Composition API + `<script setup>`
- Nuxt UI コンポーネントライブラリ推奨

### SwiftUI
- System colors / Dynamic Type / SF Symbols

### React Native
- React Native Paper / NativeBase / Tamagui
- `SafeAreaView` の使用

### Flutter
- Material 3 / Cupertino widgets
- Theme data で一元管理

---

## COMPONENT IMPLEMENTATION WORKFLOW

UIコンポーネントの実装リクエストを受けたら、以下のステップで進める:

### Step 1: コンポーネント特定
- `references/components.md` でコンポーネントパターンを特定（エイリアスで表記揺れを吸収）
- セマンティック HTML 要素と必要な ARIA 属性を確認

### Step 2: リファレンス参照
- `references/design-systems.md` でユーザーのスタックに最適なデザインシステムを選択
- 複雑なコンポーネント（Dialog, Data Table, Date Picker 等）は 2-3 の実装を比較
- 必要に応じて `component.gallery/components/{slug}/` で横断検索

### Step 3: 実装チェックリスト
- [ ] **セマンティック HTML** — 正しい要素を使用
- [ ] **ARIA 属性** — roles, states, labels
- [ ] **キーボードナビゲーション** — Tab, Enter, Escape, Arrow keys
- [ ] **フォーカス管理** — 可視フォーカスインジケータ、モーダルのフォーカストラップ
- [ ] **状態** — Default, hover, focus, active, disabled, loading, error
- [ ] **命名** — 確立されたコンポーネント名を使用（エイリアスは components.md で確認）

---

## UX ANTI-PATTERNS（絶対に避けること）

1. **絵文字をアイコンに使わない** — 必ず SVG アイコン（Heroicons, Lucide, Phosphor）を使用
2. **クリッカブル要素に `cursor-pointer` を忘れない**
3. **ホバー/フォーカス状態がない** — 必ずトランジション付きで実装
4. **コントラスト不足** — WCAG AA（4.5:1）を必ずクリア
5. **z-index の乱用** — 計画的に管理（10, 20, 30, 40, 50）
6. **アニメーション過多** — `prefers-reduced-motion` を尊重
7. **モバイル非対応** — Mobile-first で設計
8. **フォームの UX が悪い** — インラインバリデーション、明確なエラー表示
9. **ローディング状態がない** — Skeleton / Spinner を実装
10. **AI っぽいデザイン** — purple/pink グラデーション、generic なイラストを避ける

---

## DESIGN SYSTEM OUTPUT FORMAT

デザインシステムを提案する際は、以下のフォーマットで出力:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 DESIGN SYSTEM: [Project Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐 PATTERN: [Landing Page Pattern]
🎭 STYLE: [UI Style Name]
🎨 COLORS:
   Primary:    [hex] ([name])
   Secondary:  [hex] ([name])
   CTA:        [hex] ([name])
   Background: [hex] ([name])
   Text:       [hex] ([name])
✏️ TYPOGRAPHY: [Heading Font] / [Body Font]
   Google Fonts: [URL]
✨ KEY EFFECTS: [animations, transitions]
🚫 ANTI-PATTERNS: [what to avoid]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## VIBE CODING UI（AI UI生成のベストプラクティス）

AIでUIを生成する際の7つの原則:

### 1. スケッチ優先、プロンプト後
- テキストから始めない。**Excalidraw** 等でワイヤーフレームを描く
- ボックス、ボタン、画像配置を視覚化してからAIに渡す
- 「この構造に正確に従って」と指示 → AIは想像より模倣が得意

### 2. 好みのUIをスクショ
- **Dribbble**, **Mobbin**, 気に入ったサイトから具体的なセクションをスクショ
- ナビバー、プライシングカード、ヒーローセクション等を個別にキャプチャ
- 「このスタイルをコピーして」と添付 → 結果が劇的に改善

### 3. ムードボードでカラー指定
- 「モダンで温かみのある」では毎回同じ青になる
- **Nano Banner** 等のムードボード生成ツールで画像を作成
- その画像を「このカラーパレットを参考に」と渡す

### 4. コード前にデザインシステム定義
- ブランドカラー、タイポグラフィ、スペーシングルールを先に決める
- このスキルの Step 2 で必ずデザインシステムを生成してから実装
- 一貫性のなさがAI UIの最大の問題

### 5. アンチパターンルールを厳守
- このスキルの「UX ANTI-PATTERNS」と「INDUSTRY-SPECIFIC REASONING RULES」を参照
- AIデフォルトのグラデーション禁止ルールを適用
- 「他のAIアプリと同じ見た目にするな」をシステムに組み込む

### 6. スクショを主要コミュニケーション手段に
- AIは模倣が得意、想像が苦手
- 視覚的コンテキストを多く与えるほど推測が減る
- 「クリーンに」と書くより、クリーンの実例を見せる

### 7. フォントとアイコンで差別化
- AIデフォルトの Inter + Lucide は即座にAI生成バレ
- **Google Fonts** からユニークなフォントを選択
- Lucide を **Phosphor**, **Heroicons**, **Tabler** に変更
- 小さな変更でテンプレート感が消える

---

## TROUBLESHOOTING

### デザインが「AIっぽい」と感じる場合

- purple/pink グラデーションを避ける
- generic なイラスト・アイコンを避ける
- 実際のコンテンツ/画像を使用する

### レスポンシブが崩れる場合

1. Mobile-first で再設計
2. `flex-wrap` / `grid` の使用を確認
3. 固定幅（px）を相対単位（%、rem）に変更

### コントラストが不足している場合

WCAG AA 基準（4.5:1）を満たすツールで確認:
- WebAIM Contrast Checker
- Chrome DevTools > Rendering > CSS Overview

---

## REFERENCES

詳細データは以下を参照:
- `references/styles-catalog.md` — 67スタイル完全一覧 + ダッシュボードスタイル
- `references/color-typography.md` — カラーパレット + フォントペアリング20選 + チャート推奨
- `references/components.md` — 60コンポーネントパターン（セマンティックHTML、ARIA、キーボードナビ、複雑度）
- `references/design-systems.md` — 95+プロダクションデザインシステム（スタック別索引、Best-in-Class一覧）
