# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with uPlot.

| File | Purpose |
|---|---|
| `index.html` | Single-file app. `LABELS` = exact official MAVIR legend names (from mavir.hu/web/mavir/rendszerterheles) per key; internal keys stay English. `DEFAULT_ON` = actual real consumption (`net_actual`) + production (`net_plan_gen`; MAVIR has no actual-production series, so planned generation stands in); other series hidden but toggleable. Series visibility persists to `localStorage["mavir.series.v1"]` (per stable key) via the uPlot `setSeries` hook; `isOn()` restores it on load, falling back to `DEFAULT_ON` for keys absent from storage. Loads today ±1 day (window straddles midnight). `nowLinePlugin` draws the "Most" boundary at last non-null actual (`ACTUAL_KEYS`). uPlot rendered in Europe/Budapest via `tzDate`. See change: add-mavir-load-sync |
