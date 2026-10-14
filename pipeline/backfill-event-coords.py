#!/usr/bin/env python3
"""backfill-event-coords.py — Fill NULL latitude/longitude on upcoming events.

Coord-less events are invisible to the site's ZIP / near-me radius search.
Ingestion now geocodes at insert time (event_geocode.py, wired into
temple-events-scraper.py and scrape-spiritual-events.py); this backfills
the existing backlog. Groups events by (venue_name, city, state) so each
unique venue costs one Nominatim lookup; PATCHes every event in the group.

Usage:
  python3 -u backfill-event-coords.py              # Backfill all upcoming
  python3 -u backfill-event-coords.py --dry-run    # Report only
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from event_geocode import geocode_venue

ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
REST = f"{SB_URL}/rest/v1"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def curl(method, path, payload=None):
    cmd = ["curl", "-sS", "--max-time", "30", "-X", method, f"{REST}{path}",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal"]
    if payload is not None:
        cmd += ["--data-binary", json.dumps(payload)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    return r


def fetch_missing():
    rows, offset = [], 0
    while True:
        r = curl("GET", f"/events?select=id,title,venue_name,city,state,source"
                        f"&date=gte.{TODAY}&latitude=is.null"
                        f"&order=id&limit=500&offset={offset}")
        batch = json.loads(r.stdout)
        if not isinstance(batch, list) or not batch:
            break
        rows.extend(batch)
        if len(batch) < 500:
            break
        offset += 500
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    missing = fetch_missing()
    print(f"Upcoming events missing latitude: {len(missing)}")

    groups = {}
    for ev in missing:
        key = (ev.get("venue_name") or "", ev.get("city") or "",
               ev.get("state") or "")
        groups.setdefault(key, []).append(ev)
    print(f"Unique (venue, city, state) groups: {len(groups)}\n")

    filled_venue = filled_city = still_missing = patch_errors = 0
    failures = []
    for (venue, city, state), evs in sorted(groups.items()):
        lat, lon, level = geocode_venue(venue, city, state)
        label = f"{venue} ({city}, {state}) — {len(evs)} events"
        if lat is None:
            still_missing += len(evs)
            failures.append(label)
            print(f"  ✗ {label}: no geocode result")
            continue
        print(f"  ✓ {label}: {level} → {lat:.4f},{lon:.4f}")
        if args.dry_run:
            if level == "venue":
                filled_venue += len(evs)
            else:
                filled_city += len(evs)
            continue
        for ev in evs:
            r = curl("PATCH", f"/events?id=eq.{ev['id']}",
                     {"latitude": lat, "longitude": lon})
            if r.returncode == 0 and not r.stdout.strip():
                if level == "venue":
                    filled_venue += 1
                else:
                    filled_city += 1
            else:
                patch_errors += 1
                print(f"    ⚠ PATCH failed for {ev['id']}: {r.stdout[:120]} {r.stderr[:120]}")

    print(f"\n=== {'DRY RUN — ' if args.dry_run else ''}Summary ===")
    print(f"Filled (venue-level): {filled_venue}")
    print(f"Filled (city fallback): {filled_city}")
    print(f"Still missing: {still_missing}")
    if patch_errors:
        print(f"PATCH errors: {patch_errors}")
    if failures:
        print("Failed groups:")
        for f in failures:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
