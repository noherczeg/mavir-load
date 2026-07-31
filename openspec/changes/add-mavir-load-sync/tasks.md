# Tasks — add-mavir-load-sync

## 1. Sync script (Python)
- [x] 1.1 Write `sync/fetch.py`: compute ±12h window in `Europe/Budapest`, build
      the export URL, fetch with 3-attempt retry (1 + 2), fail non-zero on
      exhaustion. Verify: run against the live endpoint, confirm a 200 xlsx.
- [x] 1.2 Parse the xlsx (`openpyxl`), map columns F/C/I/J/K/D/E/G → English
      keys, normalize timestamps to ISO-8601, empty cells → `null`, ignore B/H.
      Verify: parse `report/export.xlsx`, assert 97 points and correct keys.
- [x] 1.3 Upsert into `data/<date>.json` by timestamp, prefer newer non-null,
      never overwrite non-null with null, keep chronological order.
      Verify: unit test — second merge with a null field leaves the prior value.
- [x] 1.4 Log run outcome (fetched N points, changed files) and exit codes.
      Verify: successful run logs a summary; forced failure exits non-zero.

## 2. Scheduling (GitHub Actions)
- [x] 2.1 Add `.github/workflows/sync.yml`: cron `*/30 * * * *` + manual
      dispatch, set up Python, run `sync/fetch.py`, `git commit` only if
      `data/` changed, push. Verify: manual dispatch produces/updates a
      `data/*.json` commit.
- [x] 2.2 Confirm workflow-failure email/notification path (built-in).
      Verify: a deliberately failing run reports failure in the Actions UI.

## 3. Web app (GitHub Pages + uPlot)
- [x] 3.1 `web/index.html` + uPlot: fetch `data/<date>.json`, render the
      time-series chart. Verify: open locally against a sample file, chart draws.
- [x] 3.2 Mark the present-moment boundary (last non-null actual) with a "Most"
      line. Verify: boundary aligns with where actuals end.
- [x] 3.3 Default series = pessimistic (`gross_actual`→`gross_est` consumption,
      `net_plan_gen` production); other series toggleable. Verify: defaults match.
- [x] 3.4 Hungarian `labels.hu` map for all axis/legend/tooltip/marker strings.
      Verify: no English visible in the UI.
- [ ] 3.5 Enable GitHub Pages  (manual: GitHub Settings → Pages, after first push) on the repo. Verify: public URL renders the chart.

## 4. Docs
- [x] 4.1 README: what it does, the $0 architecture, how to run the sync
      locally, Pages URL. Update directory `AGENTS.md` rows for new files.
