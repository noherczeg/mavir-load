# sync/

Python sync job: fetch MAVIR xlsx export, normalize, upsert into `data/<date>.json`.

| File | Purpose |
|---|---|
| `fetch.py` | Entry `main()`. `window_ms()` floors now to 15-min grid, ±12h in Europe/Budapest. `fetch()` retries 3x (1+2), validates ZIP magic. `parse()` (openpyxl, read_only) maps cols F/C/I/J/K/D/E/G→English keys via `COLUMN_MAP`, ISO-8601 timestamps, skips certified B/H. `upsert()` groups by Budapest date, merges by `t` preferring newer non-null (`_merge_point` never null-overwrites), writes iff changed. Exits non-zero on fetch/parse failure. See change: add-mavir-load-sync |
| `test_sync.py` | Offline pytest: `test_parse_sample` (97 pts from fixture), merge prefers-non-null + noop, window is 24h wide. See change: add-mavir-load-sync |
| `requirements.txt` | `openpyxl>=3.1`. See change: add-mavir-load-sync |
| `fixtures/export.xlsx` | Committed sample export used as offline parse fixture. See change: add-mavir-load-sync |
