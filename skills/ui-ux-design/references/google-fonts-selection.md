# Google Fonts Selection

Use this file when choosing fonts for a UI. It compresses the Google Fonts metadata table and the extended typography pairing table into practical decision rules.

## Font Selection Rules

- Prefer system fonts or already-installed project fonts for small fixes.
- Add a web font only when it changes brand character or materially improves readability.
- Limit to two families for most UI; three only when there is a clear display/body/mono split.
- Load only required weights. Start with `400`, `500`, `600`, `700`.
- For dashboards and tools, legibility beats novelty.
- For CJK/Japanese UI, verify glyph coverage and fallback behavior before relying on a Latin-centric pairing.

## Reliable UI Sans

| Font | Use For | Notes |
|---|---|---|
| Inter | SaaS, dashboards, general UI | Very common; add character elsewhere if it feels generic |
| Plus Jakarta Sans | Enterprise SaaS, admin, polished B2B | Professional, slightly warmer than Inter |
| DM Sans | Marketing UI, product pages, friendly apps | Good body face, pairs with expressive display |
| Manrope | Fintech, dashboards, B2B | Geometric and compact |
| Sora | Apps, education, approachable SaaS | Friendly, modern |
| Outfit | Geometric/Bauhaus-flavored UI | Works as single-family system |
| Space Grotesk | Portfolios, tech, brutalist/kinetic UI | Use carefully for dense body text |
| Public Sans | Government, civic, accessibility-forward UI | Neutral and practical |
| Roboto | Android/Material UI | Good default when matching platform norms |
| Source Sans 3 | Healthcare, public service, readable products | Calm and utilitarian |

## Display and Editorial Faces

| Font | Pair With | Use For |
|---|---|---|
| Playfair Display | Inter, Source Sans 3 | Luxury, editorial, beauty |
| Fraunces | Work Sans, Inter | Warm expressive brands |
| DM Serif Display | DM Sans | Classic-modern product pages |
| Cormorant Garamond | Montserrat, Source Sans 3 | Premium, wellness, academia |
| EB Garamond | Crimson Text | Academic, archival, literary |
| Calistoga | Inter | Boutique SaaS, warm product hero |
| Abril Fatface | Open Sans, Inter | Bold editorial headlines |
| Bebas Neue | Open Sans | Poster-like landing pages |
| Anton | Epilogue, Inter | Neo-brutal / Gen Z campaigns |
| Syncopate | Space Mono | Kinetic, automotive, music |

## Mono and Technical Faces

| Font | Use For | Notes |
|---|---|---|
| JetBrains Mono | Code, terminal, developer tools | Strong default for technical labels |
| Space Mono | Swiss/technical labels, editorial metadata | Distinctive, less code-editor-like |
| IBM Plex Mono | Data-heavy enterprise UI | Pairs well with IBM Plex Sans/Serif |
| Geist Mono | Modern developer tools | Good with Geist/Inter-like sans |
| DM Mono | Lightweight technical labels | Softer than JetBrains Mono |

## High-Value Pairings

| Pairing | Category | Best For |
|---|---|---|
| Inter + Inter | Sans + Sans | Clean SaaS and dashboards |
| Plus Jakarta Sans + Plus Jakarta Sans | Sans + Sans | Enterprise SaaS |
| Space Grotesk + DM Sans | Display Sans + Sans | Startups, portfolios |
| Playfair Display + Source Sans 3 | Serif + Sans | Luxury/editorial |
| Cormorant Garamond + Montserrat | Serif + Sans | Beauty/wellness |
| Fraunces + Work Sans | Serif + Sans | Nonprofit, artisan, warm brands |
| Bricolage Grotesque + Geist | Display Sans + Sans | AI/dev tools with character |
| Archivo + Inter | Sans + Sans | News, data-heavy publishing |
| JetBrains Mono + Inter | Mono + Sans | Developer tools |
| Doto + Space Grotesk | Display + Sans | Nothing/industrial style |
| EB Garamond + Crimson Text | Serif + Serif | Academic/archival |
| Syncopate + Space Mono | Display + Mono | Kinetic/futuristic |
| Orbitron + JetBrains Mono | Tech Display + Mono | Cyberpunk/HUD |
| Nunito + DM Sans | Rounded Display + Sans | Claymorphism, children/education |
| Kalam + Patrick Hand | Handwritten + Handwritten | Sketch/journaling, not dense UI |

## Avoid

- Loading every weight from Google Fonts for a single page.
- Using display fonts for body copy.
- Using low x-height serif body text in dashboards.
- Combining two highly expressive families.
- Relying on a Latin-only mood board for Japanese text.
- Using novelty fonts for labels, numbers, tables, or legal text.

## Font Data Source

Derived from `google-fonts.csv` and `typography.csv`. The original Google Fonts metadata table is too large for direct reference use, so this file keeps decision-ready families and pairings only.
