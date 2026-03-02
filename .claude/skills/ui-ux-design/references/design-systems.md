# Design System Reference — 95+ Production Systems

> コンポーネント実装時に参照すべきプロダクションデザインシステム一覧。テックスタック別に整理。

## Usage

1. ユーザーのテックスタックを特定
2. 該当セクションから最適なデザインシステムを選択
3. GitHub リポジトリの `src/components/{name}/` を参照
4. 複雑なコンポーネントは 2-3 のリファレンスを比較

---

## React + Tailwind CSS

| Design System | GitHub | Notes |
|---------------|--------|-------|
| **shadcn/ui** | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | Copy-paste コンポーネント、Radix UI ベース。Next.js との親和性高い |
| **HeroUI** | [heroui-inc/heroui](https://github.com/heroui-inc/heroui) | 旧 NextUI。Tailwind + React Aria |
| **Flowbite** | [themesberg/flowbite](https://github.com/themesberg/flowbite) | Tailwind ユーティリティベース |
| **Catalyst (Tailwind Labs)** | [tailwindlabs/catalyst](https://github.com/tailwindlabs/catalyst) | Tailwind 公式 UI キット、Headless UI ベース |
| **DaisyUI** | [saadeghi/daisyui](https://github.com/saadeghi/daisyui) | Tailwind プラグイン型。テーマ豊富 |
| **Park UI** | [cschroeter/park-ui](https://github.com/cschroeter/park-ui) | Ark UI + Tailwind / Panda CSS |

## React — Headless / Accessibility-First

| Design System | GitHub | Notes |
|---------------|--------|-------|
| **Radix UI** | [radix-ui/primitives](https://github.com/radix-ui/primitives) | ヘッドレスプリミティブ。shadcn/ui の基盤 |
| **Ariakit** | [ariakit/ariakit](https://github.com/ariakit/ariakit) | WAI-ARIA 準拠のヘッドレスコンポーネント |
| **React Aria (Adobe)** | [adobe/react-spectrum](https://github.com/adobe/react-spectrum) | アクセシビリティの金字塔。フック型 |
| **Headless UI** | [tailwindlabs/headlessui](https://github.com/tailwindlabs/headlessui) | Tailwind Labs 公式。React + Vue 対応 |
| **Ark UI** | [chakra-ui/ark](https://github.com/chakra-ui/ark) | Chakra チーム製ヘッドレス。State machine ベース |
| **Downshift** | [downshift-js/downshift](https://github.com/downshift-js/downshift) | Autocomplete / Select 特化 |

## React — Full-Featured

| Design System | GitHub | Company | Component Count |
|---------------|--------|---------|-----------------|
| **Chakra UI** | [chakra-ui/chakra-ui](https://github.com/chakra-ui/chakra-ui) | — | 50+ |
| **Ant Design** | [ant-design/ant-design](https://github.com/ant-design/ant-design) | Alibaba | 60+ |
| **Material UI (MUI)** | [mui/material-ui](https://github.com/mui/material-ui) | — | 50+ |
| **Mantine** | [mantinedev/mantine](https://github.com/mantinedev/mantine) | — | 100+ |
| **Fluent UI** | [microsoft/fluentui](https://github.com/microsoft/fluentui) | Microsoft | 60+ |
| **Carbon** | [carbon-design-system/carbon](https://github.com/carbon-design-system/carbon) | IBM | 40+ |
| **Polaris** | [Shopify/polaris](https://github.com/Shopify/polaris) | Shopify | 55+ |
| **Primer** | [primer](https://github.com/primer) | GitHub | 40+ |
| **Gestalt** | [pinterest/gestalt](https://github.com/pinterest/gestalt) | Pinterest | 50+ |
| **Base Web** | [uber/baseweb](https://github.com/uber/baseweb) | Uber | 55+ |
| **Blueprint** | [palantir/blueprint](https://github.com/palantir/blueprint) | Palantir | 40+ |
| **Evergreen** | [segmentio/evergreen](https://github.com/segmentio/evergreen) | Segment | 30+ |
| **Elastic UI** | [elastic/eui](https://github.com/elastic/eui) | Elastic | 60+ |
| **Ring UI** | [JetBrains/ring-ui](https://github.com/JetBrains/ring-ui) | JetBrains | 50+ |
| **Paste** | [twilio-labs/paste](https://github.com/twilio-labs/paste) | Twilio | 80+ |
| **Orbit** | [kiwicom/orbit](https://github.com/kiwicom/orbit) | Kiwi.com | 40+ |
| **Spark** | [adevinta/spark](https://github.com/adevinta/spark) | Adevinta | 40+ |

## Vue

| Design System | GitHub | Notes |
|---------------|--------|-------|
| **Quasar** | [quasarframework/quasar](https://github.com/quasarframework/quasar) | 70+ コンポーネント。SSR, PWA, Electron 対応 |
| **Vuetify** | [vuetifyjs/vuetify](https://github.com/vuetifyjs/vuetify) | Material Design 3 ベース |
| **Naive UI** | [tusen-ai/naive-ui](https://github.com/tusen-ai/naive-ui) | 80+ コンポーネント。TypeScript |
| **PrimeVue** | [primefaces/primevue](https://github.com/primefaces/primevue) | 90+ コンポーネント。テーマ豊富 |
| **Element Plus** | [element-plus/element-plus](https://github.com/element-plus/element-plus) | Vue 3 版 Element UI |
| **Headless UI** | [tailwindlabs/headlessui](https://github.com/tailwindlabs/headlessui) | Vue 対応あり |
| **Cedar** | [rei/rei-cedar](https://github.com/rei/rei-cedar) | REI アウトドアブランド |
| **Nuxt UI** | [nuxt/ui](https://github.com/nuxt/ui) | Nuxt 公式 UI ライブラリ |

## Web Components

| Design System | GitHub | Company |
|---------------|--------|---------|
| **Web Awesome (Shoelace)** | [shoelace-style/webawesome](https://github.com/shoelace-style/webawesome) | — |
| **Material Web** | [material-components/material-web](https://github.com/material-components/material-web) | Google |
| **Lion** | [ing-bank/lion](https://github.com/ing-bank/lion) | ING Bank |
| **Spectrum Web Components** | [adobe/spectrum-web-components](https://github.com/adobe/spectrum-web-components) | Adobe |
| **Red Hat Design System** | [RedHat-UX/red-hat-design-system](https://github.com/RedHat-UX/red-hat-design-system) | Red Hat |
| **Porsche Design System** | [porsche-design-system](https://github.com/porsche-design-system/porsche-design-system) | Porsche |
| **Clarity** | [vmware-clarity/ng-clarity](https://github.com/vmware-clarity/ng-clarity) | VMware |
| **Calcite** | [Esri/calcite-design-system](https://github.com/Esri/calcite-design-system) | Esri |
| **PatternFly** | [patternfly/patternfly-elements](https://github.com/patternfly/patternfly-elements) | Red Hat |

## Angular

| Design System | GitHub | Company |
|---------------|--------|---------|
| **Angular Material** | [angular/components](https://github.com/angular/components) | Google |
| **PrimeNG** | [primefaces/primeng](https://github.com/primefaces/primeng) | — |
| **Clarity** | [vmware-clarity/ng-clarity](https://github.com/vmware-clarity/ng-clarity) | VMware |
| **Taiga UI** | [taiga-family/taiga-ui](https://github.com/taiga-family/taiga-ui) | — |

## Svelte

| Design System | GitHub | Notes |
|---------------|--------|-------|
| **Skeleton** | [skeletonlabs/skeleton](https://github.com/skeletonlabs/skeleton) | Tailwind ベース |
| **Melt UI** | [melt-ui/melt-ui](https://github.com/melt-ui/melt-ui) | ヘッドレスプリミティブ |
| **Bits UI** | [huntabyte/bits-ui](https://github.com/huntabyte/bits-ui) | Melt UI ベースのコンポーネント |

---

## Component Lookup Strategy

コンポーネント実装時の参照順序：

```
1. ユーザーのスタック確認 → 対応セクション参照
2. ヘッドレスライブラリでアクセシビリティパターン確認
   - React: Radix UI / React Aria / Ariakit
   - Vue: Headless UI
   - Web Components: Lion / Shoelace
3. フルフィーチャーライブラリで UI パターン確認
   - 最低 2-3 実装を比較
4. component.gallery で横断検索
   → https://component.gallery/components/{slug}/
```

## Quick Reference: Best-in-Class by Component

特に優れた実装を持つデザインシステム（迷った時はこれを参照）：

| Component | Best Reference | Why |
|-----------|---------------|-----|
| Dialog / Modal | Radix UI, React Aria | Focus trap, Escape, overlay 管理が完璧 |
| Select / Combobox | Downshift, Ariakit | Edge case（検索、多言語、仮想スクロール）対応 |
| Date Picker | React Aria, Ant Design | カレンダーロジック + i18n + a11y |
| Data Table | Ant Design, Elastic UI, TanStack Table | ソート、フィルタ、仮想化、列リサイズ |
| Toast / Snackbar | Sonner, Mantine | スタック管理、自動消去、アクション付き |
| Accordion | Radix UI, Headless UI | アニメーション + キーボードナビ |
| Tabs | Radix UI, Chakra UI | 自動/手動アクティベーション、キーボード |
| Carousel | Embla Carousel | 軽量、タッチ対応、カスタマイズ性 |
| Form | React Hook Form + Zod | バリデーション、パフォーマンス、型安全 |
| Tree View | Blueprint, Elastic UI | 大規模データ、仮想化、ドラッグ&ドロップ |
