# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with uPlot.

| File | Purpose |
|---|---|
| `index.html` | Single-file app. `LABELS` = Hungarian display names per key; internal keys stay English. `DEFAULT_ON` = pessimistic defaults (`gross_actual`, `gross_est`, `net_plan_gen`); other series hidden but toggleable. Loads today ±1 day (window straddles midnight). `nowLinePlugin` draws the "Most" boundary at last non-null actual (`ACTUAL_KEYS`). uPlot rendered in Europe/Budapest via `tzDate`. See change: add-mavir-load-sync |
