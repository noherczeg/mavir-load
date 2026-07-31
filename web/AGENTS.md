# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with Chart.js v4.

| File | Purpose |
|---|---|
| `index.html` | Single-file app. Chart.js v4 + luxon + chartjs-adapter-luxon (CDN UMD). `LABELS` = exact official MAVIR legend names (from mavir.hu/web/mavir/rendszerterheles) per key; internal keys stay English. `COLORS` = 8 distinct hues (avoids red — reserved for "Most"). `DEFAULT_ON` = `gross_actual` + `gross_est` + `net_plan_gen`; other datasets `hidden` but toggleable. Floating hover tooltip (`interaction.mode:index`, `intersect:false`) shows all visible series at the cursor, sorted desc, null-filtered, title in Europe/Budapest — replaces legend value-tracking. Series visibility persists to `localStorage["mavir.series.v1"]` (per stable key) via a custom `legend.onClick` that toggles `setDatasetVisibility` then `saveVisibility` (reads `chart.isDatasetVisible(i)`); `isOn()` restores on load, falling back to `DEFAULT_ON`. Loads today ±1 day (window straddles midnight). `nowLinePlugin` (Chart.js plugin, `afterDatasetsDraw`) draws the "Most" boundary at last non-null actual (`ACTUAL_KEYS`). Time x-axis in Europe/Budapest via luxon adapter `zone`. Fullscreen responsive via `responsive:true` + `maintainAspectRatio:false` in a flex `#wrap` (Chart.js handles resize; no manual sizing). See change: add-mavir-load-sync |
