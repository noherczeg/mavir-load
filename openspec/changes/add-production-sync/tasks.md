# Tasks — add-production-sync

## 1. Sync script (Python)
- [x] 1.1 Generalize `sync/fetch.py` from one `CHART_ID` to a small two-entry
      chart table `[(7678, LOAD_COLUMN_MAP), (4401, PROD_COLUMN_MAP)]`; derive
      `VALUE_KEYS` as the union of both maps' non-`t` keys. Verify: existing
      load tests still pass unchanged.
- [x] 1.2 Add `PROD_COLUMN_MAP` for 4401: B→`prod_gross_plan`,
      C→`prod_gross_actual`, D→`prod_net_plan`, E→`prod_net_actual`; A→`t`.
      Verify: parse a committed 4401 fixture, assert keys + a known value.
- [x] 1.3 Fetch each chart independently: a failed fetch/parse of one chart is
      logged and skipped, the other still upserts. Verify: unit test — a chart
      that raises on fetch leaves the other chart's points committed.
- [x] 1.4 Merge both charts' points into the same `data/<date>.json` by shared
      `t`; confirm the never-overwrite-non-null-with-null rule leaves `prod_*`
      intact when 4401 is skipped. Verify: unit test on merged output.
- [x] 1.5 Per-chart run logging (which charts succeeded, N points each).
      Verify: successful run logs a per-chart summary.

## 2. Fixtures & tests
- [x] 2.1 Commit `sync/fixtures/export_4401.xlsx` (a real 4401 export sample).
      Verify: file present, opens with openpyxl.
- [x] 2.2 Extend `sync/test_sync.py`: 4401 parse test + independent-failure
      merge test. Verify: `python -m pytest test_sync.py -q` green.

## 3. Web app (chart overlay)
- [x] 3.1 Add the four `prod_*` keys to `LABELS` (exact MAVIR Hungarian names)
      and `COLORS` in `web/index.html`. Verify: legend shows the production
      series in Hungarian.
- [x] 3.2 Set the pessimistic default production series per design decision #4
      (confirm gross-plan vs net-plan for the future segment). Verify: defaults
      match the confirmed choice.
- [x] 3.3 Add `prod_gross_actual` to the actual-key set driving the "Most"
      boundary. Verify: boundary reflects where generation actuals end.
- [x] 3.4 Confirm single MW y-axis renders both families sanely; adjust axis
      title / page header wording if broadened. Verify: chart draws locally
      against a merged sample day.

## 4. Docs
- [x] 4.1 Update `sync/AGENTS.md` and `web/AGENTS.md` rows for the two-chart
      flow and new `prod_*` series; note `data/<date>.json` gained `prod_*`
      keys in `docs`/README as needed. Update directory `AGENTS.md` per the
      Documentation Update Protocol.
