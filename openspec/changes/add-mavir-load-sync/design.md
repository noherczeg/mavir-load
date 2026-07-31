# Design — MAVIR load sync + chart

## Data source

```
GET https://rtdwweb.mavir.hu/rtdwweb/webuser/chart/7678/export
    ?exportType=xlsx&fromTime=<ms>&toTime=<ms>&periodType=min&period=15
```

- No auth, no cookies. Plain GET returns ~9.5 KB xlsx (Apache POI, `inlineStr`
  cells, empty `sharedStrings`).
- `fromTime`/`toTime` are epoch milliseconds. `period=15` → 15-min points.
- 24h window (±12h) → ~97 data rows.

### Columns (sheet1, row 1 = header)

| Col | Header (Hungarian)                                | Key             | Nature   |
|-----|---------------------------------------------------|-----------------|----------|
| A   | Időpont                                           | `t`             | time     |
| B   | Bruttó hitelesített rendszerterhelés tény         | `gross_certified` | actual (lagged, **v1: skip**) |
| C   | Bruttó rendszerterhelés becslés (dayahead)        | `gross_est`     | forecast |
| D   | Nettó terv rendszertermelés                       | `net_plan_gen`  | plan (generation) |
| E   | Nettó terv rendszerterhelés                       | `net_plan_load` | plan (load) |
| F   | Bruttó tény rendszerterhelés                      | `gross_actual`  | actual   |
| G   | Bruttó terv rendszerterhelés                      | `gross_plan`    | plan (load) |
| H   | Nettó tény rendszerterhelés - net.ker.elsz.meres  | `net_certified` | actual (lagged, **v1: skip**) |
| I   | Nettó terhelés                                    | `net_load`      | actual   |
| J   | Nettó rendszerterhelés tény - üzemirányítási      | `net_actual`    | actual   |
| K   | Nettó rendszerterhelés becslés (dayahead)         | `net_est`       | forecast |

Timestamps arrive as `2026.07.31 01:15:00 +0200`; normalize to ISO-8601 at
ingest (`2026-07-31T01:15:00+02:00`).

## Key decisions

### 1. "Now" boundary is data-driven, not clock-driven
Actual columns (F/I/J) go null at the present moment; forecast/plan columns
continue. Detect the boundary as the last timestamp where any actual column is
non-null. Do not compute it from the wall clock — robust against the export
being pulled slightly early/late.

### 2. Window math (Europe/Budapest)
Compute `now` in `Europe/Budapest`, then `fromTime = now - 12h`,
`toTime = now + 12h`, both as epoch ms. DST is handled by using a tz-aware
`now`; the epoch-ms conversion is absolute so the offset is implicit.

### 3. Storage: daily JSON, upsert by timestamp
`data/<YYYY-MM-DD>.json`. On each run, for every fetched point: match by `t`;
fill any null field with the newly fetched non-null value; **never overwrite a
non-null value with null**. This lets a later run backfill late-arriving fields
without clobbering earlier actuals. Commit only if the file content changed.

Rejected: single `latest.json` (loses history of late arrivals); SQLite/binary
(kills readable diffs, adds a WASM dependency in the chart for no benefit at
this data size — ~30 KB/day, ~11 MB/year).

### 4. Retry
1 initial attempt + up to 2 retries (3 total), short backoff between attempts.
A non-200, timeout, or unparseable body counts as a failure. After all attempts
fail, the run exits non-zero (GitHub emails on workflow failure).

### 5. Pessimistic default series (human-facing)
- **Consumption** headline = `gross_actual` (past) → `gross_est` (future).
  Gross > net, so gross is the conservative (higher) consumption view.
- **Production** headline = `net_plan_gen` (only generation column; plan
  understates margin = conservative).
- Where a same-timestamp choice exists: max for load, min for generation.
- Remaining columns available as toggleable series so the actual→forecast
  handoff at the "now" line is visible.

### 6. Hungarian UI
Internal keys stay English; a `labels.hu` map in the frontend renders every
user-facing string in Hungarian (axis titles, legend, tooltip, "Most" marker).
No i18n framework.

## Architecture

```
GitHub Actions (cron */30, retry x2)
  fetch xlsx --> parse (openpyxl) --> normalize (ISO + short keys)
    --> upsert data/<date>.json (prefer newer non-null)
    --> commit iff changed
GitHub Pages: web/index.html + uPlot --> fetch data/<date>.json --> chart
Cost: $0
```

## Open questions

- Chart date range: single day vs multi-day scrollback (v1 = current + maybe
  previous day). Decide during implementation; storage already supports either.
