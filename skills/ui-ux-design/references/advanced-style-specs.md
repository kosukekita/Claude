# Advanced Style Specs

Use this file when `styles-catalog.md` names a style but the implementation needs concrete visual rules. This is a compressed reference from the large design catalog; it is intentionally selective.

## Inclusion Rules

- Include styles that affect UI implementation: layout, type scale, surfaces, motion, accessibility, component treatment.
- Exclude backup duplicates and long prose examples.
- Prefer concrete do/don't rules over aesthetic description.

## Bauhaus

- Composition: geometric primitives, asymmetric balance, visible grid tension.
- Palette: primary red, blue, yellow plus black/white. Avoid muddy secondary palettes.
- Typography: geometric sans, heavy uppercase for headings, short labels.
- Layout: strong diagonals, circles/squares/triangles as structural devices, not decoration only.
- Best for: design-forward landing pages, culture apps, creative tools, product launches.
- Avoid for: compliance-heavy dashboards, enterprise admin, long-form reading.

## Monochrome

- Composition: hierarchy comes from size, spacing, weight, and contrast, not hue.
- Palette: black, white, greys. Add one signal color only if the task needs state/action.
- Typography: editorial or Swiss; tighten display type, keep body readable.
- Surfaces: borders and whitespace over shadows.
- Best for: portfolios, galleries, luxury, technical products.
- Risk: if everything is the same grey, the UI becomes flat and slow to scan.

## Modern Dark

- Backgrounds: use layered near-black values (`#020203`, `#050506`, `#0A0A0C`) instead of one black.
- Text: primary near-white, secondary cool grey.
- Accent: one saturated accent for active state or CTA; do not paint every card edge.
- Components: subtle borders, low-opacity surfaces, no heavy blur by default.
- Accessibility: verify muted text; dark UIs often fail on secondary labels.

## SaaS Boutique

- Character: polished, confident, minimal, but not generic.
- Typography: display serif or distinctive display face for hero; neutral sans for UI.
- Layout: product screenshot or live UI should be first-viewport evidence.
- Motion: micro-interactions, not continuous background animation.
- CTA: one primary action, visible early, with accent contrast.

## Terminal / CLI

- Palette: near-black background, mono text, green/amber/red for command status.
- Typography: monospace only when the content benefits from code/data character.
- Components: ASCII-like dividers, command rows, status chips, log density.
- Avoid: fake hacker clutter, illegible green-on-black body copy, animated noise.

## Kinetic / Motion-Driven

- Motion is part of hierarchy: entrance, state change, and continuity should clarify intent.
- Use transforms and opacity. Avoid animating layout properties.
- Always provide `prefers-reduced-motion`.
- Keep hover movement small for productivity UI; reserve large motion for brand/portfolio pages.

## Flat Design

- Hierarchy: color blocks, type weight, icon clarity, spacing.
- Components: no decorative depth; rely on clear states and direct labels.
- Accessibility: active/focus/disabled states must be explicit because depth cues are absent.
- Best for: cross-platform apps, dashboards, icon-heavy interfaces.

## Material Design / Material You

- Use semantic surfaces, tonal palettes, and state layers.
- Respect platform expectations on Android; do not mix Material density with unrelated web card styling.
- Components should expose state: hover, pressed, focus, selected, disabled.
- Use Roboto/system scale only if it fits the product; otherwise keep Material principles, not necessarily Material typography.

## Neo Brutalism

- Visual language: thick borders, hard shadows, high contrast, loud color, intentional imbalance.
- Typography: bold geometric sans; avoid thin weights.
- Interaction: hard shadow shifts or pressed offsets.
- Best for: youth culture, creative tools, campaigns.
- Avoid for: healthcare, finance, government, dense forms.

## Bold Typography

- Type is the primary visual asset. Use a strong ratio between hero and body.
- Keep copy short; long lines ruin the style.
- Use underline bars, labels, or mono captions for structure.
- Avoid using every heading at display scale. Reserve the largest size for one moment.

## Academia

- Palette: parchment, ink, mahogany, brass, deep green or navy.
- Typography: serif-first, optionally engraved small caps for labels.
- Layout: generous margins, footnote-like metadata, long-form rhythm.
- Accessibility: many academic palettes are low contrast; test before shipping.

## Cyberpunk

- Palette: dark base with cyan/magenta/green signals.
- Shape: chamfered panels, HUD lines, dense status readouts.
- Typography: display tech face for headings, mono for data.
- Avoid: neon everywhere, glitch text in body copy, low-contrast magenta text.

## Claymorphism

- Surfaces: rounded, tactile, soft shadows, pastel blocks.
- Typography: rounded display for headings, clean sans for body.
- Best for: education, children, playful onboarding, creative apps.
- Risk: low contrast and oversized corners can make controls feel imprecise.

## Enterprise

- Palette: navy/slate/blue with restrained success/warning/destructive states.
- Layout: dense but calm; prioritize tables, filters, state summaries, auditability.
- Typography: neutral sans, predictable scales, no expressive display type.
- Components: clear affordance, keyboard support, visible loading/error/empty states.

## Sketch / Hand-Drawn

- Use for prototype, education, journaling, or creative contexts.
- Keep hand-drawn effects away from legal/financial/data-critical content.
- Pair playful headings with legible body text.
- Do not fake roughness with unreadable labels.

## Neumorphism

- Background and surfaces must share a material family.
- Shadows: paired light/dark shadows; avoid black shadows.
- Inputs should look inset; buttons/cards can be raised.
- Accessibility: contrast is the main failure mode. Use strong text color and visible focus.
- Avoid for data-heavy UI and critical workflows.

## Style Data Source

Derived from `ui-ux-pro-max/src/ui-ux-pro-max/data/design.csv`. `draft.csv` was treated as a backup duplicate and not imported.
