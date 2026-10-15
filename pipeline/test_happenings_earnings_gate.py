#!/usr/bin/env python3
"""Gate tests for earnings briefs in daily-happenings-v2.py (2026-10-13).

Covers the fix for source-less, under-length earnings previews:
- earnings brief with < 2 sources is suppressed
- earnings brief under the 200-word floor is suppressed after one expansion retry
- earnings brief meeting both bars is inserted WITH sources + word_count
- non-earnings briefs: UPDATED 2026-10-14 — Kiran extended the ≥2-source
  gate to ALL new articles, so non-earnings briefs are now suppressed
  without 2 verified sources too (no word floor for them). The earnings
  cases above are unchanged from the 2026-10-13 spec.
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

print("D. non-earnings markets item, NO sources -> suppressed (≥2-source gate, 2026-10-14)")
plain = {"label": "US Stock Markets Closed (Holiday)", "detail": "NYSE, Nasdaq",
         "category": "markets", "search_terms": [], "emoji": "🏛️", "start_time_utc": None}
inserts, item, n = run_case([SHORT_BODY], plain)
check("suppressed (no insert)", len(inserts) == 0)
check("item left unlinked", not item.get("link"))

print("D2. non-earnings item WITH 2 item sources -> inserted, sources attached, no word floor")
plain2 = dict(plain, sources=[
    {"name": "NYSE Holiday Calendar", "url": "https://www.nyse.com/markets/hours-calendars"},
    {"name": "Nasdaq Trading Calendar", "url": "https://www.nasdaq.com/market-activity/stock-market-holiday-schedule"},
])
inserts, item, n = run_case([SHORT_BODY], plain2)
check("inserted once", len(inserts) == 1)
if inserts:
    check("row carries the 2 sources", len(inserts[0].get("sources") or []) == 2)
    check("no word_count imposed on non-earnings", "word_count" not in inserts[0])
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

print("F. headline_names_company — the 2026-10-14 JPMorgan/Morgan trap")
ROUNDUP = "Bank Earnings Kick Off Mixed: JPMorgan Misses, Citi and Goldman Beat"
check("MS does NOT match roundup (morgan inside JPMorgan)",
      not dh.headline_names_company(ROUNDUP, "Morgan Stanley"))
check("MS matches a headline naming Morgan Stanley",
      dh.headline_names_company(
          "Morgan Stanley Beats Estimates as Bank of America Misses", "Morgan Stanley"))
check("BAC does NOT match roundup (generic 'Bank' is not a name form)",
      not dh.headline_names_company(ROUNDUP, "Bank of America Corporation"))
check("BAC matches a headline naming Bank of America",
      dh.headline_names_company(
          "Bank of America Misses Estimates on Settlement Charge",
          "Bank of America Corporation"))
check("JPM matches roundup (squashed token 'jpmorgan')",
      dh.headline_names_company(ROUNDUP, "J P Morgan Chase & Co"))
check("JPM does NOT match a Morgan Stanley headline",
      not dh.headline_names_company("Morgan Stanley Beats Estimates",
                                    "J P Morgan Chase & Co"))
check("Citigroup matches roundup via 'Citi' brand form",
      dh.headline_names_company(ROUNDUP, "Citigroup"))
check("Citigroup matches its full name",
      dh.headline_names_company("Citigroup Profit Rises on Trading", "Citigroup"))
check("Johnson & Johnson does NOT match roundup (body-only coverage)",
      not dh.headline_names_company(ROUNDUP, "Johnson & Johnson"))
check("Goldman Sachs matches roundup",
      dh.headline_names_company(ROUNDUP, "Goldman Sachs"))

print("F2. search patterns keep recall for all-generic names (BAC hole)")
pats = dh._company_search_patterns("Bank of America Corporation")
check("BAC patterns include *america*", "*america*" in pats, f"pats={pats}")
check("BAC patterns include the full-name phrase", "*bank of america*" in pats,
      f"pats={pats}")
check("BAC patterns never search bare *bank*", "*bank*" not in pats, f"pats={pats}")
check("MS patterns include *morgan* and *stanley*",
      {"*morgan*", "*stanley*"} <= set(dh._company_search_patterns("Morgan Stanley")))

print("G. match_articles earnings branch — stubbed candidate search")
ROUNDUP_ROW = {"slug": "bank-earnings-kick-off-mixed-jpmorgan-misses-citi-goldman-beat",
               "headline": ROUNDUP, "published_at": "2026-10-13T21:24:39+00:00"}
NEW_ROW = {"slug": "morgan-stanley-beats-estimates-bank-of-america-misses-settlement-charge",
           "headline": "Morgan Stanley Beats Estimates as Bank of America Misses on $1.2 Billion Settlement Charge",
           "published_at": "2026-10-14T23:05:00+00:00"}


def earnings_row_item(label, symbol):
    return {"label": label, "detail": f"{symbol} · Before Market",
            "category": "markets", "kind": "earnings", "symbol": symbol,
            "sources": [], "search_terms": [symbol.lower()], "emoji": "📊",
            "start_time_utc": None}


dh._supabase_search_rows = lambda pattern, cutoff, limit=5: [ROUNDUP_ROW]
items = dh.match_articles([
    earnings_row_item("Morgan Stanley Earnings", "MS"),
    earnings_row_item("Bank of America Corporation Earnings", "BAC"),
    earnings_row_item("J P Morgan Chase & Co Earnings", "JPM"),
])
by_label = {i["label"]: i for i in items}
check("MS unlinked when only the Oct-13 roundup exists",
      not by_label["Morgan Stanley Earnings"].get("link"))
check("BAC unlinked when only the Oct-13 roundup exists",
      not by_label["Bank of America Corporation Earnings"].get("link"))
check("JPM linked to the roundup its headline names",
      by_label["J P Morgan Chase & Co Earnings"].get("link")
      == f"/articles/{ROUNDUP_ROW['slug']}")

dh._supabase_search_rows = lambda pattern, cutoff, limit=5: [NEW_ROW, ROUNDUP_ROW]
items = dh.match_articles([
    earnings_row_item("Morgan Stanley Earnings", "MS"),
    earnings_row_item("Bank of America Corporation Earnings", "BAC"),
])
check("MS links the results roundup once it exists",
      items[0].get("link") == f"/articles/{NEW_ROW['slug']}")
check("BAC links the results roundup once it exists",
      items[1].get("link") == f"/articles/{NEW_ROW['slug']}")

print("H. results_repoint_pass — repoint, retire, gap (stubbed Supabase)")
from datetime import datetime as _dt, timedelta as _td, timezone as _tz
_yday = (_dt.now(_tz.utc) - _td(days=1)).strftime("%Y-%m-%d")
_future = (_dt.now(_tz.utc) + _td(days=3)).strftime("%Y-%m-%d")
FAKE_ROWS = [
    {"id": "r1", "date": _yday, "label": "Bank of America Corporation Earnings",
     "detail": "BAC · Before Market",
     "link": "/articles/happening-2026-10-13-bank-of-america-corporation-earnings",
     "category": "markets"},
    {"id": "r2", "date": _yday, "label": "Globex Corporation Earnings",
     "detail": "GLBX · Before Market",
     "link": "/articles/happening-2026-10-13-globex-corporation-earnings",
     "category": "markets"},
    {"id": "r3", "date": _future, "label": "Future Corp Earnings",
     "detail": "FUT · Before Market",
     "link": "/articles/happening-2099-01-01-future-corp-earnings",
     "category": "markets"},
]
patches = []


def fake_sb_curl(method, path, payload=None):
    if method == "GET":
        return [dict(r) for r in FAKE_ROWS]
    patches.append((method, path, payload))
    return []


dh._sb_curl = fake_sb_curl
dh._find_results_article = (
    lambda company, date_str: {"slug": "real-bac-results"}
    if company.startswith("Bank of America") else None)
res = dh.results_repoint_pass()
check("one row repointed", res["repointed"] == 1, f"res={res}")
check("one gap flagged (Globex, window >6h past, no coverage)",
      res["gaps"] == 1, f"res={res}")
check("future row left pending", res["pending"] == 1, f"res={res}")
check("happening row PATCHed to results link",
      any(p[0] == "PATCH" and p[1] == "daily_happenings?id=eq.r1"
          and p[2] == {"link": "/articles/real-bac-results"} for p in patches),
      f"patches={patches}")
check("stub article PATCHed to draft",
      any(p[0] == "PATCH" and "happening-2026-10-13-bank-of-america" in p[1]
          and p[2] == {"status": "draft"} for p in patches), f"patches={patches}")
check("no PATCH for the gap company",
      not any("globex" in p[1] for p in patches))

print()
if FAILURES:
    print(f"FAILED: {len(FAILURES)} check(s): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
