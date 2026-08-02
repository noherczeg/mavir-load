# web/

Static GitHub Pages chart. Fetches `../data/<date>.json`, renders with Chart.js v4.

| File | Purpose |
|---|---|
| `index.html` | Renders Chart.js v4 chart. Filters data to current ±12 hours. Links GitHub repository with accessible logo. Persists series visibility. Draws `Most` boundary at last actual point. See change: add-mavir-load-sync |
