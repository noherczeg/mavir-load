# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with Chart.js v4.

| File | Purpose |
|---|---|
| `index.html` | Renders Chart.js v4 chart overlaying load + production (`prod_*`) series on one MW axis. Filters data to current ±12 hours. `LABELS`/`COLORS`/`KEYS` include the 4 `prod_*` keys (exact MAVIR Hungarian names). `DEFAULT_ON` pessimistic = gross_actual/gross_est + prod_gross_actual→prod_gross_plan. `ACTUAL_KEYS` includes `prod_gross_actual` for the `Most` boundary. Persists series visibility by key. Links GitHub repo with accessible logo. See change: add-production-sync |
