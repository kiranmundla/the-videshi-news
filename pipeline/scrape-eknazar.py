#!/usr/bin/env python3
"""
scrape-eknazar.py — Scrape Indian community events from eknazar.com
and upsert them into the Supabase `events` table.

eknazar.com is a major Indian-diaspora community portal with events across
40+ US cities. Each city has a listing page at eknazar.com/{city}/Events/.
Events are HTML-rendered with title, date, venue, time, and image.

Usage:
    python3 pipeline/scrape-eknazar.py              # Today's rotation (~8 cities)
    python3 pipeline/scrape-eknazar.py --all         # All cities (full sweep)
    python3 pipeline/scrape-eknazar.py --city bayarea # Single city
    python3 pipeline/scrape-eknazar.py --dry-run     # Print events without inserting
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
from html import unescape

sys.stdout.reconfigure(line_buffering=True)

# ── Env ───────────────────────────────────────────────────────────────────

SB_URL = os.environ.get("SUPABASE_URL", "").strip('"')
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip('"')
REST = f"{SB_URL}/rest/v1"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.eknazar.com"


def curl_get(url: str, timeout: int = 20) -> str | None:
    """Fetch a URL via curl subprocess (avoids proxy issues with requests)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout),
             "-H", f"User-Agent: {UA}", url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception as e:
        print(f"  ⚠ curl failed for {url}: {e}")
    return None


def curl_post_json(url: str, data: list | dict, extra_headers: dict = None) -> tuple[int, str]:
    """POST JSON via curl. Returns (status_code, body)."""
    headers = [
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: resolution=merge-duplicates",
    ]
    if extra_headers:
        for k, v in extra_headers.items():
            headers.extend(["-H", f"{k}: {v}"])

    payload = json.dumps(data)
    try:
        result = subprocess.run(
            ["curl", "-s", "-w", "\n%{http_code}", "-X", "POST",
             *headers, "-d", payload, "--max-time", "30", url],
            capture_output=True, text=True, timeout=35
        )
        parts = result.stdout.rsplit('\n', 1)
        body = parts[0] if len(parts) > 1 else ""
        code = int(parts[-1]) if parts[-1].isdigit() else 0
        return code, body
    except Exception as e:
        print(f"  ⚠ curl POST failed: {e}")
        return 0, str(e)


def curl_get_json(url: str) -> list | None:
    """GET JSON from Supabase REST via curl."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15",
             "-H", f"apikey: {SB_KEY}",
             "-H", f"Authorization: Bearer {SB_KEY}",
             url],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except:
        pass
    return None

# ── City list ─────────────────────────────────────────────────────────────
# Slugs match eknazar URL paths. State mapping for DB storage.

CITIES = [
    # Batch 0 (Mon) — West Coast
    {"slug": "bayarea", "display": "Bay Area", "state": "CA"},
    {"slug": "losangeles", "display": "Los Angeles", "state": "CA"},
    {"slug": "sandiego", "display": "San Diego", "state": "CA"},
    {"slug": "seattle", "display": "Seattle", "state": "WA"},
    {"slug": "portland", "display": "Portland", "state": "OR"},
    {"slug": "sacramento", "display": "Sacramento", "state": "CA"},
    # Batch 1 (Tue) — Northeast
    {"slug": "newyork", "display": "New York", "state": "NY"},
    {"slug": "newjersey", "display": "New Jersey", "state": "NJ"},
    {"slug": "boston", "display": "Boston", "state": "MA"},
    {"slug": "philadelphia", "display": "Philadelphia", "state": "PA"},
    {"slug": "hartford", "display": "Hartford", "state": "CT"},
    {"slug": "newhampshire", "display": "New Hampshire", "state": "NH"},
    # Batch 2 (Wed) — South
    {"slug": "atlanta", "display": "Atlanta", "state": "GA"},
    {"slug": "dallas", "display": "Dallas", "state": "TX"},
    {"slug": "houston", "display": "Houston", "state": "TX"},
    {"slug": "austin", "display": "Austin", "state": "TX"},
    {"slug": "sanantonio", "display": "San Antonio", "state": "TX"},
    {"slug": "charlotte", "display": "Charlotte", "state": "NC"},
    # Batch 3 (Thu) — Southeast + DC
    {"slug": "washington", "display": "Washington", "state": "DC"},
    {"slug": "tampa", "display": "Tampa", "state": "FL"},
    {"slug": "orlando", "display": "Orlando", "state": "FL"},
    {"slug": "miami", "display": "Miami", "state": "FL"},
    {"slug": "nashville", "display": "Nashville", "state": "TN"},
    {"slug": "richmond", "display": "Richmond", "state": "VA"},
    {"slug": "raleigh", "display": "Raleigh", "state": "NC"},
    # Batch 4 (Fri) — Midwest
    {"slug": "chicago", "display": "Chicago", "state": "IL"},
    {"slug": "detroit", "display": "Detroit", "state": "MI"},
    {"slug": "columbus", "display": "Columbus", "state": "OH"},
    {"slug": "indianapolis", "display": "Indianapolis", "state": "IN"},
    {"slug": "minneapolis", "display": "Minneapolis", "state": "MN"},
    {"slug": "cleveland", "display": "Cleveland", "state": "OH"},
    # Batch 5 (Sat) — Mountain + more
    {"slug": "denver", "display": "Denver", "state": "CO"},
    {"slug": "phoenix", "display": "Phoenix", "state": "AZ"},
    {"slug": "lasvegas", "display": "Las Vegas", "state": "NV"},
    {"slug": "saltlakecity", "display": "Salt Lake City", "state": "UT"},
    {"slug": "kansascity", "display": "Kansas City", "state": "MO"},
    {"slug": "saintlouis", "display": "Saint Louis", "state": "MO"},
    # Batch 6 (Sun) — Remaining
    {"slug": "pittsburgh", "display": "Pittsburgh", "state": "PA"},
    {"slug": "cincinnati", "display": "Cincinnati", "state": "OH"},
    {"slug": "milwaukee", "display": "Milwaukee", "state": "WI"},
    {"slug": "memphis", "display": "Memphis", "state": "TN"},
    {"slug": "oklahomacity", "display": "Oklahoma City", "state": "OK"},
    {"slug": "omaha", "display": "Omaha", "state": "NE"},
    {"slug": "alabama", "display": "Alabama", "state": "AL"},
    {"slug": "arkansas", "display": "Arkansas", "state": "AR"},
    {"slug": "mississippi", "display": "Mississippi", "state": "MS"},
    {"slug": "tallahassee", "display": "Tallahassee", "state": "FL"},
    {"slug": "jacksonville", "display": "Jacksonville", "state": "FL"},
]

# ── Category rules ────────────────────────────────────────────────────────

CATEGORY_RULES = [
    ("Religious", ["temple", "gurdwara", "mosque", "puja", "pooja", "havan",
                   "kirtan", "bhajan", "aarti", "satsang", "prayer",
                   "yoga", "meditation", "sound bath", "sound healing",
                   "enlightenment", "bhagavad gita", "spiritual",
                   "swami", "guru", "ramadan", "diwali pooja"]),
    ("Music",    ["concert", "live music", "dj ", "musical", "singer",
                  "sangeet", "ghazal", "melody", "unplugged", "carnatic",
                  "hindustani", "tabla", "sitar", "veena", "flute"]),
    ("Dance",    ["garba", "dandiya", "bollywood night", "bollywood party",
                  "bhangra", "dance class", "dance workshop", "kathak",
                  "bharatanatyam", "kuchipudi", "raas"]),
    ("Food",     ["food festival", "cooking class", "biryani", "food fest",
                  "culinary", "chef", "potluck", "dinner", "brunch"]),
    ("Comedy",   ["comedy", "stand up", "standup", "laugh", "comic"]),
    ("Festival", ["diwali", "holi", "onam", "pongal", "ugadi", "baisakhi",
                  "navratri", "ganesh", "independence day", "republic day",
                  "eid", "lohri", "makar sankranti"]),
    ("Networking", ["networking", "meetup", "mixer", "speed dating",
                    "singles", "matchmaking", "matrimonial"]),
    ("Education",  ["workshop", "seminar", "webinar", "training",
                    "bootcamp", "certification", "tutorial", "class",
                    "course", "learning"]),
    ("Sports",     ["cricket", "badminton", "kabaddi", "marathon",
                    "run ", "5k", "10k", "tournament", "sports"]),
    ("Film",       ["movie", "film", "screening", "cinema", "bollywood film"]),
    ("Business",   ["startup", "entrepreneurship", "business", "venture",
                    "investment", "tech talk", "hackathon"]),
    ("Kids",       ["kids", "children", "family", "youth"]),
]


def categorize(title: str) -> str:
    """Assign a category based on title keywords."""
    lower = title.lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return cat
    return "Community"


# ── HTML parsing helpers ──────────────────────────────────────────────────

def clean(text: str) -> str:
    """Clean HTML entities and extra whitespace."""
    text = unescape(text or "")
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_date(date_str: str) -> str | None:
    """Parse 'DD Mon YYYY' into YYYY-MM-DD."""
    date_str = date_str.strip()
    for fmt in ("%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_location(loc_str: str) -> tuple[str, str, str]:
    """
    Parse 'Location: Venue Name, City,STATE' into (venue, city, state).
    Returns best-effort tuple.
    """
    loc = clean(loc_str)
    loc = re.sub(r'^Location:\s*', '', loc, flags=re.IGNORECASE)

    if loc.upper().startswith("ONLINE"):
        return ("Online", "", "")

    # Try to extract state code from end (2 uppercase letters)
    m = re.search(r',\s*([A-Z]{2})\s*$', loc)
    state = m.group(1) if m else ""
    if state:
        loc = loc[:m.start()].strip()

    # Split remaining on last comma for city
    parts = loc.rsplit(',', 1)
    if len(parts) == 2:
        venue = parts[0].strip()
        city = parts[1].strip()
    else:
        venue = loc
        city = ""

    return (venue, city, state)


def make_slug(title: str, event_id: str) -> str:
    """Create a URL slug from title + event ID."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:70]
    return f"{slug}-{event_id}"


# ── Scraping ──────────────────────────────────────────────────────────────

def scrape_city(city: dict) -> list[dict]:
    """Scrape all events from an eknazar city listing page."""
    url = f"{BASE}/{city['slug']}/Events/"
    print(f"\n🔍 {city['display']} ({url})")

    html = curl_get(url)
    if not html:
        print(f"  ⚠ Failed to fetch {url}")
        return []
    events = []

    # Parse events from the evenLists divs
    # Pattern: <dl id='EVENT_ID'> ... date ... title ... location ... time ... image
    pattern = re.compile(
        r"<dl\s+id='(\d+)'[^>]*>"  # event ID
        r".*?"
        r"<dt><center><span>(.*?)</span>"  # start date
        r"(?:.*?<span>(.*?)</span>)?"  # optional end date (multi-day)
        r".*?</dt>"
        r".*?"
        r"<img\s+src='([^']+)'"  # image URL
        r".*?"
        r"<h6><a\s+href=[\"']([^\"']+)[\"']>(.*?)</a></h6>"  # link + title
        r"(.*?)"  # rest of the li (location + time)
        r"</li>",
        re.DOTALL
    )

    for m in pattern.finditer(html):
        event_id = m.group(1)
        raw_date = clean(m.group(2))
        raw_end_date = clean(m.group(3)) if m.group(3) else None
        image_url = m.group(4)
        event_href = m.group(5)
        title = clean(m.group(6))
        rest = m.group(7)

        if not title or not raw_date:
            continue

        date = parse_date(raw_date)
        if not date:
            continue

        end_date = parse_date(raw_end_date) if raw_end_date else None

        # Skip past events
        try:
            if datetime.strptime(date, "%Y-%m-%d").date() < datetime.now().date():
                continue
        except:
            pass

        # Parse location
        loc_match = re.search(r'<span>(Location:.*?)</span>', rest, re.DOTALL)
        venue_name, city_name, state = "", "", city["state"]
        if loc_match:
            venue_name, city_name, state_parsed = parse_location(loc_match.group(1))
            if state_parsed:
                state = state_parsed

        # If city empty, use the eknazar city display name
        if not city_name:
            city_name = city["display"]

        # Parse time
        time_match = re.search(r"eventTime[^>]*><strong>(.*?)</strong>", rest)
        event_time = clean(time_match.group(1)) if time_match else ""

        # Build detail page URL
        if event_href.startswith("http"):
            detail_url = event_href
        elif event_href.startswith("/"):
            detail_url = BASE + event_href
        else:
            detail_url = f"{BASE}/{city['slug']}/Events/{event_href}"

        # Registration URL
        ticket_url = f"{BASE}/Events/register.php?cid={event_id}"

        # Full-size image (replace thumbnail width with larger)
        if image_url and not image_url.startswith("http"):
            image_url = BASE + image_url

        # Build slug
        slug = make_slug(title, event_id)

        event = {
            "title": title,
            "date": date,
            "end_date": end_date,
            "time": event_time,
            "venue_name": venue_name,
            "city": city_name,
            "state": state,
            "category": categorize(title),
            "description": "",  # filled from detail page if fetched
            "image_url": image_url,
            "ticket_url": detail_url,  # detail page is more useful than register.php
            "source": "eknazar",
            "source_id": f"eknazar_{event_id}",
            "slug": slug,
            "_detail_url": detail_url,
            "_event_id": event_id,
        }
        events.append(event)

    # Deduplicate within city (same event_id can appear in featured + other sections)
    seen_ids = set()
    unique = []
    for e in events:
        if e["_event_id"] not in seen_ids:
            seen_ids.add(e["_event_id"])
            unique.append(e)

    print(f"  📋 Found {len(unique)} upcoming events")
    return unique


def fetch_detail(event: dict) -> None:
    """Fetch event detail page to enrich description and organizer."""
    url = event.get("_detail_url", "")
    if not url:
        return

    html = curl_get(url, timeout=15)
    if not html:
        return

    # Extract description from Event Details section
    desc_match = re.search(
        r'<B>Event Details</B>\s*(?:<br/?>\s*)*(.+?)(?=</TD>)',
        html, re.DOTALL
    )
    if desc_match:
        desc = clean(desc_match.group(1))
        if len(desc) > 10:
            event["description"] = desc[:2000]

    # Extract organizer
    org_match = re.search(
        r'<B>Organized by</B>.*?<TD[^>]*>(.*?)</TD>',
        html, re.DOTALL
    )
    if org_match:
        organizer = clean(org_match.group(1))
        if organizer:
            event["organizer"] = organizer

    # Extract full address from Venue section
    venue_match = re.search(
        r'<B>Venue</B>.*?<TD[^>]*>(.*?)(?:<br/>\s*<a href="https://maps\.google|<p>|<script)',
        html, re.DOTALL
    )
    if venue_match:
        addr_parts = re.split(r'<br/?>', venue_match.group(1))
        addr_parts = [clean(p) for p in addr_parts if clean(p)]
        if len(addr_parts) >= 2:
            # First part is venue name, rest is address
            full_addr = ', '.join(addr_parts[1:])
            event["street_address"] = full_addr[:255]

    # Try to get full-size image
    img_match = re.search(r"<img\s+src='(https://www\.eknazar\.com/Events/uploaded/[^']+)'\s+width='600'", html)
    if img_match:
        event["image_url"] = img_match.group(1)


# ── Dedup + upsert ────────────────────────────────────────────────────────

def add_fingerprints(events: list) -> None:
    """Add cross-source content fingerprints."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from event_dedup import content_fingerprint
        for e in events:
            e["content_fingerprint"] = content_fingerprint(
                e["title"], e["date"], e["city"]
            )
    except ImportError:
        print("  ⚠ event_dedup not found, skipping fingerprints")
        for e in events:
            raw = f"{e['title'][:60].lower()}|{e['date']}|{e['city'].lower()}"
            e["content_fingerprint"] = hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_existing() -> tuple[set, set]:
    """Fetch existing eknazar source IDs and all fingerprints."""
    existing_ids = set()
    existing_fps = set()

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from event_dedup import get_all_fingerprints
        existing_fps = get_all_fingerprints()
    except:
        pass

    # Fetch existing eknazar source_ids
    data = curl_get_json(f"{REST}/events?source=eq.eknazar&select=source_id&limit=5000")
    if data and isinstance(data, list):
        for e in data:
            existing_ids.add(e.get("source_id", ""))

    return existing_ids, existing_fps


def upsert_events(events: list) -> int:
    """Upsert events to Supabase."""
    if not events:
        return 0

    seen_slugs = set()
    for e in events:
        # Remove internal fields
        e.pop("_detail_url", None)
        e.pop("_event_id", None)

        slug = e["slug"]
        while slug in seen_slugs:
            slug = slug[:75] + "-" + format(int(time.time() * 1000) % 10000, 'x')
        seen_slugs.add(slug)
        e["slug"] = slug
        e["updated_at"] = datetime.now(timezone.utc).isoformat()

    batch_size = 50
    total = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        code, body = curl_post_json(f"{REST}/events?on_conflict=source,source_id", batch)
        if code in (200, 201):
            total += len(batch)
        else:
            print(f"  ⚠ Upsert failed ({code}): {body[:300]}")
            for ev in batch:
                c2, b2 = curl_post_json(f"{REST}/events?on_conflict=source,source_id", [ev])
                if c2 in (200, 201):
                    total += 1
                else:
                    print(f"    ⚠ Failed for '{ev['title'][:40]}': {b2[:200]}")

    return total


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape eknazar.com for Indian community events")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--city", type=str, default=None, help="Single city slug (e.g. 'bayarea')")
    parser.add_argument("--all", action="store_true", help="Scrape all cities")
    parser.add_argument("--day", type=int, choices=range(7), default=None,
                        help="Day-of-week rotation (0-6). Splits cities into 7 daily slices.")
    parser.add_argument("--no-details", action="store_true",
                        help="Skip detail page fetches (faster, less data)")
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
    elif args.all:
        cities = CITIES
    elif args.day is not None:
        cities = [c for i, c in enumerate(CITIES) if i % 7 == args.day]
        print(f"📅 Day {args.day} batch: {', '.join(c['display'] for c in cities)} ({len(cities)} cities)")
    else:
        rotation_day = datetime.now().weekday()
        cities = [c for i, c in enumerate(CITIES) if i % 7 == rotation_day]
        print(f"📅 Auto day {rotation_day}: {', '.join(c['display'] for c in cities)} ({len(cities)} cities)")

    # Fetch existing data for dedup
    existing_ids, existing_fps = set(), set()
    if not args.dry_run:
        existing_ids, existing_fps = get_existing()
        print(f"📊 Existing: {len(existing_ids)} eknazar IDs, {len(existing_fps)} fingerprints")

    all_events = []
    inserted_ids = set()  # Track source_ids inserted this run

    print(f"\n🔍 Scraping eknazar.com ({len(cities)} cities)...\n")

    for city in cities:
        events = scrape_city(city)

        if not events:
            continue

        # Add fingerprints
        add_fingerprints(events)

        # Filter out already-existing events (DB + this run)
        new_events = []
        for e in events:
            sid = e["source_id"]
            if sid in existing_ids or sid in inserted_ids:
                continue
            if e.get("content_fingerprint") in existing_fps:
                continue
            inserted_ids.add(sid)
            new_events.append(e)

        if not new_events:
            print(f"  ⏭ All {len(events)} events already exist")
            continue

        # Fetch detail pages for new events (rate-limited)
        if not args.no_details:
            for i, e in enumerate(new_events):
                fetch_detail(e)
                if i < len(new_events) - 1:
                    time.sleep(0.5)  # Be nice to eknazar

        print(f"  ✅ {len(new_events)} new events (filtered from {len(events)})")
        all_events.extend(new_events)

        time.sleep(1.0)  # Rate limit between cities

    print(f"\n{'='*60}")
    print(f"Total new events: {len(all_events)}")

    if args.dry_run:
        for e in all_events[:20]:
            print(f"  📅 {e['date']} | {e['title'][:50]} | {e['city']}, {e['state']}")
            if e.get("description"):
                print(f"     📝 {e['description'][:80]}...")
            print(f"     🔗 {e['ticket_url']}")
        if len(all_events) > 20:
            print(f"  ... and {len(all_events) - 20} more")
        return

    if all_events:
        count = upsert_events(all_events)
        print(f"\n✅ Inserted {count}/{len(all_events)} events from eknazar")
    else:
        print("\nNo new events to insert.")


if __name__ == "__main__":
    main()
