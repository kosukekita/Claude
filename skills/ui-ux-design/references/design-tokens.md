# Design Tokens

Use this file when creating or reviewing a design system, theme, or component token contract.

## Three-Layer Token Model

```
Primitive -> Semantic -> Component
```

- Primitive: raw values such as `--color-blue-600`, `--space-4`, `--radius-md`.
- Semantic: purpose aliases such as `--color-primary`, `--color-background`, `--color-danger`.
- Component: local decisions such as `--button-bg`, `--card-border`, `--input-ring`.

Do not bind components directly to primitive values unless the project has no token system yet.

## Minimum Token Set

```css
:root {
  --color-background: #ffffff;
  --color-foreground: #0f172a;
  --color-card: #ffffff;
  --color-card-foreground: #0f172a;
  --color-muted: #f1f5f9;
  --color-muted-foreground: #64748b;
  --color-primary: #2563eb;
  --color-primary-foreground: #ffffff;
  --color-secondary: #e2e8f0;
  --color-secondary-foreground: #0f172a;
  --color-accent: #ea580c;
  --color-accent-foreground: #ffffff;
  --color-destructive: #dc2626;
  --color-destructive-foreground: #ffffff;
  --color-border: #e2e8f0;
  --color-ring: #2563eb;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
}
```

## Component Token Pattern

| Component | Token | Default | Hover | Active | Disabled |
|---|---|---|---|---|---|
| Button | background | primary | primary-hover | primary-active | muted |
| Button | text | primary-foreground | primary-foreground | primary-foreground | muted-foreground |
| Button | border | transparent | transparent | transparent | border |
| Input | background | background | background | background | muted |
| Input | border | border | foreground | ring | border |
| Card | background | card | card | card | card |
| Card | border | border | border | border | border |
| Badge | background | muted | muted | muted | muted |

## Tailwind Integration

```js
export default {
  theme: {
    extend: {
      colors: {
        background: "var(--color-background)",
        foreground: "var(--color-foreground)",
        primary: "var(--color-primary)",
        accent: "var(--color-accent)",
        border: "var(--color-border)",
        ring: "var(--color-ring)"
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)"
      }
    }
  }
}
```

## Validation Checklist

- No hardcoded brand colors inside component files unless they define primitives.
- Every interactive component has hover, focus, active, disabled, loading, and error behavior where applicable.
- Focus ring token is visible on both light and dark surfaces.
- Semantic state colors are not reused for unrelated decoration.
- Dark mode is semantic-token swap, not duplicated component CSS.
- Spacing tokens follow an 8px base unless the project already uses another scale.
- Component tokens map to user-facing state, not implementation detail.

## Token Source

Derived from the source `design-system` subskill token references. Slide-generation material was intentionally excluded as out of scope for this UI/UX skill.
