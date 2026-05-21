---
name: ui-ux-design
description: "Web/mobile UI の設計・実装・レビュー・改善で使用する。ランディングページ、ダッシュボード、デザインシステム、レスポンシブUI、ボタン・モーダル・フォーム等のコンポーネント実装に対応し、視覚階層・余白・色・タイポグラフィ・状態設計・アクセシビリティを補助する。React/Next.js/Tailwind/Vue/Svelte/HTML および Nothing 系UI参照に対応。67スタイル、96カラーパレット、59フォントペアリング、95+デザインシステム参照、60コンポーネントパターン収録。Use when user requests UI/UX work: design, build, create, implement, review, fix, improve web/mobile interfaces or UI components. Trigger phrases: ランディングページ, ダッシュボード, UI設計, フロントエンド, React, Tailwind, デザインシステム, カラーパレット, レスポンシブ, website, landing page, portfolio, SaaS, e-commerce, コンポーネント, accordion, modal, datepicker, drawer, button, tabs, dialog, form, tooltip, card, table, widget, Nothing style, Nothing design, monochrome industrial, モノクロ, きれい, デザイン感度, LP, UI作成. File types: .html, .tsx, .jsx, .vue, .svelte."
---

# UI/UX Design Intelligence

## CORE RULES

1. タスク種別を最初に判定し、TASK ROUTING に従って処理を切り替える。
2. ユーザーの既存デザインシステム・トークン・規約がある場合は必ずそれを優先する。
3. 新規UI設計時のみデザインシステムを明示的に定義する（小規模修正時は省略）。
4. 実装時はアクセシビリティ・レスポンシブ・状態設計を必ず確認する。
5. 参照ファイルは必要なものだけ読む。

## RULE PRECEDENCE

ルールが競合する場合は以下の優先順位に従う：

1. ユーザーの明示的な指定
2. 既存プロジェクトのデザインシステム・トークン
3. 特定スタイル仕様（例：Nothing / Monochrome Industrial）
4. 業界別デフォルトルール（INDUSTRY DEFAULTS）
5. 一般品質ルール（QUALITY CHECKS）

---

## TASK ROUTING

タスク種別に応じて処理を切り替える：

| タスク種別 | 判断基準 | 処理フロー |
|---|---|---|
| **新規ページ / LP / Dashboard** | 「作って」「設計して」「作成して」 | 要件分析 → デザインシステム定義 → 実装 → 品質チェック |
| **既存UI の修正 / レビュー** | 「直して」「改善して」「レビューして」「このUIを」 | 問題特定 → 最小修正 → 品質チェック |
| **コンポーネント実装** | 特定コンポーネント名（modal, button, form 等） | references 参照 → アクセシビリティ確認 → 実装 |
| **デザインシステム提案のみ** | 「デザインの方向性を」「色を決めて」 | DESIGN SYSTEM FORMAT で出力、コード生成不要 |

### 既存UI修正時の追加ルール

- 既存デザインシステム・トークン・コンポーネント規約を優先する
- 要求されていない全面再設計をしない
- 新しいフォント・色・ライブラリを安易に追加しない
- 問題点と修正意図を簡潔に説明してから変更する

---

## CORE WORKFLOW

### Step 1: 要件分析
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page 等
- **Style keywords**: minimal, playful, professional, elegant, dark mode 等
- **Industry**: healthcare, fintech, gaming, education 等（→ INDUSTRY DEFAULTS で自動選択）
- **Stack**: React, Next.js, Vue, HTML+Tailwind（デフォルト）等

### Step 2: デザイン方向の決定
新規設計時のみ以下の5要素を決定して提示：

1. **Pattern** — ランディングページ構造 / レイアウトパターン
2. **Style** — UIスタイル（67種から選択。詳細は `references/styles-catalog.md`）
3. **Colors** — カラーパレット（詳細は `references/color-typography.md`）
4. **Typography** — フォントペアリング（詳細は `references/color-typography.md`）
5. **Key Effects** — アニメーション・インタラクション

> **Nothing Style 選択時**（RULE PRECEDENCE 3 が適用）：`references/nothing-design.md` の完全なトークン・コンポーネント仕様に従う。通常の Colors/Typography 選択をスキップし、Nothing トークンシステムをそのまま適用する。

### Step 3: 実装
- デザイン方向に基づいてコードを生成
- コンポーネント実装時は `references/components.md` と `references/design-systems.md` を参照

### Step 4: 品質チェック
QUALITY CHECKS セクションの MUST 項目を全て確認してから出力する。新規LP/ページ生成時は DEFAULT VISUAL QUALITY も内部確認する（hero spacing, heading impact, CTA prominence, color restraint, typography, card treatment, hover states, mobile typography, realistic content）。

---

## QUALITY CHECKS

### MUST（全タスク必須）

- [ ] **アクセシビリティ** — セマンティック HTML、ARIA 属性、WCAG AA（コントラスト比 4.5:1 以上）
- [ ] **キーボード** — Tab / Enter / Escape / Arrow キー操作、可視フォーカスインジケータ
- [ ] **レスポンシブ** — 375px / 768px / 1024px / 1440px、本文 min 16px
- [ ] **インタラクション状態** — hover / focus / active / disabled / loading / error
- [ ] **`prefers-reduced-motion`** の尊重

### DEFAULT VISUAL QUALITY（新規設計時の品質基準）

**視覚階層**
- フォントサイズに明確な段差（例: 48px / 24px / 16px / 14px）
- 見出しウェイト 700-900、本文 400-500
- CTA ボタンが画面内で最も目立つ要素

**スペーシング**
- 8px グリッド（8, 16, 24, 32, 48, 64, 96, 128px）
- セクション間余白: min 80px（モバイル）/ min 120px（デスクトップ）
- カード内パディング: 24px 以上

**カラー・タイポグラフィ**
- 使用色は最大5色以内（プライマリ・セカンダリ・背景・テキスト・アクセント）
- 本文の行間（line-height）: 1.6〜1.8
- 1行の文字数: 45〜75文字（`max-w-prose` or `max-w-2xl`）

**コンポーネント**
- ボタン padding: `px-6 py-3`（小）/ `px-8 py-4`（大）以上
- カード: `border border-gray-100 shadow-sm`
- ホバー: `transition-all duration-150-300ms`
- SVG アイコン使用（絵文字をアイコン代わりに使わない）

### AVOID BY DEFAULT

- purple / pink グラデーション（AI生成バレ）
- Inter + Lucide のデフォルト組み合わせをそのまま使用（意図を持って選ぶなら可）
- "Lorem ipsum" や "Empower your workflow" 等の generic コンテンツ
- z-index の無計画な乱用

---

## VISUAL DESIGN SENSIBILITY（Hallmark 原則）

全 UI タスクに適用する設計原則：

**原則1: 余白は要素と同等に重要**
空白を怖がらない。セクション間は `py-20 md:py-32` を基本、8px グリッドで管理する。

**原則2: タイポグラフィで格を出す**
見出しは大きく・重く・字間を詰める。本文は読みやすく。フォントは意図を持って選ぶ（Geist / DM Sans / Plus Jakarta Sans 等を検討）。

**原則3: 色数を絞ってコントラストで演出**
ブランドカラー1色 + ニュートラル + アクセント1色が基本。色を使うなら理由を持つ。

**原則4: コンポーネントに「重み」をつける**
ボタン・カード・入力フォームに適切な padding / shadow / border を与えて存在感を出す。

**原則5: 視覚階層を3段階で設計**
Level 1（Hero/CTA）→ Level 2（見出し/強調）→ Level 3（本文/補足）で明確に分ける。

**原則6: ディテールで差をつける**
ボーダーは薄く（`border-gray-100`）、shadow は控えめに（`shadow-sm` / `shadow-md`）、角丸は統一する。

**原則7: 状態設計でリッチ感を出す**
hover: scale-up、active: scale-down、disabled: opacity-50、loading: pulse/spin を実装する。

---

## INDUSTRY DEFAULTS

ユーザーのプロダクト業界に合わせて自動選択（RULE PRECEDENCE 4）：

| 業界 | Style Priority | Typography | Anti-patterns |
|---|---|---|---|
| Tech & SaaS | Minimalism, Glassmorphism, AI-Native UI | Inter / Geist / SF Pro | 過度な装飾、スキューモーフィズム |
| Healthcare | Accessible & Ethical, Soft UI | Source Sans Pro / Noto Sans | ダークモード、派手なアニメーション |
| Fintech | Glassmorphism, Minimalism, Dark Mode | Inter / IBM Plex | AI purple/pink gradients |
| E-commerce | Flat Design, 3D Product Preview, Bento Grid | DM Sans / Poppins | 情報過多、CTA不明確 |
| Beauty / Wellness | Soft UI, Organic Biophilic | Cormorant Garamond / Montserrat | ネオン色、ダークモード |
| Portfolio / Creative | Motion-Driven, Brutalism | Space Grotesk / Syne | ジェネリックテンプレート感 |
| Education | Claymorphism, Inclusive Design | Nunito / Quicksand | 複雑なナビゲーション、小フォント |
| Gaming | Cyberpunk, 3D Hyperrealism, HUD | Rajdhani / Orbitron | 退屈なレイアウト |
| Developer Tools / Hardware | **Nothing / Monochrome Industrial** | Doto / Space Grotesk / Space Mono | Gradients, shadows, skeleton loaders |

---

## STACK GUIDELINES

| Stack | ポイント |
|---|---|
| HTML + Tailwind（デフォルト） | Semantic HTML5、utility-first、Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` |
| React / Next.js | shadcn/ui 推奨、`use client`/`use server` 適切な使い分け、`references/design-systems.md` 参照 |
| Vue / Nuxt | Composition API + `<script setup>`、Nuxt UI 推奨 |
| SwiftUI | System colors / Dynamic Type / SF Symbols |
| React Native | React Native Paper / Tamagui、`SafeAreaView` 使用 |
| Flutter | Material 3 / Cupertino、Theme data で一元管理 |

---

## VISUAL INPUT PREFERENCE

ユーザーがスクリーンショット・ワイヤーフレーム・ムードボードを提供している場合は、抽象的な言葉より視覚参照を優先してレイアウト・色・密度を判断する。不足していて品質に大きく影響する場合のみ、必要な視覚資料を提案する。

詳細は `references/vibe-coding.md` を参照。

---

## OUTPUT FORMATS

### デザインシステム提案フォーマット

新規UI設計やユーザーがデザイン方向の提案を求めた場合に使用。小規模修正・既存コンポーネント修正では必要な判断のみ内部適用し、このフォーマットの出力は省略する。

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN SYSTEM: [Project Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PATTERN:     [Landing Page Pattern]
STYLE:       [UI Style Name]
COLORS:
  Primary:    [hex] ([name])
  Secondary:  [hex] ([name])
  CTA:        [hex] ([name])
  Background: [hex] ([name])
  Text:       [hex] ([name])
TYPOGRAPHY:  [Heading Font] / [Body Font]
EFFECTS:     [animations, transitions]
AVOID:       [anti-patterns for this project]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## REFERENCES

- `references/styles-catalog.md` — 67スタイル完全一覧 + ダッシュボードスタイル
- `references/color-typography.md` — カラーパレット + フォントペアリング20選 + チャート推奨
- `references/components.md` — 60コンポーネントパターン（セマンティックHTML、ARIA、キーボードナビ、複雑度）
- `references/design-systems.md` — 95+プロダクションデザインシステム（スタック別索引、Best-in-Class一覧）
- `references/nothing-design.md` — Nothing Design System 完全仕様（哲学、トークン、コンポーネント、プラットフォーム対応）
- `references/vibe-coding.md` — AI UI生成のベストプラクティス（スケッチ優先、スクショ活用、ムードボード等）

---

> Source: [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) v2.2 をベースに Hallmark 原則を統合。
