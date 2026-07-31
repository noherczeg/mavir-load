# Add MAVIR load sync + interactive chart

## Why

MAVIR publishes Hungarian grid system-load data (actuals + day-ahead forecasts)
as an unauthenticated xlsx export at 15-minute resolution. We want a durable,
queryable history of this data and a public interactive chart — hosted as
cheaply as possible (target: $0). Because the endpoint needs no auth and the
payload is tiny (~9.5 KB per pull), no server is required: GitHub Actions can be
the scheduler + compute, the git repo is the storage, and GitHub Pages serves
the chart.

## What Changes

- **Sync job** (Python, run by GitHub Actions cron every 30 min): fetch the
  xlsx for the previous 12h + next 12h, retry up to 2 times on failure, parse,
  normalize, and upsert into `data/<date>.json`. Commit only when data changed.
- **Storage**: versioned JSON under `data/`, one file per calendar day
  (Europe/Budapest). Upsert by timestamp, preferring newer non-null values so
  actuals never get overwritten by nulls/estimates. No RDBMS, no SQLite.
- **Web app**: static GitHub Pages site (uPlot) that fetches the JSON and draws
  an interactive time-series chart. All user-facing labels in Hungarian. Default
  series follow the "pessimistic for humans" rule (max load, min generation).

## Impact

- New: `sync/` (Python sync script), `data/` (generated JSON), `web/` (static
  chart), `.github/workflows/sync.yml`.
- New capabilities: `load-sync`, `load-chart`.
- No existing code affected (greenfield repo).
- Cost: $0 (public repo → unlimited Actions minutes + free Pages).

## Non-goals

- Certified/final columns (`Bruttó hitelesített`, `Nettó certified`) are skipped
  in v1 — MAVIR publishes them with a multi-day lag, outside the ±12h window.
  A future backfill job can add them.
- No alerting beyond GitHub's built-in workflow-failure email.
- No database, API server, or auth.

## Discipline Skills

- `observability-instrumentation` — the sync job is an external-call cron; it
  needs enough logging/failure signal to tell what happened in a run.
- `code-simplification` — keep the stack lean per the "$0, super simple" goal.
