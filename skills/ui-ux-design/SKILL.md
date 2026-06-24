---
name: ui-ux-design
description: "Web/mobile UI の設計・実装・レビュー・改善で使用する。ランディングページ、ダッシュボード、デザインシステム、レスポンシブUI、ボタン・モーダル・フォーム等のコンポーネント実装に対応し、視覚階層・余白・色・タイポグラフィ・状態設計・アクセシビリティを補助する。React/Next.js/Tailwind/Vue/Svelte/HTML および Nothing 系UI参照に対応。67スタイル、96カラーパレット、59フォントペアリング、95+デザインシステム参照、60コンポーネントパターン収録。Use when user requests UI/UX work: design, build, create, implement, review, fix, improve web/mobile interfaces or UI components. Trigger phrases: ランディングページ, ダッシュボード, UI設計, フロントエンド, React, Tailwind, デザインシステム, カラーパレット, レスポンシブ, website, landing page, portfolio, SaaS, e-commerce, コンポーネント, accordion, modal, datepicker, drawer, button, tabs, dialog, form, tooltip, card, table, widget, Nothing style, Nothing design, monochrome industrial, モノクロ, きれい, デザイン感度, LP, UI作成, Swiss design, International Typographic Style, グリッドシステム, grid system, editorial, magazine layout, 雑誌風, Vignelli, Müller-Brockmann, ミュラー・ブロックマン, wayfinding, サイン計画, グリッド検証, baseline grid. 横スクロール, 横はみ出し, overscroll, ゴムのように揺れる, iOS Safari, touch-action, モバイル横ずれ, スライダーが動かない. File types: .html, .tsx, .jsx, .vue, .svelte."
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
| **Swiss / editorial / グリッド駆動 / identity** | 「Swiss design」「International Typographic Style」「雑誌風」「グリッドシステム」「Vignelli」「Müller-Brockmann」「グリッドが乗ってるか検証して」「wayfinding/サイン」 | `references/swiss-modernism.md` の規律に従う → `scripts/` でトークン/scaffold 生成 → `verify_grid.js` で 0px 検証 |
| **デザインシステム提案のみ** | 「デザインの方向性を」「色を決めて」 | DESIGN SYSTEM FORMAT で出力、コード生成不要 |
| **モバイルWeb 不具合（横はみ出し / 揺れ / タッチ）** | 「スマホで横に動く」「ゴムのように揺れる」「overscroll」「横スクロールできてしまう」「スライダー/つまみが動かず画面が動く」「iOS Safari」 | `references/mobile-web-pitfalls.md` に従う → まず実測で「DOM はみ出し」か「Safari バウンス」かを切り分け → 原因に応じて修正（推測で直さない） |

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
>
> **Swiss-modernism / International Typographic Style / editorial・magazine / Vignelli / Müller-Brockmann 選択時**（RULE PRECEDENCE 3 が適用）：`references/swiss-modernism.md` の規律に従う。原色1アクセント＋グロテスク書体＋flush-left＋厳格なグリッドを採用し、`scripts/vignelli_system.py`（トークン）/`scripts/grid_tokens.py`（グリッド scaffold）を使い、Web 実装は **subgrid bands・baseline ロック・display type の optical alignment** を実装したうえで `scripts/verify_grid.js` で 0px 遵守を検証する（「グリッドが乗っているか検証したい」要求の本命）。

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
- [ ] **日本語/CJKテキストの折り返し** — 和文は単語境界が無いため、放置すると「マットレ／ス」のように単語途中で改行される。**第一の対処はCSSでなくコピー**：体言止め・箇条書き・短文化で「そもそも折り返しが起きない文」にする（mybest等の優良比較サイトは改行が要るほど長い文を載せない＝短文はスキャン速度=CVRも上げる）。CSSは最小限に：本文に `word-break: auto-phrase; line-break: strict;`（文節折り返し）＋ `html, body { overflow-x: hidden }`（横スクロール安全弁）＋ 行をまたがせたくない短い強調語だけ `<strong class="nobr">…</strong>`＋`.nobr{white-space:nowrap}`。**`keep-all` は短ラベルのみに限定**（本文・表・英数字混じりに掛けると逆に横はみ出しを起こす）。`overflow-wrap` は `normal`（`break-word`/`anywhere` は英数字混じり語や `<b>` 強調句を途中で割る）。**アンチパターン：改行崩れをCSSの折り返し指定を積み増して直そうとすると、横スクロール等の副作用で悪化する。崩れたらまず「文を短くできないか」を先に問う**。検証は実機幅（375px）目視＋`b/strong/h*` の `getClientRects().length>1` 機械検出＋`document.documentElement.scrollWidth <= clientWidth`（横はみ出し0）
- [ ] **インタラクティブUIは必ず実際に機能させる** — タブ・フィルタ・診断・トグル等「押せそうに見える」要素は、見た目だけのダミーにしない。比較/レビューサイトでは動かないUIが「作りかけ」に見え、信頼を直接破壊する（装飾の不足より致命的）。JSなしでも CSS `:has()`（例 `.filter:has(#tab-x:checked) .item:not([data-x]){display:none}`）やラジオ+ラベルで実装でき、`:has()` 非対応の保険に最小JSを併設する。**検証：実際にクリックして対象だけ表示/絞り込みされるか（件数バッジと一致するか）を機械確認する。色が変わるだけ＝未完成**
- [ ] **テーブルはモバイルで横スクロールさせない** — 内容を読むのに横スクロールが要る表はUIの敗北（スキャンできない）。列数で出し分ける：**3〜5列**はセル文言を体言止めで短縮＋`min-width`撤廃＋`table-layout:fixed`＋**セル内のみ**`overflow-wrap:anywhere`で全列を画面内に収める（セル内縦折返しで吸収）。**6列以上**は360px幅に横並びで収めるのは物理的に不可能なので、`@media`で**縦積みカード化**（`thead`を視覚的に隠し、各`<td>`に`data-label`＋`td::before{content:attr(data-label)}`でラベル表示、`tr`をカード化）。**この方式はセル文言を一切変えず構造だけ変換できる**（規制チェック済みテキストを温存）。デスクトップ（≥641px）は通常テーブルを維持。タブ等のピル列も横スクロールより`flex-wrap:wrap`で全件2段表示が迷子防止に勝る。**検証：360/375/390pxで`scrollWidth<=clientWidth`（横はみ出し0）かつ全列/全項目が画面内に見えるか**

### DEFAULT VISUAL QUALITY（新規設計時の品質基準）

**視覚階層**
- フォントサイズに明確な段差（例: 48px / 24px / 16px / 14px）
- 見出しウェイト 700-900、本文 400-500
- CTA ボタンが画面内で最も目立つ要素

**スペーシング**
- 8px グリッド（8, 16, 24, 32, 48, 64, 96, 128px）
- セクション間余白: min 80px（モバイル）/ min 120px（デスクトップ）
- カード内パディング: 24px 以上
- **画面左右の余白（ガター）: モバイル min 20–24px / デスクトップ 24–32px**。文字・ボタンが画面端ギリギリだと窮屈で安っぽく見える。ヒーロー見出しが大きいほど余白を厚めに
- **ハマりどころ**: `.hero-inner` 等で `padding: 64px 0`（左右0）を指定すると、親 `.container` の左右 padding を上書きして**テキストが画面端にベタ付き**になる。上下だけ足すなら `padding-top/padding-bottom` を使い、左右ガターを潰さない。**実機で要素の左端 px を測って検証**

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

## 比較・レビュー・アフィリサイトの「密度」原則

「mybestよりショボい」と言われる原因は装飾不足ではなく**情報設計の不足**であることが多い。装飾を盛る前に次を満たす：

1. **商品カードは単一テンプレに完全規格化** — 全カードが同じ要素・同じ順序で並ぶ（1枚でもスコアや一言が欠けると「作りかけ」に見える）。「整って見える」の正体は規格化であって飾りではない。
2. **数値テーブルで根拠を見せる** — 印象語や星だけは薄い。スペック比較表＋仕様マトリクス（タイプ別特性・条件別目安）でスキャンできる根拠を出す。数値で語ると規制順守（医療・薬機法等）と「中立メディア」ブランドが両立する。
3. **スコアの配点を開示** — 「総合◯点」だけでは恣意的に見える。「体圧分散35%/…（当サイト調べ）」の1行で透明性を出す。評価軸の責任分離（監修=選び方／順位=編集部）も明示。
4. **星評価＋数値スコアの二重表示は冗長** — 連続量は「横バー＋素点数値＋レターグレード(A/B/C・色分け)」に一本化するのが最速でスキャンできる。レビュー件数が埋まらない（匿名・新規）なら星は外す。
5. **結論先出し＋簡易診断のダブル着地** — 「迷ったらこれ（結論）」と「あなた向けはこれ（診断）」の両入口。診断は CSS `:has()` でJSゼロ実装可。
6. まとめ＝**①押したら効く ②全部そろっている ③数値で根拠が見える ④読まなくてもスキャンできる**。装飾投資より情報設計投資。

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
| Portfolio / Creative | Motion-Driven, Brutalism, **Swiss-modernism** | Space Grotesk / Syne / Helvetica | ジェネリックテンプレート感 |
| Editorial / Publishing / News | **Swiss / International Typographic Style（Müller-Brockmann grid）** | Inter / Helvetica Now / Archivo ＋ mono | 装飾過多、justified本文、グリッド無視、warm-cream "Claude look" |
| Identity / Branding / Wayfinding | **Vignelli Canon（color as identifier）** | Helvetica（＋Bodoni/Garamond/Futura/Times の6基本書体） | 2サイズ超、新奇書体、装飾的な色 |
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
- `references/swiss-modernism.md` — Swiss / International Typographic Style 完全仕様（Vignelli Canon の規律＋Müller-Brockmann のモジュラーグリッド。subgrid bands・baseline ロック・optical alignment・0px グリッド検証まで）
- `references/vibe-coding.md` — AI UI生成のベストプラクティス（スケッチ優先、スクショ活用、ムードボード等）
- `references/mobile-web-pitfalls.md` — モバイルWeb の横はみ出し / iOS Safari 横バウンス / タッチ操作奪取の切り分け手順と対処（visualViewport 実測、100vw・min-width:0、overflow:clip が fixed に効かない件、`touch-action: pan-y pinch-zoom`。a11y を壊さず横揺れを止める）

### SCRIPTS（`references/swiss-modernism.md` から使用）

- `scripts/vignelli_system.py` — Vignelli Canon トークン生成（CSS/SCSS/JSON、原色パレット・2サイズスケール・5グリッド・罫・鉄道サイン）。ネットワーク/認証不要
- `scripts/grid_tokens.py` — Müller-Brockmann グリッド scaffold 生成（単一真実源の :root トークン、subgrid bands、グリッドオーバーレイ、optical-alignment JS、`--scaffold` で完結HTML）
- `scripts/verify_grid.js` — Puppeteer グリッド検証（列遵守・オーバーレイ一致・baseline・optical ink を複数幅で 0px assert）。Env: `CHROME`, `PUP`

---

> Source: [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) v2.2 をベースに Hallmark 原則を統合。Swiss-modernism（Vignelli Canon / Müller-Brockmann）は [hyperagent-public-skills](https://github.com/alexmcdonnell-airtable/hyperagent-public-skills) より統合（固有ツール参照は汎用化）。
