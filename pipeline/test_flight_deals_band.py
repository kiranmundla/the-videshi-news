#!/usr/bin/env python3
"""Unit tests for flight-deals.py Phase 1 band scope (2026-10-15).

Kiran's scope: rolling 3 months, ONE duration band per market —
India ~3-week trips (sample inside 19-23 days), international
~1-week trips (5-9 days) — cheapest fare in the band wins and the
cell reports the winning trip's actual dates + duration_days.
The international matrix is a separate market with separate files.

All Duffel responses are mocked — NO provider calls.
Run: python3 pipeline/test_flight_deals_band.py
"""

import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "flight_deals", Path(__file__).with_name("flight-deals.py"))
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

MIN_DATE = date(2026, 10, 17)
MONTHS = fd.rolling_months(3, MIN_DATE)


def offer(price, airline="TestAir"):
    return {"price": str(price), "airline": airline, "currency": "USD",
            "bags": {"checked": 2},
            "slices": [{"stops": 0, "fare_brand": "Economy"}]}


class TestSampleDurations(unittest.TestCase):
    def test_india_band_spread(self):
        self.assertEqual(fd.sample_durations(fd.BAND_INDIA, 2), [20, 22])

    def test_intl_band_spread(self):
        self.assertEqual(fd.sample_durations(fd.BAND_INTL, 2), [6, 8])

    def test_single_sample_is_band_center(self):
        self.assertEqual(fd.sample_durations(fd.BAND_INDIA, 1), [21])
        self.assertEqual(fd.sample_durations(fd.BAND_INTL, 1), [7])

    def test_samples_stay_inside_band(self):
        for band in (fd.BAND_INDIA, fd.BAND_INTL):
            for n in (1, 2, 3, 5, 9):
                picked = fd.sample_durations(band, n)
                self.assertTrue(all(
                    band["min_days"] <= d <= band["max_days"]
                    for d in picked))


class TestPlannedCounts(unittest.TestCase):
    """The budget shape Kiran approved: India 144/day, intl 480/week."""

    def test_india_matrix_is_144(self):
        keys = fd.planned_search_keys(
            fd.ALL_ROUTES, fd.BAND_INDIA, MONTHS, 2,
            fd.sample_durations(fd.BAND_INDIA, 2), MIN_DATE)
        self.assertEqual(len(keys), 12 * 3 * 2 * 2)

    def test_intl_matrix_is_480(self):
        keys = fd.planned_search_keys(
            fd.INTL_ROUTES, fd.BAND_INTL, MONTHS, 2,
            fd.sample_durations(fd.BAND_INTL, 2), MIN_DATE)
        self.assertEqual(len(keys), 40 * 3 * 2 * 2)

    def test_planned_keys_use_band_durations(self):
        keys = fd.planned_search_keys(
            [("SFO", "DEL", "Bay Area", "Delhi")], fd.BAND_INDIA,
            [(2026, 11)], 2, [20, 22], MIN_DATE)
        spans = {(date.fromisoformat(r) - date.fromisoformat(d)).days
                 for _o, _d, d, r in keys}
        self.assertEqual(spans, {20, 22})


class TestBandCellSelection(unittest.TestCase):
    def setUp(self):
        self._saved = (fd.CACHE_MODE, fd.RESUME_MODE, fd.ABORTED,
                       fd.run_duffel_search)
        fd.CACHE_MODE = False
        fd.RESUME_MODE = False
        fd.ABORTED = False

    def tearDown(self):
        (fd.CACHE_MODE, fd.RESUME_MODE, fd.ABORTED,
         fd.run_duffel_search) = self._saved

    def test_cheapest_across_band_wins_with_its_own_duration(self):
        # Longer trip cheaper: 22d -> $800, 20d -> $950. The cell must
        # be the 22-day trip, labelled 22 — not a generic "3 weeks".
        def fake_search(origin, dest, dep, ret):
            days = (date.fromisoformat(ret)
                    - date.fromisoformat(dep)).days
            return [offer(950 if days == 20 else 800)]
        fd.run_duffel_search = fake_search
        cell = fd.find_cheapest_window(
            "SFO", "DEL", 2026, 11, fd.BAND_INDIA, 2, [20, 22],
            MIN_DATE, 0)
        self.assertIsNotNone(cell)
        self.assertEqual(cell["price_min"], 800)
        self.assertEqual(cell["duration_days"], 22)
        span = (date.fromisoformat(cell["ret_date"])
                - date.fromisoformat(cell["dep_date"])).days
        self.assertEqual(span, 22)
        self.assertEqual(cell["band"], "in-3wk")
        self.assertNotIn("weeks", cell)

    def test_all_band_durations_are_searched(self):
        seen = []

        def fake_search(origin, dest, dep, ret):
            seen.append((dep, ret))
            return [offer(1000)]
        fd.run_duffel_search = fake_search
        fd.find_cheapest_window("SFO", "SYD", 2026, 11, fd.BAND_INTL,
                                 2, [6, 8], MIN_DATE, 0)
        spans = {(date.fromisoformat(r) - date.fromisoformat(d)).days
                 for d, r in seen}
        self.assertEqual(spans, {6, 8})
        self.assertEqual(len(seen), 4)  # 2 departures x 2 durations


class TestHistoryKeys(unittest.TestCase):
    def test_band_records_key_on_band(self):
        rec = {"route": "SFO-DEL", "year": 2026, "month": 11,
               "band": "in-3wk", "duration_days": 22}
        self.assertEqual(fd.cell_key(rec),
                         ("SFO-DEL", 2026, 11, "in-3wk"))

    def test_legacy_records_never_match_band_cells(self):
        legacy = {"route": "SFO-DEL", "year": 2026, "month": 11,
                  "weeks": 3}
        band = {"route": "SFO-DEL", "year": 2026, "month": 11,
                "band": "in-3wk", "duration_days": 21}
        self.assertNotEqual(fd.cell_key(legacy), fd.cell_key(band))
        # ...so a legacy baseline produces no change annotation and
        # no drop for the first band snapshot (honest restart).
        cell = dict(band, price_min=900, route="SFO-DEL",
                    date_range="x", origin_metro="Bay Area",
                    dest_metro="Delhi", cheapest_airline="TestAir")
        drops = fd.compute_changes([cell], [dict(
            legacy, price_min=1200, as_of="2026-10-14")])
        self.assertEqual(drops, [])
        self.assertNotIn("change_vs_prev", cell)


class TestIntlMarketSeparation(unittest.TestCase):
    def test_intl_files_are_separate(self):
        self.assertEqual(fd.INTL_OUTPUT_FILE.name,
                         "flight-deals-intl.json")
        self.assertNotEqual(fd.INTL_OUTPUT_FILE, fd.OUTPUT_FILE)
        self.assertNotEqual(fd.INTL_HISTORY_FILE, fd.HISTORY_FILE)
        self.assertNotEqual(fd.INTL_RUN_STATE_FILE, fd.RUN_STATE_FILE)

    def test_intl_routes_cover_trending_top8(self):
        dests = {d for _o, d, _om, _dm in fd.INTL_ROUTES}
        self.assertEqual(dests, {"SYD", "DPS", "SJD", "CAI", "NAN",
                                 "CDG", "ATH", "HNL"})
        origins = {o for o, _d, _om, _dm in fd.INTL_ROUTES}
        self.assertEqual(origins, {"SFO", "LAX", "JFK", "ORD", "DFW"})
        self.assertEqual(len(fd.INTL_ROUTES), 40)
        # Destination slug mapping for the destinations builder.
        self.assertEqual(fd.INTL_AIRPORT_SLUG["SYD"], "australia")
        self.assertEqual(fd.INTL_AIRPORT_SLUG["HNL"], "hawaii")


if __name__ == "__main__":
    unittest.main(verbosity=2)
