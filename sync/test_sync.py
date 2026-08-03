"""Offline tests for the sync logic. Run: python -m pytest sync/test_sync.py

Uses the committed sample report/export.xlsx (no network).
"""
from pathlib import Path

import fetch

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SAMPLE = FIXTURES / "export.xlsx"
SAMPLE_4401 = FIXTURES / "export_4401.xlsx"


def _keys(colmap):
    return {v for k, v in colmap.items() if k != "A"}


def test_parse_sample():
    points = fetch.parse(SAMPLE.read_bytes())
    assert len(points) == 97
    first = points[0]
    # ISO-8601 timestamp with Budapest offset
    assert first["t"] == "2026-07-31T01:15:00+02:00"
    # load value keys present, certified columns absent
    assert _keys(fetch.LOAD_COLUMN_MAP).issubset(first.keys())
    assert "gross_certified" not in first
    # F (gross_actual) present in the past, forecast (C) present too
    assert first["gross_actual"] == 4681.422
    assert first["gross_est"] == 4654.94
    # a future row has null actuals but a forecast
    last = points[-1]
    assert last["gross_actual"] is None


def test_merge_prefers_non_null():
    existing = {"t": "x", "gross_actual": 100.0, "gross_est": None}
    fresh = {"t": "x", "gross_actual": None, "gross_est": 42.0}
    changed = fetch._merge_point(existing, fresh)
    assert changed is True
    assert existing["gross_actual"] == 100.0  # non-null NOT overwritten by null
    assert existing["gross_est"] == 42.0  # null filled from fresh


def test_merge_noop_when_nothing_new():
    existing = {"t": "x", "gross_actual": 100.0}
    fresh = {"t": "x", "gross_actual": None}
    assert fetch._merge_point(existing, fresh) is False


def test_parse_4401_production():
    points = fetch.parse(SAMPLE_4401.read_bytes(), fetch.PROD_COLUMN_MAP)
    assert len(points) == 97
    first = points[0]
    assert first["t"] == "2026-08-03T08:15:00+02:00"
    assert _keys(fetch.PROD_COLUMN_MAP).issubset(first.keys())
    # B/C/D populated, E (net actual) lagged -> null in window
    assert first["prod_gross_plan"] == 3651.43
    assert first["prod_gross_actual"] == 3348.061
    assert first["prod_net_plan"] == 3885.244
    assert first["prod_net_actual"] is None


def test_merge_combines_load_and_prod():
    # A load point and a prod point at the same timestamp merge into one.
    load = {"t": "x", "gross_actual": 100.0}
    prod = {"t": "x", "prod_gross_actual": 50.0}
    merged = dict(load)
    assert fetch._merge_point(merged, prod) is True
    assert merged == {"t": "x", "gross_actual": 100.0, "prod_gross_actual": 50.0}


def test_independent_chart_failure(tmp_path, monkeypatch):
    # 4401 fetch fails, 7678 succeeds -> load data is still upserted, run ok.
    monkeypatch.setattr(fetch, "DATA_DIR", tmp_path)

    def fake_fetch(url):
        if "chart/4401/" in url:
            raise RuntimeError("boom")
        return SAMPLE.read_bytes()

    monkeypatch.setattr(fetch, "fetch", fake_fetch)
    assert fetch.main() == 0
    written = list(tmp_path.glob("*.json"))
    assert written, "load data should be committed despite 4401 failure"
    # no prod_* keys leaked from the failed chart
    import json

    for f in written:
        for pt in json.loads(f.read_text())["points"]:
            assert not any(k.startswith("prod_") for k in pt)


def test_all_charts_failing_exits_nonzero(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        fetch, "fetch", lambda url: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    assert fetch.main() == 1


def test_window_ms_is_24h_wide():
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime(2026, 7, 31, 12, 0, tzinfo=ZoneInfo("Europe/Budapest"))
    lo, hi = fetch.window_ms(now)
    assert hi - lo == 24 * 3600 * 1000
