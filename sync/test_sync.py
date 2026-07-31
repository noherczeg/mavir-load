"""Offline tests for the sync logic. Run: python -m pytest sync/test_sync.py

Uses the committed sample report/export.xlsx (no network).
"""
from pathlib import Path

import fetch

SAMPLE = Path(__file__).resolve().parent / "fixtures" / "export.xlsx"


def test_parse_sample():
    points = fetch.parse(SAMPLE.read_bytes())
    assert len(points) == 97
    first = points[0]
    # ISO-8601 timestamp with Budapest offset
    assert first["t"] == "2026-07-31T01:15:00+02:00"
    # value keys present, certified columns absent
    assert set(fetch.VALUE_KEYS).issubset(first.keys())
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


def test_window_ms_is_24h_wide():
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime(2026, 7, 31, 12, 0, tzinfo=ZoneInfo("Europe/Budapest"))
    lo, hi = fetch.window_ms(now)
    assert hi - lo == 24 * 3600 * 1000
