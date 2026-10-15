#!/usr/bin/env python3
"""Unit tests for flight-deals.py query pacing (Kiran, 2026-10-15:
"Let's pace our queries").

All Duffel responses are mocked and the clock is fake — these tests
make NO provider calls and never really sleep.
Run: python3 pipeline/test_flight_deals_pacing.py
"""

import importlib.util
import json
import os
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

spec = importlib.util.spec_from_file_location(
    "flight_deals", Path(__file__).with_name("flight-deals.py"))
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

# The exact per-user limit payload observed live on 2026-10-15.
LIMIT_PAYLOAD = {
    "broker_error": True,
    "offer_request_id": "orq_test",
    "ok": False,
    "response": {"error": "per-user connector request limit exceeded"},
    "retriable": False,
    "retry_after": "60",
    "status": 429,
}

OK_PAYLOAD = {"ok": True, "offers": [{"price": "999"}]}

QUALIFYING_OFFER = {
    "price": "999",
    "airline": "Test Air",
    "currency": "USD",
    "bags": {"checked": 2},
    "slices": [{"stops": 0, "fare_brand": "Economy"}],
}


class FakeClock:
    """Monotonic clock whose sleep() records and advances time."""

    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def advance(self, seconds):
        self.now += seconds


class PacingTestBase(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self._saved = (fd.PACER, fd.SLEEP_FN, fd.NOW_FN, fd.PAUSES,
                       fd.JITTER_FN, fd.REQUEST_COUNT, fd.FAILED_COUNT,
                       fd.RESUMED_COUNT, fd.ABORTED, fd.ABORT_REASON,
                       fd.CACHE_MODE, fd.RESUME_MODE, fd.RESUME_TTL_S)
        fd.SLEEP_FN = self.clock.sleep
        fd.NOW_FN = self.clock.monotonic
        fd.JITTER_FN = lambda: 0.0
        fd.PAUSES = fd.PauseBudget(max_pauses=10, max_total_wait_s=1200)
        fd.REQUEST_COUNT = 0
        fd.FAILED_COUNT = 0
        fd.RESUMED_COUNT = 0
        fd.ABORTED = False
        fd.ABORT_REASON = None

    def tearDown(self):
        (fd.PACER, fd.SLEEP_FN, fd.NOW_FN, fd.PAUSES, fd.JITTER_FN,
         fd.REQUEST_COUNT, fd.FAILED_COUNT, fd.RESUMED_COUNT, fd.ABORTED,
         fd.ABORT_REASON, fd.CACHE_MODE, fd.RESUME_MODE,
         fd.RESUME_TTL_S) = self._saved

    def fake_run_factory(self, payloads, starts):
        """A subprocess.run stand-in: records the (fake) start time of
        each attempt and writes the next payload to the stdout file."""
        it = iter(payloads)

        def fake_run(cmd, stdout=None, stderr=None, timeout=None):
            starts.append(self.clock.now)
            stdout.write(json.dumps(next(it)))
            stdout.flush()
            return SimpleNamespace(returncode=0, stderr=b"")

        return fake_run

    def use_cache_file(self, origin, dest, dep, ret, payload):
        tmp = fd.cache_file_path(origin, dest, dep, ret)
        tmp.write_text(json.dumps(payload))
        self.addCleanup(lambda: tmp.exists() and tmp.unlink())
        return tmp


class TestPacerUnit(PacingTestBase):
    def test_default_interval_is_7s(self):
        self.assertEqual(fd.DEFAULT_PACE_SECONDS, 7.0)
        self.assertEqual(fd.Pacer().interval_s, 7.0)

    def test_first_request_never_waits(self):
        p = fd.Pacer(7)
        self.assertEqual(p.wait(), 0.0)
        self.assertEqual(self.clock.sleeps, [])
        self.assertEqual(p.requests, 1)

    def test_back_to_back_request_waits_full_interval(self):
        p = fd.Pacer(7)
        p.wait()
        self.assertEqual(p.wait(), 7.0)
        self.assertEqual(self.clock.sleeps, [7.0])
        self.assertEqual(p.total_wait_s, 7.0)
        self.assertEqual(p.requests, 2)

    def test_partial_elapsed_waits_only_the_remainder(self):
        p = fd.Pacer(7)
        p.wait()
        self.clock.advance(3)
        self.assertEqual(p.wait(), 4.0)
        self.assertEqual(self.clock.sleeps, [4.0])

    def test_slow_previous_request_needs_no_wait(self):
        p = fd.Pacer(7)
        p.wait()
        self.clock.advance(20)  # previous search itself took 20s
        self.assertEqual(p.wait(), 0.0)
        self.assertEqual(self.clock.sleeps, [])

    def test_zero_interval_disables_pacing(self):
        p = fd.Pacer(0)
        for _ in range(3):
            self.assertEqual(p.wait(), 0.0)
        self.assertEqual(self.clock.sleeps, [])
        self.assertEqual(p.requests, 3)
        self.assertEqual(p.total_wait_s, 0.0)

    def test_negative_interval_clamps_to_off(self):
        self.assertEqual(fd.Pacer(-5).interval_s, 0.0)


class TestResolvePaceSeconds(PacingTestBase):
    def setUp(self):
        super().setUp()
        self._env = os.environ.get("DUFFEL_PACE_SECONDS")
        os.environ.pop("DUFFEL_PACE_SECONDS", None)

    def tearDown(self):
        if self._env is None:
            os.environ.pop("DUFFEL_PACE_SECONDS", None)
        else:
            os.environ["DUFFEL_PACE_SECONDS"] = self._env
        super().tearDown()

    def test_default_when_nothing_set(self):
        self.assertEqual(fd.resolve_pace_seconds(None), 7.0)

    def test_env_beats_default(self):
        os.environ["DUFFEL_PACE_SECONDS"] = "12.5"
        self.assertEqual(fd.resolve_pace_seconds(None), 12.5)

    def test_env_zero_disables(self):
        os.environ["DUFFEL_PACE_SECONDS"] = "0"
        self.assertEqual(fd.resolve_pace_seconds(None), 0.0)

    def test_cli_beats_env(self):
        os.environ["DUFFEL_PACE_SECONDS"] = "12.5"
        self.assertEqual(fd.resolve_pace_seconds(3), 3.0)

    def test_unparseable_env_falls_back_to_default(self):
        os.environ["DUFFEL_PACE_SECONDS"] = "soon"
        self.assertEqual(fd.resolve_pace_seconds(None), 7.0)


class TestLiveSearchSpacing(PacingTestBase):
    ORIGIN, DEST = "ZZZ", "QQQ"

    def test_live_attempts_are_spaced_by_the_interval(self):
        fd.PACER = fd.Pacer(7)
        starts = []
        fake = self.fake_run_factory([OK_PAYLOAD] * 3, starts)
        with mock.patch.object(fd.subprocess, "run", fake):
            for dep in ("2099-01-05", "2099-01-06", "2099-01-07"):
                kind, _ = fd._duffel_search_once(
                    self.ORIGIN, self.DEST, dep, "2099-01-26")
                self.assertEqual(kind, "ok")
                self.addCleanup(
                    lambda d=dep: fd.cache_file_path(
                        self.ORIGIN, self.DEST, d, "2099-01-26")
                    .unlink(missing_ok=True))
        self.assertEqual(starts, [1000.0, 1007.0, 1014.0])
        self.assertEqual(self.clock.sleeps, [7.0, 7.0])
        self.assertEqual(fd.REQUEST_COUNT, 3)
        self.assertEqual(fd.PACER.requests, 3)
        self.assertEqual(fd.PACER.total_wait_s, 14.0)

    def test_pause_retry_is_not_double_delayed(self):
        # A retry after a 60s provider pause starts 60s after the
        # first attempt — well past the 7s interval — so pacing must
        # add NO extra wait on top of the pause.
        fd.PACER = fd.Pacer(7)
        starts = []
        fake = self.fake_run_factory([LIMIT_PAYLOAD, OK_PAYLOAD], starts)
        self.use_cache_file(self.ORIGIN, self.DEST, "2099-01-05",
                            "2099-01-26", OK_PAYLOAD)  # cleanup only
        with mock.patch.object(fd.subprocess, "run", fake):
            offers = fd.run_duffel_search(self.ORIGIN, self.DEST,
                                          "2099-01-05", "2099-01-26")
        self.assertEqual(offers, [{"price": "999"}])
        self.assertEqual(starts, [1000.0, 1060.0])
        self.assertEqual(self.clock.sleeps, [60.0])  # the pause only
        self.assertEqual(fd.PACER.total_wait_s, 0.0)
        self.assertEqual(fd.PACER.requests, 2)
        self.assertEqual(fd.PAUSES.pauses_taken, 1)


class TestCacheHitsNotPaced(PacingTestBase):
    ORIGIN, DEST = "ZZZ", "QQQ"

    def test_cache_lookups_never_touch_the_pacer(self):
        fd.PACER = fd.Pacer(999)
        self.use_cache_file(self.ORIGIN, self.DEST, "2099-01-05",
                            "2099-01-26",
                            {"ok": True, "offers": [QUALIFYING_OFFER]})
        offers = fd.cached_ok_offers(self.ORIGIN, self.DEST,
                                     "2099-01-05", "2099-01-26")
        self.assertEqual(offers, [QUALIFYING_OFFER])
        replayed = fd.cache_search(self.ORIGIN, self.DEST, "2099-01-05",
                                   "2099-01-26")
        self.assertEqual(replayed, [QUALIFYING_OFFER])
        self.assertEqual(fd.PACER.requests, 0)
        self.assertEqual(self.clock.sleeps, [])

    def test_resume_cell_served_entirely_from_cache_is_not_delayed(self):
        # Every planned sample for this cell has a fresh cached ok
        # response: find_cheapest_window must complete with zero live
        # requests and zero pacing sleeps.
        fd.PACER = fd.Pacer(999)
        fd.CACHE_MODE = False
        fd.RESUME_MODE = True
        fd.RESUME_TTL_S = 48 * 3600
        min_date = date(2099, 1, 1)
        durations = fd.sample_durations(fd.BAND_INDIA, 2)
        deps = fd.sample_departures(2099, 1, 2, min_date)
        self.assertEqual(len(deps) * len(durations), 4)
        for dep in deps:
            for days in durations:
                ret = dep + timedelta(days=days)
                self.use_cache_file(
                    self.ORIGIN, self.DEST, dep.isoformat(),
                    ret.isoformat(),
                    {"ok": True, "offers": [QUALIFYING_OFFER]})
        cell = fd.find_cheapest_window(
            self.ORIGIN, self.DEST, 2099, 1, fd.BAND_INDIA, 2,
            durations, min_date, 0)
        self.assertIsNotNone(cell)
        self.assertEqual(fd.RESUMED_COUNT, 4)
        self.assertEqual(cell["cache_samples"], 4)
        self.assertEqual(fd.PACER.requests, 0)
        self.assertEqual(self.clock.sleeps, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
