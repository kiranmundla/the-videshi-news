#!/usr/bin/env python3
"""Tests for the search-interest signal + LIVE trending
(fetch-search-interest.py + build-travel-destinations.py).

The shadow pilot flipped LIVE on 2026-10-15 (Kiran: "Flip to real
trending now, with those conditions"): compute_live_ranking() is the
production scoring, and the builder additionally writes a legacy
(pre-flip) comparison artifact for the Nov 9 review checkpoint.

NO network: momentum math runs on synthetic series; the scoring tests
use fabricated records; the determinism test runs the real builder
against local data files only.

Run: python3 pipeline/test_search_interest.py
"""

import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

PIPELINE = Path(__file__).parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, PIPELINE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fsi = load_module("fetch_search_interest", "fetch-search-interest.py")
btd = load_module("build_travel_destinations", "build-travel-destinations.py")


def daily_series(prior_value, recent_value, end=date(2026, 10, 14)):
    """84 prior days at prior_value, then 28 recent days at recent_value."""
    out = {}
    start = end - timedelta(days=111)
    for i in range(112):
        d = start + timedelta(days=i)
        out[d] = prior_value if i < 84 else recent_value
    return out


class MomentumMath(unittest.TestCase):
    def test_rising_series(self):
        m = fsi.compute_momentum(daily_series(100, 150))
        self.assertIsNotNone(m)
        self.assertAlmostEqual(m["momentum"], 0.5, places=6)
        self.assertAlmostEqual(m["recent_mean"], 150.0)
        self.assertAlmostEqual(m["prior_mean"], 100.0)

    def test_flat_series(self):
        m = fsi.compute_momentum(daily_series(100, 100))
        self.assertAlmostEqual(m["momentum"], 0.0, places=6)

    def test_falling_series(self):
        m = fsi.compute_momentum(daily_series(200, 100))
        self.assertAlmostEqual(m["momentum"], -0.5, places=6)

    def test_thin_coverage_is_null(self):
        thin = {date(2026, 10, 14) - timedelta(days=i): 100
                for i in range(10)}
        self.assertIsNone(fsi.compute_momentum(thin))

    def test_zero_prior_is_null(self):
        self.assertIsNone(fsi.compute_momentum(daily_series(0, 100)))

    def test_empty_is_null(self):
        self.assertIsNone(fsi.compute_momentum({}))

    def test_weekly_series_momentum(self):
        values = [50.0] * 16 + [100.0] * 4
        self.assertAlmostEqual(fsi.momentum_from_weekly(values), 1.0)
        self.assertIsNone(fsi.momentum_from_weekly([50.0] * 10))
        self.assertIsNone(fsi.momentum_from_weekly(None))


def make_record(slug, name, season_pts=50, value_pts=15, fare_pts=None,
                fare_from=None):
    return {
        "slug": slug, "name": name, "eligible_for_picks": True,
        "fare_from": fare_from,
        "trending": {"components": [
            {"id": "season_fit", "points": season_pts, "max": 50,
             "reason": "test"},
            {"id": "offpeak_value", "points": value_pts, "max": 20,
             "reason": "test"},
            {"id": "fare_drop", "points": fare_pts, "max": 30,
             "reason": "test"},
        ]},
    }


class LiveScoring(unittest.TestCase):
    def test_component_rescaling_and_null_fare(self):
        rec = make_record("aaa", "Aaa")  # season 50, value 15, fare null
        search = {"destinations": {"aaa": {
            "wiki": {"momentum": 0.0, "recent_mean": 1000.0},
            "trends": None}}}
        _, ranking, _ = btd.compute_live_ranking([rec], search)
        top = ranking[0]
        comps = {c["id"]: c for c in top["components"]}
        self.assertEqual(comps["season_fit"]["points"], 40)      # 50→40
        self.assertEqual(comps["offpeak_value"]["points"], 8)    # 15→8
        self.assertIsNone(comps["fare_drop"]["points"])          # null stays
        # Flat wiki momentum, single-entry cohort (no level spread):
        # level 0 + round(15 * 0.5) = 8
        self.assertEqual(comps["search_interest"]["points"], 8)
        self.assertEqual(top["max_score"], 40 + 30 + 10)         # no fare max
        self.assertEqual(top["signal_source"], "wikimedia")

    def test_flat_wiki_momentum_points(self):
        # Two-destination cohort so the level normalization is defined.
        recs = [make_record("aaa", "Aaa"), make_record("bbb", "Bbb")]
        search = {"destinations": {
            "aaa": {"wiki": {"momentum": 0.0, "recent_mean": 1000.0},
                    "trends": None},
            "bbb": {"wiki": {"momentum": 0.0, "recent_mean": 100.0},
                    "trends": None}}}
        _, ranking, _ = btd.compute_live_ranking(recs, search)
        by_slug = {r["slug"]: r for r in ranking}
        comp = {c["id"]: c for c in by_slug["aaa"]["components"]}
        # level: aaa is cohort max → 15; momentum flat → round(15*0.5)=8
        self.assertEqual(comp["search_interest"]["points"], 23)
        comp_b = {c["id"]: c for c in by_slug["bbb"]["components"]}
        self.assertEqual(comp_b["search_interest"]["points"], 8)  # level 0 + 8

    def test_trends_preferred_over_wiki(self):
        rec = make_record("aaa", "Aaa")
        search = {"destinations": {"aaa": {
            "wiki": {"momentum": -0.4, "recent_mean": 1000.0},
            "trends": {"blended_momentum": 0.5,
                       "us_momentum": 0.5, "in_momentum": 0.5}}}}
        _, ranking, _ = btd.compute_live_ranking([rec], search)
        top = ranking[0]
        comp = {c["id"]: c for c in top["components"]}
        self.assertEqual(top["signal_source"], "google-trends")
        self.assertEqual(comp["search_interest"]["points"], 30)  # +50% → full

    def test_no_search_data_is_null_component(self):
        rec = make_record("aaa", "Aaa")
        _, ranking, _ = btd.compute_live_ranking([rec], {"destinations": {}})
        comp = {c["id"]: c for c in ranking[0]["components"]}
        self.assertIsNone(comp["search_interest"]["points"])
        self.assertEqual(ranking[0]["max_score"], 40 + 20 * 0 + 10)  # 50
        self.assertIsNone(ranking[0]["signal_source"])

    def test_fare_points_rescaled(self):
        rec = make_record("aaa", "Aaa", fare_pts=30,
                          fare_from={"price_min": 900})
        _, ranking, _ = btd.compute_live_ranking([rec], {"destinations": {}})
        comp = {c["id"]: c for c in ranking[0]["components"]}
        self.assertEqual(comp["fare_drop"]["points"], 20)        # 30→20
        self.assertEqual(ranking[0]["max_score"], 40 + 10 + 20)   # search null

    def test_tie_break_fare_then_search_then_name(self):
        # Same score for all three: fare-backed wins; then search-backed;
        # then alphabetical as documented last resort.
        plain = make_record("ccc", "Ccc")
        fare = make_record("bbb", "Bbb", fare_pts=None,
                           fare_from={"price_min": 900})
        # Bbb has fare data but the same total: give it fare_pts 0 so its
        # score equals the others' (fare 0 rescaled = 0).
        fare["trending"]["components"][2]["points"] = 0
        _, ranking, _ = btd.compute_live_ranking([plain, fare], {"destinations": {}})
        self.assertEqual(ranking[0]["slug"], "bbb")   # fare data breaks tie
        self.assertEqual(ranking[1]["slug"], "ccc")

        a = make_record("aaa", "Aaa")
        b = make_record("bbb2", "Bbb")
        _, ranking, _ = btd.compute_live_ranking([b, a], {"destinations": {}})
        self.assertEqual([r["slug"] for r in ranking], ["aaa", "bbb2"])

    def test_live_records_not_mutated(self):
        rec = make_record("aaa", "Aaa")
        before = json.dumps(rec, sort_keys=True)
        btd.compute_live_ranking([rec], {"destinations": {}})
        self.assertEqual(json.dumps(rec, sort_keys=True), before)


class LiveDeterminism(unittest.TestCase):
    """Post-flip invariants for the real builder:
    - the live file is deterministic (byte-identical across runs);
    - the legacy-comparison artifact is a pure side output — deleting
      it changes nothing about the live file, and it is recreated;
    - the artifact's live stats agree with the live file it shipped
      with (its top8 IS the live trending_now top 8).
    (The pilot-era invariant "live output must not depend on the
    search-interest input" died with the flip BY DESIGN — the signal
    is the ranking now.)"""

    def test_live_output_deterministic(self):
        repo = PIPELINE.parent
        live_file = repo / "public" / "data" / "travel-destinations.json"
        original_live = live_file.read_bytes()
        try:
            subprocess.run([sys.executable, "-u",
                            str(PIPELINE / "build-travel-destinations.py")],
                           check=True, capture_output=True, text=True)
            run1 = live_file.read_bytes()
            self.assertTrue(btd.SHADOW_FILE.exists(),
                            "legacy comparison artifact should be written")
            comparison = json.loads(btd.SHADOW_FILE.read_text())
            live = json.loads(run1)
            self.assertEqual(comparison["stats"]["top8"],
                             live["trending_now"][:8],
                             "comparison artifact's live top8 disagrees "
                             "with the live file")
            self.assertIn("legacy_top8", comparison)
            # Run 2: comparison artifact deleted — live must not move.
            btd.SHADOW_FILE.unlink()
            subprocess.run([sys.executable, "-u",
                            str(PIPELINE / "build-travel-destinations.py")],
                           check=True, capture_output=True, text=True)
            run2 = live_file.read_bytes()
            self.assertEqual(run1, run2,
                             "live travel-destinations.json is not "
                             "deterministic across runs")
            self.assertTrue(btd.SHADOW_FILE.exists(),
                            "legacy comparison artifact not recreated")
        finally:
            # Restore the production state: rebuild once more and put
            # back the exact live bytes this test started from.
            subprocess.run([sys.executable, "-u",
                            str(PIPELINE / "build-travel-destinations.py")],
                           check=True, capture_output=True, text=True)
            live_file.write_bytes(original_live)


if __name__ == "__main__":
    unittest.main(verbosity=2)
