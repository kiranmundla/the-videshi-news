#!/usr/bin/env python3
"""Unit tests for flight-deals.py resume ordering + cache provenance.

Covers the 2026-10-15 stall fix: --resume runs must process routes
with missing cells first (the fixed tier order starved EWR-BOM /
IAD-DEL / ATL-DEL / BOS-DEL at the provider limit), the resume cache
TTL must span the daily boundary, and cells served from cache must
keep their true fetch date (fetched_as_of), never the reuse date.

All Duffel responses are mocked or replayed from hand-written cache
files — these tests make NO provider calls.
Run: python3 pipeline/test_flight_deals_ordering.py
"""

import importlib.util
import json
import os
import time
import unittest
from datetime import date, timedelta
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "flight_deals", Path(__file__).with_name("flight-deals.py"))
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

DURATIONS = [2, 3, 4]
MONTHS = [(2026, 10), (2026, 11), (2026, 12),
          (2027, 1), (2027, 2), (2027, 3)]
FINISHED = ["SFO-DEL", "SFO-BLR", "JFK-DEL", "JFK-BOM", "ORD-DEL",
            "DFW-HYD", "LAX-DEL", "SEA-DEL"]  # the 8 routes that complete


def route_cells(route_key, durations=DURATIONS, months=MONTHS):
    return fd.planned_cell_ids(route_key, durations, months)


def snapshot_with(cells_by_route):
    """Build a snapshot dict whose routes carry the given cell ids."""
    routes = {}
    for route_key, ids in cells_by_route.items():
        origin, dest = route_key.split("-")
        by_weeks = {}
        for cid in ids:
            _rk, ym, wk = cid.split(":")
            y, m = (int(x) for x in ym.split("-"))
            by_weeks.setdefault(wk.rstrip("w"), []).append(
                {"year": y, "month": m})
        routes[route_key] = {
            "origin": origin, "destination": dest,
            "calendar": by_weeks.get(str(fd.PRIMARY_WEEKS), []),
            "calendars_by_weeks": by_weeks,
        }
    return {"routes": routes}


class TestSnapshotCellIds(unittest.TestCase):
    def test_calendars_by_weeks(self):
        snap = snapshot_with({"SFO-DEL": route_cells("SFO-DEL")})
        self.assertEqual(fd.snapshot_cell_ids(snap),
                         route_cells("SFO-DEL"))

    def test_primary_calendar_fallback(self):
        snap = {"routes": {"SFO-DEL": {
            "calendar": [{"year": 2026, "month": 11, "weeks": 3}]}}}
        self.assertEqual(fd.snapshot_cell_ids(snap),
                         {"SFO-DEL:2026-11:3w"})

    def test_empty_and_none(self):
        self.assertEqual(fd.snapshot_cell_ids(None), set())
        self.assertEqual(fd.snapshot_cell_ids({}), set())


class TestIncompleteFirstOrdering(unittest.TestCase):
    def setUp(self):
        cells = {rk: route_cells(rk) for rk in FINISHED}
        # EWR-BOM mirrors reality: only Oct + Nov at 2w ever landed.
        cells["EWR-BOM"] = {"EWR-BOM:2026-10:2w", "EWR-BOM:2026-11:2w"}
        self.snapshot = snapshot_with(cells)

    def ordered_keys(self, snapshot, prev=None):
        ordered = fd.order_routes_incomplete_first(
            fd.ALL_ROUTES, DURATIONS, MONTHS, snapshot, prev)
        return [(f"{r[0]}-{r[1]}", m) for r, m in ordered]

    def test_never_completed_routes_go_first(self):
        keys = self.ordered_keys(self.snapshot)
        first_four = [rk for rk, _m in keys[:4]]
        # 18 missing each, original tier order among ties.
        self.assertEqual(first_four,
                         ["IAD-DEL", "ATL-DEL", "BOS-DEL", "EWR-BOM"])
        self.assertEqual([m for _rk, m in keys[:3]], [18, 18, 18])
        self.assertEqual(keys[3], ("EWR-BOM", 16))
        # The 8 finished routes follow, original order, 0 missing.
        self.assertEqual([rk for rk, _m in keys[4:]], FINISHED)
        self.assertTrue(all(m == 0 for _rk, m in keys[4:]))

    def test_prev_run_cells_count_as_done(self):
        # An aborted run finished IAD-DEL (backed by cache) but never
        # wrote a snapshot: IAD must leave the priority group.
        keys = self.ordered_keys(self.snapshot,
                                 prev=route_cells("IAD-DEL"))
        self.assertEqual(keys[0][0], "ATL-DEL")
        tail = [rk for rk, m in keys if m == 0]
        self.assertIn("IAD-DEL", tail)

    def test_no_snapshot_everything_missing_tier_order(self):
        keys = self.ordered_keys(None)
        self.assertEqual([rk for rk, _m in keys],
                         [f"{o}-{d}" for o, d, _a, _b in fd.ALL_ROUTES])
        self.assertTrue(all(m == 18 for _rk, m in keys))

    def test_complete_snapshot_keeps_tier_order(self):
        full = snapshot_with({f"{o}-{d}": route_cells(f"{o}-{d}")
                              for o, d, _a, _b in fd.ALL_ROUTES})
        keys = self.ordered_keys(full)
        self.assertEqual([rk for rk, _m in keys],
                         [f"{o}-{d}" for o, d, _a, _b in fd.ALL_ROUTES])
        self.assertTrue(all(m == 0 for _rk, m in keys))


class TestTtlDefault(unittest.TestCase):
    def test_default_ttl_spans_daily_boundary(self):
        # Module default (what main() starts from) must exceed the 24h
        # job cadence; 48h = two cycles.
        self.assertEqual(fd.RESUME_TTL_S, 48 * 3600)


QUALIFYING_OFFER = {
    "price": "900", "airline": "TestAir", "currency": "USD",
    "bags": {"checked": 2},
    "slices": [{"stops": 0, "fare_brand": "Economy"}],
}


class TestFetchedAsOfProvenance(unittest.TestCase):
    YEAR, MONTH, WEEKS = 2099, 1, 3

    def setUp(self):
        self._saved = (fd.CACHE_MODE, fd.RESUME_MODE, fd.RESUME_TTL_S,
                       fd.ABORTED, fd.run_duffel_search)
        fd.ABORTED = False
        fd.CACHE_MODE = False
        fd.RESUME_MODE = False
        dep = fd.sample_departures(self.YEAR, self.MONTH, 1,
                                   date(self.YEAR, self.MONTH, 1))[0]
        self.dep = dep
        self.ret = dep + timedelta(days=self.WEEKS * 7)
        self.cache_file = fd.cache_file_path("TST", "TST",
                                             dep.isoformat(),
                                             self.ret.isoformat())
        self.addCleanup(lambda: self.cache_file.exists()
                        and self.cache_file.unlink())

    def tearDown(self):
        (fd.CACHE_MODE, fd.RESUME_MODE, fd.RESUME_TTL_S,
         fd.ABORTED, fd.run_duffel_search) = self._saved

    def find_cell(self):
        return fd.find_cheapest_window(
            "TST", "TST", self.YEAR, self.MONTH, self.WEEKS, 1,
            date(self.YEAR, self.MONTH, 1), 0)

    def test_live_cell_dated_today(self):
        fd.run_duffel_search = lambda *a, **k: [QUALIFYING_OFFER]
        cell = self.find_cell()
        self.assertIsNotNone(cell)
        self.assertEqual(cell["fetched_as_of"], date.today().isoformat())
        self.assertEqual(cell["cache_samples"], 0)

    def test_cache_served_cell_keeps_fetch_date(self):
        # A response fetched 30h ago (beyond the old 24h TTL, within
        # the new 48h) completes the cell — dated by its FETCH date.
        fd.RESUME_MODE = True
        fd.RESUME_TTL_S = 48 * 3600
        self.cache_file.write_text(json.dumps(
            {"ok": True, "offers": [QUALIFYING_OFFER]}))
        fetched_ts = time.time() - 30 * 3600
        os.utime(self.cache_file, (fetched_ts, fetched_ts))
        cell = self.find_cell()
        self.assertIsNotNone(cell)
        self.assertEqual(cell["fetched_as_of"],
                         date.fromtimestamp(fetched_ts).isoformat())
        self.assertNotEqual(cell["fetched_as_of"],
                            date.today().isoformat())
        self.assertEqual(cell["cache_samples"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
