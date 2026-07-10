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
CITIES = [
    # Batch 0 (Mon)
    {"slug": "san-francisco", "display": "San Francisco", "state": "CA"},
    {"slug": "los-angeles", "display": "Los Angeles", "state": "CA"},
    {"slug": "austin", "display": "Austin", "state": "TX"},
    {"slug": "tampa", "display": "Tampa", "state": "FL"},
    {"slug": "irvine", "display": "Irvine", "state": "CA"},
    {"slug": "orlando", "display": "Orlando", "state": "FL"},
    {"slug": "cleveland", "display": "Cleveland", "state": "OH"},
    {"slug": "milwaukee", "display": "Milwaukee", "state": "WI"},
    # Batch 1 (Tue)
    {"slug": "san-jose", "display": "San Jose", "state": "CA"},
    {"slug": "seattle", "display": "Seattle", "state": "WA"},
    {"slug": "miami", "display": "Miami", "state": "FL"},
    {"slug": "charlotte", "display": "Charlotte", "state": "NC"},
    {"slug": "plano", "display": "Plano", "state": "TX"},
    {"slug": "baltimore", "display": "Baltimore", "state": "MD"},
    {"slug": "kansas-city", "display": "Kansas City", "state": "MO"},
    # Batch 2 (Wed)
    {"slug": "new-york", "display": "New York", "state": "NY"},
    {"slug": "washington-dc", "display": "Washington", "state": "DC"},
    {"slug": "phoenix", "display": "Phoenix", "state": "AZ"},
    {"slug": "raleigh", "display": "Raleigh", "state": "NC"},
    {"slug": "fremont", "display": "Fremont", "state": "CA"},
    {"slug": "stamford", "display": "Stamford", "state": "CT"},
    {"slug": "st-louis", "display": "St Louis", "state": "MO"},
    # Batch 3 (Thu)
    {"slug": "edison-nj", "display": "Edison", "state": "NJ"},
    {"slug": "boston", "display": "Boston", "state": "MA"},
    {"slug": "denver", "display": "Denver", "state": "CO"},
    {"slug": "columbus", "display": "Columbus", "state": "OH"},
    {"slug": "sunnyvale", "display": "Sunnyvale", "state": "CA"},
    {"slug": "ann-arbor", "display": "Ann Arbor", "state": "MI"},
    {"slug": "las-vegas", "display": "Las Vegas", "state": "NV"},
    # Batch 4 (Fri)
    {"slug": "chicago", "display": "Chicago", "state": "IL"},
    {"slug": "atlanta", "display": "Atlanta", "state": "GA"},
    {"slug": "san-diego", "display": "San Diego", "state": "CA"},
    {"slug": "indianapolis", "display": "Indianapolis", "state": "IN"},
    {"slug": "cary", "display": "Cary", "state": "NC"},
    {"slug": "san-antonio", "display": "San Antonio", "state": "TX"},
    {"slug": "richmond", "display": "Richmond", "state": "VA"},
    # Batch 5 (Sat)
    {"slug": "houston", "display": "Houston", "state": "TX"},
    {"slug": "philadelphia", "display": "Philadelphia", "state": "PA"},
    {"slug": "portland", "display": "Portland", "state": "OR"},
    {"slug": "nashville", "display": "Nashville", "state": "TN"},
    {"slug": "durham", "display": "Durham", "state": "NC"},
    {"slug": "salt-lake-city", "display": "Salt Lake City", "state": "UT"},
    {"slug": "jacksonville", "display": "Jacksonville", "state": "FL"},
    # Batch 6 (Sun)
    {"slug": "dallas", "display": "Dallas", "state": "TX"},
    {"slug": "detroit", "display": "Detroit", "state": "MI"},
    {"slug": "minneapolis", "display": "Minneapolis", "state": "MN"},
    {"slug": "sacramento", "display": "Sacramento", "state": "CA"},
    {"slug": "pittsburgh", "display": "Pittsburgh", "state": "PA"},
    {"slug": "cincinnati", "display": "Cincinnati", "state": "OH"},
    {"slug": "hartford", "display": "Hartford", "state": "CT"},
]


# ---------------------------------------------------------------------------
# Content fingerprint for cross-source dedup
# ---------------------------------------------------------------------------

def content_fingerprint(date_str: str, time_str: str = "", lat=None, lon=None, venue: str = "") -> str:
    """Generate a fingerprint from date+time+location for cross-source dedup."""
    lat_r = round(float(lat), 3) if lat else 0
    lon_r = round(float(lon), 3) if lon else 0
    norm_venue = re.sub(r'[^a-z0-9]', '', (venue or '').lower())
    time_norm = (time_str or '00:00')[:5]
    raw = f"{date_str}|{time_norm}|{lat_r}|{lon_r}|{norm_venue}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


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

    try:
        r = session.get(url, headers=HEADERS, timeout=15)
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

    # Build slug
    slug = slugify(f"{title}-{locality or city['display']}-{date_str}")

    # Fingerprint
    fp = content_fingerprint(date_str, time_str or "", lat, lon, venue_name)

    return {
        "title": title,
        "description": desc,
        "date": date_str,
        "time": time_str,
        "end_date": end_date,
        "end_time": end_time,
        "city": locality or city["display"],
        "state": region or city["state"],
        "venue": venue_name,
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "category": category,
        "source": "sulekha",
        "source_url": source_url,
        "image_url": image_url,
        "ticket_url": ticket_url,
        "price": price,
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
    existing_fingerprints = set()

    if not SB_URL or not SB_KEY:
        return existing_urls, existing_fingerprints

    try:
        r = requests.get(
            f"{REST}/events?select=source_url,content_fingerprint&limit=10000",
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
            },
            timeout=15
        )
        if r.status_code == 200:
            for e in r.json():
                if e.get("source_url"):
                    existing_urls.add(e["source_url"])
                if e.get("content_fingerprint"):
                    existing_fingerprints.add(e["content_fingerprint"])
    except Exception as e:
        print(f"⚠ Failed to fetch existing events: {e}")

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
            if ev["source_url"] in existing_urls:
                skipped_url += 1
                continue
            # Cross-source fingerprint dedup
            if ev.get("content_fingerprint") and ev["content_fingerprint"] in existing_fingerprints:
                skipped_fp += 1
                continue

            all_events.append(ev)
            existing_urls.add(ev["source_url"])
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
