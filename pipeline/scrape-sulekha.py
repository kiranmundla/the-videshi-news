#!/usr/bin/env python3
"""
scrape-sulekha.py — Scrape Indian events from Sulekha Events
and upsert them into the Supabase `events` table.

Sulekha embeds JSON-LD structured data (schema.org/Event) directly in each
city page, giving us clean title, dates, venue, geo, price, images, and
organizer data with zero HTML parsing.

Usage:
    python3 scrape-sulekha.py              # Full scrape (today's day slice)
    python3 scrape-sulekha.py --dry-run    # Print events without inserting
    python3 scrape-sulekha.py --city houston
    python3 scrape-sulekha.py --day 0      # Specific day (0=Mon..6=Sun)
"""

import json
import hashlib
import os
import re
import sys
import time
import argparse
from datetime import datetime, timezone

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q", "--break-system-packages"])
    import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")
REST = f"{SB_URL}/rest/v1"

HEADERS = {
    "User-Agent": "TheVideshi/1.0 (thevideshi.com; diaspora event aggregator)"
}

# Sulekha URL pattern: https://events.sulekha.com/indian-events-in-{city-slug}
# City slugs use Sulekha's format: lowercase, hyphens
# Sulekha geo-locates by IP and ignores the URL city — we must send a
# `sulusrloc` cookie with the city/state/zip/coords to force the right city.
# Cookie format: "united states::US::{City}::::{State}::{zip}::{lat}::{lng}::0"
CITIES = [
    # Batch 0 (Mon)
    {"slug": "san-francisco", "display": "San Francisco", "state": "CA", "st": "California", "zip": "94102", "lat": 37.7749, "lng": -122.4194},
    {"slug": "los-angeles", "display": "Los Angeles", "state": "CA", "st": "California", "zip": "90001", "lat": 34.0522, "lng": -118.2437},
    {"slug": "austin", "display": "Austin", "state": "TX", "st": "Texas", "zip": "78701", "lat": 30.2672, "lng": -97.7431},
    {"slug": "tampa", "display": "Tampa", "state": "FL", "st": "Florida", "zip": "33601", "lat": 27.9506, "lng": -82.4572},
    {"slug": "irvine", "display": "Irvine", "state": "CA", "st": "California", "zip": "92602", "lat": 33.6846, "lng": -117.8265},
    {"slug": "orlando", "display": "Orlando", "state": "FL", "st": "Florida", "zip": "32801", "lat": 28.5383, "lng": -81.3792},
    {"slug": "cleveland", "display": "Cleveland", "state": "OH", "st": "Ohio", "zip": "44101", "lat": 41.4993, "lng": -81.6944},
    {"slug": "milwaukee", "display": "Milwaukee", "state": "WI", "st": "Wisconsin", "zip": "53201", "lat": 43.0389, "lng": -87.9065},
    # Batch 1 (Tue)
    {"slug": "san-jose", "display": "San Jose", "state": "CA", "st": "California", "zip": "95101", "lat": 37.3382, "lng": -121.8863},
    {"slug": "seattle", "display": "Seattle", "state": "WA", "st": "Washington", "zip": "98101", "lat": 47.6062, "lng": -122.3321},
    {"slug": "miami", "display": "Miami", "state": "FL", "st": "Florida", "zip": "33101", "lat": 25.7617, "lng": -80.1918},
    {"slug": "charlotte", "display": "Charlotte", "state": "NC", "st": "North Carolina", "zip": "28201", "lat": 35.2271, "lng": -80.8431},
    {"slug": "plano", "display": "Plano", "state": "TX", "st": "Texas", "zip": "75023", "lat": 33.0198, "lng": -96.6989},
    {"slug": "baltimore", "display": "Baltimore", "state": "MD", "st": "Maryland", "zip": "21201", "lat": 39.2904, "lng": -76.6122},
    {"slug": "kansas-city", "display": "Kansas City", "state": "MO", "st": "Missouri", "zip": "64101", "lat": 39.0997, "lng": -94.5786},
    # Batch 2 (Wed)
    {"slug": "new-york", "display": "New York", "state": "NY", "st": "New York", "zip": "10001", "lat": 40.7128, "lng": -74.0060},
    {"slug": "washington-dc", "display": "Washington", "state": "DC", "st": "District of Columbia", "zip": "20001", "lat": 38.9072, "lng": -77.0369},
    {"slug": "phoenix", "display": "Phoenix", "state": "AZ", "st": "Arizona", "zip": "85001", "lat": 33.4484, "lng": -112.0740},
    {"slug": "raleigh", "display": "Raleigh", "state": "NC", "st": "North Carolina", "zip": "27601", "lat": 35.7796, "lng": -78.6382},
    {"slug": "fremont", "display": "Fremont", "state": "CA", "st": "California", "zip": "94536", "lat": 37.5485, "lng": -121.9886},
    {"slug": "stamford", "display": "Stamford", "state": "CT", "st": "Connecticut", "zip": "06901", "lat": 41.0534, "lng": -73.5387},
    {"slug": "st-louis", "display": "St Louis", "state": "MO", "st": "Missouri", "zip": "63101", "lat": 38.6270, "lng": -90.1994},
    # Batch 3 (Thu)
    {"slug": "edison-nj", "display": "Edison", "state": "NJ", "st": "New Jersey", "zip": "08817", "lat": 40.5187, "lng": -74.4121},
    {"slug": "boston", "display": "Boston", "state": "MA", "st": "Massachusetts", "zip": "02101", "lat": 42.3601, "lng": -71.0589},
    {"slug": "denver", "display": "Denver", "state": "CO", "st": "Colorado", "zip": "80201", "lat": 39.7392, "lng": -104.9903},
    {"slug": "columbus", "display": "Columbus", "state": "OH", "st": "Ohio", "zip": "43201", "lat": 39.9612, "lng": -82.9988},
    {"slug": "sunnyvale", "display": "Sunnyvale", "state": "CA", "st": "California", "zip": "94085", "lat": 37.3688, "lng": -122.0363},
    {"slug": "ann-arbor", "display": "Ann Arbor", "state": "MI", "st": "Michigan", "zip": "48104", "lat": 42.2808, "lng": -83.7430},
    {"slug": "las-vegas", "display": "Las Vegas", "state": "NV", "st": "Nevada", "zip": "89101", "lat": 36.1699, "lng": -115.1398},
    # Batch 4 (Fri)
    {"slug": "chicago", "display": "Chicago", "state": "IL", "st": "Illinois", "zip": "60601", "lat": 41.8781, "lng": -87.6298},
    {"slug": "atlanta", "display": "Atlanta", "state": "GA", "st": "Georgia", "zip": "30301", "lat": 33.7490, "lng": -84.3880},
    {"slug": "san-diego", "display": "San Diego", "state": "CA", "st": "California", "zip": "92101", "lat": 32.7157, "lng": -117.1611},
    {"slug": "indianapolis", "display": "Indianapolis", "state": "IN", "st": "Indiana", "zip": "46201", "lat": 39.7684, "lng": -86.1581},
    {"slug": "cary", "display": "Cary", "state": "NC", "st": "North Carolina", "zip": "27511", "lat": 35.7915, "lng": -78.7811},
    {"slug": "san-antonio", "display": "San Antonio", "state": "TX", "st": "Texas", "zip": "78201", "lat": 29.4241, "lng": -98.4936},
    {"slug": "richmond", "display": "Richmond", "state": "VA", "st": "Virginia", "zip": "23218", "lat": 37.5407, "lng": -77.4360},
    # Batch 5 (Sat)
    {"slug": "houston", "display": "Houston", "state": "TX", "st": "Texas", "zip": "77001", "lat": 29.7604, "lng": -95.3698},
    {"slug": "philadelphia", "display": "Philadelphia", "state": "PA", "st": "Pennsylvania", "zip": "19101", "lat": 39.9526, "lng": -75.1652},
    {"slug": "portland", "display": "Portland", "state": "OR", "st": "Oregon", "zip": "97201", "lat": 45.5152, "lng": -122.6784},
    {"slug": "nashville", "display": "Nashville", "state": "TN", "st": "Tennessee", "zip": "37201", "lat": 36.1627, "lng": -86.7816},
    {"slug": "durham", "display": "Durham", "state": "NC", "st": "North Carolina", "zip": "27701", "lat": 35.9940, "lng": -78.8986},
    {"slug": "salt-lake-city", "display": "Salt Lake City", "state": "UT", "st": "Utah", "zip": "84101", "lat": 40.7608, "lng": -111.8910},
    {"slug": "jacksonville", "display": "Jacksonville", "state": "FL", "st": "Florida", "zip": "32099", "lat": 30.3322, "lng": -81.6557},
    # Batch 6 (Sun)
    {"slug": "dallas", "display": "Dallas", "state": "TX", "st": "Texas", "zip": "75201", "lat": 32.7767, "lng": -96.7970},
    {"slug": "detroit", "display": "Detroit", "state": "MI", "st": "Michigan", "zip": "48201", "lat": 42.3314, "lng": -83.0458},
    {"slug": "minneapolis", "display": "Minneapolis", "state": "MN", "st": "Minnesota", "zip": "55401", "lat": 44.9778, "lng": -93.2650},
    {"slug": "sacramento", "display": "Sacramento", "state": "CA", "st": "California", "zip": "95814", "lat": 38.5816, "lng": -121.4944},
    {"slug": "pittsburgh", "display": "Pittsburgh", "state": "PA", "st": "Pennsylvania", "zip": "15201", "lat": 40.4406, "lng": -79.9959},
    {"slug": "cincinnati", "display": "Cincinnati", "state": "OH", "st": "Ohio", "zip": "45201", "lat": 39.1031, "lng": -84.5120},
    {"slug": "hartford", "display": "Hartford", "state": "CT", "st": "Connecticut", "zip": "06101", "lat": 41.7658, "lng": -72.6734},
]


# ---------------------------------------------------------------------------
# Content fingerprint — uses shared cross-source module
# ---------------------------------------------------------------------------

from event_dedup import content_fingerprint, get_all_fingerprints


def slugify(text: str) -> str:
    """Create URL-safe slug from text."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-')[:120]


# ---------------------------------------------------------------------------
# Scrape Sulekha city page
# ---------------------------------------------------------------------------

def scrape_city(city: dict, session: requests.Session) -> list:
    """Scrape events from a Sulekha city page using JSON-LD structured data."""
    url = f"https://events.sulekha.com/indian-events-in-{city['slug']}"
    events = []

    # Sulekha geo-locates by IP, ignoring URL. Force the city with a location cookie.
    loc_cookie = f"united states::US::{city['display']}::::{city['st']}::{city['zip']}::{city['lat']}::{city['lng']}::0"
    cookies = {"sulusrloc": loc_cookie}

    try:
        r = session.get(url, headers=HEADERS, cookies=cookies, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ HTTP {r.status_code} for {city['display']}")
            return events
    except Exception as e:
        print(f"  ⚠ Request failed for {city['display']}: {e}")
        return events

    # Extract JSON-LD from <script type="application/ld+json">
    ld_matches = re.findall(
        r'<script\s+type="application/ld\+json">\s*([\s\S]*?)\s*</script>',
        r.text, re.IGNORECASE
    )

    for ld_text in ld_matches:
        try:
            ld_data = json.loads(ld_text)
        except json.JSONDecodeError:
            continue

        # ld_data can be a single event or an array
        items = ld_data if isinstance(ld_data, list) else [ld_data]

        for item in items:
            if item.get("@type") != "Event":
                continue

            try:
                ev = parse_event(item, city)
                if ev:
                    events.append(ev)
            except Exception as e:
                print(f"  ⚠ Parse error: {e}")
                continue

    return events


def parse_event(item: dict, city: dict) -> dict | None:
    """Parse a JSON-LD Event item into our events table schema."""
    title = (item.get("name") or "").strip()
    if not title:
        return None

    # Dates
    start = item.get("startDate", "")
    end = item.get("endDate", "")
    date_str = start[:10] if start else None
    time_str = None
    if start and "T" in start:
        time_str = start.split("T")[1][:5]

    end_date = end[:10] if end else None
    end_time = None
    if end and "T" in end:
        end_time = end.split("T")[1][:5]

    if not date_str:
        return None

    # Location
    location = item.get("location", {})
    venue_name = location.get("name", "")
    address_obj = location.get("address", {})
    street = address_obj.get("streetAddress", "")
    locality = address_obj.get("addressLocality", "")
    region = address_obj.get("addressRegion", "")
    postal = address_obj.get("postalCode", "")
    address = ", ".join(filter(None, [street, locality, region, postal]))

    geo = location.get("geo", {})
    lat = geo.get("latitude")
    lon = geo.get("longitude")

    # Description — truncate to 200 chars
    desc = (item.get("description") or title)[:200]

    # Image
    images = item.get("image", [])
    image_url = images[0] if isinstance(images, list) and images else (images if isinstance(images, str) else None)

    # Price
    offers = item.get("offers", {})
    price_val = offers.get("price")
    price = f"${price_val}" if price_val else None

    # Ticket URL
    ticket_url = offers.get("url", "")

    # Source URL (event detail page)
    source_url = item.get("url", "")

    # Organizer
    organizer_obj = item.get("organizer", {})
    organizer = organizer_obj.get("name", "")

    # Category — default to Entertainment for Sulekha events
    category = "Entertainment"

    # Build slug — append time + short hash of source URL for uniqueness
    # (multi-day events at same venue can share title+city+date)
    slug_suffix = hashlib.md5((source_url or "").encode()).hexdigest()[:6]
    time_part = (time_str or "").replace(":", "")[:4]  # e.g. "1900"
    slug = slugify(f"{title}-{locality or city['display']}-{date_str}-{time_part}-{slug_suffix}")

    # Fingerprint
    fp = content_fingerprint(title, date_str, locality or city["display"])

    return {
        "title": title,
        "description": desc,
        "date": date_str,
        "time": time_str,
        "end_date": end_date,
        "city": locality or city["display"],
        "state": region or city["state"],
        "venue_name": venue_name,
        "latitude": lat,
        "longitude": lon,
        "category": category,
        "source": "sulekha",
        "source_id": source_url,
        "image_url": image_url,
        "ticket_url": ticket_url or source_url,
        "price_range": price,
        "organizer": organizer,
        "slug": slug,
        "content_fingerprint": fp,
    }


# ---------------------------------------------------------------------------
# Get existing events for dedup
# ---------------------------------------------------------------------------

def get_existing(source: str = "sulekha"):
    """Get existing source_urls and content_fingerprints for dedup."""
    existing_urls = set()

    if not SB_URL or not SB_KEY:
        return existing_urls, set()

    try:
        r = requests.get(
            f"{REST}/events?select=source_id&limit=10000",
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
            },
            timeout=15
        )
        if r.status_code == 200:
            for e in r.json():
                if e.get("source_id"):
                    existing_urls.add(e["source_id"])
    except Exception as e:
        print(f"⚠ Failed to fetch existing events: {e}")

    # Cross-source fingerprints via shared module (uses curl)
    existing_fingerprints = get_all_fingerprints()

    return existing_urls, existing_fingerprints


# ---------------------------------------------------------------------------
# Upsert events
# ---------------------------------------------------------------------------

def upsert_events(events: list) -> int:
    """Upsert events into Supabase."""
    if not events:
        return 0

    total = 0
    for ev in events:
        try:
            r = requests.post(
                f"{REST}/events",
                headers={
                    "apikey": SB_KEY,
                    "Authorization": f"Bearer {SB_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates",
                },
                json=ev,
                timeout=15
            )
            if r.status_code in (200, 201):
                total += 1
            else:
                # Try without slug conflict (upsert on source_url)
                try:
                    r2 = requests.post(
                        f"{REST}/events",
                        headers={
                            "apikey": SB_KEY,
                            "Authorization": f"Bearer {SB_KEY}",
                            "Content-Type": "application/json",
                        },
                        json=ev,
                        timeout=15
                    )
                    if r2.status_code in (200, 201):
                        total += 1
                    else:
                        print(f"    ⚠ Upsert failed for '{ev['title'][:40]}': {r2.text[:200]}")
                except:
                    pass
        except Exception as e:
            print(f"    ⚠ Upsert error: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape Sulekha events for Indian diaspora")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--city", type=str, default=None, help="Single city slug (e.g. 'houston')")
    parser.add_argument("--day", type=int, choices=range(7), default=None,
                        help="Day-of-week batch (0=Mon..6=Sun). Full cycle = 1 week.")
    args = parser.parse_args()

    if not args.dry_run and (not SB_URL or not SB_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    cities = CITIES
    if args.city:
        cities = [c for c in CITIES if c["slug"] == args.city]
        if not cities:
            print(f"Unknown city: {args.city}. Available: {', '.join(c['slug'] for c in CITIES)}")
            sys.exit(1)
    elif args.day is not None:
        cities = [c for i, c in enumerate(CITIES) if i % 7 == args.day]
        print(f"📅 Day {args.day} batch: {', '.join(c['display'] for c in cities)} ({len(cities)} cities)")

    # Get existing events for dedup
    existing_urls, existing_fingerprints = set(), set()
    if not args.dry_run:
        existing_urls, existing_fingerprints = get_existing()
        print(f"📊 Existing: {len(existing_urls)} URLs, {len(existing_fingerprints)} fingerprints")

    print(f"\n🔍 Scraping Sulekha ({len(cities)} cities)...\n")

    session = requests.Session()
    all_events = []
    skipped_url = 0
    skipped_fp = 0

    for city in cities:
        print(f"📍 {city['display']}, {city['state']}...")
        events = scrape_city(city, session)

        for ev in events:
            # Source-level skip
            if ev["source_id"] in existing_urls:
                skipped_url += 1
                continue
            # Cross-source fingerprint dedup
            if ev.get("content_fingerprint") and ev["content_fingerprint"] in existing_fingerprints:
                skipped_fp += 1
                continue

            all_events.append(ev)
            existing_urls.add(ev["source_id"])
            if ev.get("content_fingerprint"):
                existing_fingerprints.add(ev["content_fingerprint"])

        print(f"   Found {len(events)} events")
        time.sleep(1.5)  # Rate limit

    print(f"\n📊 Total new: {len(all_events)} | Skipped (URL): {skipped_url} | Skipped (fingerprint): {skipped_fp}")

    if args.dry_run:
        for ev in all_events:
            print(f"  🎪 {ev['title'][:60]} | {ev['date']} | {ev['city']}, {ev['state']} | {ev.get('price', 'Free')}")
        print(f"\n🏁 Dry run complete — {len(all_events)} events would be inserted")
    else:
        inserted = upsert_events(all_events)
        print(f"\n✅ Inserted {inserted}/{len(all_events)} events from Sulekha")


if __name__ == "__main__":
    main()
