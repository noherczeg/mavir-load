# mavir-load

Periodically syncs the MAVIR Hungarian grid system-load export (actuals +
day-ahead forecasts, 15-minute resolution) into versioned JSON, and draws an
interactive Hungarian chart from it. **Zero-cost stack:** GitHub Actions is the
scheduler + compute, the git repo is the storage, GitHub Pages is the host.

```
GitHub Actions (cron */30, retry x2)
  fetch xlsx -> parse (openpyxl) -> normalize -> upsert data/<date>.json -> commit iff changed
GitHub Pages: web/index.html + uPlot -> fetch data/<date>.json -> interactive chart
```

## Layout

| Path | What |
|---|---|
| `index.html` | Root redirect → `web/index.html` (so the Pages root opens the app) |
| `.nojekyll` | Disables Jekyll so the README is not served as the site |
| `sync/fetch.py` | Fetch (±12h window, 3 attempts), parse, upsert daily JSON |
| `sync/test_sync.py` | Offline tests (parse + merge) using `sync/fixtures/export.xlsx` + `export_4401.xlsx` |
| `sync/requirements.txt` | `openpyxl` |
| `data/<YYYY-MM-DD>.json` | Generated, versioned load + production data (Europe/Budapest days) |
| `web/index.html` | Static uPlot chart, Hungarian labels |
| `.github/workflows/sync.yml` | Cron `*/30` + manual dispatch |

## Data model

`data/<date>.json` holds points keyed by ISO-8601 timestamp, merged from two
MAVIR charts by shared timestamp. Load keys (chart 7678): `gross_actual`,
`gross_est`, `net_actual`, `net_est`, `net_load`, `net_plan_gen`,
`net_plan_load`, `gross_plan`. Production keys (chart 4401): `prod_gross_plan`,
`prod_gross_actual`, `prod_net_plan`, `prod_net_actual`. Keys are English
internally, Hungarian in the UI. Missing values are explicit `null`. The two
charts are fetched independently — one failing never blocks the other. Certified
load columns and the lagged `prod_net_actual` are outside the ±12h window in
v1. Upsert prefers newer non-null values and never overwrites a value with
null.

The **present-moment boundary** ("Most") is data-driven: the last timestamp
where any actual column is non-null.

## Run the sync locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r sync/requirements.txt
python sync/fetch.py          # writes/updates data/*.json
```

## Tests

```bash
pip install pytest && cd sync && python -m pytest test_sync.py -q
```

## View the chart locally

Serve the repo root (so `/web` can fetch `/data`) and open `/web/index.html`:

```bash
python3 -m http.server 8000
# http://localhost:8000/web/index.html
```

## Deploy (one-time)

Enable **GitHub Pages** for the repo (Settings → Pages → deploy from branch,
root). The chart lives at `/web/index.html`. Public repo recommended:
unlimited Actions minutes + free Pages. Actions emails on workflow failure.
