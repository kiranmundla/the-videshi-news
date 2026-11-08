#!/usr/bin/env python3
"""Tests for the box-office guard in weekly-entertainment-refresh.py
(added 2026-11-07 after boxoffice.json slipped stale three times).

Run: python3 -u test_boxoffice_guard.py
"""
import importlib.util
import json
import tempfile
from datetime import date
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "weekly_refresh", Path(__file__).parent / "weekly-entertainment-refresh.py")
wr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wr)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ok  {name}")
    else:
        failed += 1
        print(f"FAIL  {name}")


MONDAY = date(2026, 11, 2)          # Monday of Nov 02 – Nov 08, 2026
LABEL = "Nov 02 – Nov 08, 2026"

# --- find_current_week_figures -------------------------------------------
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    for name in ("boxoffice-figures-2026-10-26.json",   # previous week
                 "boxoffice-figures-2026-11-02.json",   # this Monday
                 "boxoffice-figures-2026-11-05.json",   # mid-week, newer
                 "boxoffice-figures-2026-11-09.json",   # next week
                 "boxoffice-figures-bogus.json",
                 "other-file.json"):
        (td / name).write_text("[]")
    got = wr.find_current_week_figures(td, MONDAY)
    check("picks newest figures file inside the current week",
          got is not None and got.name == "boxoffice-figures-2026-11-05.json")

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    (td / "boxoffice-figures-2026-10-26.json").write_text("[]")
    check("previous week's figures file does NOT count (the Oct 26 slip)",
          wr.find_current_week_figures(td, MONDAY) is None)

with tempfile.TemporaryDirectory() as td:
    check("empty dir -> None", wr.find_current_week_figures(Path(td), MONDAY) is None)

# --- boxoffice_freshness_problem -----------------------------------------
fresh = {"week_of": LABEL, "as_of": "2026-11-02", "films": [{"title": "X"}]}
check("current week_of + in-week as_of is fresh",
      wr.boxoffice_freshness_problem(fresh, LABEL, MONDAY) is None)

stale_week = dict(fresh, week_of="Oct 26 – Nov 01, 2026")
check("last week's week_of is stale",
      wr.boxoffice_freshness_problem(stale_week, LABEL, MONDAY) is not None)

stale_asof = dict(fresh, as_of="2026-10-26")
check("in-label week but last week's as_of is stale",
      wr.boxoffice_freshness_problem(stale_asof, LABEL, MONDAY) is not None)

check("missing films is a problem",
      wr.boxoffice_freshness_problem({"week_of": LABEL, "as_of": "2026-11-02"}, LABEL, MONDAY) is not None)
check("non-dict data is a problem",
      wr.boxoffice_freshness_problem(None, LABEL, MONDAY) is not None)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
