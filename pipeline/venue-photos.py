#!/usr/bin/env python3
"""
venue-photos.py — Fetch venue photos from Google Places API
and store in the venue_images JSONB column on the events table.

Usage:
  source ~/.env.supabase
  export GOOGLE_PLACES_API_KEY=...
  python3 pipeline/venue-photos.py
"""

import json
import os
import sys
import time
from datetime import date

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("pip install requests first")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: source ~/.env.supabase first")
    sys.exit(1)
if not GOOGLE_API_KEY:
    print("ERROR: set GOOGLE_PLACES_API_KEY")
    sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

MAX_PHOTOS_PER_VENUE = 5
PHOTO_WIDTH = 800


# ── Helpers ─────────────────────────────────────────────────────────
def find_place(venue_name: str, city: str, state: str) -> dict | None:
    """Search Google Places for a venue, return first candidate."""
    query = f"{venue_name}, {city}, {state}"
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id,name",
        "key": GOOGLE_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        candidates = data.get("candidates", [])
        return candidates[0] if candidates else None
    except Exception as e:
        print(f"    ⚠ Find place error: {e}")
        return None


def get_place_photos(place_id: str) -> list[str]:
    """Fetch photo references from Place Details, return photo URLs."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "photos",
        "key": GOOGLE_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        photos = data.get("result", {}).get("photos", [])
    except Exception as e:
        print(f"    ⚠ Place details error: {e}")
        return []

    image_urls = []
    for photo in photos[:MAX_PHOTOS_PER_VENUE]:
        ref = photo.get("photo_reference")
        if not ref:
            continue
        # Use the Places photo URL directly — it redirects to the image
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth={PHOTO_WIDTH}&photo_reference={ref}&key={GOOGLE_API_KEY}"
        )
        image_urls.append(photo_url)

    return image_urls


def update_event_venue_images(event_id: str, images: list[str]) -> bool:
    """PATCH the event's venue_images column."""
    url = f"{SUPABASE_URL}/rest/v1/events?id=eq.{event_id}"
    payload = {"venue_images": images}
    try:
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"    ⚠ DB update error: {e}")
        return False


def fetch_events_needing_photos() -> list[dict]:
    """Get all upcoming events with no venue_images."""
    today = date.today().isoformat()
    url = (
        f"{SUPABASE_URL}/rest/v1/events"
        f"?select=id,venue_name,city,state,date,venue_images"
        f"&date=gte.{today}"
        f"&order=date.asc"
        f"&limit=500"
    )
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"ERROR fetching events: {r.status_code} {r.text}")
        sys.exit(1)
    events = r.json()
    # Filter to events with empty/null venue_images
    return [
        e for e in events
        if not e.get("venue_images") or (isinstance(e["venue_images"], list) and len(e["venue_images"]) == 0)
    ]


# ── Main ────────────────────────────────────────────────────────────
def main():
    print("=== Venue Photos Pipeline ===")
    print(f"Google Places API key: ...{GOOGLE_API_KEY[-6:]}")
    print()

    events = fetch_events_needing_photos()
    print(f"Found {len(events)} events needing venue photos\n")

    if not events:
        print("Nothing to do!")
        return

    # Deduplicate by venue+city to avoid redundant API calls
    venue_cache: dict[str, list[str]] = {}  # "venue|city|state" -> [urls]
    stats = {"updated": 0, "no_match": 0, "no_photos": 0, "errors": 0, "cached": 0}

    for i, ev in enumerate(events):
        venue = ev.get("venue_name") or ""
        city = ev.get("city") or ""
        state = ev.get("state") or ""
        event_id = ev["id"]

        if not venue or not city:
            stats["no_match"] += 1
            continue

        cache_key = f"{venue.lower()}|{city.lower()}|{state.lower()}"
        label = f"[{i+1}/{len(events)}] {venue}, {city}"

        # Check cache first
        if cache_key in venue_cache:
            photos = venue_cache[cache_key]
            if photos:
                if update_event_venue_images(event_id, photos):
                    stats["cached"] += 1
                    print(f"{label} → {len(photos)} photos (cached)")
                else:
                    stats["errors"] += 1
                    print(f"{label} → DB update failed (cached)")
            else:
                stats["no_photos"] += 1
                print(f"{label} → no photos (cached)")
            continue

        # Find place
        place = find_place(venue, city, state)
        if not place:
            venue_cache[cache_key] = []
            stats["no_match"] += 1
            print(f"{label} → not found on Google")
            time.sleep(0.1)
            continue

        # Get photos
        place_id = place["place_id"]
        photos = get_place_photos(place_id)
        venue_cache[cache_key] = photos

        if not photos:
            stats["no_photos"] += 1
            print(f"{label} → found but no photos")
            time.sleep(0.1)
            continue

        # Update DB
        if update_event_venue_images(event_id, photos):
            stats["updated"] += 1
            print(f"{label} → {len(photos)} photos ✓")
        else:
            stats["errors"] += 1
            print(f"{label} → DB update failed")

        time.sleep(0.1)

    print(f"\n=== Done ===")
    print(f"Updated: {stats['updated']}")
    print(f"Cached:  {stats['cached']}")
    print(f"No match: {stats['no_match']}")
    print(f"No photos: {stats['no_photos']}")
    print(f"Errors:  {stats['errors']}")


if __name__ == "__main__":
    main()
