# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with uPlot.

| File | Purpose |
|---|---|
| `index.html` | Single-file app. `LABELS` = exact official MAVIR legend names (from mavir.hu/web/mavir/rendszerterheles) per key; internal keys stay English. `DEFAULT_ON` = `gross_actual` + `gross_est` + `net_plan_gen`; other series hidden but toggleable. Series visibility persists to `localStorage["mavir.series.v1"]` (per stable key) via a click listener on `.u-legend` (uPlot's legend toggle does NOT fire the `setSeries` hook in this build, so we read `series[].show` next tick and save); `isOn()` restores it on load, falling back to `DEFAULT_ON` for keys absent from storage. Loads today ±1 day (window straddles midnight). `nowLinePlugin` draws the "Most" boundary at last non-null actual (`ACTUAL_KEYS`). uPlot rendered in Europe/Budapest via `tzDate`. CSS puts the x-series (Időpont) on its own dedicated legend row and reserves `min-width` on `.u-value` cells so hover-populated values don't reflow the legend (no layout shift). `fitChart()` sizes the plot to fill the viewport (width = client width; height = window minus header and measured legend height) and re-fits on a debounced `resize` — fully responsive, no fixed dimensions. See change: add-mavir-load-sync |
