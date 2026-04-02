# UI Component Catalog — 60 Patterns

> Source: [component.gallery](https://component.gallery/) を参考に、プロダクション実績のある60コンポーネントパターンを整理。

## Usage

ユーザーのリクエストからコンポーネント名を特定 → **Aliases** で表記揺れを吸収 → 該当パターンの実装ガイドに従う。

---

## Navigation & Structure

| Component | Aliases | Semantic HTML | Key ARIA |
|-----------|---------|---------------|----------|
| **Accordion** | Collapsible, Expandable, Disclosure | `<details>/<summary>` | `aria-expanded`, `aria-controls` |
| **Breadcrumb** | Breadcrumbs, Path | `<nav aria-label="Breadcrumb">` | `aria-current="page"` |
| **Drawer** | Side Panel, Sidebar, Sheet | `<dialog>`, `<aside>` | `aria-modal`, focus trap |
| **Mega Menu** | Dropdown Nav | `<nav>` + nested `<ul>` | `aria-haspopup`, `aria-expanded` |
| **Navigation** | Navbar, Header Nav, Top Bar | `<nav>` | `aria-label`, `aria-current` |
| **Pagination** | Pager | `<nav aria-label="Pagination">` | `aria-current="page"` |
| **Sidebar** | Side Nav, Rail | `<aside>` + `<nav>` | `aria-label` |
| **Stepper** | Wizard, Multi-step, Progress Steps | `<ol>` | `aria-current="step"` |
| **Tabs** | Tab Bar, Segmented Control | `<div role="tablist">` | `role="tab"`, `aria-selected` |
| **Tree View** | Tree, File Explorer | `<ul role="tree">` | `role="treeitem"`, `aria-expanded` |

## Data Display

| Component | Aliases | Semantic HTML | Key ARIA |
|-----------|---------|---------------|----------|
| **Avatar** | Profile Image, User Icon | `<img>` + fallback | `alt` text |
| **Badge** | Tag, Chip, Label, Pill | `<span>` | `role="status"` if dynamic |
| **Card** | Tile, Panel | `<article>` or `<div>` | — |
| **Carousel** | Slider, Slideshow, Swiper | `<div role="region">` | `aria-roledescription="carousel"`, `aria-label` |
| **Data Table** | Grid, DataGrid | `<table>` | `role="grid"`, `aria-sort` |
| **Description List** | Key-Value, Definition List | `<dl>/<dt>/<dd>` | — |
| **Empty State** | No Data, Zero State, Blank Slate | `<div>` | — |
| **Feed** | Activity Feed, Timeline | `<div role="feed">` | `aria-busy`, `aria-setsize` |
| **Icon** | Symbol, Glyph | `<svg>` | `aria-hidden="true"` (decorative), `role="img"` + `aria-label` (semantic) |
| **List** | Item List | `<ul>/<ol>` | — |
| **Stat** | Metric, KPI, Number | `<div>` | `role="status"` if live |
| **Table** | Simple Table | `<table>` | `<caption>`, `scope` |
| **Timeline** | History, Activity Log | `<ol>` | — |

## Forms & Input

| Component | Aliases | Semantic HTML | Key ARIA |
|-----------|---------|---------------|----------|
| **Autocomplete** | Combobox, Typeahead, Search Input | `<input>` + `<datalist>` | `role="combobox"`, `aria-autocomplete` |
| **Checkbox** | Check, Toggle Check | `<input type="checkbox">` | `aria-checked` |
| **Color Picker** | Color Selector | `<input type="color">` | `aria-label` |
| **Date Picker** | Calendar Input, Date Selector | `<input type="date">` or custom | `role="dialog"` for popup |
| **File Upload** | Dropzone, File Input | `<input type="file">` | `aria-describedby` |
| **Form** | Form Group, Form Layout | `<form>` | `aria-describedby` for errors |
| **Input** | Text Field, Text Input | `<input>` + `<label>` | `aria-invalid`, `aria-describedby` |
| **OTP Input** | Verification Code, PIN Input | `<input>` group | `aria-label` per digit |
| **Radio** | Radio Button, Radio Group | `<fieldset>` + `<input type="radio">` | `role="radiogroup"` |
| **Range Slider** | Slider, Range | `<input type="range">` | `aria-valuemin/max/now` |
| **Rating** | Star Rating, Review Score | `<fieldset>` + radio | `aria-label` |
| **Select** | Dropdown, Listbox, Picker | `<select>` or custom | `role="listbox"`, `aria-selected` |
| **Switch** | Toggle | `<input type="checkbox" role="switch">` | `role="switch"`, `aria-checked` |
| **Textarea** | Multi-line Input | `<textarea>` + `<label>` | `aria-invalid` |
| **Time Picker** | Time Select | `<input type="time">` | `aria-label` |

## Feedback & Overlay

| Component | Aliases | Semantic HTML | Key ARIA |
|-----------|---------|---------------|----------|
| **Alert** | Banner, Notification Bar, Callout | `<div role="alert">` | `role="alert"`, `aria-live="assertive"` |
| **Alert Dialog** | Confirm Dialog | `<dialog>` | `role="alertdialog"`, focus trap |
| **Dialog** | Modal, Popup, Lightbox | `<dialog>` | `aria-modal="true"`, focus trap, Escape close |
| **Popover** | Popup, Floating Panel | `<div>` + Popover API | `aria-haspopup`, `aria-expanded` |
| **Progress** | Progress Bar, Loading Bar | `<progress>` | `aria-valuenow/min/max` |
| **Skeleton** | Placeholder, Shimmer | `<div>` | `aria-busy="true"`, `aria-label` |
| **Snackbar** | Toast, Notification | `<div role="status">` | `aria-live="polite"` |
| **Spinner** | Loader, Loading Indicator | `<div>` | `role="status"`, `aria-label="Loading"` |
| **Tooltip** | Hint, Info Tip | `<div role="tooltip">` | `aria-describedby` |

## Actions

| Component | Aliases | Semantic HTML | Key ARIA |
|-----------|---------|---------------|----------|
| **Button** | CTA, Action | `<button>` | `aria-disabled`, `aria-busy` |
| **Button Group** | Toolbar, Action Bar | `<div role="toolbar">` | `role="toolbar"`, arrow key nav |
| **Copy Button** | Copy to Clipboard | `<button>` | `aria-label`, status feedback |
| **Dropdown Menu** | Context Menu, Action Menu | `<div role="menu">` | `role="menu"`, `role="menuitem"` |
| **FAB** | Floating Action Button | `<button>` | `aria-label` |
| **Link** | Anchor, Hyperlink | `<a>` | `aria-current` if active |
| **Split Button** | Button + Dropdown | `<button>` + `<div role="menu">` | `aria-haspopup`, `aria-expanded` |

## Layout & Container

| Component | Aliases | Semantic HTML | Key ARIA |
|-----------|---------|---------------|----------|
| **Aspect Ratio** | Ratio Box | `<div>` | — |
| **Container** | Wrapper, Content Area | `<div>` / `<main>` | — |
| **Divider** | Separator, HR | `<hr>` | `role="separator"` |
| **Grid** | Layout Grid | `<div>` (CSS Grid) | — |
| **Resizable** | Split Pane, Resize Handle | `<div>` | `role="separator"`, `aria-valuenow` |
| **Scroll Area** | Scrollable, Overflow Container | `<div>` | `tabindex="0"`, `role="region"` |
| **Stack** | VStack, HStack, Flex | `<div>` (Flexbox) | — |

---

## Keyboard Navigation Patterns

### Arrow Key Navigation
Tabs, Menu, Radio Group, Tree View, Toolbar

### Enter/Space Activation
Button, Checkbox, Link, Switch, Accordion

### Escape to Close
Dialog, Drawer, Popover, Tooltip, Dropdown Menu

### Tab to Navigate
Form fields, Card groups, General page navigation

---

## Component Complexity Tiers

実装時の見積もり参考：

| Tier | Components | Notes |
|------|-----------|-------|
| **Simple** | Button, Badge, Avatar, Icon, Divider, Link, Input, Alert | 単一要素、状態管理最小 |
| **Medium** | Card, Tabs, Accordion, Switch, Select, Tooltip, Popover, Toast | 状態管理あり、ARIA必須 |
| **Complex** | Dialog, Drawer, Data Table, Carousel, Date Picker, Autocomplete, Tree View, Stepper | Focus trap、複雑なキーボードナビ、状態管理多数 |

---

## Nothing Style Component Overrides

Nothing / Monochrome Industrial スタイル選択時、以下のコンポーネント仕様が通常のスタイリングに **優先** する。
完全なトークン値とコンポーネント仕様は `references/nothing-design.md` を参照。

| Component | Nothing Override |
|-----------|----------------|
| **Button** | Pill (999px radius), Space Mono ALL CAPS 13px, 0.06em spacing. Primary=inverted, Secondary=outline, Ghost=no border |
| **Card** | `--surface` bg, 12-16px radius, 1px border, NO shadows. Flat surfaces only |
| **Input** | Underline-preferred (bottom border only). Space Mono for data entry text |
| **Table** | Space Mono for numbers, right-aligned. No zebra striping. Active row: left 2px accent bar |
| **Progress** | Segmented discrete blocks (signature pattern). Square-ended, 2px gaps, status-colored |
| **Navigation** | Space Mono ALL CAPS labels. Bracket `[ HOME ]` or pipe `HOME | INFO` style |
| **Tags/Chips** | Pill or 4px radius, 1px border, Space Mono ALL CAPS caption size |
| **Toast/Snackbar** | **BANNED**. Use inline `[SAVED]` / `[ERROR: ...]` text instead |
| **Skeleton** | **BANNED**. Use `[LOADING...]` text or segmented spinner |
| **Dialog** | No shadows. `rgba(0,0,0,0.8)` backdrop, `--surface` + border, max 480px |
