#!/usr/bin/env python3
"""
scrape-meetup.py — Scrape Indian/desi community events from Meetup.com
and upsert them into the Supabase `events` table.

Approach: Meetup uses Next.js with Apollo cache. We fetch search pages and
extract event data from the __NEXT_DATA__ / __APOLLO_STATE__ JSON embedded
in the HTML. No API key needed.

Usage:
    python3 pipeline/scrape-meetup.py              # Full scrape
    python3 pipeline/scrape-meetup.py --dry-run     # Print events without inserting
    python3 pipeline/scrape-meetup.py --city bay-area  # Single city
"""

import json
import os
import re
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

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
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
REST = f"{SB_URL}/rest/v1"
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=representation",
}

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# Search keywords (Indian/South Asian culture)
KEYWORDS = [
    "indian", "desi", "bollywood", "hindi", "tamil", "telugu",
    "bengali", "gujarati", "punjabi", "south asian", "bhangra",
    "garba", "cricket desi", "sikh", "malayalam", "kannada", "marathi",
]

# Cities with their Meetup location param format: us--{state_lower}--{City+Name}
CITIES = [
    {"location": "us--ca--San+Francisco",  "display": "San Francisco", "state": "CA", "slug": "bay-area"},
    {"location": "us--ca--San+Jose",        "display": "San Jose",      "state": "CA", "slug": "san-jose"},
    {"location": "us--ny--New+York",        "display": "New York",      "state": "NY", "slug": "new-york"},
    {"location": "us--nj--Edison",           "display": "Edison",        "state": "NJ", "slug": "edison-nj"},
    {"location": "us--il--Chicago",          "display": "Chicago",       "state": "IL", "slug": "chicago"},
    {"location": "us--tx--Houston",          "display": "Houston",       "state": "TX", "slug": "houston"},
    {"location": "us--tx--Dallas",           "display": "Dallas",        "state": "TX", "slug": "dallas"},
    {"location": "us--ca--Los+Angeles",      "display": "Los Angeles",   "state": "CA", "slug": "los-angeles"},
    {"location": "us--wa--Seattle",          "display": "Seattle",       "state": "WA", "slug": "seattle"},
    {"location": "us--dc--Washington",       "display": "Washington",    "state": "DC", "slug": "washington-dc"},
    {"location": "us--ma--Boston",           "display": "Boston",        "state": "MA", "slug": "boston"},
    {"location": "us--ga--Atlanta",          "display": "Atlanta",       "state": "GA", "slug": "atlanta"},
    {"location": "us--pa--Philadelphia",     "display": "Philadelphia",  "state": "PA", "slug": "philadelphia"},
    {"location": "us--mi--Detroit",          "display": "Detroit",       "state": "MI", "slug": "detroit"},
]

# Category rules (same as events-ingest.py)
CATEGORY_RULES = [
    ("Competition", ["spelling bee", "math olympiad", "science olympiad", "chess tournament",
                     "robotics competition", "coding competition", "debate tournament",
                     "hackathon", "competition", "contest", "tournament"]),
    ("Education",   ["school", "class", "course", "workshop", "training", "lecture",
                     "seminar", "webinar", "certification", "study group", "learning"]),
    ("Dance",       ["dance", "bharatanatyam", "kathak", "garba", "dandiya",
                     "bhangra class", "salsa", "nritya"]),
    ("Music",       ["concert", "music", "live band", "singer", "dj ", "dj night",
                     "bollywood night", "bhangra night", "carnatic", "classical music",
                     "ghazal", "qawwali"]),
    ("Food",        ["food", "cook", "biryani", "culinary", "taste", "dinner", "brunch",
                     "lunch", "feast", "potluck", "tasting", "chai"]),
    ("Comedy",      ["comedy", "standup", "stand-up", "comedian", "laugh", "open mic"]),
    ("Sports",      ["cricket", "kabaddi", "badminton", "sport", "marathon", "run ",
                     "5k ", "10k ", "carrom"]),
    ("Religious",   ["temple", "gurdwara", "mosque", "puja", "pooja", "havan",
                     "kirtan", "bhajan", "aarti", "satsang", "prayer"]),
    ("Festival",    ["diwali", "holi", "navratri", "pongal", "onam", "eid", "vaisakhi",
                     "festival", "mela", "dussehra", "ganesh"]),
    ("Community",   ["convention", "conference", "meetup", "networking", "association",
                     "community", "gala", "fundraiser", "charity", "social"]),
    ("Cultural",    ["cultural", "art", "exhibit", "gallery", "heritage", "history",
                     "yoga", "meditation", "ayurveda"]),
]

# Relevance keywords — event title/description must contain at least one
RELEVANCE_KEYWORDS = [
    "indian", "india", "bollywood", "telugu", "tamil", "hindi", "punjabi",
    "bengali", "gujarati", "marathi", "malayalam", "kannada", "desi",
    "south asian", "garba", "dandiya", "bhangra", "diwali", "holi",
    "navratri", "pongal", "onam", "eid", "iftar", "sikh", "gurdwara",
    "carnatic", "hindustani", "bharatanatyam", "kathak",
    "kuchipudi", "biryani", "curry", "samosa", "masala",
    "ayurveda", "vedic", "sanskrit", "mehndi", "sangeet",
    "diaspora", "nri", "cricket", "kabaddi", "ipl",
    "kirtan", "bhajan", "puja", "pooja", "kundalini",
    "isha yoga", "sahaja yoga", "isha foundation",
]

FALSE_POSITIVE_PATTERNS = [
    r"(?i)indian wells",
    r"(?i)cleveland indians?(?:\s|$)",
    r"(?i)indian motorcycle",
    r"(?i)native\s+(american\s+)?indian",
    r"(?i)west indian day parade",
    r"(?i)indian island",   # Trail names
    r"(?i)magic the gathering",
    r"(?i)strong nation",
    r"(?i)zumba",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def categorize(title: str, description: str = "") -> str:
    text = f"{title} {description}".lower()
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return cat
    return "Community"  # Default for meetup events


def is_relevant(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()
    for kw in RELEVANCE_KEYWORDS:
        if kw in text:
            return True
    return False


def is_false_positive(title: str) -> bool:
    for pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(pattern, title):
            return True
    return False


def make_slug(title: str, date_str: str) -> str:
    s = f"{title} {date_str}".lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:80]


def parse_datetime(dt_str: str):
    """Parse Meetup ISO datetime string, return (date_str, time_str)."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d"), dt.strftime("%I:%M %p").lstrip("0")
    except:
        return None, None


# ---------------------------------------------------------------------------
# Meetup Scraper
# ---------------------------------------------------------------------------

def fetch_meetup_events(city: dict, keyword: str) -> list:
    """Fetch events from Meetup search page for a city+keyword combo."""
    url = "https://www.meetup.com/find/"
    params = {
        "keywords": keyword,
        "source": "EVENTS",
        "eventType": "inPerson",
        "location": city["location"],
    }

    try:
        resp = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=20)
        if resp.status_code != 200:
            return []
    except Exception as e:
        print(f"  ⚠ Request failed for {keyword}: {e}")
        return []

    # Extract __NEXT_DATA__
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        resp.text
    )
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    apollo = data.get("props", {}).get("pageProps", {}).get("__APOLLO_STATE__", {})
    if not apollo:
        return []

    # Resolve references
    photo_map = {}
    group_map = {}
    for k, v in apollo.items():
        if k.startswith("PhotoInfo:"):
            photo_map[k] = v
        elif k.startswith("Group:"):
            group_map[k] = v

    events = []
    for k, v in apollo.items():
        if not k.startswith("Event:"):
            continue

        title = v.get("title", "")
        if not title:
            continue

        # Get datetime
        dt_str = v.get("dateTime", "")
        date_str, time_str = parse_datetime(dt_str)
        if not date_str:
            continue

        # Skip past events
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date < datetime.now().date():
                continue
        except:
            continue

        # Get description (truncate for storage)
        description = v.get("description", "") or ""
        short_desc = description[:500] if description else title

        # Get venue info
        venue = v.get("venue", {}) or {}
        venue_name = ""
        venue_city = city["display"]
        venue_state = city["state"]
        lat = None
        lon = None

        if isinstance(venue, dict) and venue.get("__typename") == "Venue":
            venue_name = venue.get("name", "")
            venue_city = venue.get("city", city["display"]) or city["display"]
            venue_state = venue.get("state", city["state"]) or city["state"]
            lat = venue.get("lat")
            lon = venue.get("lng") or venue.get("lon")

        # Get image URL
        image_url = ""
        photo_ref = v.get("featuredEventPhoto") or v.get("displayPhoto")
        if isinstance(photo_ref, dict) and "__ref" in photo_ref:
            photo_data = photo_map.get(photo_ref["__ref"], {})
            image_url = photo_data.get("highResUrl") or photo_data.get("baseUrl", "")

        # Get group/organizer info
        organizer = ""
        group_ref = v.get("group")
        if isinstance(group_ref, dict) and "__ref" in group_ref:
            group_data = group_map.get(group_ref["__ref"], {})
            organizer = group_data.get("name", "")

        # Get event URL
        event_url = v.get("eventUrl", "")
        event_id = v.get("id", "")

        events.append({
            "title": title,
            "date": date_str,
            "time": time_str or "",
            "venue_name": venue_name,
            "city": venue_city,
            "state": venue_state,
            "category": categorize(title, description),
            "description": short_desc,
            "long_description": description[:2000] if description else None,
            "image_url": image_url,
            "ticket_url": event_url,
            "source": "meetup",
            "source_id": f"meetup_{event_id}",
            "organizer": organizer,
            "slug": make_slug(title, date_str),
            "latitude": float(lat) if lat else None,
            "longitude": float(lon) if lon else None,
        })

    return events


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def get_existing_events() -> set:
    """Get set of existing source_ids and (title_lower, date) tuples for dedup."""
    existing_ids = set()
    existing_title_dates = set()

    try:
        resp = requests.get(
            f"{REST}/events?select=source_id,title,date&limit=2000",
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
            },
            timeout=15
        )
        if resp.status_code == 200:
            for e in resp.json():
                if e.get("source_id"):
                    existing_ids.add(e["source_id"])
                if e.get("title") and e.get("date"):
                    # Fuzzy: normalize title for matching
                    t = re.sub(r'[^a-z0-9]', '', e["title"].lower())
                    existing_title_dates.add((t, e["date"]))
    except Exception as e:
        print(f"  ⚠ Could not fetch existing events: {e}")

    return existing_ids, existing_title_dates


def is_duplicate(event: dict, existing_ids: set, existing_title_dates: set) -> bool:
    """Check if event already exists (by source_id or fuzzy title+date)."""
    if event["source_id"] in existing_ids:
        return True
    t = re.sub(r'[^a-z0-9]', '', event["title"].lower())
    if (t, event["date"]) in existing_title_dates:
        return True
    return False


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_events(events: list) -> int:
    if not events:
        return 0

    # Ensure slugs are unique
    seen_slugs = set()
    for e in events:
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
        try:
            resp = requests.post(
                f"{REST}/events",
                headers=HEADERS,
                json=batch,
                timeout=30
            )
            if resp.status_code in (200, 201):
                total += len(batch)
            else:
                print(f"  ⚠ Upsert failed ({resp.status_code}): {resp.text[:300]}")
                # Try one at a time for this batch
                for ev in batch:
                    try:
                        r2 = requests.post(
                            f"{REST}/events",
                            headers=HEADERS,
                            json=[ev],
                            timeout=15
                        )
                        if r2.status_code in (200, 201):
                            total += 1
                        else:
                            print(f"    ⚠ Single upsert failed for '{ev['title'][:40]}': {r2.text[:200]}")
                    except:
                        pass
        except Exception as e:
            print(f"  ⚠ Upsert error: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape Meetup events for Indian diaspora")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--city", type=str, default=None, help="Single city slug (e.g. 'bay-area')")
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

    # Get existing events for dedup
    existing_ids, existing_title_dates = set(), set()
    if not args.dry_run:
        print("📋 Fetching existing events for deduplication...")
        existing_ids, existing_title_dates = get_existing_events()
        print(f"   Found {len(existing_ids)} existing source_ids, {len(existing_title_dates)} title+date combos")

    all_events = []
    seen_source_ids = set()

    print(f"\n🔍 Scraping Meetup ({len(cities)} cities × {len(KEYWORDS)} keywords)...\n")

    for city in cities:
        city_events = []
        for keyword in KEYWORDS:
            print(f"  📍 {city['display']}: \"{keyword}\"...", end=" ", flush=True)
            events = fetch_meetup_events(city, keyword)

            # Filter for relevance
            relevant = []
            for e in events:
                if is_false_positive(e["title"]):
                    continue
                if not is_relevant(e["title"], e.get("description", "")):
                    continue
                if e["source_id"] in seen_source_ids:
                    continue
                if not args.dry_run and is_duplicate(e, existing_ids, existing_title_dates):
                    continue
                seen_source_ids.add(e["source_id"])
                relevant.append(e)

            city_events.extend(relevant)
            print(f"{len(events)} found, {len(relevant)} relevant")

            # Rate limit — be nice to Meetup
            time.sleep(1.5)

        all_events.extend(city_events)
        if city_events:
            print(f"  ✅ {city['display']}: {len(city_events)} new relevant events\n")
        else:
            print(f"  ⚪ {city['display']}: no new events\n")

    print(f"\n📊 Total new relevant events: {len(all_events)}")

    if args.dry_run:
        print("\n🔍 DRY RUN — events that would be inserted:\n")
        for e in all_events:
            print(f"  [{e['category']}] {e['title']}")
            print(f"    📅 {e['date']} {e['time']} | 📍 {e['venue_name']}, {e['city']}, {e['state']}")
            print(f"    🔗 {e['ticket_url']}")
            print(f"    🏷️  {e['organizer']}")
            print()
        return

    if all_events:
        print(f"\n💾 Upserting {len(all_events)} events to Supabase...")
        count = upsert_events(all_events)
        print(f"✅ Upserted {count} events")
    else:
        print("No new events to insert.")


if __name__ == "__main__":
    main()
