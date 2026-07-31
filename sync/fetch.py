#!/usr/bin/env python3
"""Fetch the MAVIR grid-load xlsx export and upsert it into versioned daily JSON.

Runs from GitHub Actions every 30 minutes. Pulls the previous 12h + next 12h
window (Europe/Budapest), retries on failure, parses the xlsx, normalizes rows,
and merges them into data/<YYYY-MM-DD>.json preferring newer non-null values.

Stdlib only for I/O; openpyxl for xlsx parsing.
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

TZ = ZoneInfo("Europe/Budapest")
CHART_ID = 7678
BASE_URL = f"https://rtdwweb.mavir.hu/rtdwweb/webuser/chart/{CHART_ID}/export"
WINDOW = timedelta(hours=12)
MAX_ATTEMPTS = 3  # 1 initial + 2 retries
RETRY_BACKOFF_S = 5
TIMEOUT_S = 30

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# xlsx column letter -> normalized key. B (gross_certified) and H (net_certified)
# are intentionally skipped in v1 (published with multi-day lag, outside window).
COLUMN_MAP = {
    "A": "t",
    "C": "gross_est",
    "D": "net_plan_gen",
    "E": "net_plan_load",
    "F": "gross_actual",
    "G": "gross_plan",
    "I": "net_load",
    "J": "net_actual",
    "K": "net_est",
}
VALUE_KEYS = [v for k, v in COLUMN_MAP.items() if k != "A"]


def log(msg: str) -> None:
    print(f"[mavir-sync] {msg}", flush=True)


def window_ms(now: datetime | None = None) -> tuple[int, int]:
    """Return (fromTime, toTime) epoch-ms for now-12h .. now+12h in Budapest.

    `now` is floored to the 15-minute grid so the export's bins land on clean
    quarter-hour boundaries and align across runs (stable timestamps => upsert
    merges instead of accumulating near-duplicate points).
    """
    now = now or datetime.now(TZ)
    now = now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)
    from_ms = int((now - WINDOW).timestamp() * 1000)
    to_ms = int((now + WINDOW).timestamp() * 1000)
    return from_ms, to_ms


def build_url(from_ms: int, to_ms: int) -> str:
    return (
        f"{BASE_URL}?exportType=xlsx&fromTime={from_ms}&toTime={to_ms}"
        f"&periodType=min&period=15"
    )


def fetch(url: str) -> bytes:
    """Fetch the xlsx with retries. Raises RuntimeError after all attempts fail."""
    last_err: str = "unknown"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mavir-load-sync"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                body = resp.read()
            # Validate it is an xlsx (ZIP magic) before accepting.
            if not body.startswith(b"PK"):
                raise RuntimeError("body is not an xlsx (bad magic)")
            log(f"fetch ok on attempt {attempt} ({len(body)} bytes)")
            return body
        except (urllib.error.URLError, RuntimeError, TimeoutError, OSError) as exc:
            last_err = str(exc)
            log(f"fetch attempt {attempt}/{MAX_ATTEMPTS} failed: {last_err}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_S)
    raise RuntimeError(f"fetch failed after {MAX_ATTEMPTS} attempts: {last_err}")


def _norm_ts(raw: str) -> str:
    """'2026.07.31 01:15:00 +0200' -> ISO-8601 '2026-07-31T01:15:00+02:00'."""
    dt = datetime.strptime(raw.strip(), "%Y.%m.%d %H:%M:%S %z")
    return dt.isoformat()


def parse(xlsx_bytes: bytes) -> list[dict]:
    """Parse the export into a list of normalized points (ISO ts + value keys)."""
    wb = load_workbook(io.BytesIO(xlsx_bytes), read_only=True, data_only=True)
    ws = wb.active
    points: list[dict] = []
    for r, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if r == 1:
            continue  # header
        cell_by_col = {get_column_letter(i): v for i, v in enumerate(row, start=1)}
        raw_t = cell_by_col.get("A")
        if raw_t in (None, ""):
            continue
        point: dict = {"t": _norm_ts(str(raw_t))}
        for col, key in COLUMN_MAP.items():
            if key == "t":
                continue
            v = cell_by_col.get(col)
            point[key] = None if v in (None, "") else float(v)
        points.append(point)
    wb.close()
    return points


def _local_date(iso_ts: str) -> str:
    return datetime.fromisoformat(iso_ts).astimezone(TZ).date().isoformat()


def _merge_point(existing: dict, fresh: dict) -> bool:
    """Fill null fields in `existing` from `fresh`. Never overwrite non-null with
    null. Returns True if anything changed."""
    changed = False
    for key in VALUE_KEYS:
        new_val = fresh.get(key)
        if new_val is None:
            continue
        # Fill nulls and pick up genuinely changed values; never null-out.
        if existing.get(key) != new_val:
            existing[key] = new_val
            changed = True
    return changed


def upsert(points: list[dict]) -> list[Path]:
    """Merge points into data/<date>.json files. Returns changed file paths."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    by_date: dict[str, list[dict]] = {}
    for p in points:
        by_date.setdefault(_local_date(p["t"]), []).append(p)

    changed_files: list[Path] = []
    for date, day_points in by_date.items():
        path = DATA_DIR / f"{date}.json"
        if path.exists():
            doc = json.loads(path.read_text(encoding="utf-8"))
            index = {pt["t"]: pt for pt in doc["points"]}
        else:
            doc = {"date": date, "tz": "Europe/Budapest", "points": []}
            index = {}

        changed = False
        for fresh in day_points:
            cur = index.get(fresh["t"])
            if cur is None:
                index[fresh["t"]] = dict(fresh)
                changed = True
            elif _merge_point(cur, fresh):
                changed = True

        if not changed:
            continue

        doc["points"] = [index[t] for t in sorted(index)]
        doc["updated"] = datetime.now(TZ).isoformat()
        path.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        changed_files.append(path)
    return changed_files


def main() -> int:
    from_ms, to_ms = window_ms()
    url = build_url(from_ms, to_ms)
    log(f"window {from_ms}..{to_ms}")
    try:
        body = fetch(url)
        points = parse(body)
    except Exception as exc:  # noqa: BLE001 - top-level run guard
        log(f"RUN FAILED: {exc}")
        return 1
    log(f"parsed {len(points)} points")
    changed = upsert(points)
    if changed:
        log(f"changed {len(changed)} file(s): {', '.join(p.name for p in changed)}")
    else:
        log("no data changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
