# UI Decision Data

Use this file for quick implementation decisions that were represented as CSV lookup tables in the source material. It is not a full data dump; it keeps rules that change UI output.

## Product Routing

| Product Type | Primary Style | Landing Pattern | Dashboard Pattern | Key Risk |
|---|---|---|---|---|
| SaaS | Glassmorphism + flat/minimal | Hero + features + CTA | Data-dense + real-time | Generic hero without product proof |
| Micro SaaS | Flat + vibrant blocks | Minimal direct + demo | Executive summary | Too much process before value |
| E-commerce | Flat + product-forward | Product grid + trust + CTA | Sales intelligence | Weak purchase CTA |
| Healthcare | Accessible + soft UI | Trust + explanation + booking | Patient status | Low contrast or over-stimulation |
| Fintech | Minimal/glass/dark | Trust + security + CTA | Financial dashboard | Purple/pink AI look; unclear risk states |
| Education | Clay/inclusive | Problem + learning outcome + CTA | Progress dashboard | Childish treatment for adult learners |
| Developer tools | Minimal/terminal/Nothing | Product demo + docs + CTA | Real-time monitoring | Decorative terminal with no useful data |

## Landing Patterns

| Pattern | Section Order | Use When | Pitfall |
|---|---|---|---|
| Hero + Features + CTA | Hero, value prop, 3-5 features, CTA, footer | Simple SaaS/product | Features before proof |
| Hero + Testimonials + CTA | Hero, problem, solution, testimonials, CTA | Trust needs to be established | Fake/empty testimonial cards |
| Interactive Demo | Hero, live demo, use cases, CTA | Software/tools | Demo controls that do not work |
| Trust & Authority | Hero, credentials, process, proof, CTA | B2B, legal, health, finance | Decorative badges without substance |
| Minimal & Direct | Hero, product proof, pricing/CTA | Micro SaaS, utilities | Too sparse to answer objections |

## Chart Choice

| Data Need | Use | Do Not Use | Accessibility |
|---|---|---|---|
| Trend over time | Line or area | Pie/donut; line with >6 noisy series | Use labels and distinct line styles |
| Category comparison | Bar/column | Pie for ranked categories | Sort by value; show value labels |
| Part of whole | Donut/stacked/waffle | Pie with >6 segments | Provide data table fallback |
| Distribution | Box plot/histogram | Average-only KPI | Explain median/outliers |
| Flow | Sankey/funnel | Sankey for tiny datasets | Provide text summary |
| Single KPI | Stat card/gauge | Gauge for precise comparison | Include exact number and unit |

## Motion Rules

| Interaction | Duration | Property | Rule |
|---|---:|---|---|
| Button hover | 150-200ms | opacity/translate/scale | Keep displacement under 2px |
| Card hover | 200-300ms | transform/shadow | Reverse cleanly on pointer leave |
| Modal enter | 180-250ms | opacity/scale | Focus target after animation |
| Page transition | 250-400ms | opacity/translate | Respect `prefers-reduced-motion` |
| Loading | task-dependent | opacity/skeleton | Avoid fake progress if duration unknown |

## Accessibility and UX Rules

| Issue | Do | Don't | Severity |
|---|---|---|---|
| Icon-only button | Provide visible label or accessible name | Ship unlabeled icon buttons | Critical |
| Form control label | Pair input with label and accessible name | Placeholder-only forms | Critical |
| Smooth anchor navigation | Account for sticky nav offset | Let fixed nav hide target content | High |
| Mobile horizontal overflow | Measure `scrollWidth` against viewport | Hide overflow as the first move | High |
| Table on mobile | Fit 3-5 columns or card-stack 6+ columns | Force horizontal scroll | High |
| Interactive filters/tabs | Actually filter/switch content | Change only color state | High |
| Async data in React | Parallelize independent requests | Sequential await waterfall | Critical |
| Large lists | Virtualize or paginate | Render thousands of rows directly | High |

## Icon Selection

- Prefer the existing project icon library.
- Use icon-only buttons only for familiar actions and include labels/tooltips.
- For navigation: menu, arrow-left, chevron, search, close.
- For data/status: check, alert, info, clock, trend, filter.
- Do not mix icon families inside the same toolbar unless the design system already does.

## Decision Data Source

Derived from `app-interface.csv`, `charts.csv`, `landing.csv`, `motion.csv`, `products.csv`, `react-performance.csv`, `ui-reasoning.csv`, `ux-guidelines.csv`, and `icons.csv`.
