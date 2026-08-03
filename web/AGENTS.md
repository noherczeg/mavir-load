# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with Chart.js v4.

| File | Purpose |
|---|---|
| `index.html` | Renders Chart.js v4 chart on one MW axis. Filters data to current ±12 hours. Curated 4-series `LABELS`/`COLORS`/`KEYS`: `gross_actual`, `gross_plan`, `prod_gross_plan`, `prod_gross_actual` (data files still carry all keys; unused ones simply not rendered). `DEFAULT_ON`=all 4, still toggleable. Per-series `STYLE`: solid line for actuals (`tény`), dashed for plans (`terv`); production series (`prod_*`) get a faint `fadeFill()` vertical-gradient area fill. Colors: blue/violet/amber/green. `ACTUAL_KEYS`=`gross_actual`+`prod_gross_actual` drive the `Most` boundary. Visibility persisted by key under `STORE_KEY`=`mavir.series.v2` (bumped when the curated set changed). Links GitHub repo with accessible logo. See change: add-production-sync |
