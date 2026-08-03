# Design — MAVIR production sync + chart overlay

## Data source

```
GET https://rtdwweb.mavir.hu/rtdwweb/webuser/chart/4401/export
    ?exportType=xlsx&fromTime=<ms>&toTime=<ms>&periodType=min&period=15
```

- Same endpoint, auth model, and window/period params as the existing `7678`
  load pull. Returns ~6.7 KB xlsx, sheet `Exportált adatok`, ~97 data rows for a
  24h window.
- Timestamps arrive as `2026.08.03 08:15:00 +0200`; normalize to ISO-8601 at
  ingest — identical to the load path, so the two charts' points share the same
  `t` values and merge one-to-one.

### Columns (row 1 = header)

| Col | Header (Hungarian)             | Key                | Nature   |
|-----|--------------------------------|--------------------|----------|
| A   | Időpont                        | `t`                | time (shared merge key) |
| B   | Bruttó terv erőművi termelés   | `prod_gross_plan`  | plan     |
| C   | Bruttó tény erőművi termelés   | `prod_gross_actual`| actual   |
| D   | Nettó terv erőművi termelés    | `prod_net_plan`    | plan     |
| E   | Nettó hazai termelés tény      | `prod_net_actual`  | actual (lagged; null in window — mapped null-safely) |

The `prod_` prefix keeps these keys distinct from the load keys. Note the
near-homonym: load chart `7678` col D is "Nettó terv rendszer**termelés**"
(`net_plan_gen`) while production chart `4401` col D is "Nettó terv erőművi
**termelés**" (`prod_net_plan`) — similar wording, different series, so they
must not share a key.

## Key decisions

### 1. Storage: one file per day, additive `prod_*` keys (Option A)
Both charts land in the same `data/<date>.json` point objects, matched by the
shared `t`. No new storage lane, no migration of existing files — old points
simply gain `prod_*` fields as runs pick them up.

Rejected: separate `data/load/` + `data/production/` lanes (would force
migrating existing files and a two-file fetch in the web app for no benefit
given the timestamps already align 1:1).

### 2. Two independent fetches, one merged upsert
`fetch.py` iterates a small two-entry chart table `[(7678, LOAD_MAP),
(4401, PROD_MAP)]`. Each chart's fetch+parse is wrapped so a failure is logged
and skipped, not fatal — surviving charts still upsert. This is a minimal
generalization of the existing single-chart flow, **not** a config-driven
registry (Option C, rejected as over-engineering for two charts).

`VALUE_KEYS` becomes the union of both maps' value keys (minus `t`) so the
existing `_merge_point` covers production fields unchanged.

### 3. Failure isolation composes with the existing merge rule for free
`_merge_point` already never overwrites a non-null stored value with null. So
when `4401` is skipped, its points simply aren't in the fetch set — stored
`prod_*` values are untouched. No new "partial run" logic is required.

### 4. Pessimistic default production series (DECIDED)
Default production headline = `prod_gross_actual` (past) → `prod_gross_plan`
(future). Chosen to keep the gross family consistent across the actual→plan
handoff (the net-plan alternative was slightly lower/more-pessimistic but mixed
gross past with net future).

The remaining production series stay toggleable, like the load series. This
supersedes the v1 stand-in where the production headline was `net_plan_gen`
(borrowed from the load chart) because no real generation actuals existed yet.

### 5. "Most" boundary includes production actuals
Add `prod_gross_actual` to the actual-key set that computes the present-moment
boundary, so the boundary reflects where *any* actual (load or generation) ends.
`prod_net_actual` is excluded (lagged/null, would not move the boundary).

### 6. Single MW axis, Hungarian labels
Load and generation are both MW → one shared y-axis. Add the four `prod_*` keys
to the frontend `LABELS`/`COLORS` maps using MAVIR's exact Hungarian column
names. Visibility persists by stable key name, so existing `localStorage` state
needs no version bump — new keys fall back to their `DEFAULT_ON` membership.

## Architecture

```
GitHub Actions (cron */30)
  for (chart, colmap) in [ (7678, LOAD), (4401, PROD) ]:   # independent
      try: fetch xlsx -> parse -> collect points
      except: log + skip this chart
  upsert union into data/<date>.json  (prefer newer non-null)
  commit iff changed
GitHub Pages: web/index.html (Chart.js) overlays load + prod_* series
Cost: $0
```

## Open questions

- (resolved #4) default forward production series = `prod_gross_plan`.
- (resolved) page header broadened to "MAVIR rendszerterhelés és termelés".
