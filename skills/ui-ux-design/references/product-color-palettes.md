# Product Color Palettes

Use this file when a user asks for colors by product type, industry, or app category. Keep `color-typography.md` as the lightweight color theory guide; this file is the concrete token lookup.

## Palette Selection Rules

- Start from the nearest product type, then adapt to the user's existing brand colors.
- Preserve token roles: `primary`, `secondary`, `accent`, `background`, `foreground`, `card`, `muted`, `border`, `destructive`, `ring`.
- Use `accent` for action contrast, not decoration. If `primary` already dominates the UI, choose an accent from a different hue family.
- Check contrast after any modification. Source palettes were adjusted for practical WCAG contrast, but local backgrounds and opacity can break that.
- Prefer a smaller palette in implementation: primary, background, foreground, muted, accent, destructive.

## Core Web Products

| Product | Primary | Accent | Background | Foreground | Notes |
|---|---:|---:|---:|---:|---|
| SaaS general | `#2563EB` | `#EA580C` | `#F8FAFC` | `#1E293B` | Trust blue with orange CTA contrast |
| Micro SaaS | `#6366F1` | `#059669` | `#F5F3FF` | `#1E1B4B` | Indie/product-led, success accent |
| B2B service | `#0F172A` | `#0369A1` | `#F8FAFC` | `#020617` | Conservative navy, good for professional sites |
| Analytics dashboard | `#1E40AF` | `#D97706` | `#F8FAFC` | `#1E3A8A` | Blue data hierarchy with amber highlights |
| Financial dashboard | `#0F172A` | `#22C55E` | `#020617` | `#F8FAFC` | Dark surface with green positive indicators |
| AI/chatbot platform | `#7C3AED` | `#0891B2` | `#FAF5FF` | `#1E1B4B` | Purple + cyan; avoid generic AI gradient overuse |
| Developer tool / IDE | `#1E293B` | `#22C55E` | `#0F172A` | `#F8FAFC` | Code dark with run-state green |
| API developer portal | `#0F172A` | `#22C55E` | `#020617` | `#F8FAFC` | Endpoint/status semantics |
| Open source landing | `#0F172A` | `#A16207` | `#020617` | `#F8FAFC` | Star/fork/sponsor cues on dark |
| Cybersecurity platform | `#00FF41` | `#FF3333` | `#000000` | `#E0E0E0` | Use sparingly; strong theme signal |

## Commerce, Marketplace, Content

| Product | Primary | Accent | Background | Foreground | Notes |
|---|---:|---:|---:|---:|---|
| E-commerce | `#059669` | `#EA580C` | `#ECFDF5` | `#064E3B` | Purchase action contrast |
| E-commerce luxury | `#1C1917` | `#A16207` | `#FAFAF9` | `#0C0A09` | Black + gold, restrained surfaces |
| Marketplace P2P | `#7C3AED` | `#16A34A` | `#FAF5FF` | `#4C1D95` | Transaction green for trust |
| Auction platform | `#0F172A` | `#16A34A` | `#020617` | `#F8FAFC` | Bid green, outbid/destructive red |
| Digital products/downloads | `#6366F1` | `#16A34A` | `#EEF2FF` | `#312E81` | Buy/success emphasis |
| Creator economy | `#EC4899` | `#EA580C` | `#FDF2F8` | `#831843` | High-energy, use neutral whitespace |
| Newsletter platform | `#0369A1` | `#EA580C` | `#F0F9FF` | `#0C4A6E` | Subscribe action should stand apart |
| Magazine/blog | `#18181B` | `#EC4899` | `#FAFAFA` | `#09090B` | Editorial black plus single accent |
| News/media platform | `#DC2626` | `#1E40AF` | `#FEF2F2` | `#450A0A` | Breaking red with link blue |
| Review platform | `#F59E0B` | `#16A34A` | `#FFFBEB` | `#0F172A` | Star gold, positive/negative semantics |

## Health, Education, Public Service

| Product | Primary | Accent | Background | Foreground | Notes |
|---|---:|---:|---:|---:|---|
| Healthcare app | `#0891B2` | `#059669` | `#ECFEFF` | `#164E63` | Calm cyan with health green |
| Medical clinic | `#0891B2` | `#16A34A` | `#F0FDFA` | `#134E4A` | Clinical but not cold |
| Patient portal | `#0284C7` | `#16A34A` | `#F0F9FF` | `#0C4A6E` | Records, status, alert hierarchy |
| Telemedicine | `#0891B2` | `#16A34A` | `#F0FDFA` | `#134E4A` | Video/availability cues |
| Mental health | `#8B5CF6` | `#059669` | `#FAF5FF` | `#4C1D95` | Calming lavender, use motion lightly |
| Medication reminder | `#0284C7` | `#DC2626` | `#F0F9FF` | `#0F172A` | Alert red is functional only |
| Education app | `#4F46E5` | `#EA580C` | `#EEF2FF` | `#1E1B4B` | Playful but readable |
| E-learning/course | `#0D9488` | `#EA580C` | `#F0FDFA` | `#134E4A` | Progress teal, achievement orange |
| LMS | `#0D9488` | `#D97706` | `#F0FDFA` | `#134E4A` | Course/grade/chip semantics |
| Government portal | `#1E40AF` | `#16A34A` | `#EFF6FF` | `#1E3A8A` | Accessibility and high trust |

## Mobile Utility Apps

| Product | Primary | Accent | Background | Foreground | Notes |
|---|---:|---:|---:|---:|---|
| Chat/messaging | `#2563EB` | `#059669` | `#FFFFFF` | `#0F172A` | Online/available green |
| Notes/writing | `#78716C` | `#D97706` | `#FFFBEB` | `#0F172A` | Warm ink on paper |
| Habit tracker | `#D97706` | `#059669` | `#FFFBEB` | `#0F172A` | Streak + completion semantics |
| Calendar/scheduling | `#2563EB` | `#059669` | `#F8FAFC` | `#0F172A` | Availability green |
| Password manager | `#1E3A5F` | `#059669` | `#0F172A` | `#FFFFFF` | Secure dark, avoid playful accents |
| Scanner/document manager | `#1E293B` | `#2563EB` | `#F8FAFC` | `#0F172A` | Document neutral with scan blue |
| Translator | `#2563EB` | `#EA580C` | `#F8FAFC` | `#0F172A` | Global blue with action orange |
| Timer/Pomodoro | `#DC2626` | `#059669` | `#0F172A` | `#FFFFFF` | Focus/break state contrast |
| Weather | `#0284C7` | `#F59E0B` | `#F0F9FF` | `#0F172A` | Sky + sun semantics |
| VPN/privacy | `#1E3A5F` | `#22C55E` | `#0F172A` | `#FFFFFF` | Connected/secure green |

## Brand and Venue Types

| Product | Primary | Accent | Background | Foreground | Notes |
|---|---:|---:|---:|---:|---|
| Beauty/spa/wellness | `#EC4899` | `#8B5CF6` | `#FDF2F8` | `#831843` | Soft premium; avoid neon |
| Luxury/premium brand | `#1C1917` | `#A16207` | `#FAFAF9` | `#0C0A09` | Strong typography matters more than color count |
| Restaurant/food service | `#DC2626` | `#A16207` | `#FEF2F2` | `#450A0A` | Appetite red with warm gold |
| Bakery/cafe | `#92400E` | `#92400E` | `#FEF3C7` | `#78350F` | Warm, but avoid overusing cream/brown |
| Hotel/hospitality | `#1E3A8A` | `#A16207` | `#F8FAFC` | `#1E40AF` | Service navy and gold |
| Legal services | `#1E3A8A` | `#B45309` | `#F8FAFC` | `#0F172A` | Authority, avoid playful accents |
| Real estate/property | `#0F766E` | `#0369A1` | `#F0FDFA` | `#134E4A` | Trust teal and professional blue |
| Architecture/interior | `#171717` | `#A16207` | `#FFFFFF` | `#171717` | Minimal black; let imagery carry warmth |
| Museum/gallery | `#18181B` | `#18181B` | `#FAFAFA` | `#09090B` | Quiet neutral gallery system |
| Conference/symposium | `#1E3A5F` | `#A16207` | `#F8FAFC` | `#0F172A` | Institutional navy with track/keynote accent |

## Use in Tailwind/CSS

```css
:root {
  --color-primary: #2563eb;
  --color-on-primary: #ffffff;
  --color-accent: #ea580c;
  --color-background: #f8fafc;
  --color-foreground: #1e293b;
  --color-card: #ffffff;
  --color-muted: #e9eff8;
  --color-muted-foreground: #64748b;
  --color-border: #e2e8f0;
  --color-destructive: #dc2626;
  --color-ring: var(--color-primary);
}
```

## Palette Source

Derived from `ui-ux-pro-max/src/ui-ux-pro-max/data/colors.csv` (MIT, Next Level Builder). The original CSV contains 192 product-type palettes; this reference keeps representative UI-useful categories and token roles.
