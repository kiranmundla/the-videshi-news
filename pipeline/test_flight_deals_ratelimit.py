#!/usr/bin/env python3
"""Unit tests for flight-deals.py rate-limit pause/resume logic.

All Duffel responses are mocked — these tests make NO provider calls.
Run: python3 pipeline/test_flight_deals_ratelimit.py
"""

import importlib.util
import json
import os
import time
import unittest
from pathlib import Path

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


class TestClassify(unittest.TestCase):
    def test_ok_payload(self):
        kind, info = fd.classify_duffel_result(
            {"ok": True, "offers": [{"price": "999"}]}, 0, "")
        self.assertEqual(kind, "ok")
        self.assertEqual(info, [{"price": "999"}])

    def test_limit_with_retry_after_pauses(self):
        kind, info = fd.classify_duffel_result(LIMIT_PAYLOAD, 0, "")
        self.assertEqual(kind, "pause")
        self.assertEqual(info, 60.0)

    def test_limit_without_retry_after_aborts(self):
        payload = {"ok": False, "status": 429,
                   "response": {"error": "per-user connector request "
                                         "limit exceeded"}}
        kind, info = fd.classify_duffel_result(payload, 0, "")
        self.assertEqual(kind, "abort")
        self.assertIn("retry_after", info)

    def test_429_in_stderr_without_payload_aborts(self):
        kind, _ = fd.classify_duffel_result(None, 1, "HTTP 429 Too Many")
        self.assertEqual(kind, "abort")

    def test_auth_error_aborts(self):
        kind, info = fd.classify_duffel_result(None, 1, "401 Unauthorized")
        self.assertEqual(kind, "abort")
        self.assertIn("auth", info.lower())

    def test_generic_not_ok_is_plain_fail(self):
        kind, _ = fd.classify_duffel_result(
            {"ok": False, "response": {"error": "no offers found"}}, 0, "")
        self.assertEqual(kind, "fail")

    def test_generic_failure_is_plain_fail(self):
        kind, _ = fd.classify_duffel_result(None, 1, "connection reset")
        self.assertEqual(kind, "fail")


class TestPauseBudget(unittest.TestCase):
    def test_pause_count_bound(self):
        b = fd.PauseBudget(max_pauses=2, max_total_wait_s=10000)
        self.assertTrue(b.try_consume(60))
        self.assertTrue(b.try_consume(60))
        self.assertFalse(b.try_consume(60))

    def test_total_wait_bound(self):
        b = fd.PauseBudget(max_pauses=10, max_total_wait_s=100)
        self.assertTrue(b.try_consume(60))
        self.assertFalse(b.try_consume(60))  # 120 > 100

    def test_defaults_are_task_bounds(self):
        b = fd.PauseBudget()
        self.assertEqual(b.max_pauses, 10)
        self.assertEqual(b.max_total_wait_s, 1200)


class TestRunDuffelSearchWrapper(unittest.TestCase):
    def setUp(self):
        fd.ABORTED = False
        fd.ABORT_REASON = None
        fd.FAILED_COUNT = 0
        fd.PAUSES = fd.PauseBudget(max_pauses=10, max_total_wait_s=1200)
        self.sleeps = []
        fd.SLEEP_FN = self.sleeps.append
        fd.JITTER_FN = lambda: 0.0
        self._orig_once = fd._duffel_search_once

    def tearDown(self):
        fd._duffel_search_once = self._orig_once
        fd.SLEEP_FN = time.sleep

    def mock_sequence(self, seq):
        it = iter(seq)
        fd._duffel_search_once = lambda *a, **k: next(it)

    def test_pause_then_success(self):
        self.mock_sequence([("pause", 60.0), ("ok", [{"price": "1"}])])
        offers = fd.run_duffel_search("SFO", "DEL", "2026-11-01",
                                      "2026-11-22")
        self.assertEqual(offers, [{"price": "1"}])
        self.assertEqual(self.sleeps, [60.0])
        self.assertEqual(fd.PAUSES.pauses_taken, 1)
        self.assertFalse(fd.ABORTED)

    def test_budget_exhausted_aborts(self):
        fd.PAUSES = fd.PauseBudget(max_pauses=1, max_total_wait_s=1200)
        self.mock_sequence([("pause", 60.0), ("pause", 60.0)])
        offers = fd.run_duffel_search("SFO", "DEL", "2026-11-01",
                                      "2026-11-22")
        self.assertIsNone(offers)
        self.assertTrue(fd.ABORTED)
        self.assertIn("pause budget exhausted", fd.ABORT_REASON)
        self.assertEqual(self.sleeps, [60.0])  # only the first pause slept

    def test_total_wait_exhausted_aborts(self):
        fd.PAUSES = fd.PauseBudget(max_pauses=10, max_total_wait_s=90)
        self.mock_sequence([("pause", 60.0), ("pause", 60.0)])
        offers = fd.run_duffel_search("SFO", "DEL", "2026-11-01",
                                      "2026-11-22")
        self.assertIsNone(offers)
        self.assertTrue(fd.ABORTED)
        self.assertIn("pause budget exhausted", fd.ABORT_REASON)

    def test_hard_abort_no_sleep(self):
        self.mock_sequence([("abort", "hard 429")])
        offers = fd.run_duffel_search("SFO", "DEL", "2026-11-01",
                                      "2026-11-22")
        self.assertIsNone(offers)
        self.assertTrue(fd.ABORTED)
        self.assertEqual(self.sleeps, [])

    def test_plain_fail_no_abort(self):
        self.mock_sequence([("fail", "boom")])
        offers = fd.run_duffel_search("SFO", "DEL", "2026-11-01",
                                      "2026-11-22")
        self.assertIsNone(offers)
        self.assertFalse(fd.ABORTED)
        self.assertEqual(fd.FAILED_COUNT, 1)


class TestResumeCache(unittest.TestCase):
    ORIGIN, DEST, DEP, RET = "TST", "TST", "2099-01-05", "2099-01-26"

    def setUp(self):
        fd.RESUME_TTL_S = 24 * 3600
        self.tmp = fd.cache_file_path(self.ORIGIN, self.DEST, self.DEP,
                                      self.RET)
        self.addCleanup(lambda: self.tmp.exists() and self.tmp.unlink())

    def test_fresh_ok_cache_reused(self):
        self.tmp.write_text(json.dumps({"ok": True,
                                        "offers": [{"price": "5"}]}))
        offers = fd.cached_ok_offers(self.ORIGIN, self.DEST, self.DEP,
                                     self.RET)
        self.assertEqual(offers, [{"price": "5"}])

    def test_limit_error_cache_not_reused(self):
        self.tmp.write_text(json.dumps(LIMIT_PAYLOAD))
        self.assertIsNone(fd.cached_ok_offers(self.ORIGIN, self.DEST,
                                              self.DEP, self.RET))

    def test_stale_cache_not_reused(self):
        self.tmp.write_text(json.dumps({"ok": True, "offers": []}))
        old = time.time() - 25 * 3600
        os.utime(self.tmp, (old, old))
        self.assertIsNone(fd.cached_ok_offers(self.ORIGIN, self.DEST,
                                              self.DEP, self.RET))

    def test_missing_cache(self):
        self.assertIsNone(fd.cached_ok_offers(self.ORIGIN, self.DEST,
                                              self.DEP, self.RET))


if __name__ == "__main__":
    unittest.main(verbosity=2)
