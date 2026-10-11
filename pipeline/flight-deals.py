#!/usr/bin/env python3
"""
Flight deals price fetcher for The Videshi.

Searches Duffel for round-trip fares on US-India routes and writes
price data for the frontend price calendar.

Specs (Kiran's decisions):
- Max 1 stop (no 2+ stops)
- Round-trip, per person, economy
- Exclude basic economy — only fares with 2+ checked bags
- Duration: 2/3/4 weeks for India routes
- Output: price ranges + date ranges per month/season

Usage:
  python3 flight-deals.py --route SFO-DEL --weeks 3 --months 6
  python3 flight-deals.py --all --weeks 3  (all Phase 1 routes)
  python3 flight-deals.py --all --weeks 3 --dry-run  (no writes, just print)
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

# Phase 1 routes: (origin, destination, origin_metro, dest_metro)
PHASE1_ROUTES = [
    ("SFO", "DEL", "Bay Area", "Delhi"),
    ("SFO", "BLR", "Bay Area", "Bengaluru"),
    ("JFK", "DEL", "New York", "Delhi"),
    ("JFK", "BOM", "New York", "Mumbai"),
    ("ORD", "DEL", "Chicago", "Delhi"),
    ("DFW", "HYD", "Dallas", "Hyderabad"),
    ("SEA", "DEL", "Seattle", "Delhi"),
    ("LAX", "BOM", "Los Angeles", "Mumbai"),
    ("EWR", "DEL", "New York", "Delhi"),
    ("IAH", "HYD", "Houston", "Hyderabad"),
]

DATA_DIR = Path.home() / "workspace" / "the-videshi-news" / "public" / "data"
STATE_DIR = Path.home() / "workspace" / "the-videshi-news" / "pipeline" / ".state"
OUTPUT_FILE = DATA_DIR / "flight-deals.json"

# Festival seasons with (name, start_month, start_day, end_month, end_day, book_by_months)
# book_by_months = how many months ahead to book
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
        "id": "christmas-2026",
        "name": "Christmas & New Year",
        "emoji": "🎄",
        "start": (2026, 12, 20),
        "end": (2027, 1, 5),
        "book_by_months": 5,
        "note": "Peak holiday season",
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


def run_duffel_search(origin, dest, dep_date, ret_date, limit=100):
    """Run Duffel search and return offers list. Returns None on failure."""
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
    # Write to temp file (don't pipe, per skill instructions)
    tmp = Path(f"/tmp/duffel-{origin}{dest}-{dep_date}.json")
    result = subprocess.run(
        cmd, stdout=open(tmp, "w"), stderr=subprocess.PIPE,
        timeout=180,
    )
    if result.returncode != 0:
        print(f"  ❌ Duffel search failed: {result.stderr.decode()[:200]}", file=sys.stderr)
        return None
    try:
        data = json.loads(tmp.read_text())
    except Exception as e:
        print(f"  ❌ JSON parse failed: {e}", file=sys.stderr)
        return None
    if not data.get("ok"):
        print(f"  ❌ Search not ok", file=sys.stderr)
        return None
    return data.get("offers", [])


def filter_qualifying_offers(offers):
    """
    Filter to qualifying offers per Kiran's specs:
    - 2+ checked bags (excludes basic economy)
    - Max 1 stop per direction (already enforced by search, double-check)
    Returns list of (price, airline, stops, fare_brand).
    """
    qualifying = []
    for o in offers:
        bags = o.get("bags") or {}
        checked = bags.get("checked") or 0
        if checked < 2:
            continue
        # Verify max 1 stop per slice
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


def find_cheapest_window(origin, dest, year, month, weeks, samples=4):
    """
    Find the cheapest trip window in a given month.
    Samples `samples` departure dates spread across the month,
    each for `weeks` duration. Returns dict with date_range and price_range.
    """
    trip_days = weeks * 7
    # Sample departure dates: 1st, 8th, 15th, 22nd of month (or fewer if month is short)
    first = date(year, month, 1)
    # Last day of month
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)

    dep_dates = []
    d = first
    while d <= last and len(dep_dates) < samples:
        # Prefer Tue/Wed/Thu departures (cheaper per research)
        # But sample across the month for coverage
        dep_dates.append(d)
        d += timedelta(days=7)

    results = []
    for dep in dep_dates:
        ret = dep + timedelta(days=trip_days)
        dep_str = dep.isoformat()
        ret_str = ret.isoformat()
        print(f"    Searching {origin}→{dest} {dep_str} → {ret_str}...")
        offers = run_duffel_search(origin, dest, dep_str, ret_str)
        if not offers:
            continue
        qualifying = filter_qualifying_offers(offers)
        if not qualifying:
            print(f"    ⚠ No 2-bag offers found")
            continue
        prices = sorted(q["price"] for q in qualifying)
        # Price range: min to 25th percentile (representative "good" prices)
        p25_idx = max(0, int(len(prices) * 0.25) - 1)
        results.append({
            "dep": dep_str,
            "ret": ret_str,
            "min_price": prices[0],
            "p25_price": prices[p25_idx],
            "num_offers": len(qualifying),
            "cheapest_airline": min(qualifying, key=lambda q: q["price"])["airline"],
        })
        time.sleep(2)  # Be nice to the API

    if not results:
        return None

    # Pick the cheapest window
    best = min(results, key=lambda r: r["min_price"])
    # Overall range across all sampled windows
    all_mins = [r["min_price"] for r in results]
    return {
        "date_range": f"{best['dep']} → {best['ret']}",
        "dep_date": best["dep"],
        "ret_date": best["ret"],
        "price_min": round(min(all_mins)),
        "price_max": round(max(r["p25_price"] for r in results)),
        "cheapest_airline": best["cheapest_airline"],
        "num_samples": len(results),
    }


def build_route_calendar(origin, dest, weeks, months_ahead=6):
    """Build price calendar for a route."""
    today = date.today()
    calendar = []
    for i in range(months_ahead):
        # Calculate year/month
        m = today.month + i
        y = today.year + (m - 1) // 12
        m = ((m - 1) % 12) + 1

        print(f"  📅 {y}-{m:02d} ({weeks} weeks)...")
        window = find_cheapest_window(origin, dest, y, m, weeks)
        if window:
            window["year"] = y
            window["month"] = m
            window["weeks"] = weeks
            calendar.append(window)
        else:
            print(f"  ⚠ No data for {y}-{m:02d}")

    return calendar


def main():
    parser = argparse.ArgumentParser(description="Fetch flight deal prices via Duffel")
    parser.add_argument("--route", help="Single route like SFO-DEL")
    parser.add_argument("--all", action="store_true", help="All Phase 1 routes")
    parser.add_argument("--weeks", type=int, default=3, choices=[2, 3, 4],
                        help="Trip duration in weeks")
    parser.add_argument("--months", type=int, default=6,
                        help="Months ahead to search")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing files")
    args = parser.parse_args()

    if args.all:
        routes = PHASE1_ROUTES
    elif args.route:
        parts = args.route.split("-")
        if len(parts) != 2:
            print("Route must be like SFO-DEL", file=sys.stderr)
            sys.exit(1)
        # Find metro names
        metro = next((r for r in PHASE1_ROUTES if r[0] == parts[0] and r[1] == parts[1]), None)
        routes = [(parts[0], parts[1],
                   metro[2] if metro else parts[0],
                   metro[3] if metro else parts[1])]
    else:
        print("Specify --route or --all", file=sys.stderr)
        sys.exit(1)

    all_data = {
        "generated_at": None,
        "as_of": date.today().isoformat(),
        "weeks": args.weeks,
        "routes": {},
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

    for origin, dest, origin_metro, dest_metro in routes:
        route_key = f"{origin}-{dest}"
        print(f"\n✈️  {route_key} ({origin_metro} → {dest_metro}), {args.weeks} weeks")
        calendar = build_route_calendar(origin, dest, args.weeks, args.months)
        all_data["routes"][route_key] = {
            "origin": origin,
            "destination": dest,
            "origin_metro": origin_metro,
            "dest_metro": dest_metro,
            "weeks": args.weeks,
            "calendar": calendar,
        }
        print(f"  ✅ {len(calendar)} months of data")

    all_data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if args.dry_run:
        print("\n--- DRY RUN OUTPUT ---")
        print(json.dumps(all_data, indent=2)[:3000])
        return

    # Write output
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # For single route, merge with existing file
    if not args.all and OUTPUT_FILE.exists():
        existing = json.loads(OUTPUT_FILE.read_text())
        existing["routes"].update(all_data["routes"])
        existing["generated_at"] = all_data["generated_at"]
        existing["as_of"] = all_data["as_of"]
        all_data = existing

    OUTPUT_FILE.write_text(json.dumps(all_data, indent=2))
    print(f"\n✅ Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
