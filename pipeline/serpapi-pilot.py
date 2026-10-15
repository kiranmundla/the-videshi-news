#!/usr/bin/env python3
"""
SerpApi channel-comparison PILOT for The Videshi.

For a fixed, small matrix of US->India itineraries, ask Google Flights
(via SerpApi) which sellers offer the SAME itinerary and at what price —
airline-direct vs each OTA, with per-seller booking links. This is the
sample Kiran judges before any paid tier or production build.

Background: research/price-comparison-feasibility.md (2026-10-14).
A round-trip comparison costs up to 3 SerpApi searches:
  1. outbound search (returns options with departure_token)
  2. return search with that token (returns options with booking_token)
  3. booking-options call with the token (returns booking_options[]:
     seller, price, baggage prices, separate-ticket flag, booking link)

Scope (deliberately small — free tier is 250 searches/month):
  Tier-1 India routes x the 2 nearest bookable months x 4 midweek
  departures per month x ONE duration (3 weeks, per diaspora research).
  = 48 itineraries x 3 searches = 144 projected searches.
HARD BUDGET: 200 searches per run — the run aborts cleanly before any
call that would exceed it. Every real API call counts (failed searches
count against SerpApi quota too).

Idempotent / resumable: every raw response is cached under
pipeline/.state/serpapi-pilot/cache/ keyed by a hash of the query
params (api_key excluded). A re-run reuses cached responses and spends
0 new searches on anything it already fetched.

Data honesty:
- Prices are per-person round-trip totals in USD, exactly as returned.
  Nothing is normalized away: if the outbound quote and the final
  booking-options price disagree, both are recorded and the itinerary
  carries a note.
- Diaspora consolidators (Indian Eagle, TripBeam, ASAP Tickets) do not
  appear in Google Flights booking options — a known gap, stated in
  every report. They remain editorial (research/best-place-to-book.md).
- Pilot output stays in pipeline/.state/serpapi-pilot/results.json and
  pipeline/reports/ — it is NOT published to public/data until Kiran
  approves the sample and a production design exists.

Auth: SERPAPI_API_KEY must be in the environment, loaded from
~/workspace/.env.serpapi. The live run REFUSES (exit 2, zero network
calls) when it is absent. --plan and --self-test never need the key
and never touch the network.

Usage:
  python3 -u serpapi-pilot.py --plan        # matrix + projected searches
  python3 -u serpapi-pilot.py --self-test   # parser/budget/cache unit checks
  set -a; source ~/workspace/.env.serpapi; set +a
  python3 -u serpapi-pilot.py               # live pilot run (needs the key)
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

# ---------------------------------------------------------------- scope

# Tier-1 India routes (research/diaspora-travel-patterns.md) —
# (origin, destination, origin_metro, dest_metro); same list/order as
# pipeline/flight-deals.py TIER1_ROUTES.
TIER1_ROUTES = [
    ("SFO", "DEL", "Bay Area", "Delhi"),
    ("SFO", "BLR", "Bay Area", "Bengaluru"),
    ("JFK", "DEL", "New York", "Delhi"),
    ("JFK", "BOM", "New York", "Mumbai"),
    ("ORD", "DEL", "Chicago", "Delhi"),
    ("DFW", "HYD", "Dallas", "Hyderabad"),
]

DURATION_DAYS = 21          # one duration: 3 weeks (diaspora research)
MONTHS_COUNT = 2            # the 2 nearest bookable months
DEPARTURES_PER_MONTH = 4    # midweek departures sampled per route-month
MIDWEEK = (1, 2, 3)         # Tue, Wed, Thu (date.weekday(): Mon=0)
MIN_LEAD_DAYS = 10          # earliest departure = today + 10 days
SEARCHES_PER_ITINERARY = 3  # outbound + return + booking options

HARD_BUDGET = 200           # abort before exceeding; free tier is 250/mo
PACE_SECONDS = 1.0          # gentle pacing between live calls

API_URL = "https://serpapi.com/search.json"

BASE = Path.home() / "workspace" / "the-videshi-news"
STATE_DIR = BASE / "pipeline" / ".state" / "serpapi-pilot"
CACHE_DIR = STATE_DIR / "cache"
RESULTS_FILE = STATE_DIR / "results.json"
REPORTS_DIR = BASE / "pipeline" / "reports"

CONSOLIDATOR_NOTE = (
    "Diaspora consolidators (Indian Eagle, TripBeam, ASAP Tickets) do not "
    "appear in Google Flights booking options, so they are absent from "
    "every comparison here. They sometimes beat these prices; the "
    "editorial verdicts live in research/best-place-to-book.md."
)

# ---------------------------------------------------------------- matrix


def _midweek_days(start, end):
    d = start
    while d <= end:
        if d.weekday() in MIDWEEK:
            yield d
        d += timedelta(days=1)


def _pick_spaced(cands, n):
    """Pick n dates spread across the candidate list (first..last)."""
    if len(cands) <= n:
        return list(cands)
    idx = sorted({round(i * (len(cands) - 1) / (n - 1)) for i in range(n)})
    return [cands[i] for i in idx]


def bookable_months(today):
    """The MONTHS_COUNT nearest calendar months (as (year, month) pairs)
    that each offer at least DEPARTURES_PER_MONTH midweek departures on
    or after today + MIN_LEAD_DAYS."""
    start = today + timedelta(days=MIN_LEAD_DAYS)
    horizon = today + timedelta(days=120)
    by_month = {}
    for d in _midweek_days(start, horizon):
        by_month.setdefault((d.year, d.month), []).append(d)
    months = []
    for key in sorted(by_month):
        if len(by_month[key]) >= DEPARTURES_PER_MONTH:
            months.append(key)
        if len(months) == MONTHS_COUNT:
            break
    return months, by_month


def build_matrix(today):
    """The full pilot itinerary matrix: one dict per itinerary."""
    months, by_month = bookable_months(today)
    matrix = []
    for origin, dest, o_metro, d_metro in TIER1_ROUTES:
        for (y, m) in months:
            for dep in _pick_spaced(by_month[(y, m)], DEPARTURES_PER_MONTH):
                matrix.append({
                    "route": f"{origin}-{dest}",
                    "origin": origin,
                    "destination": dest,
                    "origin_metro": o_metro,
                    "dest_metro": d_metro,
                    "outbound_date": dep.isoformat(),
                    "return_date": (dep + timedelta(days=DURATION_DAYS)).isoformat(),
                    "duration_days": DURATION_DAYS,
                })
    return matrix


def plan_text(today):
    matrix = build_matrix(today)
    months, _ = bookable_months(today)
    month_names = ", ".join(
        date(y, m, 1).strftime("%B %Y") for (y, m) in months)
    lines = [
        "# SerpApi channel-comparison pilot — plan",
        "",
        f"Planned: {today.isoformat()} · Duration: 3 weeks (21 days), "
        "midweek (Tue/Wed/Thu) departures, economy, 1 adult, USD, "
        "max 1 stop (SerpApi stops=2).",
        f"Bookable months covered: {month_names} "
        f"(earliest departure = today + {MIN_LEAD_DAYS} days).",
        "",
        "| Route | Depart | Return |",
        "|---|---|---|",
    ]
    for it in matrix:
        lines.append(
            f"| {it['route']} ({it['origin_metro']} → {it['dest_metro']}) "
            f"| {it['outbound_date']} | {it['return_date']} |")
    projected = len(matrix) * SEARCHES_PER_ITINERARY
    lines += [
        "",
        f"Itineraries: {len(matrix)} "
        f"({len(TIER1_ROUTES)} routes x {len(months)} months x "
        f"{DEPARTURES_PER_MONTH} departures)",
        f"Projected searches: {projected} "
        f"({SEARCHES_PER_ITINERARY} per itinerary: outbound + return + "
        f"booking options)",
        f"Hard budget: {HARD_BUDGET} searches/run (free tier: 250/month). "
        "Cached responses from earlier runs cost 0 new searches.",
        "",
        "Per itinerary, the comparison prices ONE itinerary across "
        "sellers: the cheapest max-1-stop outbound option and its "
        "cheapest return pairing. Prices are per-person round-trip "
        "totals as returned by Google Flights via SerpApi.",
        "",
        CONSOLIDATOR_NOTE,
    ]
    return "\n".join(lines) + "\n"

# ---------------------------------------------------------------- budget


class BudgetExhausted(Exception):
    pass


class Budget:
    """Counts REAL API calls only (cache hits are free). Failed calls
    count too — SerpApi bills them against quota."""

    def __init__(self, hard_limit=HARD_BUDGET):
        self.hard_limit = hard_limit
        self.used = 0

    def spend(self):
        if self.used >= self.hard_limit:
            raise BudgetExhausted(
                f"hard budget of {self.hard_limit} searches reached")
        self.used += 1
        return self.used


# ---------------------------------------------------------------- cache


def query_hash(params):
    """Stable hash of query params (api_key must NOT be in params)."""
    canon = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:24]


class ResponseCache:
    def __init__(self, cache_dir=CACHE_DIR):
        self.dir = cache_dir

    def _path(self, params):
        return self.dir / f"{query_hash(params)}.json"

    def get(self, params):
        p = self._path(params)
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                return None
        return None

    def put(self, params, payload):
        self.dir.mkdir(parents=True, exist_ok=True)
        self._path(params).write_text(json.dumps(payload, indent=1))


# ---------------------------------------------------------------- client


def serpapi_get(params, api_key, cache, budget, log=print):
    """One SerpApi call, cache-first. Returns (payload, from_cache).
    Raises BudgetExhausted BEFORE any network call that would exceed
    the hard budget."""
    cached = cache.get(params)
    if cached is not None:
        return cached, True
    n = budget.spend()  # raises before any network traffic
    full = dict(params)
    full["api_key"] = api_key
    url = f"{API_URL}?{urlencode(full)}"
    log(f"  [search {n}/{budget.hard_limit}] "
        f"{params.get('departure_id', '')}→{params.get('arrival_id', '')} "
        f"{params.get('outbound_date', params.get('booking_token', '')[:12])}")
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "60", url],
        capture_output=True, text=True, timeout=70)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed (exit {r.returncode}): "
                           f"{r.stderr.strip()[:200]}")
    try:
        payload = json.loads(r.stdout)
    except Exception:
        raise RuntimeError("SerpApi returned non-JSON response")
    cache.put(params, payload)
    time.sleep(PACE_SECONDS)
    return payload, False


def base_params(it):
    return {
        "engine": "google_flights",
        "departure_id": it["origin"],
        "arrival_id": it["destination"],
        "outbound_date": it["outbound_date"],
        "return_date": it["return_date"],
        "type": "1",            # round trip
        "travel_class": "1",    # economy
        "adults": "1",
        "stops": "2",           # 1 stop or fewer (house rule: max 1 stop)
        "currency": "USD",
        "gl": "us",
        "hl": "en",
    }


# ---------------------------------------------------------------- parsing


def _flight_summary(entry):
    """Compact record of one flight option from a search response."""
    if not entry:
        return None
    legs = entry.get("flights") or []
    return {
        "price_quoted": entry.get("price"),
        "total_duration_min": entry.get("total_duration"),
        "airlines": sorted({leg.get("airline") for leg in legs
                            if leg.get("airline")}),
        "flight_numbers": [leg.get("flight_number") for leg in legs
                           if leg.get("flight_number")],
        "stops": max(0, len(legs) - 1),
        "departure_time": (legs[0].get("departure_airport") or {}).get("time")
        if legs else None,
        "arrival_time": (legs[-1].get("arrival_airport") or {}).get("time")
        if legs else None,
    }


def pick_outbound(resp):
    """Cheapest option (best_flights first, then other_flights) that
    carries a departure_token. Returns (entry, note)."""
    options = (resp.get("best_flights") or []) + (resp.get("other_flights")
                                                  or [])
    if not options:
        return None, "outbound search returned no flight options"
    priced = [o for o in options if isinstance(o.get("price"), (int, float))]
    pool = priced or options
    chosen = min(pool, key=lambda o: o.get("price")
                 if isinstance(o.get("price"), (int, float)) else float("inf"))
    if not chosen.get("departure_token"):
        return None, "cheapest outbound option has no departure_token"
    return chosen, None


def pick_return(resp):
    """Cheapest return option carrying a booking_token.
    Returns (entry, note)."""
    options = (resp.get("best_flights") or []) + (resp.get("other_flights")
                                                  or [])
    if not options:
        return None, "return search returned no flight options"
    with_token = [o for o in options if o.get("booking_token")]
    if not with_token:
        return None, "no return option carries a booking_token"
    priced = [o for o in with_token
              if isinstance(o.get("price"), (int, float))]
    pool = priced or with_token
    return min(pool, key=lambda o: o.get("price")
               if isinstance(o.get("price"), (int, float))
               else float("inf")), None


def _seller_record(name, price, airline_direct, separate_tickets,
                   option_title, baggage_prices, extensions,
                   booking_request, marketed_as=None, legs=None):
    req = booking_request or {}
    return {
        "name": name,
        "price": price,
        "airline_direct": airline_direct,
        "separate_tickets": separate_tickets,
        "option_title": option_title,
        "baggage_prices": baggage_prices or [],
        "baggage_note": "; ".join(baggage_prices) if baggage_prices else None,
        "extensions": extensions or [],
        "booking_link": req.get("url"),
        "booking_link_requires_post": bool(req.get("post_data")),
        "marketed_as": marketed_as or [],
        "legs": legs,
    }


def parse_booking_options(resp):
    """Parse a booking-options response into seller records.

    Documented shape: resp["booking_options"] is a list of entries,
    each either {"together": {...one seller for the whole trip...}} or
    {"separately": [{...}, {...}]} (separate tickets per part). Each
    seller object carries book_with, price, airline (true when the
    seller IS the airline), baggage_prices (strings), option_title,
    extensions, and booking_request {url, post_data?}.

    Returns (sellers, notes). Raw values are preserved as returned;
    discrepancies are surfaced as notes, never silently normalized.
    """
    notes = []
    if not isinstance(resp, dict):
        return [], ["booking-options response was not a JSON object"]
    if resp.get("error"):
        notes.append(f"API error in booking-options response: "
                     f"{resp['error']}")
    options = resp.get("booking_options")
    if not options:
        notes.append("no booking_options returned for this itinerary")
        return [], notes
    sellers = []
    for entry in options:
        if not isinstance(entry, dict):
            notes.append("skipped a non-object booking option entry")
            continue
        if "together" in entry:
            o = entry.get("together") or {}
            sellers.append(_seller_record(
                name=o.get("book_with"),
                price=o.get("price"),
                airline_direct=bool(o.get("airline")),
                separate_tickets=False,
                option_title=o.get("option_title"),
                baggage_prices=o.get("baggage_prices"),
                extensions=o.get("extensions"),
                booking_request=o.get("booking_request"),
                marketed_as=o.get("marketed_as"),
            ))
        elif "separately" in entry:
            parts = entry.get("separately") or []
            legs = []
            total = 0
            priced = True
            for part in parts:
                p_price = part.get("price")
                if isinstance(p_price, (int, float)):
                    total += p_price
                else:
                    priced = False
                legs.append({
                    "name": part.get("book_with"),
                    "price": p_price,
                    "booking_link":
                        (part.get("booking_request") or {}).get("url"),
                })
            names = " + ".join(
                str(leg["name"]) for leg in legs if leg["name"])
            sellers.append(_seller_record(
                name=names or None,
                price=total if priced and parts else None,
                airline_direct=bool(parts) and all(
                    bool(p.get("airline")) for p in parts),
                separate_tickets=True,
                option_title=None,
                baggage_prices=None,
                extensions=None,
                booking_request=None,
                legs=legs,
            ))
            notes.append(
                "a separate-tickets option is present (outbound and "
                "return sold as separate tickets — no protected "
                "connection)")
        else:
            notes.append("skipped a booking option with neither "
                         "'together' nor 'separately'")
    if any(s["price"] is None for s in sellers):
        notes.append("at least one seller was returned without a price; "
                     "it is recorded as-is and excluded from the "
                     "cheapest-seller calculation")
    return sellers, notes

# ---------------------------------------------------------------- run


def run_itinerary(it, api_key, cache, budget, log=print):
    """The 3-search flow for one itinerary. Returns a result record;
    failures land in the record's notes, never crash the run."""
    rec = dict(it)
    rec["outbound"] = None
    rec["return_leg"] = None
    rec["sellers"] = []
    rec["cheapest_seller"] = None
    rec["spread_usd"] = None
    rec["price_insights"] = None
    rec["notes"] = []
    rec["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    params = base_params(it)
    try:
        out_resp, _ = serpapi_get(params, api_key, cache, budget, log)
        if out_resp.get("error"):
            rec["notes"].append(
                f"outbound search API error: {out_resp['error']}")
            return rec
        outbound, note = pick_outbound(out_resp)
        if outbound is None:
            rec["notes"].append(note)
            return rec
        rec["outbound"] = _flight_summary(outbound)

        ret_params = dict(params)
        ret_params["departure_token"] = outbound["departure_token"]
        ret_resp, _ = serpapi_get(ret_params, api_key, cache, budget, log)
        if ret_resp.get("error"):
            rec["notes"].append(
                f"return search API error: {ret_resp['error']}")
            return rec
        ret, note = pick_return(ret_resp)
        if ret is None:
            rec["notes"].append(note)
            return rec
        rec["return_leg"] = _flight_summary(ret)
        rec["price_insights"] = ret_resp.get("price_insights")

        book_params = {"engine": "google_flights",
                       "booking_token": ret["booking_token"],
                       "currency": "USD", "gl": "us", "hl": "en"}
        book_resp, _ = serpapi_get(book_params, api_key, cache, budget,
                                   log)
        sellers, notes = parse_booking_options(book_resp)
        rec["sellers"] = sellers
        rec["notes"].extend(notes)
        priced = [s for s in sellers
                  if isinstance(s.get("price"), (int, float))]
        if priced:
            cheapest = min(priced, key=lambda s: s["price"])
            for s in sellers:
                s["is_cheapest"] = s is cheapest
            rec["cheapest_seller"] = cheapest["name"]
            rec["spread_usd"] = (max(s["price"] for s in priced)
                                 - cheapest["price"])
            quoted = (rec["outbound"] or {}).get("price_quoted")
            if isinstance(quoted, (int, float)) \
                    and quoted != cheapest["price"]:
                rec["notes"].append(
                    f"outbound search quoted ${quoted:,} round trip; "
                    f"booking options price the selected itinerary from "
                    f"${cheapest['price']:,} — both recorded as returned")
        return rec
    except BudgetExhausted:
        raise
    except Exception as e:  # one bad itinerary must not kill the pilot
        rec["notes"].append(f"failed mid-flow: {e}")
        return rec


def render_report(results):
    """Human-readable sample report — the artifact Kiran judges."""
    lines = [
        "# SerpApi channel-comparison pilot — sample report",
        "",
        f"Generated: {results['generated_at']} · "
        f"Searches used: {results['searches_used']} "
        f"(hard budget {results['search_budget']}; free tier 250/mo)",
        "",
        "Prices are per-person round-trip totals in USD, exactly as "
        "returned by Google Flights via SerpApi for the selected "
        "itinerary (cheapest max-1-stop outbound + cheapest return "
        "pairing, 3-week trip, midweek departure).",
        "",
        f"> {CONSOLIDATOR_NOTE}",
        "",
    ]
    by_route = {}
    for rec in results["itineraries"]:
        by_route.setdefault(rec["route"], []).append(rec)
    for route in sorted(by_route):
        recs = by_route[route]
        first = recs[0]
        lines.append(f"## {first['origin']} → {first['destination']} "
                     f"({first['origin_metro']} → {first['dest_metro']})")
        lines.append("")
        for rec in recs:
            lines.append(f"### Depart {rec['outbound_date']} → return "
                         f"{rec['return_date']} (3 weeks)")
            ob = rec.get("outbound") or {}
            if ob:
                lines.append(
                    f"Outbound: {', '.join(ob.get('flight_numbers') or [])}"
                    f" ({', '.join(ob.get('airlines') or [])}, "
                    f"{ob.get('stops')} stop(s)) · "
                    f"Return: {', '.join((rec.get('return_leg') or {}).get('flight_numbers') or [])}")
            lines.append("")
            if rec["sellers"]:
                lines.append("| Seller | Price | vs cheapest | "
                             "Airline-direct? | Bags | Flags |")
                lines.append("|---|---|---|---|---|---|")
                cheapest_price = min(
                    s["price"] for s in rec["sellers"]
                    if isinstance(s.get("price"), (int, float)))
                for s in sorted(
                        rec["sellers"],
                        key=lambda s: s["price"]
                        if isinstance(s.get("price"), (int, float))
                        else float("inf")):
                    price = (f"${s['price']:,}"
                             if isinstance(s.get("price"), (int, float))
                             else "—")
                    diff = (f"+${s['price'] - cheapest_price:,}"
                            if isinstance(s.get("price"), (int, float))
                            and s["price"] != cheapest_price else "—")
                    flags = []
                    if s.get("is_cheapest"):
                        flags.append("CHEAPEST")
                    if s.get("separate_tickets"):
                        flags.append("SEPARATE TICKETS")
                    if s.get("booking_link_requires_post"):
                        flags.append("link needs POST payload (in raw "
                                     "cache)")
                    lines.append(
                        f"| {s['name']} | {price} | {diff} | "
                        f"{'yes' if s.get('airline_direct') else 'no'} | "
                        f"{s.get('baggage_note') or '—'} | "
                        f"{'; '.join(flags) or '—'} |")
                lines.append("")
                direct = [s for s in rec["sellers"]
                          if s.get("airline_direct")
                          and isinstance(s.get("price"), (int, float))]
                if direct:
                    d = min(direct, key=lambda s: s["price"])
                    delta = d["price"] - cheapest_price
                    lines.append(
                        f"Channel spread: cheapest is "
                        f"**{rec['cheapest_seller']}** at "
                        f"${cheapest_price:,}; airline-direct "
                        f"({d['name']}) is ${d['price']:,}"
                        + (f" (+${delta:,})" if delta else " (matches "
                           "cheapest)") +
                        f"; total spread ${rec['spread_usd']:,}.")
                else:
                    lines.append(
                        f"Channel spread: cheapest is "
                        f"**{rec['cheapest_seller']}** at "
                        f"${cheapest_price:,}; no airline-direct seller "
                        f"was returned for this itinerary; total spread "
                        f"${rec['spread_usd']:,}.")
                lines.append("")
            for note in rec["notes"]:
                lines.append(f"- ⚠️ {note}")
            if rec["notes"]:
                lines.append("")
    return "\n".join(lines) + "\n"


def run(today=None):
    api_key = os.environ.get("SERPAPI_API_KEY", "").strip()
    if not api_key:
        print("REFUSING TO RUN: SERPAPI_API_KEY is not set — zero API "
              "calls made.\n"
              "The key belongs in ~/workspace/.env.serpapi. Load it "
              "with:\n"
              "  set -a; source ~/workspace/.env.serpapi; set +a\n"
              "  python3 -u pipeline/serpapi-pilot.py",
              file=sys.stderr)
        return 2
    today = today or date.today()
    matrix = build_matrix(today)
    print(f"Pilot matrix: {len(matrix)} itineraries, projected "
          f"{len(matrix) * SEARCHES_PER_ITINERARY} searches "
          f"(hard budget {HARD_BUDGET})")
    cache = ResponseCache()
    budget = Budget()
    records = []
    aborted = False
    for i, it in enumerate(matrix, 1):
        print(f"[{i}/{len(matrix)}] {it['route']} "
              f"{it['outbound_date']} → {it['return_date']}")
        try:
            records.append(run_itinerary(it, api_key, cache, budget))
        except BudgetExhausted as e:
            print(f"ABORTING CLEANLY: {e}. Remaining itineraries "
                  f"skipped; cached responses make a re-run resume "
                  f"where this stopped.")
            aborted = True
            break
    results = {
        "pilot": "serpapi-channel-comparison",
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "searches_used": budget.used,
        "search_budget": HARD_BUDGET,
        "aborted_on_budget": aborted,
        "scope": {
            "routes": [r[0] + "-" + r[1] for r in TIER1_ROUTES],
            "duration_days": DURATION_DAYS,
            "departures": "midweek (Tue/Wed/Thu)",
            "max_stops": 1,
            "passengers": 1,
            "cabin": "economy",
            "currency": "USD",
        },
        "global_notes": [CONSOLIDATOR_NOTE],
        "itineraries": records,
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(results, indent=1))
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    report_file = REPORTS_DIR / f"serpapi-pilot-{stamp}.md"
    report_file.write_text(render_report(results))
    print(f"Done. Searches used: {budget.used}. "
          f"Results: {RESULTS_FILE} · Report: {report_file}")
    return 0

# ---------------------------------------------------------------- fixture


# Hand-built fixture shaped like the documented booking-options
# response (field structure per SerpApi's Google Flights Booking
# Options API docs). Prices/names are invented for parser validation.
FIXTURE_BOOKING_RESPONSE = {
    "search_metadata": {"status": "Success"},
    "selected_flights": [
        {"flights": [{"airline": "Air India",
                      "flight_number": "AI 176"}],
         "type": "Round trip"},
    ],
    "baggage_prices": {"together": ["1 free carry-on",
                                    "1st checked bag: 99-187"]},
    "booking_options": [
        {"together": {
            "book_with": "Air India",
            "airline": True,
            "marketed_as": ["AI 176", "AI 175"],
            "price": 1142,
            "option_title": "Economy Value",
            "extensions": ["Ticket changes for a fee", "Standard seat"],
            "baggage_prices": ["1 free carry-on",
                               "1st checked bag up to 23 kg free"],
            "booking_request": {
                "url": "https://www.google.com/travel/clk/f",
                "post_data": "u=FIXTUREPOSTDATA",
            },
        }},
        {"together": {
            "book_with": "Expedia",
            "price": 1127,
            "option_title": "Economy",
            "extensions": ["No refunds"],
            "baggage_prices": ["1 free carry-on",
                               "1st checked bag: $75"],
            "booking_request": {
                "url": "https://www.google.com/travel/clk/f",
            },
        }},
        {"separately": [
            {"book_with": "United", "airline": True, "price": 601,
             "booking_request": {
                 "url": "https://www.google.com/travel/clk/f"}},
            {"book_with": "Lufthansa", "airline": True, "price": 559,
             "booking_request": {
                 "url": "https://www.google.com/travel/clk/f"}},
        ]},
        {"together": {
            "book_with": "MysterySeller",
            "option_title": "Economy",
            "booking_request": {
                "url": "https://www.google.com/travel/clk/f"},
        }},
    ],
}


def self_test():
    failures = []

    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            failures.append(label)

    print("Parser checks (fixture shaped like the documented "
          "booking-options response):")
    sellers, notes = parse_booking_options(FIXTURE_BOOKING_RESPONSE)
    check(len(sellers) == 4, "4 sellers parsed (2 together, 1 "
                             "separately, 1 unpriced)")
    by_name = {s["name"]: s for s in sellers}
    check(by_name["Air India"]["airline_direct"] is True,
          "airline-direct flag from 'airline: true'")
    check(by_name["Air India"]["price"] == 1142, "together price kept "
                                                 "as returned")
    check("23 kg" in (by_name["Air India"]["baggage_note"] or ""),
          "baggage note joined from baggage_prices")
    check(by_name["Air India"]["booking_link_requires_post"] is True,
          "post_data presence flagged on booking link")
    check(by_name["Expedia"]["booking_link_requires_post"] is False,
          "plain URL booking link not flagged")
    sep = by_name.get("United + Lufthansa")
    check(sep is not None and sep["separate_tickets"] is True,
          "separately entry flagged as separate tickets")
    check(sep is not None and sep["price"] == 1160,
          "separately price = sum of parts (601 + 559)")
    check(any("separate-tickets" in n for n in notes),
          "separate-tickets note surfaced")
    check(by_name["MysterySeller"]["price"] is None
          and any("without a price" in n for n in notes),
          "unpriced seller recorded as-is with a note")
    priced = [s for s in sellers
              if isinstance(s.get("price"), (int, float))]
    cheapest = min(priced, key=lambda s: s["price"])
    check(cheapest["name"] == "Expedia" and cheapest["price"] == 1127,
          "cheapest seller = Expedia $1,127")

    empty_sellers, empty_notes = parse_booking_options({})
    check(empty_sellers == [] and bool(empty_notes),
          "empty response -> no sellers, explicit note")

    print("Budget checks:")
    b = Budget(hard_limit=2)
    b.spend()
    b.spend()
    try:
        b.spend()
        check(False, "budget refuses the call that would exceed the cap")
    except BudgetExhausted:
        check(True, "budget refuses the call that would exceed the cap")

    print("Cache-key checks:")
    p1 = {"engine": "google_flights", "departure_id": "SFO",
          "outbound_date": "2026-11-03"}
    p2 = {"outbound_date": "2026-11-03", "departure_id": "SFO",
          "engine": "google_flights"}
    p3 = dict(p1, outbound_date="2026-11-04")
    check(query_hash(p1) == query_hash(p2),
          "param order does not change the cache key")
    check(query_hash(p1) != query_hash(p3),
          "different params -> different cache key")

    print("Matrix checks:")
    matrix = build_matrix(date(2026, 10, 14))
    check(len(matrix) == 48, f"matrix = 48 itineraries "
                             f"(got {len(matrix)})")
    check(len(matrix) * SEARCHES_PER_ITINERARY <= HARD_BUDGET,
          "projected searches fit the hard budget")
    check(all(m["duration_days"] == 21 for m in matrix),
          "single duration: 3 weeks")
    check(all(date.fromisoformat(m["outbound_date"]).weekday()
              in MIDWEEK for m in matrix),
          "all departures are Tue/Wed/Thu")

    if failures:
        print(f"\nSELF-TEST FAILED: {len(failures)} check(s)")
        return 1
    print("\nSELF-TEST PASSED")
    return 0


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", action="store_true",
                    help="print the itinerary matrix + projected "
                         "search count; no network, no key needed")
    ap.add_argument("--self-test", action="store_true",
                    help="unit-check parser/budget/cache/matrix "
                         "against a fixture; no network, no key needed")
    args = ap.parse_args()
    if args.plan:
        print(plan_text(date.today()), end="")
        return 0
    if args.self_test:
        return self_test()
    return run()


if __name__ == "__main__":
    sys.exit(main())
