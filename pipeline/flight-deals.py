#!/usr/bin/env python3
"""
Flight deals price fetcher for The Videshi. (Phase B)

Searches Duffel for round-trip fares on US-India routes and writes
price data for the frontend price calendar, plus a snapshot history
used for fare-drop detection ("down $X since <date>" is the return
trigger — deals are the #1 reason readers come back).

Specs (Kiran's decisions):
- Max 1 stop (no 2+ stops)
- Round-trip, per person, economy
- Exclude basic economy — only fares with 2+ checked bags
- Duration: 2/3/4 weeks for India routes (never 1 week — research)
- Discovery only: honest price ranges with as-of timestamps,
  direct links, no affiliates
- Departure sampling defaults to Tue/Wed/Thu (cheapest days to fly)

Coverage: Tier-1 + Tier-2 India routes (research/diaspora-travel-patterns.md)
x next 6 months rolling x durations 2/3/4 weeks. Sampling is deliberately
sparse (default 2 midweek departure dates per month/duration cell) so a
full run stays within a sane Duffel request budget:
  12 routes x 3 durations x 6 months x 2 samples = 432 requests max.

History: every run appends one JSON line per route/month/duration cell
to pipeline/.state/flight-deals-history.jsonl. Drops are computed vs the
previous snapshot for the same cell, and vs the trailing average once
>=3 prior snapshots exist. The Phase 1 output (2026-10-11) seeds the
first baseline honestly (baseline_as_of is carried on every drop).

Usage:
  python3 flight-deals.py --all                      (full Tier-1+2 matrix)
  python3 flight-deals.py --tier 1                   (Tier-1 only)
  python3 flight-deals.py --route SFO-DEL            (single route, all durations)
  python3 flight-deals.py --all --dry-run            (search + print, no writes)
  python3 flight-deals.py --all --samples 3          (denser sampling)
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

# Tier 1 (research: build first) — (origin, destination, origin_metro, dest_metro)
TIER1_ROUTES = [
    ("SFO", "DEL", "Bay Area", "Delhi"),
    ("SFO", "BLR", "Bay Area", "Bengaluru"),
    ("JFK", "DEL", "New York", "Delhi"),
    ("JFK", "BOM", "New York", "Mumbai"),
    ("ORD", "DEL", "Chicago", "Delhi"),
    ("DFW", "HYD", "Dallas", "Hyderabad"),
]

# Tier 2 (research)
TIER2_ROUTES = [
    ("LAX", "DEL", "Los Angeles", "Delhi"),
    ("SEA", "DEL", "Seattle", "Delhi"),
    ("EWR", "BOM", "New York", "Mumbai"),
    ("IAD", "DEL", "Washington DC", "Delhi"),
    ("ATL", "DEL", "Atlanta", "Delhi"),
    ("BOS", "DEL", "Boston", "Delhi"),
]

ALL_ROUTES = TIER1_ROUTES + TIER2_ROUTES
INDIA_DURATIONS = [2, 3, 4]
PRIMARY_WEEKS = 3  # calendar kept at routes[key]["calendar"] for back-compat

DATA_DIR = Path.home() / "workspace" / "the-videshi-news" / "public" / "data"
STATE_DIR = Path.home() / "workspace" / "the-videshi-news" / "pipeline" / ".state"
OUTPUT_FILE = DATA_DIR / "flight-deals.json"
HISTORY_FILE = STATE_DIR / "flight-deals-history.jsonl"

MIN_LEAD_DAYS = 2          # earliest departure = today + 2 days
MIDWEEK = (1, 2, 3)        # Tue, Wed, Thu (date.weekday(): Mon=0)
DROP_MIN_PCT = 4.0         # a drop is "notable" at >= 4% ...
DROP_MIN_ABS = 40          # ... and >= $40 vs the previous snapshot

# Festival seasons: id, name, window, book_by_months (research doc §2/§5)
FESTIVAL_SEASONS = [
    {
        "id": "diwali-2026",
        "name": "Diwali",
        "emoji": "🪔",
        "start": (2026, 11, 6),
        "end": (2026, 11, 10),
        "book_by_months": 4,
        "note": "5-day festival",
    },
    {
        "id": "thanksgiving-2026",
        "name": "Thanksgiving",
        "emoji": "🦃",
        "start": (2026, 11, 25),
        "end": (2026, 11, 29),
        "book_by_months": 2,
        "note": "Long-weekend trips",
    },
    {
        "id": "christmas-2026",
        "name": "Christmas & New Year",
        "emoji": "🎄",
        "start": (2026, 12, 20),
        "end": (2027, 1, 5),
        "book_by_months": 5,
        "note": "Peak holiday season",
    },
    {
        "id": "holi-2027",
        "name": "Holi",
        "emoji": "🎨",
        "start": (2027, 3, 22),
        "end": (2027, 3, 22),
        "book_by_months": 2,
        "note": "Shoulder season — moderate fares",
    },
    {
        "id": "diwali-2027",
        "name": "Diwali",
        "emoji": "🪔",
        "start": (2027, 10, 29),
        "end": (2027, 11, 2),
        "book_by_months": 4,
        "note": "5-day festival",
    },
]

REQUEST_COUNT = 0
FAILED_COUNT = 0
RATE_LIMITED = False
CACHE_MODE = False
ATTEMPTED = {}  # route_key -> searches with a cache file present (cache mode)


def cache_search(origin, dest, dep_date, ret_date):
    """Cache-mode stand-in for run_duffel_search: replays a raw Duffel
    response saved by an earlier live run. Makes NO API calls. Returns
    offers, [] for a saved error response, or None if no file exists
    (search never attempted)."""
    global REQUEST_COUNT, FAILED_COUNT
    REQUEST_COUNT += 1
    route_key = f"{origin}-{dest}"
    tmp = Path(f"/tmp/duffel-{origin}{dest}-{dep_date}-{ret_date}.json")
    if not tmp.exists():
        return None
    ATTEMPTED[route_key] = ATTEMPTED.get(route_key, 0) + 1
    try:
        data = json.loads(tmp.read_text())
    except Exception:
        FAILED_COUNT += 1
        return []
    if not data.get("ok"):
        FAILED_COUNT += 1
        return []
    return data.get("offers", [])


def run_duffel_search(origin, dest, dep_date, ret_date, limit=100):
    """Run Duffel search and return offers list. Returns None on failure.

    Counts every request. A 429 sets RATE_LIMITED and aborts the run —
    per the Duffel connector rules, a rate limit ends calls for the task.
    """
    global REQUEST_COUNT, FAILED_COUNT, RATE_LIMITED
    REQUEST_COUNT += 1
    cmd = [
        "duffel", "search",
        "--origin", origin,
        "--destination", dest,
        "--departure-date", dep_date,
        "--return-date", ret_date,
        "--adults", "1",
        "--cabin", "economy",
        "--max-connections", "1",
        "--limit", str(limit),
        "--compact",
    ]
    # Write to temp file (don't pipe, per connector instructions).
    # Ret date in the name: durations share dep dates.
    tmp = Path(f"/tmp/duffel-{origin}{dest}-{dep_date}-{ret_date}.json")
    try:
        with open(tmp, "w") as fh:
            result = subprocess.run(cmd, stdout=fh, stderr=subprocess.PIPE,
                                    timeout=180)
    except subprocess.TimeoutExpired:
        FAILED_COUNT += 1
        print("  ❌ Duffel search timed out", file=sys.stderr)
        return None
    if result.returncode != 0:
        FAILED_COUNT += 1
        err = result.stderr.decode()[:300]
        if "429" in err:
            RATE_LIMITED = True
        print(f"  ❌ Duffel search failed: {err}", file=sys.stderr)
        return None
    try:
        data = json.loads(tmp.read_text())
    except Exception as e:
        FAILED_COUNT += 1
        print(f"  ❌ JSON parse failed: {e}", file=sys.stderr)
        return None
    if not data.get("ok"):
        FAILED_COUNT += 1
        blob = json.dumps(data)[:300]
        if "429" in blob or "rate_limit" in blob:
            RATE_LIMITED = True
        print(f"  ❌ Search not ok: {blob}", file=sys.stderr)
        return None
    return data.get("offers", [])


def filter_qualifying_offers(offers):
    """
    Filter to qualifying offers per Kiran's specs:
    - 2+ checked bags (excludes basic economy)
    - Max 1 stop per direction (already enforced by search, double-check)
    Returns list of {price, airline, stops, fare_brand, currency}.
    """
    qualifying = []
    for o in offers:
        bags = o.get("bags") or {}
        checked = bags.get("checked") or 0
        if checked < 2:
            continue
        slices = o.get("slices", [])
        max_stops = max((s.get("stops", 0) for s in slices), default=0)
        if max_stops > 1:
            continue
        try:
            price = float(o["price"])
        except (KeyError, ValueError, TypeError):
            continue
        qualifying.append({
            "price": price,
            "airline": o.get("airline", "Unknown"),
            "stops": max_stops,
            "fare_brand": (slices[0].get("fare_brand") if slices else "N/A"),
            "currency": o.get("currency", "USD"),
        })
    return qualifying


def midweek_dates(year, month, min_date):
    """All Tue/Wed/Thu dates in (year, month) on/after min_date."""
    first = date(year, month, 1)
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    out = []
    d = first
    while d <= last:
        if d >= min_date and d.weekday() in MIDWEEK:
            out.append(d)
        d += timedelta(days=1)
    return out


def sample_departures(year, month, samples, min_date):
    """Pick `samples` midweek departure dates spread across the month."""
    cands = midweek_dates(year, month, min_date)
    if not cands:
        return []
    if len(cands) <= samples:
        return cands
    picks = []
    for i in range(samples):
        # Middle of each equal slice of the candidate list (spread).
        idx = (2 * i + 1) * len(cands) // (2 * samples)
        picks.append(cands[idx])
    return picks


def rolling_months(months_ahead, min_date):
    """Next `months_ahead` (year, month) pairs that have >=1 sample date."""
    out = []
    y, m = min_date.year, min_date.month
    guard = 0
    while len(out) < months_ahead and guard < 24:
        if midweek_dates(y, m, min_date):
            out.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
        guard += 1
    return out


def find_cheapest_window(origin, dest, year, month, weeks, samples, min_date,
                         sleep_s):
    """
    Find the cheapest trip window in a given month for `weeks` duration.
    Samples `samples` midweek departure dates spread across the month.
    Returns a calendar cell dict, or None if no qualifying offers found.
    """
    trip_days = weeks * 7
    dep_dates = sample_departures(year, month, samples, min_date)
    results = []
    for dep in dep_dates:
        if RATE_LIMITED:
            break
        ret = dep + timedelta(days=trip_days)
        dep_str, ret_str = dep.isoformat(), ret.isoformat()
        print(f"    Searching {origin}→{dest} {dep_str} → {ret_str}...")
        offers = (cache_search(origin, dest, dep_str, ret_str) if CACHE_MODE
                  else run_duffel_search(origin, dest, dep_str, ret_str))
        if not offers:
            continue
        qualifying = filter_qualifying_offers(offers)
        if not qualifying:
            print("    ⚠ No 2-bag offers found")
            continue
        prices = sorted(q["price"] for q in qualifying)
        p25_idx = max(0, int(len(prices) * 0.25) - 1)
        results.append({
            "dep": dep_str,
            "ret": ret_str,
            "min_price": prices[0],
            "p25_price": prices[p25_idx],
            "num_offers": len(qualifying),
            "cheapest_airline": min(qualifying, key=lambda q: q["price"])["airline"],
        })
        if sleep_s:
            time.sleep(sleep_s)

    if not results:
        return None

    best = min(results, key=lambda r: r["min_price"])
    all_mins = [r["min_price"] for r in results]
    return {
        "date_range": f"{best['dep']} → {best['ret']}",
        "dep_date": best["dep"],
        "ret_date": best["ret"],
        "price_min": round(min(all_mins)),
        "price_max": round(max(r["p25_price"] for r in results)),
        "cheapest_airline": best["cheapest_airline"],
        "num_samples": len(results),
        "year": year,
        "month": month,
        "weeks": weeks,
    }


# ── History / fare-drop detection ────────────────────────────────────

def cell_key(rec):
    return (rec["route"], rec["year"], rec["month"], rec["weeks"])


def load_history():
    if not HISTORY_FILE.exists():
        return []
    out = []
    for line in HISTORY_FILE.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def seed_history_from_output():
    """Seed history from the existing flight-deals.json (Phase 1 output).

    Used once, when no history file exists yet. The seed lines carry the
    Phase 1 generated_at/as_of so drop baselines are honestly dated.
    Returns a list of history records (not yet written).
    """
    if not OUTPUT_FILE.exists():
        return []
    try:
        old = json.loads(OUTPUT_FILE.read_text())
    except Exception:
        return []
    gen = old.get("generated_at")
    as_of = old.get("as_of")
    seeds = []
    for route_key, r in (old.get("routes") or {}).items():
        for cell in r.get("calendar") or []:
            seeds.append({
                "observed_at": gen,
                "as_of": as_of,
                "source": "phase1-output-seed",
                "route": route_key,
                "origin": r.get("origin"),
                "destination": r.get("destination"),
                "year": cell["year"],
                "month": cell["month"],
                "weeks": cell["weeks"],
                "dep_date": cell["dep_date"],
                "ret_date": cell["ret_date"],
                "price_min": cell["price_min"],
                "price_max": cell["price_max"],
                "cheapest_airline": cell.get("cheapest_airline"),
                "num_samples": cell.get("num_samples"),
            })
    return seeds


def compute_changes(cells, history):
    """Annotate each cell with change vs previous snapshot (+ trailing avg).

    cells: list of calendar cell dicts (each has 'route' injected).
    history: prior records only (not including the current run).
    Returns the notable-drops list.
    """
    prev_by_key = {}
    priors_by_key = {}
    for rec in history:
        k = cell_key(rec)
        priors_by_key.setdefault(k, []).append(rec)
        prev_by_key[k] = rec  # file order = chronological; last wins

    drops = []
    for cell in cells:
        k = cell_key(cell)
        prev = prev_by_key.get(k)
        if not prev:
            continue
        delta = prev["price_min"] - cell["price_min"]
        delta_pct = round(100.0 * delta / prev["price_min"], 1) if prev["price_min"] else 0.0
        change = {
            "prev_price_min": prev["price_min"],
            "prev_as_of": prev.get("as_of"),
            "delta": delta,
            "delta_pct": delta_pct,
        }
        priors = priors_by_key.get(k, [])
        if len(priors) >= 3:
            avg = sum(p["price_min"] for p in priors) / len(priors)
            change["trailing_avg_price_min"] = round(avg)
            change["delta_vs_trailing_avg"] = round(avg - cell["price_min"])
            change["delta_vs_trailing_avg_pct"] = (
                round(100.0 * (avg - cell["price_min"]) / avg, 1) if avg else 0.0)
        cell["change_vs_prev"] = change
        if delta >= DROP_MIN_ABS and delta_pct >= DROP_MIN_PCT:
            drops.append({
                "route": cell["route"],
                "origin_metro": cell.get("origin_metro"),
                "dest_metro": cell.get("dest_metro"),
                "year": cell["year"],
                "month": cell["month"],
                "weeks": cell["weeks"],
                "date_range": cell["date_range"],
                "was": prev["price_min"],
                "now": cell["price_min"],
                "drop_abs": delta,
                "drop_pct": delta_pct,
                "baseline_as_of": prev.get("as_of"),
                "cheapest_airline": cell.get("cheapest_airline"),
            })
    drops.sort(key=lambda d: (-d["drop_pct"], -d["drop_abs"]))
    return drops


def flag_cheapest(calendar):
    """Flag the cheapest-month cell within one route+duration calendar."""
    if not calendar:
        return None
    best = min(calendar, key=lambda c: c["price_min"])
    best["cheapest_month"] = True
    return {
        "year": best["year"], "month": best["month"], "weeks": best["weeks"],
        "price_min": best["price_min"], "date_range": best["date_range"],
    }


# ── Main ─────────────────────────────────────────────────────────────

def resolve_routes(args):
    if args.route:
        parts = args.route.split("-")
        if len(parts) != 2:
            print("Route must be like SFO-DEL", file=sys.stderr)
            sys.exit(1)
        metro = next((r for r in ALL_ROUTES if r[0] == parts[0] and r[1] == parts[1]), None)
        return [(parts[0], parts[1],
                 metro[2] if metro else parts[0],
                 metro[3] if metro else parts[1])]
    if args.tier == "1":
        return TIER1_ROUTES
    if args.tier == "2":
        return TIER2_ROUTES
    return ALL_ROUTES


def main():
    parser = argparse.ArgumentParser(description="Fetch flight deal prices via Duffel (Phase B)")
    parser.add_argument("--route", help="Single route like SFO-DEL")
    parser.add_argument("--all", action="store_true", help="All Tier-1 + Tier-2 routes")
    parser.add_argument("--tier", choices=["1", "2"], help="Only this tier")
    parser.add_argument("--durations", default="2,3,4",
                        help="Comma-separated trip durations in weeks (default 2,3,4)")
    parser.add_argument("--weeks", type=int, choices=[2, 3, 4],
                        help="Legacy: single duration")
    parser.add_argument("--months", type=int, default=6,
                        help="Months ahead to search (default 6)")
    parser.add_argument("--samples", type=int, default=2,
                        help="Departure dates sampled per month/duration (default 2)")
    parser.add_argument("--max-requests", type=int, default=600,
                        help="Abort if the planned matrix exceeds this many Duffel requests")
    parser.add_argument("--sleep", type=float, default=0.5,
                        help="Seconds to sleep between searches (default 0.5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing files")
    parser.add_argument("--from-cache", action="store_true",
                        help="Replay saved Duffel responses from /tmp "
                             "(no API calls). Only routes whose planned "
                             "searches were all attempted are kept.")
    args = parser.parse_args()

    global CACHE_MODE
    CACHE_MODE = args.from_cache

    if not (args.all or args.tier or args.route):
        print("Specify --all, --tier, or --route", file=sys.stderr)
        sys.exit(1)

    durations = [args.weeks] if args.weeks else [
        int(x) for x in args.durations.split(",") if x.strip()]
    routes = resolve_routes(args)
    today = date.today()
    min_date = today + timedelta(days=MIN_LEAD_DAYS)
    months = rolling_months(args.months, min_date)

    estimate = len(routes) * len(durations) * len(months) * args.samples
    print(f"Plan: {len(routes)} routes x {len(durations)} durations "
          f"x {len(months)} months x {args.samples} samples "
          f"= up to {estimate} Duffel requests")
    print(f"Months: {[(y, m) for y, m in months]} | earliest departure {min_date}")
    if CACHE_MODE:
        print("CACHE MODE: replaying saved responses, no Duffel calls.")
    if estimate > args.max_requests and not CACHE_MODE:
        print(f"❌ Plan exceeds --max-requests {args.max_requests}; "
              f"narrow the matrix (e.g. --tier 1) or raise the cap.",
              file=sys.stderr)
        sys.exit(2)

    all_data = {
        "generated_at": None,
        "as_of": today.isoformat(),
        "weeks": PRIMARY_WEEKS,
        "durations": durations,
        "routes": {},
        "biggest_drops": [],
        "festival_seasons": FESTIVAL_SEASONS,
        "spec": {
            "max_stops": 1,
            "trip_type": "round-trip",
            "pricing": "per-person",
            "cabin": "economy",
            "min_checked_bags": 2,
            "note": "Excludes basic economy. Prices are snapshots, not live.",
        },
    }

    all_cells = []  # every calendar cell this run, with route context
    for origin, dest, origin_metro, dest_metro in routes:
        if RATE_LIMITED:
            break
        route_key = f"{origin}-{dest}"
        print(f"\n✈️  {route_key} ({origin_metro} → {dest_metro})")
        calendars_by_weeks = {}
        route_cheapest = []
        for weeks in durations:
            if RATE_LIMITED:
                break
            print(f"  Duration: {weeks} weeks")
            calendar = []
            for (y, m) in months:
                if RATE_LIMITED:
                    break
                print(f"  📅 {y}-{m:02d} ({weeks} weeks)...")
                cell = find_cheapest_window(origin, dest, y, m, weeks,
                                             args.samples, min_date, args.sleep)
                if cell:
                    calendar.append(cell)
                else:
                    print(f"  ⚠ No data for {y}-{m:02d} ({weeks}w)")
            cheapest = flag_cheapest(calendar)
            if cheapest:
                route_cheapest.append(cheapest)
            calendars_by_weeks[str(weeks)] = calendar
            for cell in calendar:
                cell["route"] = route_key
                cell["origin_metro"] = origin_metro
                cell["dest_metro"] = dest_metro
                all_cells.append(cell)
            print(f"  ✅ {len(calendar)} months of data ({weeks}w)")

        primary = calendars_by_weeks.get(str(PRIMARY_WEEKS), [])
        cheapest_overall = (min(route_cheapest, key=lambda c: c["price_min"])
                            if route_cheapest else None)
        all_data["routes"][route_key] = {
            "origin": origin,
            "destination": dest,
            "origin_metro": origin_metro,
            "dest_metro": dest_metro,
            "weeks": PRIMARY_WEEKS,
            "calendar": primary,
            "calendars_by_weeks": calendars_by_weeks,
            "cheapest_overall": cheapest_overall,
        }

    if CACHE_MODE:
        planned_per_route = len(durations) * len(months) * args.samples
        kept = []
        for rk in list(all_data["routes"]):
            if ATTEMPTED.get(rk, 0) >= planned_per_route:
                kept.append(rk)
            else:
                print(f"  🗑  {rk}: only {ATTEMPTED.get(rk, 0)}/{planned_per_route} "
                      f"searches attempted — route dropped (incomplete)")
                del all_data["routes"][rk]
        all_cells = [c for c in all_cells if c["route"] in kept]

    print(f"\n{'Cache reads' if CACHE_MODE else 'Duffel requests made'}: "
          f"{REQUEST_COUNT} (failed: {FAILED_COUNT})")
    if RATE_LIMITED:
        print("❌ Aborted: Duffel rate limit (429). No files written — "
              "existing flight-deals.json left untouched.", file=sys.stderr)
        sys.exit(3)

    if not all_cells:
        print("❌ No data collected at all. No files written — "
              "existing flight-deals.json left untouched.", file=sys.stderr)
        sys.exit(1)

    all_data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # History: seed from the old output (once), then compare, then append.
    history = load_history()
    seeds = []
    if not history:
        seeds = seed_history_from_output()
        history = seeds
        if seeds:
            print(f"Seeded history baseline from existing output: "
                  f"{len(seeds)} cells (as_of {seeds[0].get('as_of')})")

    drops = compute_changes(all_cells, history)
    all_data["biggest_drops"] = drops[:12]
    print(f"Notable drops vs previous snapshot: {len(drops)}")
    for d in drops[:12]:
        print(f"  ↓ {d['route']} {d['year']}-{d['month']:02d} ({d['weeks']}w): "
              f"${d['was']} → ${d['now']} (-${d['drop_abs']}, -{d['drop_pct']}%) "
              f"baseline {d['baseline_as_of']}")

    if args.dry_run:
        print("\n--- DRY RUN (no files written) ---")
        print(json.dumps(all_data, indent=2)[:3000])
        return

    # Append this run's observations to history.
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    now_iso = all_data["generated_at"]
    run_source = ("flight-deals.py --from-cache (salvaged live run)"
                  if CACHE_MODE else "flight-deals.py")
    lines = [json.dumps(s) for s in seeds]
    for cell in all_cells:
        lines.append(json.dumps({
            "observed_at": now_iso,
            "as_of": today.isoformat(),
            "source": run_source,
            "route": cell["route"],
            "origin": cell["route"].split("-")[0],
            "destination": cell["route"].split("-")[1],
            "year": cell["year"],
            "month": cell["month"],
            "weeks": cell["weeks"],
            "dep_date": cell["dep_date"],
            "ret_date": cell["ret_date"],
            "price_min": cell["price_min"],
            "price_max": cell["price_max"],
            "cheapest_airline": cell.get("cheapest_airline"),
            "num_samples": cell.get("num_samples"),
        }))
    with open(HISTORY_FILE, "a") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"📜 History: appended {len(lines)} lines to {HISTORY_FILE.name}")

    # Write output. Single-route runs merge into the existing file.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if args.route and OUTPUT_FILE.exists():
        existing = json.loads(OUTPUT_FILE.read_text())
        existing["routes"].update(all_data["routes"])
        existing["generated_at"] = all_data["generated_at"]
        existing["as_of"] = all_data["as_of"]
        existing["durations"] = sorted(set(
            (existing.get("durations") or []) + durations))
        existing["biggest_drops"] = all_data["biggest_drops"]
        existing["festival_seasons"] = FESTIVAL_SEASONS
        all_data = existing

    OUTPUT_FILE.write_text(json.dumps(all_data, indent=2))
    print(f"✅ Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
