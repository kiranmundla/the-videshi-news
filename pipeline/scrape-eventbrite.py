#!/usr/bin/env python3
"""
scrape-eventbrite.py — Scrape Indian/desi community events from Eventbrite
and upsert them into the Supabase `events` table.

Approach: Eventbrite search pages embed JSON-LD (schema.org ItemList) with
full event details including geo coordinates, venue, dates, and descriptions.
No API key needed — just fetch the HTML and parse the structured data.

Usage:
    python3 pipeline/scrape-eventbrite.py              # Full scrape
    python3 pipeline/scrape-eventbrite.py --dry-run     # Print events without inserting
    python3 pipeline/scrape-eventbrite.py --city austin  # Single city
    python3 pipeline/scrape-eventbrite.py --batch a      # Run batch A only
"""

import json
import os
import re
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta

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

# Search keywords (Indian/South Asian culture + professional/tech)
KEYWORDS = [
    "indian",
    "bollywood",
    "desi",
    "tamil",
    "telugu",
    "punjabi",
    "hindi",
    "gujarati",
    "south-asian",
    "bengali",
    "garba",
    "bhangra",
    "yoga-indian",
    "tech-meetup-indian",
    "networking-south-asian",
    "professional-indian",
]

# Cities — Eventbrite URL format: /d/{state}--{city-slug}/{keyword}/
CITIES = [
    # Batch A — West Coast + NY/NJ + Mountain/Midwest (16 cities)
    {"eb": "ca--san-francisco",  "display": "San Francisco", "state": "CA", "slug": "san-francisco",  "batch": "a"},
    {"eb": "ca--san-jose",       "display": "San Jose",      "state": "CA", "slug": "san-jose",       "batch": "a"},
    {"eb": "ca--fremont",        "display": "Fremont",       "state": "CA", "slug": "fremont",        "batch": "a"},
    {"eb": "ca--sunnyvale",      "display": "Sunnyvale",     "state": "CA", "slug": "sunnyvale",      "batch": "a"},
    {"eb": "ca--los-angeles",    "display": "Los Angeles",   "state": "CA", "slug": "los-angeles",    "batch": "a"},
    {"eb": "ca--san-diego",      "display": "San Diego",     "state": "CA", "slug": "san-diego",      "batch": "a"},
    {"eb": "ca--irvine",         "display": "Irvine",        "state": "CA", "slug": "irvine",         "batch": "a"},
    {"eb": "ca--sacramento",     "display": "Sacramento",    "state": "CA", "slug": "sacramento",     "batch": "a"},
    {"eb": "wa--seattle",        "display": "Seattle",       "state": "WA", "slug": "seattle",        "batch": "a"},
    {"eb": "or--portland",       "display": "Portland",      "state": "OR", "slug": "portland",       "batch": "a"},
    {"eb": "ny--new-york",       "display": "New York",      "state": "NY", "slug": "new-york",       "batch": "a"},
    {"eb": "nj--edison",         "display": "Edison",        "state": "NJ", "slug": "edison",         "batch": "a"},
    {"eb": "az--phoenix",        "display": "Phoenix",       "state": "AZ", "slug": "phoenix",        "batch": "a"},
    {"eb": "co--denver",         "display": "Denver",        "state": "CO", "slug": "denver",         "batch": "a"},
    {"eb": "mn--minneapolis",    "display": "Minneapolis",   "state": "MN", "slug": "minneapolis",    "batch": "a"},
    {"eb": "oh--columbus",       "display": "Columbus",      "state": "OH", "slug": "columbus",       "batch": "a"},
    # Batch B — South + Midwest + East (17 cities)
    {"eb": "il--chicago",        "display": "Chicago",       "state": "IL", "slug": "chicago",        "batch": "b"},
    {"eb": "tx--houston",        "display": "Houston",       "state": "TX", "slug": "houston",        "batch": "b"},
    {"eb": "tx--dallas",         "display": "Dallas",        "state": "TX", "slug": "dallas",         "batch": "b"},
    {"eb": "tx--austin",         "display": "Austin",        "state": "TX", "slug": "austin",         "batch": "b"},
    {"eb": "tx--plano",          "display": "Plano",         "state": "TX", "slug": "plano",          "batch": "b"},
    {"eb": "dc--washington",     "display": "Washington",    "state": "DC", "slug": "washington-dc",  "batch": "b"},
    {"eb": "ma--boston",         "display": "Boston",        "state": "MA", "slug": "boston",          "batch": "b"},
    {"eb": "ga--atlanta",        "display": "Atlanta",       "state": "GA", "slug": "atlanta",        "batch": "b"},
    {"eb": "pa--philadelphia",   "display": "Philadelphia",  "state": "PA", "slug": "philadelphia",   "batch": "b"},
    {"eb": "mi--detroit",        "display": "Detroit",       "state": "MI", "slug": "detroit",        "batch": "b"},
    {"eb": "fl--miami",          "display": "Miami",         "state": "FL", "slug": "miami",          "batch": "b"},
    {"eb": "fl--tampa",          "display": "Tampa",         "state": "FL", "slug": "tampa",          "batch": "b"},
    {"eb": "nc--charlotte",      "display": "Charlotte",     "state": "NC", "slug": "charlotte",      "batch": "b"},
    {"eb": "nc--raleigh",        "display": "Raleigh",       "state": "NC", "slug": "raleigh",        "batch": "b"},
    {"eb": "in--indianapolis",   "display": "Indianapolis",  "state": "IN", "slug": "indianapolis",   "batch": "b"},
    {"eb": "tn--nashville",      "display": "Nashville",     "state": "TN", "slug": "nashville",      "batch": "b"},
    {"eb": "nj--jersey-city",    "display": "Jersey City",   "state": "NJ", "slug": "jersey-city",    "batch": "b"},
]

# Category rules (same as other scrapers)
CATEGORY_RULES = [
    # Spiritual/Religious FIRST
    ("Religious",   ["temple", "gurdwara", "mosque", "puja", "pooja", "havan",
                     "kirtan", "bhajan", "aarti", "satsang", "prayer",
                     "yoga", "meditation", "sound bath", "sound healing",
                     "pranayama", "dhyana", "mantra", "bhakti", "vedic",
                     "ayurveda", "kundalini", "reiki", "chakra", "inner engineering",
                     "sadhguru", "devotional", "sacred", "chanting", "sufi",
                     "mindfulness", "spiritual"]),
    ("Festival",    ["diwali", "holi", "navratri", "pongal", "onam", "eid", "vaisakhi",
                     "festival", "mela", "dussehra", "ganesh", "independence day"]),
    ("Competition", ["spelling bee", "math olympiad", "science olympiad", "chess tournament",
                     "robotics competition", "coding competition", "hackathon",
                     "competition", "contest", "tournament"]),
    ("Entertainment", ["bollywood night", "bollywood festive", "bollywood singing",
                       "bollyx", "dj party", "afterparty", "after party",
                       "cruise party", "rooftop party", "yacht party",
                       "bollywood rock", "show", "club", "lounge"]),
    ("Music",       ["concert", "live music", "live band", "singer", "dj night",
                     "bhangra night", "carnatic", "classical music",
                     "ghazal", "qawwali", "raagas"]),
    ("Dance",       ["dance", "bharatanatyam", "kathak", "garba", "dandiya",
                     "bhangra class", "nritya", "bachata", "cha-cha",
                     "forró", "bollyx"]),
    ("Comedy",      ["comedy", "standup", "stand-up", "comedian", "laugh", "open mic"]),
    ("Food",        ["food", "cook", "biryani", "culinary", "taste", "dinner", "brunch",
                     "lunch", "feast", "potluck", "tasting", "chai", "restaurant",
                     "cuisine", "wine", "foodie"]),
    ("Sports",      ["cricket", "kabaddi", "badminton", "sport", "marathon",
                     "run ", "5k ", "10k ", "carrom"]),
    # Education LAST
    ("Education",   ["school", "certification", "study group",
                     "seminar", "webinar", "course"]),
    ("Cultural",    ["cultural", "art", "exhibit", "gallery", "heritage", "history"]),
    ("Community",   ["convention", "conference", "meetup", "networking", "association",
                     "community", "gala", "fundraiser", "charity", "social",
                     "workshop", "class", "training", "lecture", "learning",
                     "startup", "professional", "tech meetup"]),
]

RELEVANCE_KEYWORDS = [
    "indian", "india", "bollywood", "telugu", "tamil", "hindi", "punjabi",
    "bengali", "gujarati", "marathi", "malayalam", "kannada", "desi",
    "south asian", "garba", "dandiya", "bhangra", "diwali", "holi",
    "navratri", "pongal", "onam", "eid", "iftar", "sikh", "gurdwara",
    "temple", "carnatic", "hindustani", "bharatanatyam", "kathak",
    "kuchipudi", "biryani", "curry", "samosa", "masala",
    "yoga", "ayurveda", "vedic", "sanskrit", "mehndi", "sangeet",
    "diaspora", "nri", "cricket", "kabaddi", "ipl",
    "kirtan", "bhajan", "puja", "pooja", "chai",
    "rangoli", "kolam", "kundalini",
    "isha yoga", "sahaja yoga", "isha foundation",
]

FALSE_POSITIVE_PATTERNS = [
    r"(?i)indian wells",
    r"(?i)cleveland indians?(?:\s|$)",
    r"(?i)indian motorcycle",
    r"(?i)native\s+(american\s+)?indian",
    r"(?i)west indian day parade",
    r"(?i)indian island",
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
    return "Community"


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


def parse_iso_date(dt_str: str):
    """Parse ISO date/datetime string, return (date_str, time_str)."""
    if not dt_str:
        return None, None
    try:
        if "T" in dt_str:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%I:%M %p").lstrip("0")
        else:
            return dt_str[:10], None
    except Exception:
        return None, None


def extract_event_id(url: str) -> str:
    """Extract Eventbrite event ID from URL (the digits after 'tickets-')."""
    m = re.search(r'tickets-(\d+)', url)
    if m:
        return m.group(1)
    # fallback — last segment of URL path
    parts = url.rstrip("/").split("/")
    for p in reversed(parts):
        if p.isdigit():
            return p
    return url


# ---------------------------------------------------------------------------
# Eventbrite Scraper
# ---------------------------------------------------------------------------

def fetch_eventbrite_page(city: dict, keyword: str, page: int = 1) -> list:
    """Fetch events from an Eventbrite search page via JSON-LD."""
    url = f"https://www.eventbrite.com/d/{city['eb']}/{keyword}/"
    params = {}
    if page > 1:
        params["page"] = page

    try:
        resp = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=20)
        if resp.status_code != 200:
            return []
    except Exception as e:
        print(f"  ⚠ Request failed: {e}")
        return []

    html = resp.text

    # Extract JSON-LD blocks
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>',
        html, re.DOTALL
    )

    events = []
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue

        # Look for ItemList
        if isinstance(data, dict) and data.get("@type") == "ItemList":
            for item in data.get("itemListElement", []):
                event_data = item.get("item", item)
                if event_data.get("@type") != "Event":
                    continue

                name = event_data.get("name", "")
                if not name:
                    continue

                date_str, time_str = parse_iso_date(event_data.get("startDate"))
                if not date_str:
                    continue

                # Skip past events
                try:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if event_date < datetime.now().date():
                        continue
                except Exception:
                    continue

                end_date_str, _ = parse_iso_date(event_data.get("endDate"))

                description = event_data.get("description", "") or ""
                event_url = event_data.get("url", "")
                image_url = event_data.get("image", "")

                # Location info
                location = event_data.get("location", {}) or {}
                venue_name = ""
                venue_city = city["display"]
                venue_state = city["state"]
                lat = None
                lon = None

                if isinstance(location, dict):
                    venue_name = location.get("name", "")
                    address = location.get("address", {}) or {}
                    geo = location.get("geo", {}) or {}

                    if isinstance(address, dict):
                        venue_city = address.get("addressLocality", city["display"]) or city["display"]
                        venue_state = address.get("addressRegion", city["state"]) or city["state"]

                    if isinstance(geo, dict):
                        try:
                            lat = float(geo["latitude"]) if geo.get("latitude") else None
                            lon = float(geo["longitude"]) if geo.get("longitude") else None
                        except (ValueError, TypeError):
                            pass

                eb_id = extract_event_id(event_url)
                source_id = f"eventbrite_{eb_id}"

                events.append({
                    "title": name,
                    "date": date_str,
                    "end_date": end_date_str,
                    "time": time_str or "",
                    "venue_name": venue_name,
                    "city": venue_city,
                    "state": venue_state,
                    "category": categorize(name, description),
                    "description": description[:500] if description else name,
                    "long_description": description[:2000] if description else None,
                    "image_url": image_url,
                    "ticket_url": event_url,
                    "source": "eventbrite",
                    "source_id": source_id,
                    "organizer": "",
                    "slug": make_slug(name, date_str),
                    "latitude": lat,
                    "longitude": lon,
                })

    return events


def fetch_all_pages(city: dict, keyword: str, max_pages: int = 3) -> list:
    """Fetch multiple pages of Eventbrite results for a city+keyword combo."""
    all_events = []
    for page in range(1, max_pages + 1):
        events = fetch_eventbrite_page(city, keyword, page)
        all_events.extend(events)
        if len(events) < 15:  # Eventbrite returns ~20 per page; if less, no more pages
            break
        if page < max_pages:
            time.sleep(1.2)
    return all_events


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def get_existing_events() -> tuple:
    existing_ids = set()
    existing_title_dates = set()

    try:
        resp = requests.get(
            f"{REST}/events?select=source_id,title,date&limit=3000",
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
                    t = re.sub(r'[^a-z0-9]', '', e["title"].lower())
                    existing_title_dates.add((t, e["date"]))
    except Exception as e:
        print(f"  ⚠ Could not fetch existing events: {e}")

    return existing_ids, existing_title_dates


def normalize_title(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r'&amp;', '&', t)
    t = re.sub(r'[^a-z0-9 ]', '', t)
    t = re.sub(r'\b(jan|feb|mar|apr|may|june?|july?|aug|sept?|oct|nov|dec)\b', '', t)
    t = re.sub(r'\b\d+\b', '', t)
    t = re.sub(r'\bfree\b', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def is_duplicate(event: dict, existing_ids: set, existing_title_dates: set) -> bool:
    if event["source_id"] in existing_ids:
        return True
    t = re.sub(r'[^a-z0-9]', '', event["title"].lower())
    if (t, event["date"]) in existing_title_dates:
        return True
    # Fuzzy prefix match
    tn = normalize_title(event["title"])[:25]
    for (et, ed) in existing_title_dates:
        if ed == event["date"] and tn and tn == et[:25]:
            return True
    return False


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_events(events: list) -> int:
    if not events:
        return 0

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
                            print(f"    ⚠ Failed for '{ev['title'][:40]}': {r2.text[:200]}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"  ⚠ Upsert error: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape Eventbrite events for Indian diaspora")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--city", type=str, default=None, help="Single city slug (e.g. 'austin')")
    parser.add_argument("--batch", type=str, default=None, choices=["a", "b"],
                        help="Run batch a or b")
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
    elif args.batch:
        cities = [c for c in CITIES if c.get("batch") == args.batch]
        print(f"📦 Running batch {args.batch.upper()}: {len(cities)} cities")

    # Get existing events for dedup
    existing_ids, existing_title_dates = set(), set()
    if not args.dry_run:
        print("📋 Fetching existing events for deduplication...")
        existing_ids, existing_title_dates = get_existing_events()
        print(f"   Found {len(existing_ids)} existing source_ids, {len(existing_title_dates)} title+date combos")

    all_events = []
    seen_source_ids = set()
    seen_batch_keys = set()

    print(f"\n🔍 Scraping Eventbrite ({len(cities)} cities × {len(KEYWORDS)} keywords)...\n")

    for city in cities:
        city_events = []

        for keyword in KEYWORDS:
            print(f"  📍 {city['display']}: \"{keyword}\"...", end=" ", flush=True)

            events = fetch_all_pages(city, keyword, max_pages=2)

            # Filter for relevance
            relevant = []
            for e in events:
                if is_false_positive(e["title"]):
                    continue
                if not is_relevant(e["title"], e.get("description", "")):
                    continue
                if e["source_id"] in seen_source_ids:
                    continue
                batch_key = normalize_title(e["title"])[:25] + "|" + e["date"]
                if batch_key in seen_batch_keys:
                    continue
                if not args.dry_run and is_duplicate(e, existing_ids, existing_title_dates):
                    continue
                seen_source_ids.add(e["source_id"])
                seen_batch_keys.add(batch_key)
                relevant.append(e)

            city_events.extend(relevant)
            print(f"{len(events)} found, {len(relevant)} relevant")

            # Rate limit — be nice to Eventbrite
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
            if e.get("latitude"):
                print(f"    📌 ({e['latitude']}, {e['longitude']})")
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
