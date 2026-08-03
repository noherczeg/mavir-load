# sync/

Python sync job: fetch MAVIR xlsx export, normalize, upsert into `data/<date>.json`.

| File | Purpose |
|---|---|
| `fetch.py` | Entry `main()` loops `CHARTS`=((7678,`LOAD_COLUMN_MAP`),(4401,`PROD_COLUMN_MAP`)); each chart fetched independently (per-chart try/except, one failing never blocks the other), all points merged into same daily file. `window_ms()` floors now to 15-min grid, ±12h Europe/Budapest. `fetch()` retries 3x (1+2), validates ZIP magic. `parse(bytes, colmap=LOAD_COLUMN_MAP)` (openpyxl read_only) maps cols→English keys, ISO-8601 ts; load skips certified B/H, prod maps B/C/D/E→`prod_*` (E lagged/null). `upsert()` groups by Budapest date, merges by `t` preferring newer non-null (`_merge_point` iterates fresh's keys, key-set agnostic, never null-overwrites), writes iff changed. Exits non-zero only if ALL charts fail. `VALUE_KEYS`=union of both maps. See change: add-production-sync |
| `test_sync.py` | Offline pytest: `test_parse_sample` (97 load pts), `test_parse_4401_production` (97 prod pts, E null), merge prefers-non-null/noop/combines-families, `test_independent_chart_failure` (4401 fails→load still committed, no prod leak), `test_all_charts_failing_exits_nonzero`, window 24h wide. See change: add-production-sync |
| `requirements.txt` | `openpyxl>=3.1`. See change: add-mavir-load-sync |
| `fixtures/export.xlsx` | Committed 7678 load sample; offline parse fixture. See change: add-mavir-load-sync |
| `fixtures/export_4401.xlsx` | Committed 4401 production sample; offline parse fixture. See change: add-production-sync |
