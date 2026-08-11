#!/usr/bin/env python3
"""
scrape-sulekha.py — Scrape Indian events from Sulekha Events
and upsert them into the Supabase `events` table.

Two-phase approach:
  1. City listing pages: discover events via JSON-LD structured data
  2. Detail pages: visit each new event's page to extract the full
     description, street address, zip code, and richer metadata

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
    {"slug": "santa-clara", "display": "Santa Clara", "state": "CA", "st": "California", "zip": "95050", "lat": 37.3541, "lng": -121.9552},
    {"slug": "milpitas", "display": "Milpitas", "state": "CA", "st": "California", "zip": "95035", "lat": 37.4323, "lng": -121.8996},
    {"slug": "cupertino", "display": "Cupertino", "state": "CA", "st": "California", "zip": "95014", "lat": 37.3230, "lng": -122.0322},
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
    {"slug": "fairfax", "display": "Fairfax", "state": "VA", "st": "Virginia", "zip": "22030", "lat": 38.8462, "lng": -77.3064},
    {"slug": "herndon", "display": "Herndon", "state": "VA", "st": "Virginia", "zip": "20170", "lat": 38.9696, "lng": -77.3861},
    {"slug": "ashburn", "display": "Ashburn", "state": "VA", "st": "Virginia", "zip": "20147", "lat": 39.0438, "lng": -77.4874},
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
    {"slug": "plainsboro", "display": "Plainsboro", "state": "NJ", "st": "New Jersey", "zip": "08536", "lat": 40.3487, "lng": -74.5946},
    {"slug": "iselin", "display": "Iselin", "state": "NJ", "st": "New Jersey", "zip": "08830", "lat": 40.5751, "lng": -74.3223},
    {"slug": "piscataway", "display": "Piscataway", "state": "NJ", "st": "New Jersey", "zip": "08854", "lat": 40.5526, "lng": -74.4610},
]

# ---------------------------------------------------------------------------
# Shared imports
# ---------------------------------------------------------------------------

from event_dedup import content_fingerprint, get_all_fingerprints


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-')[:120]


# ---------------------------------------------------------------------------
# Category detection from event content
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Dance": [
        "garba", "dandiya", "raas", "navratri", "kathak",
        "bharatanatyam", "bhangra", "dance competition", "dance night",
    ],
    "Music": [
        "concert", "live music", "singer", "singing", "qawwali",
        "ghazal", "carnatic", "hindustani", "bhajan", "sufi night",
        "musical", "unplugged",
    ],
    "Comedy": [
        "comedy", "standup", "stand-up", "comedian", "laughs",
        "comedy show", "comic",
    ],
    "Religious": [
        "temple", "puja", "pooja", "prayer", "kirtan", "satsang",
        "mandir", "gurudwara", "mosque", "aarti", "ganesh",
        "durga", "ram navami", "janmashtami",
    ],
    "Spiritual": [
        "meditation", "mindfulness", "inner peace", "spiritual",
        "vipassana", "dhamma", "yoga retreat",
    ],
    "Festival": [
        "diwali", "holi", "eid", "onam", "pongal", "baisakhi",
        "ugadi", "lohri", "mela", "festival", "makar sankranti",
    ],
    "Food": [
        "food festival", "cooking", "chef", "dinner gala",
        "brunch", "tasting", "culinary",
    ],
    "Cultural": [
        "cultural", "heritage", "exhibition", "art show",
        "film screening", "movie", "play", "drama", "theater",
        "theatre", "literary",
    ],
    "Sports": [
        "cricket", "kabaddi", "badminton", "tournament",
        "marathon", "run ", "yoga", "sports",
    ],
    "Education": [
        "workshop", "seminar", "webinar", "training",
        "hackathon", "conference", "summit", "symposium",
    ],
    "Community": [
        "meetup", "networking", "fundraiser", "volunteer",
        "charity", "gala", "reunion", "mixer",
    ],
    "Shopping": [
        "trunk show", "exhibition sale", "jewelry",
        "fashion show", "bazaar", "sale event",
    ],
}


def detect_category(title: str, description: str) -> str:
    """Detect event category from title and description keywords.
    Title matches take priority over description matches."""
    title_lower = title.lower()
    text = f"{title} {description}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                return category

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category

    return "Entertainment"


# ---------------------------------------------------------------------------
# Phase 1: Scrape city listing page for event URLs + basic data
# ---------------------------------------------------------------------------

def scrape_city(city: dict, session: requests.Session) -> list:
    url = f"https://events.sulekha.com/indian-events-in-{city['slug']}"
    events = []

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

    ld_matches = re.findall(
        r'<script\s+type="application/ld\+json">\s*([\s\S]*?)\s*</script>',
        r.text, re.IGNORECASE
    )

    for ld_text in ld_matches:
        try:
            ld_data = json.loads(ld_text)
        except json.JSONDecodeError:
            continue

        items = ld_data if isinstance(ld_data, list) else [ld_data]

        for item in items:
            if item.get("@type") != "Event":
                continue
            try:
                ev = parse_listing_event(item, city)
                if ev:
                    events.append(ev)
            except Exception as e:
                print(f"  ⚠ Parse error: {e}")

    return events


def parse_listing_event(item: dict, city: dict) -> dict | None:
    title = (item.get("name") or "").strip()
    if not title:
        return None

    start = item.get("startDate", "")
    end = item.get("endDate", "")
    date_str = start[:10] if start else None
    time_str = None
    if start and "T" in start:
        time_str = start.split("T")[1][:5]
    end_date = end[:10] if end else None
    if not date_str:
        return None

    location = item.get("location", {})
    venue_name = location.get("name", "")
    address_obj = location.get("address", {})
    street = address_obj.get("streetAddress", "").strip()
    locality = address_obj.get("addressLocality", "").strip()
    region = address_obj.get("addressRegion", "").strip()
    postal = address_obj.get("postalCode", "").strip()

    geo = location.get("geo", {})
    lat = geo.get("latitude")
    lon = geo.get("longitude")

    listing_desc = (item.get("description") or "").strip()

    images = item.get("image", [])
    image_url = images[0] if isinstance(images, list) and images else (images if isinstance(images, str) else None)

    offers = item.get("offers", {})
    price_val = offers.get("price")
    price = f"${price_val}" if price_val else None

    ticket_url = offers.get("url", "")
    source_url = item.get("url", "")

    organizer_obj = item.get("organizer", {})
    organizer = organizer_obj.get("name", "").strip()

    category = detect_category(title, listing_desc)

    slug_suffix = hashlib.md5((source_url or "").encode()).hexdigest()[:6]
    time_part = (time_str or "").replace(":", "")[:4]
    slug = slugify(f"{title}-{locality or city['display']}-{date_str}-{time_part}-{slug_suffix}")

    fp = content_fingerprint(title, date_str, locality or city["display"])

    return {
        "title": title,
        "description": listing_desc or title,
        "date": date_str,
        "time": time_str,
        "end_date": end_date,
        "city": locality or city["display"],
        "state": region or city["state"],
        "venue_name": venue_name,
        "street_address": street or None,
        "zip_code": postal or None,
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
        "_detail_url": source_url,
    }


# ---------------------------------------------------------------------------
# Phase 2: Enrich each event by visiting its detail page
# ---------------------------------------------------------------------------

def enrich_from_detail(event: dict, session: requests.Session) -> dict:
    url = event.get("_detail_url", "")
    if not url:
        return event

    try:
        r = session.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"    ⚠ Detail page HTTP {r.status_code}")
            return event
    except Exception as e:
        print(f"    ⚠ Detail page failed: {e}")
        return event

    html = r.text

    # Full event description
    long_desc = extract_event_description(html)
    if long_desc:
        event["long_description"] = long_desc
        # Use first meaningful paragraph as short description
        first_para = long_desc.split("\n")[0].strip()
        if len(first_para) > 20:
            event["description"] = first_para[:500]

    # Street address and zip from detail page structured data
    street_match = re.search(r'"streetAddress"\s*:\s*"([^"]+)"', html)
    postal_match = re.search(r'"postalCode"\s*:\s*"([^"]+)"', html)
    if street_match:
        event["street_address"] = street_match.group(1).strip()
    if postal_match:
        event["zip_code"] = postal_match.group(1).strip()

    # Re-detect category with full description for better accuracy
    if long_desc:
        event["category"] = detect_category(event["title"], long_desc)

    # og:image as fallback if listing didn't have one
    if not event.get("image_url"):
        og_img = re.search(r"og:image['\"]?\s+content=['\"]([^'\"]+)", html)
        if og_img:
            event["image_url"] = og_img.group(1).strip()

    return event


def extract_event_description(html: str) -> str | None:
    """Extract full event description from Sulekha detail page.
    Content lives between 'Event Description' heading and T&C / boilerplate."""
    idx_start = html.find("Event Description")
    if idx_start < 0:
        og = re.search(r"og:description['\"]?\s+content=['\"]([^'\"]+)", html)
        return og.group(1).strip() if og else None

    chunk = html[idx_start:]

    end_markers = [
        "Terms &amp; Conditions",
        "Terms & Conditions",
        "Why buy with Sulekha",
    ]
    end_idx = len(chunk)
    for marker in end_markers:
        pos = chunk.find(marker)
        if 0 < pos < end_idx:
            end_idx = pos

    desc_html = chunk[:end_idx]

    text = re.sub(r'<br\s*/?>', '\n', desc_html)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n\s*\n+', '\n', text).strip()

    if text.startswith("Event Description"):
        text = text[len("Event Description"):].strip()

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    if len(text) < 50:
        return None

    return text[:5000]


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------

def get_existing():
    existing_urls = set()
    if not SB_URL or not SB_KEY:
        return existing_urls, set()

    try:
        r = requests.get(
            f"{REST}/events?select=source_id&limit=10000",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        if r.status_code == 200:
            for e in r.json():
                if e.get("source_id"):
                    existing_urls.add(e["source_id"])
    except Exception as e:
        print(f"⚠ Failed to fetch existing events: {e}")

    existing_fingerprints = get_all_fingerprints()
    return existing_urls, existing_fingerprints


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_events(events: list) -> int:
    if not events:
        return 0

    total = 0
    for ev in events:
        ev_clean = {k: v for k, v in ev.items() if not k.startswith("_")}
        try:
            r = requests.post(
                f"{REST}/events",
                headers={
                    "apikey": SB_KEY,
                    "Authorization": f"Bearer {SB_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates",
                },
                json=ev_clean,
                timeout=15
            )
            if r.status_code in (200, 201):
                total += 1
            else:
                try:
                    r2 = requests.post(
                        f"{REST}/events",
                        headers={
                            "apikey": SB_KEY,
                            "Authorization": f"Bearer {SB_KEY}",
                            "Content-Type": "application/json",
                        },
                        json=ev_clean,
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
    parser = argparse.ArgumentParser(description="Scrape Sulekha events")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--city", type=str, default=None)
    parser.add_argument("--day", type=int, choices=range(7), default=None)
    parser.add_argument("--skip-detail", action="store_true",
                        help="Skip detail page enrichment (faster, less data)")
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

    existing_urls, existing_fingerprints = set(), set()
    if not args.dry_run:
        existing_urls, existing_fingerprints = get_existing()
        print(f"📊 Existing: {len(existing_urls)} URLs, {len(existing_fingerprints)} fingerprints")

    print(f"\n🔍 Scraping Sulekha ({len(cities)} cities)...\n")

    session = requests.Session()
    all_events = []
    skipped_url = 0
    skipped_fp = 0

    # Phase 1: Discover events from listing pages
    for city in cities:
        print(f"📍 {city['display']}, {city['state']}...")
        events = scrape_city(city, session)

        for ev in events:
            if ev["source_id"] in existing_urls:
                skipped_url += 1
                continue
            if ev.get("content_fingerprint") and ev["content_fingerprint"] in existing_fingerprints:
                skipped_fp += 1
                continue

            all_events.append(ev)
            existing_urls.add(ev["source_id"])
            if ev.get("content_fingerprint"):
                existing_fingerprints.add(ev["content_fingerprint"])

        print(f"   Found {len(events)} events")
        time.sleep(1.5)

    print(f"\n📊 Total new: {len(all_events)} | Skipped (URL): {skipped_url} | Skipped (fingerprint): {skipped_fp}")

    # Phase 2: Enrich from detail pages
    if all_events and not args.skip_detail:
        print(f"\n📄 Enriching {len(all_events)} events from detail pages...\n")
        enriched = 0
        for i, ev in enumerate(all_events):
            print(f"  [{i+1}/{len(all_events)}] {ev['title'][:50]}...")
            enrich_from_detail(ev, session)
            if ev.get("long_description"):
                enriched += 1
            time.sleep(1.0)
        print(f"\n📊 Enriched {enriched}/{len(all_events)} with full descriptions")

    if args.dry_run:
        for ev in all_events:
            desc_len = len(ev.get("long_description") or "")
            addr = ev.get("street_address") or "no address"
            zc = ev.get("zip_code") or "no zip"
            print(f"  🎪 {ev['title'][:55]} | {ev['date']} | {ev['city']}, {ev['state']}")
            print(f"     Cat: {ev['category']} | Addr: {addr} | Zip: {zc} | Desc: {desc_len} chars")
        print(f"\n🏁 Dry run complete — {len(all_events)} events would be inserted")
    else:
        inserted = upsert_events(all_events)
        print(f"\n✅ Inserted {inserted}/{len(all_events)} events from Sulekha")


if __name__ == "__main__":
    main()
