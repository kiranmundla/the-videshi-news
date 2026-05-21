#!/usr/bin/env python3
"""
venue-seatmaps.py — Fetch seating chart images from Ticketmaster API
for events sourced from Ticketmaster and store seatmap_url in the events table.

Uses the `ticketmaster` CLI to search for events and get seat_map_url
from event details.

Usage:
    python3 pipeline/venue-seatmaps.py              # Full run
    python3 pipeline/venue-seatmaps.py --dry-run     # Preview without updating
"""

import json
import os
import re
import sys
import time
import subprocess
import argparse
from datetime import date

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ENV_FILE = os.path.expanduser("~/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

SB_HEADERS = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_tm_events():
    """Get all upcoming Ticketmaster-sourced events that don't have seatmap_url yet."""
    today = date.today().isoformat()
    r = requests.get(
        f"{SB_URL}/rest/v1/events",
        params={
            "select": "id,title,source_id,venue_name,city,state,date,seatmap_url",
            "source": "eq.ticketmaster",
            "date": f"gte.{today}",
            "limit": "200",
        },
        headers=SB_HEADERS,
    )
    r.raise_for_status()
    events = r.json()
    # Filter to those without seatmap
    return [e for e in events if not e.get("seatmap_url")]


def search_tm_event(title: str, state: str) -> list:
    """Search Ticketmaster for events matching title and state."""
    # Simplify title for search - take first meaningful part
    # E.g. "Diljit Dosanjh – Aura World Tour 2026" -> "Diljit Dosanjh"
    search_term = title.split("–")[0].split("-")[0].split(":")[0].strip()
    # Also remove year
    search_term = re.sub(r'\b20\d{2}\b', '', search_term).strip()

    try:
        result = subprocess.run(
            ["ticketmaster", "search-events",
             "--keyword", search_term,
             "--state-code", state or "",
             "--size", "10",
             "--sort", "date,asc"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        return data.get("events", [])
    except Exception as e:
        print(f"    ⚠ Search failed: {e}")
        return []


def get_event_seatmap(event_id: str) -> str | None:
    """Get the seatmap URL from Ticketmaster event details."""
    try:
        result = subprocess.run(
            ["ticketmaster", "event-details", "--event-id", event_id],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        event = data.get("event", {})
        return event.get("seat_map_url")
    except Exception as e:
        print(f"    ⚠ Details failed: {e}")
        return None


def update_seatmap(event_id: str, seatmap_url: str) -> bool:
    """Update the seatmap_url in Supabase."""
    r = requests.patch(
        f"{SB_URL}/rest/v1/events?id=eq.{event_id}",
        headers=SB_HEADERS,
        json={"seatmap_url": seatmap_url},
    )
    return r.status_code in (200, 204)


def find_best_match(our_event: dict, tm_events: list) -> dict | None:
    """Find the best matching TM event by venue + date."""
    our_venue = (our_event.get("venue_name") or "").lower()
    our_date = our_event.get("date", "")

    for tm_evt in tm_events:
        tm_venue = (tm_evt.get("venue") or "").lower()
        tm_date = tm_evt.get("date", "")
        
        # Match on date and venue name similarity
        if tm_date == our_date:
            # Exact venue match or close enough
            if our_venue and tm_venue and (
                our_venue in tm_venue or tm_venue in our_venue
                or our_venue.split()[0] == tm_venue.split()[0]
            ):
                return tm_evt
        
    # Fallback: same venue name regardless of date (same tour, different date format)
    for tm_evt in tm_events:
        tm_venue = (tm_evt.get("venue") or "").lower()
        if our_venue and tm_venue and (
            our_venue in tm_venue or tm_venue in our_venue
        ):
            return tm_evt

    # Last fallback: just return first result if artist matches well
    if tm_events:
        return tm_events[0]
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch seatmaps for TM events")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    events = get_tm_events()
    print(f"📊 Found {len(events)} Ticketmaster events needing seatmaps\n")

    if not events:
        print("✅ All events already have seatmaps!")
        return

    # Cache: venue+state -> seatmap_url (avoid duplicate API calls for same venue)
    venue_cache: dict[str, str | None] = {}
    success = 0
    failed = 0

    for i, event in enumerate(events):
        title = event["title"]
        venue = event["venue_name"] or ""
        state = event["state"] or ""
        cache_key = f"{venue.lower()}|{state.lower()}"

        print(f"[{i+1}/{len(events)}] {title}")
        print(f"         📍 {venue}, {state}")

        # Check cache first
        if cache_key in venue_cache:
            seatmap_url = venue_cache[cache_key]
            if seatmap_url:
                print(f"         ✅ Cached seatmap")
                if not args.dry_run:
                    update_seatmap(event["id"], seatmap_url)
                success += 1
            else:
                print(f"         ⚪ Cached: no seatmap available")
                failed += 1
            continue

        # Search for the event on Ticketmaster
        tm_events = search_tm_event(title, state)
        if not tm_events:
            print(f"         ❌ Not found on Ticketmaster")
            venue_cache[cache_key] = None
            failed += 1
            time.sleep(0.3)
            continue

        # Find best match
        match = find_best_match(event, tm_events)
        if not match:
            print(f"         ❌ No matching event found")
            venue_cache[cache_key] = None
            failed += 1
            time.sleep(0.3)
            continue

        tm_id = match.get("id") or match.get("hex_id")
        if not tm_id:
            print(f"         ❌ No event ID in match")
            venue_cache[cache_key] = None
            failed += 1
            time.sleep(0.3)
            continue

        print(f"         🔍 Matched: {match.get('name')} @ {match.get('venue')} (id={tm_id})")

        # Get seatmap from event details
        seatmap_url = get_event_seatmap(tm_id)
        time.sleep(0.3)  # Rate limit

        if seatmap_url:
            print(f"         🎫 Seatmap: {seatmap_url[:80]}...")
            venue_cache[cache_key] = seatmap_url
            if not args.dry_run:
                if update_seatmap(event["id"], seatmap_url):
                    success += 1
                else:
                    print(f"         ❌ Failed to update DB")
                    failed += 1
            else:
                success += 1
        else:
            print(f"         ⚪ No seatmap available for this venue")
            venue_cache[cache_key] = None
            failed += 1

    print(f"\n📊 Results: {success} seatmaps found, {failed} not available")
    if args.dry_run:
        print("   (dry run — no DB updates)")


if __name__ == "__main__":
    main()
