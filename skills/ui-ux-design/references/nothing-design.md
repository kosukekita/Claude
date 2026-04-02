# Nothing Design System — Complete Reference

> Source: [nothing-design-skill](https://github.com/dominikmartn/nothing-design-skill) v3.0.0 (MIT License)
> Style #50 in styles-catalog.md. Use when "Nothing style" / "Monochrome Industrial" is selected.

---

## 1. PHILOSOPHY

6つの基本原則:

1. **Subtract, don't add** — すべてのピクセルに存在理由が必要
2. **Type drives hierarchy** — 色や装飾ではなく、タイポグラフィで階層を表現
3. **Dark and light modes are equals** — ライトモードはダークの派生ではなく、同等のファーストクラス
4. **Structure is ornament** — グリッドとデータ関係を露出させる。装飾は構造そのもの
5. **Restraint signals confidence** — 控えめさが信頼を生む
6. **Precision over personality** — 個性より精密さ

---

## 2. CRAFT RULES

### 2.1 Three-Layer Rule

すべての画面に正確に3つの重要度レベル:

| Layer | Role | Typography | Size |
|-------|------|-----------|------|
| **Primary** | ヒーロー要素（1つのみ） | Large display type | 48–96px |
| **Secondary** | 補足コンテキスト | Body / subheading | Tight spacing |
| **Tertiary** | メタデータ、システム情報 | ALL CAPS monospace | Faded, edges |

### 2.2 Font Discipline

画面あたりの最大制約:
- **2 font families** (Space Grotesk + Space Mono; Doto はヒーロー限定)
- **3 font sizes**
- **2 weights**

### 2.3 Spacing as Meaning

```
4–8px    = グループ化された要素
16px     = 同じグループ内の異なるアイテム
32–48px  = 新しいセクション
64–96px  = 新しいコンテキスト
```

### 2.4 Color as Hierarchy

- 色でコンテンツを飾らない — テキストの明度（opacity）で階層を表現
- Red (#D71921) はシグナルとしてのみ使用（装飾禁止）
- インタラクティブ要素は #007AFF (dark) / #5B9BF6 (light)

### 2.5 Compositional Balance

- 要素は左上揃え（centered layouts を避ける）
- ホワイトスペースは意図的に — 余白は「空き」ではなく「構造」
- グリッドは 4/8/12 カラム、ガター 16–24px

### 2.6 The Nothing Vibe

- 計器的（Instrumental） — ダッシュボード、コントロールパネルの美学
- 工業的（Industrial） — 機械のインターフェースのような精密さ
- ドットマトリクスモチーフ — Nothing Phone のグリフインターフェースからの引用

---

## 3. TOKENS

### 3.1 Typography

**Font Stack:**

| Role | Primary | Fallback |
|------|---------|----------|
| Display | Doto (400–700, variable dot-size) | Space Mono |
| Body / UI | Space Grotesk (300, 400, 500, 700) | DM Sans |
| Data / Labels | Space Mono (400, 700) | JetBrains Mono |

**Google Fonts:**
```
https://fonts.googleapis.com/css2?family=Doto:wght@400;700&family=Space+Grotesk:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap
```

**Type Scale (9 levels):**

| Token | Size | Line Height | Tracking | Notes |
|-------|------|-------------|----------|-------|
| `--display-xl` | 72px | 1.0 | -0.03em | Doto only |
| `--display-lg` | 48px | 1.05 | -0.02em | Doto or Space Grotesk |
| `--display-md` | 36px | 1.1 | -0.02em | |
| `--heading` | 24px | 1.2 | -0.01em | |
| `--subheading` | 18px | 1.3 | 0em | |
| `--body` | 16px | 1.5 | 0em | Default |
| `--body-sm` | 14px | 1.5 | 0.01em | |
| `--caption` | 12px | 1.4 | 0.04em | |
| `--label` | 11px | 1.2 | 0.08em | ALL CAPS, monospace |

**Typographic Rules:**
- 数値は常に Space Mono（等幅で桁揃え）
- ラベル・カテゴリは ALL CAPS + letter-spacing 0.06–0.08em
- 本文の最大幅: 65ch

### 3.2 Color System

**Dark Mode:**

| Token | Hex | Role |
|-------|-----|------|
| `--black` | #000000 | Primary background |
| `--surface` | #111111 | Card / panel background |
| `--surface-raised` | #1A1A1A | Elevated surface |
| `--border` | #222222 | Decorative border |
| `--border-visible` | #333333 | Intentional border |
| `--text-disabled` | #666666 | Disabled text (4.0:1) |
| `--text-secondary` | #999999 | Secondary text (6.3:1) |
| `--text-primary` | #E8E8E8 | Primary text (16.5:1) |
| `--text-display` | #FFFFFF | Display text (21:1) |

**Light Mode:**

| Token | Hex | Role |
|-------|-----|------|
| `--black` | #F5F5F5 | Primary background |
| `--surface` | #FFFFFF | Card / panel background |
| `--surface-raised` | #F0F0F0 | Elevated surface |
| `--border` | #E0E0E0 | Decorative border |
| `--border-visible` | #CCCCCC | Intentional border |
| `--text-disabled` | #999999 | Disabled text |
| `--text-secondary` | #666666 | Secondary text |
| `--text-primary` | #333333 | Primary text |
| `--text-display` | #000000 | Display text |

**Accent & Status (both modes):**

| Token | Hex | Usage |
|-------|-----|-------|
| `--accent` | #D71921 | Urgent, destructive, active |
| `--accent-subtle` | rgba(215,25,33,0.15) | Accent background |
| `--success` | #4A9E5C | Positive status |
| `--warning` | #D4A843 | Warning status |
| `--error` | #D71921 | Error (shares accent) |
| `--info` | #999999 | Informational |
| `--interactive` | #007AFF (dark) / #5B9BF6 (light) | Links, interactive |

### 3.3 Spacing (8px base)

| Token | Value |
|-------|-------|
| `--space-2xs` | 2px |
| `--space-xs` | 4px |
| `--space-sm` | 8px |
| `--space-md` | 16px |
| `--space-lg` | 24px |
| `--space-xl` | 32px |
| `--space-2xl` | 48px |
| `--space-3xl` | 64px |
| `--space-4xl` | 96px |

### 3.4 Motion & Interaction

- **Duration:** 150–250ms (micro), 300–400ms (transitions)
- **Easing:** `cubic-bezier(0.25, 0.1, 0.25, 1)` — ease-out, no bounce
- **Hover:** borders/text の明度変更のみ（scale や shadow は使わない）
- **Opacity > Position:** 表示切り替えはフェードを優先

### 3.5 Iconography

- Monoline, 1.5px stroke
- 24×24 base (20×20 live area)
- Round caps and joins
- テキスト色を継承（`currentColor`）
- 最大 5–6 strokes per icon
- **推奨:** Lucide (default) or Phosphor (thin weights)

### 3.6 Dot-Matrix Motif (Signature Element)

```css
.dot-grid {
  background-image: radial-gradient(circle, var(--border-visible) 1px, transparent 1px);
  background-size: 16px 16px;
}

.dot-grid-subtle {
  background-image: radial-gradient(circle, var(--border) 0.5px, transparent 0.5px);
  background-size: 12px 12px;
}
```

装飾的背景・セクション区切り・空白エリアの質感付けに使用。

---

## 4. COMPONENTS

### Cards & Surfaces
- Borderless with divider separation
- Border-radius: 12–16px (standard), 8px (compact), 4px (technical)
- Padding: 16–24px
- **NO shadows** — 1px border + surface color で区別

### Buttons
| Variant | Style |
|---------|-------|
| Primary | Inverted (white on black / black on white) |
| Secondary | 1px border outline |
| Ghost | No border, text only |
| Destructive | accent color fill |

共通: **Pill shape (999px radius)**, Space Mono 13px ALL CAPS, letter-spacing 0.06em, padding 12px/24px, min-height 44px

### Input Fields
- **Underline-preferred** (bottom border only) or full-border
- Labels: ALL CAPS, `--caption` size
- Focus: border transitions to `--text-primary`
- Error: border shifts to `--accent`
- Data entry text: Space Mono

### Lists & Data Rows
- Full-width dividers (1px `--border`)
- Left-aligned labels, right-aligned values
- Hierarchical indentation: 16–24px per level

### Tables
- Space Mono for numbers, Space Grotesk for text
- Numbers right-aligned
- No zebra striping
- Active row: left 2px solid `--accent` indicator
- Header: ALL CAPS `--label` size

### Navigation
- Mobile: bottom bar
- Desktop: horizontal text links
- Active state: ALL CAPS Space Mono + dot or underline indicator
- Style: bracket `[ HOME ]` or pipe `HOME | INFO` patterns

### Tags & Chips
- Bordered pills or technical squares (4px radius)
- 1px border, minimal padding (4px/12px)
- ALL CAPS, `--caption` or `--label` size

### Segmented Controls
- 2–4 segments maximum
- Active: inverted colors
- Transition: 200ms ease-out

### Progress Bars (Signature Component)
- **Discrete rectangular blocks** with 2px gaps (NOT continuous bars)
- Status-color fills (success/warning/accent)
- Paired numeric readout (e.g., "74%")
- States: neutral, over-limit (accent), good (success), moderate (warning)

### Widgets & Metrics
- Large left-aligned metric value (display type)
- Category label above (ALL CAPS, `--label`)
- Instrumental gauge motifs

### Overlays & Dialogs
- Backdrop: `rgba(0, 0, 0, 0.8)` (dark) / `rgba(0, 0, 0, 0.5)` (light)
- Centered modal, max-width 480px
- `--surface` background + `--border-visible` border
- **NO shadows, NO blur**
- Bottom sheets: drag-to-dismiss

---

## 5. ANTI-PATTERNS

以下は Nothing スタイル選択時に **絶対禁止**:

| Banned | 代替 |
|--------|------|
| Gradients | Flat solid colors |
| Shadows (box-shadow, drop-shadow) | 1px borders |
| Blur effects (backdrop-filter) | Solid opacity backgrounds |
| Skeleton screens | `[LOADING...]` text or segmented spinner |
| Toast popups | Inline status text `[SAVED]` / `[ERROR: ...]` |
| Emojis as icons | SVG icons (Lucide/Phosphor) |
| Parallax scrolling | Static or fade transitions |
| Spring / bounce easing | `cubic-bezier(0.25, 0.1, 0.25, 1)` |
| Border-radius >16px on cards | 12–16px max |
| Sad/happy illustrations | Typography and data only |
| Purple/pink AI gradients | Monochrome palette |

---

## 6. PLATFORM MAPPING

### 6.1 HTML / CSS

CSS Custom Properties で全トークンを定義:

```css
:root {
  /* Typography */
  --font-display: 'Doto', 'Space Mono', monospace;
  --font-body: 'Space Grotesk', 'DM Sans', sans-serif;
  --font-data: 'Space Mono', 'JetBrains Mono', monospace;

  /* Apply dark or light mode tokens here */
}
```

- `rem` for typography, `px` for spacing and borders
- `prefers-color-scheme` media query or `.theme-dark` / `.theme-light` class toggle

### 6.2 SwiftUI / iOS

```swift
extension Color {
    static let surface = Color(hex: "111111")
    static let textPrimary = Color(hex: "E8E8E8")
    static let accent = Color(hex: "D71921")
    // ...
}
```

- `@Environment(\.colorScheme)` for appearance mode
- Register Doto, Space Grotesk, Space Mono in Info.plist
- SF Symbols は Nothing スタイルに不適合 — カスタムアイコンを使用

### 6.3 React / Tailwind

Tailwind config で Nothing トークンをマッピング:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'nothing-surface': '#111111',
        'nothing-border': '#222222',
        'nothing-border-visible': '#333333',
        'nothing-text-secondary': '#999999',
        'nothing-text-primary': '#E8E8E8',
        'nothing-accent': '#D71921',
      },
      fontFamily: {
        display: ['Doto', 'Space Mono', 'monospace'],
        body: ['Space Grotesk', 'DM Sans', 'sans-serif'],
        data: ['Space Mono', 'JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'nothing': '12px',
        'nothing-compact': '8px',
        'nothing-technical': '4px',
        'nothing-pill': '999px',
      },
    },
  },
}
```

---

## 7. WORKFLOW (Nothing-specific)

Nothing スタイルが選択された場合の実装フロー:

1. **Google Fonts を宣言** — Doto + Space Grotesk + Space Mono
2. **Dark / Light を選択** — ユーザーの指定 or デフォルト Dark
3. **Three-Layer Hierarchy を設計** — Primary / Secondary / Tertiary を決定
4. **Craft Rules を適用** — Font Discipline、Spacing as Meaning
5. **トークン値を参照** — このファイルの Section 3 から正確な値を使用
6. **コンポーネントを構築** — Section 4 のパターンに従う
7. **Anti-patterns を検証** — Section 5 の禁止リストを最終チェック
