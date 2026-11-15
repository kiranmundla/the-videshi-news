"""Regression tests: event dedup lookups must see the WHOLE table.

PostgREST clamps any single request to 1000 rows on this project.
The events table passed 1000 rows long ago (5,042 on 2026-11-15), so
every single-shot `limit=5000` dedup fetch silently saw only page 1:
AllEvents' lookup (the reported defect), Meetup's twin, the temple
scraper's existing-id/title sets, scrape-temples' fingerprints, and
event_dedup.find_cross_source_duplicates. All now paginate through
event_dedup.fetch_all_event_rows.

Also covers the fuzzy-title leg: it compared a space-preserving
normalized title against the space-stripped exact set and could
essentially never match; it now compares normalized vs normalized.

Live test (needs .env.supabase): python3 -u test_event_dedup_pagination.py
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Load .env.supabase like the scrapers do.
_env = os.path.expanduser("~/workspace/.env.supabase")
if os.path.exists(_env):
    for line in open(_env):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FAIL = []


def check(label, cond):
    print(("  ok " if cond else "  FAIL ") + label)
    if not cond:
        FAIL.append(label)


from event_dedup import fetch_all_event_rows  # noqa: E402

print("fetch_all_event_rows paginates past the 1000-row clamp")
rows = fetch_all_event_rows("source_id,title,date")
check(f"fetched {len(rows)} rows (> 1000)", len(rows) > 1000)

ae = load("scrape_allevents", "scrape-allevents.py")
ids, tds, fps, nts = ae.get_existing_events()
check(f"allevents existing source_ids {len(ids)} (> 1000)", len(ids) > 1000)
check("allevents norm-title set populated", len(nts) > 1000)

print("fuzzy leg: normalized vs normalized")
existing_norm = {("diwali mela celebration", "2026-11-08")}
ev = {"source_id": "ae_new_1", "title": "Diwali Mela Celebration 2026",
      "date": "2026-11-08", "city": "Houston"}
check("number-suffixed twin is a duplicate",
      ae.is_duplicate(ev, set(), set(), set(), existing_norm))
ev2 = {"source_id": "ae_new_2", "title": "Classical Dance Recital",
       "date": "2026-11-08", "city": "Houston"}
check("unrelated event is not a duplicate",
      not ae.is_duplicate(ev2, set(), set(), set(), existing_norm))

print("temple scraper existing ids paginate")
tes = load("temple_events_scraper", "temple-events-scraper.py")
tids = tes.get_existing_source_ids()
check(f"temple existing source_ids {len(tids)} (> 1000)", len(tids) > 1000)

print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
