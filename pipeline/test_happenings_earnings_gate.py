#!/usr/bin/env python3
"""Gate tests for earnings briefs in daily-happenings-v2.py (2026-10-13).

Covers the fix for source-less, under-length earnings previews:
- earnings brief with < 2 sources is suppressed
- earnings brief under the 200-word floor is suppressed after one expansion retry
- earnings brief meeting both bars is inserted WITH sources + word_count
- non-earnings briefs are unaffected (no sources required, no word floor)
- get_earnings() attaches kind/symbol/sources (Nasdaq calendar + verified IR)

Run: python3 -u test_happenings_earnings_gate.py   (no network, no publishing)
"""
import importlib.util
import os
import sys

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

spec = importlib.util.spec_from_file_location(
    "daily_happenings_v2", os.path.join(os.path.dirname(__file__), "daily-happenings-v2.py"))
dh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dh)

LONG_BODY = "<p>" + " ".join(
    ["Investors will watch revenue trends across each business segment, management "
     "guidance for the coming quarter, margin and cost pressures, credit quality, and "
     "capital returns in the form of dividends and share buybacks when the company "
     "reports its quarterly results."] * 8) + "</p>"   # ~264 words
SHORT_BODY = "<p>" + " ".join(["Company reports earnings today."] * 10) + "</p>"  # 40 words

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def run_case(gpt_bodies, item):
    """Run ensure_happening_briefs with stubbed GPT/insert; return (inserts, item)."""
    inserts = []
    calls = {"n": 0}

    def fake_gpt(it, api_key):
        body = gpt_bodies[min(calls["n"], len(gpt_bodies) - 1)]
        calls["n"] += 1
        return {"headline": "H", "subheadline": "S", "body_html": body,
                "key_takeaways": ["a", "b"]}

    dh._brief_exists = lambda slug: False
    dh._gpt_brief = fake_gpt
    dh._insert_brief = lambda row: inserts.append(row) or True
    item = dict(item)
    dh.ensure_happening_briefs([item], "2026-10-14")
    return inserts, item, calls["n"]


def earnings_item(sources):
    return {"label": "Acme Earnings", "detail": "ACME · Before Market",
            "category": "markets", "kind": "earnings", "symbol": "ACME",
            "sources": sources, "search_terms": ["acme"], "emoji": "📊",
            "start_time_utc": None}


TWO_SOURCES = [
    {"name": "Nasdaq Earnings Calendar",
     "url": "https://www.nasdaq.com/market-activity/earnings?date=2026-10-14"},
    {"name": "Acme Investor Relations", "url": "https://investor.example.com/"},
]

print("A. earnings, 2 sources, always-short body -> suppressed after retry")
inserts, item, n = run_case([SHORT_BODY], earnings_item(TWO_SOURCES))
check("suppressed (no insert)", len(inserts) == 0)
check("expansion retry attempted", n == 2, f"gpt calls={n}")
check("item left unlinked", not item.get("link"))

print("B. earnings, 2 sources, short then long -> inserted with sources + word_count")
inserts, item, n = run_case([SHORT_BODY, LONG_BODY], earnings_item(TWO_SOURCES))
check("inserted once", len(inserts) == 1)
if inserts:
    check("row has >= 2 sources", len(inserts[0].get("sources") or []) >= 2)
    check("row word_count >= floor", (inserts[0].get("word_count") or 0) >= dh.EARNINGS_BRIEF_MIN_WORDS,
          f"word_count={inserts[0].get('word_count')}")
check("item linked", bool(item.get("link")))

print("C. earnings, 1 source, long body -> suppressed (source gate)")
inserts, item, n = run_case([LONG_BODY], earnings_item(TWO_SOURCES[:1]))
check("suppressed (no insert)", len(inserts) == 0)
check("item left unlinked", not item.get("link"))

print("D. non-earnings markets item, short body -> inserted as before (no regression)")
plain = {"label": "US Stock Markets Closed (Holiday)", "detail": "NYSE, Nasdaq",
         "category": "markets", "search_terms": [], "emoji": "🏛️", "start_time_utc": None}
inserts, item, n = run_case([SHORT_BODY], plain)
check("inserted once", len(inserts) == 1)
check("item linked", bool(item.get("link")))

print("E. get_earnings() attaches kind/sources from the Nasdaq payload")
dh.curl_json = lambda url, headers=None: {"data": {"rows": [
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "time": "time-pre-market"},
    {"symbol": "ABBV", "name": "AbbVie Inc.", "time": "time-pre-market"},
    {"symbol": "ZZZZ", "name": "Not Watchlist Co", "time": "time-pre-market"},
]}}
items = dh.get_earnings("2026-10-14")
by_symbol = {i["symbol"]: i for i in items}
check("watchlist only", set(by_symbol) == {"JPM", "ABBV"}, f"got {sorted(by_symbol)}")
jpm = by_symbol.get("JPM", {})
check("kind=earnings", jpm.get("kind") == "earnings")
check("JPM has 2 sources", len(jpm.get("sources") or []) == 2)
check("source 1 is Nasdaq calendar w/ date",
      (jpm.get("sources") or [{}])[0].get("url", "").endswith("date=2026-10-14"))
check("source 2 is JPM IR", (jpm.get("sources") or [{}, {}])[1].get("url") == dh.EARNINGS_IR_URLS["JPM"])
abbv = by_symbol.get("ABBV", {})
check("ABBV has only the calendar source (IR unverified)", len(abbv.get("sources") or []) == 1)

print()
if FAILURES:
    print(f"FAILED: {len(FAILURES)} check(s): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
