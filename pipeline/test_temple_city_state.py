#!/usr/bin/env python3
"""Regression tests for city_state_valid in temple-events-scraper.py.

The BAPS Orlando garble (2026-10-30): a 41-city-expansion directory
entry carried city='Mandir', state='Orlando'. Both fields were
non-empty, so the events inserted and published under a nonsense city.
city_state_valid is the guard at page-recovery time and at insert time.
"""
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "temple_events_scraper",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "temple-events-scraper.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CASES = [
    # (city, state, expected)
    ("Orlando", "FL", True),
    ("Morrisville", "NC", True),
    ("Mandir", "Orlando", False),   # the actual garble
    ("Orlando", "Florida", False),  # state must be the abbreviation
    ("", "FL", False),
    ("Orlando", "", False),
    ("", "", False),
    (None, None, False),
    ("Temple", "TX", False),        # venue word as city
    ("Atlanta", "GA", True),
    ("Washington", "DC", True),
]

failures = 0
for city, state, expected in CASES:
    got = mod.city_state_valid(city, state)
    ok = got == expected
    failures += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}: city_state_valid({city!r}, {state!r}) "
          f"= {got} (expected {expected})")

print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
raise SystemExit(1 if failures else 0)
