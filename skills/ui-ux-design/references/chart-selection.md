# Chart Selection

Use this file to pick the right chart for a given data shape, then set the render technology, colors, accessibility grade, and interaction level correctly. Each entry preserves the SVG/Canvas volume threshold, exact hex color guidance, recommended libraries, accessibility grade with its mandatory fallback, and the intended interactive level from the source data. Entries are grouped by Data Type. Accessibility grades run AAA (best) to D (fundamentally inaccessible — never use as the sole representation).

## Quick Index

| No | Data Type | Best Chart | A11y Grade | Interactive Level |
|---|---|---|---|---|
| 1 | Trend Over Time | Line Chart | AA | Hover + Zoom |
| 2 | Compare Categories | Bar Chart (Horizontal or Vertical) | AAA | Hover + Sort |
| 3 | Part-to-Whole | Pie Chart or Donut | C | Hover + Drill |
| 4 | Correlation / Distribution | Scatter Plot or Bubble Chart | B | Hover + Brush |
| 5 | Heatmap / Intensity | Heat Map or Choropleth | B | Hover + Zoom |
| 6 | Geographic Data | Choropleth Map or Bubble Map | B | Pan + Zoom + Drill |
| 7 | Funnel / Flow | Funnel Chart or Sankey | AA | Hover + Drill |
| 8 | Performance vs Target | Gauge Chart or Bullet Chart | AA | Hover |
| 9 | Time-Series Forecast | Line with Confidence Band | AA | Hover + Toggle |
| 10 | Anomaly Detection | Line Chart with Highlights | AA | Hover + Alert |
| 11 | Hierarchical / Nested Data | Treemap | C | Hover + Drilldown |
| 12 | Flow / Process Data | Sankey Diagram | C | Hover + Drilldown |
| 13 | Cumulative Changes | Waterfall Chart | AA | Hover |
| 14 | Multi-Variable Comparison | Radar / Spider Chart | B | Hover + Toggle |
| 15 | Stock / Trading OHLC | Candlestick Chart | B | Real-time + Hover + Zoom |
| 16 | Relationship / Connection Data | Network Graph | D | Drilldown + Hover + Drag |
| 17 | Distribution / Statistical | Box Plot | AA | Hover |
| 18 | Performance vs Target (Compact) | Bullet Chart | AAA | Hover |
| 19 | Proportional / Percentage | Waffle Chart | AA | Hover |
| 20 | Hierarchical Proportional | Sunburst Chart | C | Drilldown + Hover |
| 21 | Root Cause Analysis | Decomposition Tree | AA | Drill + Expand |
| 22 | 3D Spatial Data | 3D Scatter / Surface Plot | D | Rotate + Zoom + VR |
| 23 | Real-Time Streaming | Streaming Area Chart | B | Real-time + Pause + Zoom |
| 24 | Sentiment / Emotion | Word Cloud with Sentiment | C | Hover + Filter |
| 25 | Process Mining | Process Map / Graph | B | Drag + Node-Click |

---

## 1. Trend Over Time

Keywords: trend, time-series, line, growth, timeline, progress.

- **Best chart**: Line Chart. Secondary: Area Chart, Smooth Area.
- **When to use**: Data has a time axis; user needs to observe rise/fall trends or rate of change over a continuous period.
- **When NOT to use**: Fewer than 4 data points (use stat card); more than 6 series (visual noise); no time dimension exists.
- **Data volume threshold**: `<1000 pts: SVG; ≥1000 pts: Canvas + downsampling; >10000: aggregate to intervals`.
- **Color guidance**: Primary: `#0080FF`. Multiple series: distinct colors + distinct line styles. Fill: 20% opacity.
- **Accessibility grade**: AA. Differentiate series by line style (solid/dashed/dotted) not color alone. Add pattern overlays for colorblind users.
- **A11y fallback**: Dashed/dotted lines per series; togglable data table with timestamps and values.
- **Library recommendation**: Chart.js, Recharts, ApexCharts.
- **Interactive level**: Hover + Zoom.

## 2. Compare Categories

Keywords: compare, categories, bar, comparison, ranking.

- **Best chart**: Bar Chart (Horizontal or Vertical). Secondary: Column Chart, Grouped Bar.
- **When to use**: Comparing discrete categories by magnitude; ranking or ordering is the core insight; categories ≤ 15.
- **When NOT to use**: Categories > 15 (use table or search); data has time dimension (use line); showing proportions (use waffle/stacked).
- **Data volume threshold**: `<20 categories: vertical bar; 20–50: horizontal bar; >50: paginated table`.
- **Color guidance**: Each bar: distinct color. Grouped: same hue family. Always sort descending by value.
- **Accessibility grade**: AAA. Value labels on each bar by default. Sort control for user reordering.
- **A11y fallback**: Value labels always visible; provide CSV export.
- **Library recommendation**: Chart.js, Recharts, D3.js.
- **Interactive level**: Hover + Sort.

## 3. Part-to-Whole

Keywords: part-to-whole, pie, donut, percentage, proportion, share.

- **Best chart**: Pie Chart or Donut. Secondary: Stacked Bar, Waffle Chart.
- **When to use**: ≤5 categories; one dominant segment vs rest; emphasis on visual proportion over exact values.
- **When NOT to use**: Categories > 5; slice differences < 5% (visually indistinguishable); user needs precise values; accessibility-first context.
- **Data volume threshold**: `Max 6 slices; beyond that switch to stacked bar 100%`.
- **Color guidance**: 5–6 max colors. Contrasting palette. Largest slice at 12 o'clock. Always label slices with %.
- **Accessibility grade**: C. Pie charts fail WCAG for colorblind users. Slices rely on color alone. Avoid as primary chart in a11y contexts.
- **A11y fallback**: Must provide stacked bar alternative + percentage data table as mandatory fallback.
- **Library recommendation**: Chart.js, Recharts, D3.js.
- **Interactive level**: Hover + Drill.

## 4. Correlation / Distribution

Keywords: correlation, distribution, scatter, relationship, pattern, cluster.

- **Best chart**: Scatter Plot or Bubble Chart. Secondary: Heat Map, Matrix.
- **When to use**: Exploring relationship between two continuous variables; identifying clusters or outliers in a dataset.
- **When NOT to use**: Variables are categorical (use grouped bar); fewer than 20 points (patterns aren't meaningful); mobile-primary context.
- **Data volume threshold**: `<500 pts: SVG; 500–5000: Canvas at 0.6–0.8 opacity; >5000: hexbin or aggregate first`.
- **Color guidance**: Color axis: gradient (blue → red). Bubble size: relative to 3rd variable. Opacity: 0.6–0.8 to show density.
- **Accessibility grade**: B. Provide data table alternative. Combine color + shape distinction for colorblind users.
- **A11y fallback**: Data table with correlation coefficient annotation; shape markers (circle/square/triangle) per group.
- **Library recommendation**: D3.js, Plotly, Recharts.
- **Interactive level**: Hover + Brush.

## 5. Heatmap / Intensity

Keywords: heatmap, heat-map, intensity, density, matrix, calendar.

- **Best chart**: Heat Map or Choropleth. Secondary: Grid Heat Map, Bubble Heat.
- **When to use**: Showing intensity/density across a 2D grid; time-based patterns (e.g., activity by hour × day).
- **When NOT to use**: Fewer than 20 cells (use bar); user needs to read exact values; colorblind users without pattern fallback.
- **Data volume threshold**: `Up to 10,000 cells efficiently; beyond that aggregate; calendar heatmap: 365 cells max per SVG`.
- **Color guidance**: Gradient: Cool (blue) to Hot (red). Divergent scale for ±data. Always include numeric color legend.
- **Accessibility grade**: B. Pattern overlay for colorblind users. Numerical value on hover. Legend must include scale ticks.
- **A11y fallback**: Numerical overlay on hover; downloadable grid table with row/column labels.
- **Library recommendation**: D3.js, Plotly, ApexCharts.
- **Interactive level**: Hover + Zoom.

## 6. Geographic Data

Keywords: geographic, map, location, region, geo, spatial, choropleth.

- **Best chart**: Choropleth Map or Bubble Map. Secondary: Geographic Heat Map.
- **When to use**: Data has a regional/location dimension; spatial distribution is the core insight for the user.
- **When NOT to use**: Regions have very different sizes making visual comparison misleading (use bar); mobile-primary context.
- **Data volume threshold**: `<1000 regions: SVG; ≥1000: Canvas/WebGL (Deck.gl); global maps: tile-based rendering`.
- **Color guidance**: Single color gradient per region group. Categorized colors for discrete types. Legend with clear scale breaks.
- **Accessibility grade**: B. Include text labels for major regions. Provide keyboard navigation between regions.
- **A11y fallback**: Region text labels; sortable data table by region name and value; keyboard-navigable regions.
- **Library recommendation**: D3.js, Mapbox, Leaflet.
- **Interactive level**: Pan + Zoom + Drill.

## 7. Funnel / Flow

Keywords: funnel, flow, conversion, drop-off, pipeline, stages.

- **Best chart**: Funnel Chart or Sankey. Secondary: Waterfall (for flows).
- **When to use**: Sequential multi-stage process; showing conversion or drop-off rates between defined stages.
- **When NOT to use**: Stages aren't sequential; values don't decrease monotonically (use bar); fewer than 3 stages.
- **Data volume threshold**: `3–8 stages optimal; beyond 8 stages group minor steps into 'Other'`.
- **Color guidance**: Stages: single color gradient (start → end). Show conversion % between each stage. Highlight biggest drop.
- **Accessibility grade**: AA. Explicit conversion % as text per stage. Stage labels always visible. Linear list view as fallback.
- **A11y fallback**: Provide linear list view with stage name + count + drop-off %; keyboard traversal.
- **Library recommendation**: D3.js, Recharts, Custom SVG.
- **Interactive level**: Hover + Drill.

## 8. Performance vs Target

Keywords: performance, target, kpi, gauge, goal, threshold, progress.

- **Best chart**: Gauge Chart or Bullet Chart. Secondary: Dial, Thermometer.
- **When to use**: Single KPI measured against a defined target or threshold; dashboard summary context.
- **When NOT to use**: No target or benchmark exists; comparing multiple KPIs at once (use bullet chart grid).
- **Data volume threshold**: `Single metric per gauge; for 3+ KPIs use bullet chart grid layout`.
- **Color guidance**: Performance: Red → Yellow → Green gradient. Target: marker line. Threshold zones clearly differentiated.
- **Accessibility grade**: AA. Always show numerical value + % of target as text beside chart. Never rely on color position alone.
- **A11y fallback**: Numerical value + % of target shown as visible text; ARIA live region for real-time updates.
- **Library recommendation**: D3.js, ApexCharts, Custom SVG.
- **Interactive level**: Hover.

## 9. Time-Series Forecast

Keywords: forecast, prediction, confidence, band, projection, estimate.

- **Best chart**: Line with Confidence Band. Secondary: Ribbon Chart.
- **When to use**: Historical data + model predictions; communicating uncertainty range to non-technical stakeholders.
- **When NOT to use**: No historical baseline; prediction confidence is too low to be useful; audience is not data-literate.
- **Data volume threshold**: `Keep historical window to 30–90 days for readability; forecast horizon ≤ 30% of visible x-axis range`.
- **Color guidance**: Actual: solid line `#0080FF`. Forecast: dashed `#FF9500`. Confidence band: 15% opacity fill same hue.
- **Accessibility grade**: AA. Toggle between actual-only and forecast views. Legend must distinguish lines beyond color (solid vs dashed).
- **A11y fallback**: Toggle actual/forecast independently; legend labels must include line-style description.
- **Library recommendation**: Chart.js, ApexCharts, Plotly.
- **Interactive level**: Hover + Toggle.

## 10. Anomaly Detection

Keywords: anomaly, outlier, spike, alert, detection, monitoring, deviation.

- **Best chart**: Line Chart with Highlights. Secondary: Scatter with Alert.
- **When to use**: Monitoring a time-series for outliers; alerting users to unexpected spikes or dips in operational data.
- **When NOT to use**: Anomalies are predefined categories (use bar with highlight); real-time context without a pause control.
- **Data volume threshold**: `Stream at ≤60fps with Canvas; batch: up to 10,000 pts; mark anomalies as a separate data layer`.
- **Color guidance**: Normal: `#0080FF` solid line. Anomaly marker: `#FF0000` circle + filled. Alert band: `#FFF3CD` background zone.
- **Accessibility grade**: AA. Use shape marker (not color only) for anomaly points. Add text annotation per anomaly event.
- **A11y fallback**: Text alert annotation per anomaly; anomaly summary list panel alongside chart.
- **Library recommendation**: D3.js, Plotly, ApexCharts.
- **Interactive level**: Hover + Alert.

## 11. Hierarchical / Nested Data

Keywords: hierarchy, nested, treemap, parent, children, breakdown, drill.

- **Best chart**: Treemap. Secondary: Sunburst, Nested Donut, Icicle.
- **When to use**: Showing size relationships within a hierarchy; overview of proportional structure (e.g., budget breakdown).
- **When NOT to use**: Hierarchy depth > 3 levels (too complex to read); user needs to compare sibling values precisely.
- **Data volume threshold**: `<200 nodes: SVG; 200–1000: Canvas; >1000: paginate or pre-filter before rendering`.
- **Color guidance**: Parent nodes: distinct hues. Children: lighter shades of same hue. White separator borders: 2–3px.
- **Accessibility grade**: C. Poor baseline accessibility. Always provide table alternative as primary view. Label all large areas.
- **A11y fallback**: Collapsible tree table as primary view; treemap as supplementary visual only.
- **Library recommendation**: D3.js, Recharts, ApexCharts.
- **Interactive level**: Hover + Drilldown.

## 12. Flow / Process Data

Keywords: flow, process, sankey, distribution, source, target, transfer.

- **Best chart**: Sankey Diagram. Secondary: Alluvial, Chord Diagram.
- **When to use**: Showing how quantities flow between nodes; multi-source multi-target distribution.
- **When NOT to use**: Flow directions form loops (use network graph); fewer than 3 source-target pairs; mobile-primary context.
- **Data volume threshold**: `<50 flows: SVG; ≥50: Canvas; >200 flows: aggregate minor flows into 'Other' node`.
- **Color guidance**: Gradient from source to target color. Flow opacity: 0.4–0.6. Node labels always visible.
- **Accessibility grade**: C. Structural flow charts cannot be conveyed by color alone. Provide flow table. Avoid on mobile.
- **A11y fallback**: Flow table (Source → Target → Value); keyboard-traversable node list with tab stops.
- **Library recommendation**: D3.js (d3-sankey), Plotly.
- **Interactive level**: Hover + Drilldown.

## 13. Cumulative Changes

Keywords: waterfall, cumulative, variance, incremental, bridge, delta.

- **Best chart**: Waterfall Chart. Secondary: Stacked Bar, Cascade.
- **When to use**: Showing how individual positive/negative components add up to a final total (e.g., P&L, budget variance).
- **When NOT to use**: Changes are not additive; more than 12 bars (readability breaks); audience expects a simple total.
- **Data volume threshold**: `4–12 bars optimal; beyond 12 aggregate minor items into a single 'Other' bar`.
- **Color guidance**: Increases: `#4CAF50`. Decreases: `#F44336`. Start total: `#2196F3`. End total: `#0D47A1`. Running total line: dashed.
- **Accessibility grade**: AA. Color + directional arrow icon per bar (not color alone). Labels on every bar.
- **A11y fallback**: Table with running total column; directional arrow icons per row.
- **Library recommendation**: ApexCharts, Highcharts, Plotly.
- **Interactive level**: Hover.

## 14. Multi-Variable Comparison

Keywords: radar, spider, multi-variable, attributes, dimensions, comparison.

- **Best chart**: Radar / Spider Chart. Secondary: Parallel Coordinates, Grouped Bar.
- **When to use**: Comparing multiple entities across the same fixed set of attributes (e.g., product feature comparison).
- **When NOT to use**: Axes > 8 (unreadable); values need precise comparison (use grouped bar); audience unfamiliar with radar charts.
- **Data volume threshold**: `2–3 datasets maximum per chart; 5–8 axes; beyond 8 axes switch to parallel coordinates`.
- **Color guidance**: Single dataset: `#0080FF` at 20% fill. Multiple: distinct hues with 30% fill. Border: full opacity.
- **Accessibility grade**: B. Limit axes to 5–8. Always provide grouped bar chart alternative for precise reading.
- **A11y fallback**: Grouped bar chart as mandatory alternative; include raw data table.
- **Library recommendation**: Chart.js, Recharts, ApexCharts.
- **Interactive level**: Hover + Toggle.

## 15. Stock / Trading OHLC

Keywords: stock, trading, ohlc, candlestick, finance, price, volume.

- **Best chart**: Candlestick Chart. Secondary: OHLC Bar, Heikin-Ashi.
- **When to use**: Financial time-series with Open/High/Low/Close data; trading or investment product context only.
- **When NOT to use**: Non-financial audience; no OHLC data available (use line chart); accessibility-first context.
- **Data volume threshold**: `Real-time: Canvas required. Historical: paginate by time range. Max 500 candles visible at once`.
- **Color guidance**: Bullish: `#26A69A`. Bearish: `#EF5350`. Volume bars: 40% opacity below. Body fill vs hollow for OHLC style.
- **Accessibility grade**: B. Provide OHLC data table. Colorblind: use fill vs outline pattern (bullish = filled, bearish = hollow).
- **A11y fallback**: OHLC data table with sortable columns; numeric summary panel (daily change %).
- **Library recommendation**: Lightweight Charts (TradingView), ApexCharts.
- **Interactive level**: Real-time + Hover + Zoom.

## 16. Relationship / Connection Data

Keywords: network, graph, nodes, edges, connections, relationships, force.

- **Best chart**: Network Graph. Secondary: Hierarchical Tree, Adjacency Matrix.
- **When to use**: Mapping connections between entities; network topology or social graph exploration context.
- **When NOT to use**: Node count > 500 without clustering pre-applied; user needs precise connection counts; mobile context.
- **Data volume threshold**: `≤100 nodes: SVG; 101–500: Canvas; >500: must apply clustering/LOD before rendering`.
- **Color guidance**: Node types: categorical colors. Edges: `#90A4AE` at 60% opacity. Highlight path: `#F59E0B`.
- **Accessibility grade**: D. Fundamentally inaccessible without alternative. Never use as sole representation. Always provide list alternative.
- **A11y fallback**: Adjacency list table (Node A → Node B → Weight); hierarchical tree view when structure allows.
- **Library recommendation**: D3.js (d3-force), Vis.js, Cytoscape.js.
- **Interactive level**: Drilldown + Hover + Drag.

## 17. Distribution / Statistical

Keywords: distribution, statistical, spread, median, outlier, quartile, boxplot.

- **Best chart**: Box Plot. Secondary: Violin Plot, Beeswarm.
- **When to use**: Showing spread, median, and outliers of a dataset; comparing distributions across multiple groups.
- **When NOT to use**: Fewer than 20 data points per group (distribution is not meaningful); audience unfamiliar with statistical charts.
- **Data volume threshold**: `Any sample size; aggregated representation so rendering is ⚡ Excellent at any volume`.
- **Color guidance**: Box fill: `#BBDEFB`. Border: `#1976D2`. Median line: `#D32F2F` bold. Outlier dots: `#F44336`.
- **Accessibility grade**: AA. Include stats summary table. Annotate outlier count in chart subtitle.
- **A11y fallback**: Stats summary table (min / Q1 / median / Q3 / max / mean); outlier count annotation.
- **Library recommendation**: Plotly, D3.js, Chart.js (plugin).
- **Interactive level**: Hover.

## 18. Performance vs Target (Compact)

Keywords: bullet, compact, kpi, dashboard, target, benchmark, range.

- **Best chart**: Bullet Chart. Secondary: Gauge, Progress Bar.
- **When to use**: Dashboard with multiple KPIs side by side; space-constrained contexts where a gauge is too large.
- **When NOT to use**: Single KPI with emphasis (use gauge); data has no defined target range; fewer than 3 KPIs.
- **Data volume threshold**: `Ideal for 3–10 bullet charts in a grid; scales to any count efficiently`.
- **Color guidance**: Qualitative ranges: `#FFCDD2` / `#FFF9C4` / `#C8E6C9` (bad/ok/good). Performance bar: `#1976D2`. Target: black 3px marker.
- **Accessibility grade**: AAA. All values always visible as text. Color ranges are labeled with text thresholds not color alone.
- **A11y fallback**: Numerical values always visible (not hover-only); color ranges labeled with threshold text.
- **Library recommendation**: D3.js, Plotly, Custom SVG.
- **Interactive level**: Hover.

## 19. Proportional / Percentage

Keywords: waffle, percentage, proportion, progress, filled, grid.

- **Best chart**: Waffle Chart. Secondary: Pictogram, Stacked Bar 100%.
- **When to use**: Showing what fraction of a whole is filled; percentage progress in a visually engaging and accessible format.
- **When NOT to use**: More than 5 categories (use stacked bar); exact values matter over visual proportion; very tight space.
- **Data volume threshold**: `10×10 grid standard (100 cells); for > 5 categories switch to stacked 100% bar`.
- **Color guidance**: 3–5 categories max. 2–3px gap between cells. Each category a distinct accessible color pair.
- **Accessibility grade**: AA. Better than pie for accessibility. Percentage text label always visible. Each cell has aria-label.
- **A11y fallback**: Percentage text always visible; grid cells labeled with aria-label value; provide legend.
- **Library recommendation**: D3.js, React-Waffle, Custom CSS Grid.
- **Interactive level**: Hover.

## 20. Hierarchical Proportional

Keywords: sunburst, hierarchy, nested, proportion, radial, circle.

- **Best chart**: Sunburst Chart. Secondary: Treemap, Icicle, Circle Packing.
- **When to use**: Exploring nested proportions where both hierarchy and relative size matter (e.g., org spend breakdown).
- **When NOT to use**: More than 3 hierarchy levels (outer rings become unreadable); precision matters over overview; mobile.
- **Data volume threshold**: `<100 nodes: SVG; 100–500: Canvas; >500: filter to top N before rendering`.
- **Color guidance**: Center to outer: darker to lighter hue. Each level 15–20% lighter. Contrasting border between sectors.
- **Accessibility grade**: C. Poor accessibility beyond 2 levels. Mandatory table alternative required for any production use.
- **A11y fallback**: Collapsible indented list with percentages; breadcrumb trail for current drill-down state.
- **Library recommendation**: D3.js (d3-hierarchy), Recharts, ApexCharts.
- **Interactive level**: Drilldown + Hover.

## 21. Root Cause Analysis

Keywords: root cause, decomposition, tree, hierarchy, drill-down, ai-split, attribution.

- **Best chart**: Decomposition Tree. Secondary: Decision Tree, Flow Chart.
- **When to use**: Decomposing a metric into contributing factors; AI-assisted analysis or BI drill-down scenarios.
- **When NOT to use**: No clear parent-child causal relationship; audience expects a summary rather than exploration.
- **Data volume threshold**: `Up to 5 levels deep; limit visible nodes to 20 per level for readability; lazy-load deeper levels`.
- **Color guidance**: Positive impact nodes: `#2563EB`. Negative impact nodes: `#EF4444`. Neutral connectors: `#94A3B8`.
- **Accessibility grade**: AA. Keyboard-navigable expand/collapse. Screen reader announces node value and % contribution.
- **A11y fallback**: Keyboard expand/collapse tree; screen reader announces node label + value + % impact.
- **Library recommendation**: Power BI (native), React-Flow, Custom D3.js.
- **Interactive level**: Drill + Expand.

## 22. 3D Spatial Data

Keywords: 3d, spatial, immersive, terrain, molecular, volumetric, point-cloud.

- **Best chart**: 3D Scatter / Surface Plot. Secondary: Volumetric Rendering, Point Cloud.
- **When to use**: Scientific/engineering context where Z-axis carries essential info not expressible in 2D.
- **When NOT to use**: 2D projection conveys the same insight; mobile context; accessibility-required environments; standard business dashboards.
- **Data volume threshold**: `WebGL required. Deck.gl: up to 1M points. Three.js: LOD required beyond 50,000 pts`.
- **Color guidance**: Depth cues: lighting and shading. Z-axis: color gradient (cool → warm). Transparent overlapping: opacity 0.4.
- **Accessibility grade**: D. 3D spatial charts are fundamentally inaccessible. Must not be used as primary chart type in any product UI.
- **A11y fallback**: Mandatory 2D projection view + data table; do not use as primary chart type in product UI.
- **Library recommendation**: Three.js, Deck.gl, Plotly 3D.
- **Interactive level**: Rotate + Zoom + VR.

## 23. Real-Time Streaming

Keywords: streaming, real-time, ticker, live, velocity, pulse, monitoring.

- **Best chart**: Streaming Area Chart. Secondary: Ticker Tape, Moving Gauge.
- **When to use**: Live monitoring dashboards; IoT/ops data updating at ≥1 Hz; user needs current value at a glance.
- **When NOT to use**: Update frequency < 1/min (use periodic-refresh line chart); flashing content without reduced-motion support.
- **Data volume threshold**: `Canvas/WebGL required. Buffer last 60–300s of data. Downsample older data on scroll`.
- **Color guidance**: Current pulse: `#00FF00` (dark theme) or `#0080FF` (light theme). History: fading opacity. Grid: dark background.
- **Accessibility grade**: B. Pause/resume control required. Current value as large visible text KPI. Respect prefers-reduced-motion.
- **A11y fallback**: Pause/resume button required; current value shown as large text KPI; prefers-reduced-motion: freeze animation.
- **Library recommendation**: Smoothed D3.js, CanvasJS.
- **Interactive level**: Real-time + Pause + Zoom.

## 24. Sentiment / Emotion

Keywords: sentiment, emotion, nlp, opinion, feeling, text-analysis.

- **Best chart**: Word Cloud with Sentiment. Secondary: Sentiment Arc, Radar Chart.
- **When to use**: NLP output visualization; exploratory analysis of text corpus sentiment; frequency-weighted keyword overview.
- **When NOT to use**: Precise values matter (word size is inherently imprecise); screen-reader context; corpus < 50 items.
- **Data volume threshold**: `50–5000 terms optimal. Beyond 5000: apply top-N filtering before render. Avoid on mobile`.
- **Color guidance**: Positive: `#22C55E`. Negative: `#EF4444`. Neutral: `#94A3B8`. Word size maps to frequency.
- **Accessibility grade**: C. Word clouds fail screen readers. Never use as sole output of NLP analysis. Always pair with list view.
- **A11y fallback**: Sortable list view by frequency with sentiment label column; word cloud as supplementary only.
- **Library recommendation**: D3-cloud, Highcharts, Nivo.
- **Interactive level**: Hover + Filter.

## 25. Process Mining

Keywords: process, mining, variants, path, bottleneck, log, event.

- **Best chart**: Process Map / Graph. Secondary: Directed Acyclic Graph (DAG), Petri Net.
- **When to use**: Analyzing event logs to visualize actual process flows; identifying bottlenecks and deviations in ops/product funnels.
- **When NOT to use**: No event log data available; audience expects a static flowchart (use diagram tool); node count > 100 without pre-filtering.
- **Data volume threshold**: `<30 nodes: SVG; 30–100: Canvas; >100: apply variant filtering (top 80% of cases) before rendering`.
- **Color guidance**: Happy path: `#10B981` thick line. Deviations: `#F59E0B` thin line. Bottleneck nodes: `#EF4444` fill.
- **Accessibility grade**: B. Complex graphs are hard to navigate. Provide path summary text. Highlight top 3 bottlenecks as annotations.
- **A11y fallback**: Path summary table (variant → frequency → avg duration); top 3 bottlenecks as text annotation panel.
- **Library recommendation**: React-Flow, Cytoscape.js, Recharts.
- **Interactive level**: Drag + Node-Click.

---

Source: ui-ux-pro-max charts.csv (MIT)
