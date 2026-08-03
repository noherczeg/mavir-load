# Add MAVIR production (generation) sync + chart overlay

## Why

The current pipeline syncs only MAVIR chart `7678` — Hungarian grid
**rendszerterhelés** (system load / demand). MAVIR publishes the complementary
side of the balance, **erőművi termelés** (power-plant production / generation),
as chart `4401` on the same unauthenticated endpoint, same 15-minute grid, same
window mechanics. Pulling it gives the chart both sides of the grid picture
(what is consumed vs. what is generated) for the same $0 cost — the payload is
another ~6.7 KB per pull.

## What Changes

- **Sync job**: extend `sync/fetch.py` to also fetch chart `4401` for the same
  ±12h window, parse its columns, and merge them into the **same**
  `data/<date>.json` points keyed by the shared 15-minute timestamp, under
  distinct `prod_*` keys.
- **Failure isolation**: the two chart fetches are independent — a failed `4401`
  pull never blocks committing fresh `7678` data (and vice versa). The existing
  never-overwrite-non-null-with-null merge rule means a skipped chart leaves its
  last-known values untouched with zero special-casing.
- **Web app**: extend `web/index.html` to overlay the production series
  alongside load on the same Chart.js chart (single MW axis), with Hungarian
  labels and the existing per-series toggle/persistence.

## Impact

- Modified: `sync/fetch.py`, `sync/test_sync.py`, `web/index.html`.
- New fixture: `sync/fixtures/export_4401.xlsx` (offline parse test).
- Storage: same `data/<date>.json` files gain `prod_*` keys (additive, no
  migration of existing files).
- New capability: `production-sync`. Modified capability: `load-chart`.
- Cost: unchanged ($0).

## Non-goals

- `Nettó hazai termelés tény` (4401 col E) publishes with a lag and is all-null
  inside the ±12h window in observed samples — it is mapped null-safely but not
  relied upon in v1 (same treatment as the certified load columns).
- No separate storage lane or second workflow file — one job, one commit.
- No new database, API server, or auth.

## Discipline Skills

- `observability-instrumentation` — the added external call needs per-chart
  logging so a run makes clear which charts succeeded.
- `code-simplification` — generalize to two charts without introducing a
  heavyweight registry; keep the "$0, super simple" ethos.
