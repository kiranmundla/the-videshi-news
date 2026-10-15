#!/usr/bin/env python3
"""Unit tests for flight-deals.py India metros grid (2026-10-15).

Kiran's "India Metros Scroll": the full 10-origin x 5-metro India
grid. The daily core covers 12 routes; the other 38 pairs (incl. all
of CCU) refresh on a weekly rhythm via a small DAILY SLICE, so the
week's ~456 searches never hit Duffel's per-user wall in one sitting.
The slice state (pipeline/.state/flight-deals-metros-state.json) is
the durable memory that makes the slicing work across VM restarts.

All Duffel responses are mocked — NO provider calls.
Run: python3 pipeline/test_flight_deals_metros.py
"""

import importlib.util
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "flight_deals", Path(__file__).with_name("flight-deals.py"))
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

TODAY = date(2026, 10, 15)


def days_ago(n):
    return (TODAY - timedelta(days=n)).isoformat()


def snap_with(route_key, fetched):
    """Minimal snapshot dict with one route whose newest cell was
    fetched on `fetched` (None = empty calendar)."""
    cal = [] if fetched is None else [
        {"year": 2026, "month": 11, "band": "in-3wk",
         "fetched_as_of": fetched}]
    return {"routes": {route_key: {"calendar": cal}}}


class TestGridShape(unittest.TestCase):
    def test_38_grid_pairs(self):
        self.assertEqual(len(fd.METROS_ROUTES), 38)

    def test_disjoint_from_core(self):
        core = {f"{o}-{d}" for o, d, _om, _dm in fd.ALL_ROUTES}
        grid = {f"{o}-{d}" for o, d, _om, _dm in fd.METROS_ROUTES}
        self.assertEqual(len(core), 12)
        self.assertFalse(core & grid)

    def test_union_is_full_10x5_grid(self):
        core = {f"{o}-{d}" for o, d, _om, _dm in fd.ALL_ROUTES}
        grid = {f"{o}-{d}" for o, d, _om, _dm in fd.METROS_ROUTES}
        origins = {o for o, _om in fd.METROS_ORIGINS}
        dests = {d for d, _dm in fd.METROS_DESTS}
        self.assertEqual(len(origins), 10)
        self.assertEqual(dests, {"DEL", "BOM", "BLR", "HYD", "CCU"})
        self.assertEqual(core | grid,
                         {f"{o}-{d}" for o in origins for d in dests})

    def test_ccu_from_every_origin(self):
        grid = {f"{o}-{d}" for o, d, _om, _dm in fd.METROS_ROUTES}
        ccu = {k for k in grid if k.endswith("-CCU")}
        self.assertEqual(len(ccu), 10)

    def test_grid_budget_within_weekly_cap(self):
        """38 routes x 12 searches = 456 <= the ~460/week budget."""
        months = fd.rolling_months(3, TODAY + timedelta(days=2))
        keys = fd.planned_search_keys(
            fd.METROS_ROUTES, fd.BAND_INDIA, months, 2,
            fd.sample_durations(fd.BAND_INDIA, 2),
            TODAY + timedelta(days=2))
        self.assertEqual(len(keys), 456)
        self.assertLessEqual(len(keys), 460)

    def test_daily_slice_budget(self):
        """Default slice of 6 routes = 72 searches/day alongside the
        daily core's 144 — the anti-rate-wall design point."""
        self.assertEqual(fd.METROS_SLICE_SIZE * 12, 72)


class TestSliceSelection(unittest.TestCase):
    def setUp(self):
        self.routes = fd.METROS_ROUTES

    def pick(self, snapshot=None, state=None, size=6, fill=False):
        return fd.select_metros_slice(self.routes, snapshot or {},
                                      state or {"routes": {}}, TODAY,
                                      size, fill=fill)

    def keys(self, picked):
        return [f"{o}-{d}" for o, d, _om, _dm in picked]

    def test_never_attempted_all_due_first_slice(self):
        picked = self.pick()
        self.assertEqual(len(picked), 6)
        self.assertEqual(self.keys(picked),
                         self.keys(self.routes[:6]))

    def test_slice_size_zero_means_all_due(self):
        picked = self.pick(size=0)
        self.assertEqual(len(picked), 38)

    def test_fresh_snapshot_route_not_due(self):
        rk = "SFO-BOM"
        snapshot = snap_with(rk, days_ago(2))
        picked = self.keys(self.pick(snapshot=snapshot, size=0))
        self.assertNotIn(rk, picked)
        self.assertEqual(len(picked), 37)

    def test_stale_snapshot_route_due(self):
        rk = "SFO-BOM"
        snapshot = snap_with(rk, days_ago(8))
        picked = self.keys(self.pick(snapshot=snapshot, size=0))
        self.assertIn(rk, picked)

    def test_no_fares_route_rests_a_week(self):
        rk = "SFO-CCU"
        state = {"routes": {rk: {"last_attempt": days_ago(1),
                                 "outcome": "no_fares", "cells": 0,
                                 "newest_fetched": None}}}
        picked = self.keys(self.pick(state=state, size=0))
        self.assertNotIn(rk, picked)

    def test_no_fares_route_due_after_rest(self):
        rk = "SFO-CCU"
        state = {"routes": {rk: {"last_attempt": days_ago(8),
                                 "outcome": "no_fares", "cells": 0,
                                 "newest_fetched": None}}}
        picked = self.keys(self.pick(state=state, size=0))
        self.assertIn(rk, picked)

    def test_cells_outcome_without_snapshot_still_due(self):
        """The aborted-write case: the attempt computed cells but the
        snapshot never landed — the route must stay due (resume makes
        the retry cheap), NOT rest for a week."""
        rk = "LAX-BOM"
        state = {"routes": {rk: {"last_attempt": days_ago(0),
                                 "outcome": "cells", "cells": 3,
                                 "newest_fetched": days_ago(0)}}}
        picked = self.keys(self.pick(state=state, size=0))
        self.assertIn(rk, picked)

    def test_never_attempted_beats_stale(self):
        """Work order: brand-new routes before stale refreshes."""
        stale_rk = "SFO-BOM"
        snapshot = snap_with(stale_rk, days_ago(9))
        picked = self.keys(self.pick(snapshot=snapshot, size=0))
        self.assertEqual(picked[-1], stale_rk)

    def test_fill_mode_same_day_no_fares_rests(self):
        rk = "SFO-CCU"
        state = {"routes": {rk: {"last_attempt": TODAY.isoformat(),
                                 "outcome": "no_fares", "cells": 0,
                                 "newest_fetched": None}}}
        picked = self.keys(self.pick(state=state, size=0, fill=True))
        self.assertNotIn(rk, picked)

    def test_fill_mode_old_no_fares_retried(self):
        """Fill mode ignores the 7-day rest for OLD no-fare results —
        the rolling window moved, so the fill gives them one fresh
        shot today."""
        rk = "SFO-CCU"
        state = {"routes": {rk: {"last_attempt": days_ago(3),
                                 "outcome": "no_fares", "cells": 0,
                                 "newest_fetched": None}}}
        picked = self.keys(self.pick(state=state, size=0, fill=True))
        self.assertIn(rk, picked)


class TestStatePersistence(unittest.TestCase):
    def test_attempt_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metros-state.json"
            cal = [{"fetched_as_of": "2026-10-14"},
                   {"fetched_as_of": "2026-10-15"}]
            fd.record_metros_attempt("SFO-CCU", cal, "2026-10-15",
                                     path=path)
            fd.record_metros_attempt("SFO-BOM", [], "2026-10-15",
                                     path=path)
            state = fd.load_metros_state(path)
            rec = state["routes"]["SFO-CCU"]
            self.assertEqual(rec["outcome"], "cells")
            self.assertEqual(rec["cells"], 2)
            self.assertEqual(rec["newest_fetched"], "2026-10-15")
            self.assertEqual(state["routes"]["SFO-BOM"]["outcome"],
                             "no_fares")

    def test_missing_state_file_is_empty(self):
        state = fd.load_metros_state(Path("/nonexistent/x.json"))
        self.assertEqual(state, {"routes": {}})

    def test_corrupt_state_file_is_empty(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metros-state.json"
            path.write_text("{not json")
            self.assertEqual(fd.load_metros_state(path), {"routes": {}})


class TestSnapshotFreshness(unittest.TestCase):
    def test_newest_cell_date_wins(self):
        snapshot = {"routes": {"SFO-BOM": {"calendar": [
            {"fetched_as_of": "2026-10-10"},
            {"fetched_as_of": "2026-10-12"},
            {"fetched_as_of": "2026-10-11"},
        ]}}}
        self.assertEqual(
            fd.snapshot_route_freshness(snapshot)["SFO-BOM"],
            "2026-10-12")

    def test_empty_calendar_is_none(self):
        snapshot = {"routes": {"SFO-BOM": {"calendar": []}}}
        self.assertIsNone(
            fd.snapshot_route_freshness(snapshot)["SFO-BOM"])

    def test_empty_snapshot(self):
        self.assertEqual(fd.snapshot_route_freshness(None), {})
        self.assertEqual(fd.snapshot_route_freshness({}), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
