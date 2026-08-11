#!/usr/bin/env python3
"""
scrape-allevents.py — Scrape Indian/desi events from AllEvents.in
and upsert them into the Supabase `events` table.

Approach: AllEvents.in has public listing pages at allevents.in/<city>/indian.
Event cards in the HTML have data-eid, data-link, data-name attributes.
Individual event pages contain rich JSON-LD structured data with full details
including geo coordinates, description, dates, venue, and pricing.

Usage:
    python3 pipeline/scrape-allevents.py              # Full scrape
    python3 pipeline/scrape-allevents.py --dry-run     # Print events without inserting
    python3 pipeline/scrape-allevents.py --city houston # Single city
"""

import json
import hashlib
import os
import re
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

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

# Search keywords to append to city URL
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
    "tech-meetup-indian",
    "startup-desi",
    "networking-south-asian",
    "professional-indian",
    "yoga",
]

# Cities (AllEvents URL slug format)
CITIES = [
    # Batch A — West Coast + NY/NJ + some expanded (16 cities)
    {"ae": "san-francisco", "display": "San Francisco", "state": "CA", "batch": "a"},
    {"ae": "san-jose", "display": "San Jose", "state": "CA", "batch": "a"},
    {"ae": "fremont", "display": "Fremont", "state": "CA", "batch": "a"},
    {"ae": "los-angeles", "display": "Los Angeles", "state": "CA", "batch": "a"},
    {"ae": "seattle", "display": "Seattle", "state": "WA", "batch": "a"},
    {"ae": "new-york", "display": "New York", "state": "NY", "batch": "a"},
    {"ae": "jersey-city", "display": "Jersey City", "state": "NJ", "batch": "a"},
    {"ae": "edison", "display": "Edison", "state": "NJ", "batch": "a"},
    {"ae": "san-diego", "display": "San Diego", "state": "CA", "batch": "a"},
    {"ae": "portland", "display": "Portland", "state": "OR", "batch": "a"},
    {"ae": "sacramento", "display": "Sacramento", "state": "CA", "batch": "a"},
    {"ae": "irvine", "display": "Irvine", "state": "CA", "batch": "a"},
    {"ae": "sunnyvale", "display": "Sunnyvale", "state": "CA", "batch": "a"},
    {"ae": "phoenix", "display": "Phoenix", "state": "AZ", "batch": "a"},
    {"ae": "denver", "display": "Denver", "state": "CO", "batch": "a"},
    {"ae": "minneapolis", "display": "Minneapolis", "state": "MN", "batch": "a"},
    # Batch B — South, Midwest, East + expanded (16 cities)
    {"ae": "chicago", "display": "Chicago", "state": "IL", "batch": "b"},
    {"ae": "houston", "display": "Houston", "state": "TX", "batch": "b"},
    {"ae": "dallas", "display": "Dallas", "state": "TX", "batch": "b"},
    {"ae": "washington-dc", "display": "Washington", "state": "DC", "batch": "b"},
    {"ae": "boston", "display": "Boston", "state": "MA", "batch": "b"},
    {"ae": "atlanta", "display": "Atlanta", "state": "GA", "batch": "b"},
    {"ae": "philadelphia", "display": "Philadelphia", "state": "PA", "batch": "b"},
    {"ae": "detroit", "display": "Detroit", "state": "MI", "batch": "b"},
    {"ae": "austin", "display": "Austin", "state": "TX", "batch": "b"},
    {"ae": "miami", "display": "Miami", "state": "FL", "batch": "b"},
    {"ae": "tampa", "display": "Tampa", "state": "FL", "batch": "b"},
    {"ae": "charlotte", "display": "Charlotte", "state": "NC", "batch": "b"},
    {"ae": "raleigh", "display": "Raleigh", "state": "NC", "batch": "b"},
    {"ae": "columbus", "display": "Columbus", "state": "OH", "batch": "b"},
    {"ae": "indianapolis", "display": "Indianapolis", "state": "IN", "batch": "b"},
    {"ae": "nashville", "display": "Nashville", "state": "TN", "batch": "b"},
    {"ae": "plano", "display": "Plano", "state": "TX", "batch": "b"},
    # Batch C — Tier 2 metros (high Indian/South Asian population)
    {"ae": "cary", "display": "Cary", "state": "NC", "batch": "c"},
    {"ae": "durham", "display": "Durham", "state": "NC", "batch": "c"},
    {"ae": "pittsburgh", "display": "Pittsburgh", "state": "PA", "batch": "c"},
    {"ae": "orlando", "display": "Orlando", "state": "FL", "batch": "c"},
    {"ae": "baltimore", "display": "Baltimore", "state": "MD", "batch": "c"},
    {"ae": "stamford", "display": "Stamford", "state": "CT", "batch": "c"},
    {"ae": "ann-arbor", "display": "Ann Arbor", "state": "MI", "batch": "c"},
    {"ae": "san-antonio", "display": "San Antonio", "state": "TX", "batch": "c"},
    {"ae": "salt-lake-city", "display": "Salt Lake City", "state": "UT", "batch": "c"},
    # Batch D — More Tier 2 metros
    {"ae": "cincinnati", "display": "Cincinnati", "state": "OH", "batch": "d"},
    {"ae": "cleveland", "display": "Cleveland", "state": "OH", "batch": "d"},
    {"ae": "kansas-city", "display": "Kansas City", "state": "MO", "batch": "d"},
    {"ae": "st-louis", "display": "St Louis", "state": "MO", "batch": "d"},
    {"ae": "las-vegas", "display": "Las Vegas", "state": "NV", "batch": "d"},
    {"ae": "richmond", "display": "Richmond", "state": "VA", "batch": "d"},
    {"ae": "fairfax", "display": "Fairfax", "state": "VA", "batch": "d"},
    {"ae": "herndon", "display": "Herndon", "state": "VA", "batch": "d"},
    {"ae": "ashburn", "display": "Ashburn", "state": "VA", "batch": "d"},
    {"ae": "plainsboro", "display": "Plainsboro", "state": "NJ", "batch": "c"},
    {"ae": "iselin", "display": "Iselin", "state": "NJ", "batch": "c"},
    {"ae": "piscataway", "display": "Piscataway", "state": "NJ", "batch": "c"},
    {"ae": "jacksonville", "display": "Jacksonville", "state": "FL", "batch": "d"},
    {"ae": "hartford", "display": "Hartford", "state": "CT", "batch": "d"},
    {"ae": "milwaukee", "display": "Milwaukee", "state": "WI", "batch": "d"},
]

# Category rules
CATEGORY_RULES = [
    # Spiritual/Religious FIRST — yoga, meditation, etc. should never be Education
    ("Religious",   ["temple", "gurdwara", "mosque", "puja", "pooja", "havan",
                     "kirtan", "bhajan", "aarti", "satsang", "prayer",
                     "yoga", "meditation", "sound bath", "sound healing",
                     "pranayama", "dhyana", "mantra", "bhakti", "vedic",
                     "ayurveda", "kundalini", "reiki", "chakra", "inner engineering",
                     "sadhguru", "devotional", "sacred", "chanting", "sufi",
                     "mindfulness", "spiritual"]),
    ("Festival",    ["diwali", "holi", "navratri", "pongal", "onam", "eid", "vaisakhi",
                     "festival", "mela", "dussehra", "ganesh"]),
    ("Competition", ["spelling bee", "math olympiad", "science olympiad", "chess tournament",
                     "robotics competition", "coding competition", "hackathon",
                     "competition", "contest", "tournament"]),
    # Entertainment / Music / Dance BEFORE Education
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
    ("Food",        ["food", "cook", "biryani", "culinary", "dinner", "brunch",
                     "lunch", "feast", "potluck", "tasting", "chai", "restaurant",
                     "cuisine", "wine", "foodie"]),
    ("Sports",      ["cricket", "kabaddi", "badminton", "sport", "marathon",
                     "run ", "5k ", "10k "]),
    # Education LAST — only if nothing else matched
    ("Education",   ["school", "certification", "study group",
                     "seminar", "webinar", "course"]),
    ("Cultural",    ["cultural", "art", "exhibit", "gallery", "heritage", "history"]),
    ("Community",   ["convention", "conference", "meetup", "networking", "association",
                     "community", "gala", "fundraiser", "charity",
                     "workshop", "class", "training", "lecture", "learning",
                     "party", "night"]),
]

RELEVANCE_KEYWORDS = [
    "indian", "india", "bollywood", "telugu", "tamil", "hindi", "punjabi",
    "bengali", "gujarati", "marathi", "malayalam", "kannada", "desi",
    "south asian", "garba", "dandiya", "bhangra", "diwali", "holi",
    "navratri", "pongal", "onam", "eid", "iftar", "sikh", "gurdwara",
    "temple", "carnatic", "hindustani", "bharatanatyam", "kathak",
    "kuchipudi", "biryani", "curry", "samosa", "masala",
    "yoga", "ayurveda", "vedic", "sanskrit", "mehndi", "sangeet",
    "diaspora", "nri", "cricket", "kabaddi",
    "kirtan", "bhajan", "puja", "pooja", "chai",
    "rangoli", "kolam",
    "tech meetup", "startup", "networking", "professional",
]

FALSE_POSITIVE_PATTERNS = [
    r"(?i)indian wells",
    r"(?i)cleveland indians?(?:\s|$)",
    r"(?i)indian motorcycle",
    r"(?i)native\s+(american\s+)?indian",
    r"(?i)west indian day parade",
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
    return "Entertainment"  # Default for AllEvents


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
        # Handle full datetime
        if "T" in dt_str:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%I:%M %p").lstrip("0")
        else:
            # Date only
            return dt_str[:10], None
    except:
        return None, None


# ---------------------------------------------------------------------------
# AllEvents.in Scraper
# ---------------------------------------------------------------------------

def scrape_listing_page(city: dict, keyword: str) -> list:
    """Scrape a single AllEvents listing page and extract event card info."""
    url = f"https://allevents.in/{city['ae']}/{keyword}"

    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if resp.status_code != 200:
            return []
    except Exception as e:
        print(f"  ⚠ Request failed for {url}: {e}")
        return []

    html = resp.text

    # Extract event cards from HTML using data attributes
    # Pattern: <li class="event-card event-card-link" data-eid="..." data-link="..." data-name="...">
    cards = re.findall(
        r'<li\s+class="event-card event-card-link"\s+'
        r'data-eid="([^"]*)"\s+'
        r'data-link="([^"]*)"\s+'
        r'data-name="([^"]*)"',
        html
    )

    events = []
    for eid, link, name in cards:
        if not eid or not link:
            continue
        events.append({
            "ae_id": eid,
            "link": link,
            "name": name,
        })

    return events


def strip_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&quot;', '"').replace('&nbsp;', ' ')
    # Collapse whitespace but preserve paragraph breaks
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def fetch_event_details(event_url: str) -> dict | None:
    """Fetch individual event page and extract JSON-LD + HTML description."""
    try:
        resp = requests.get(event_url, headers={"User-Agent": UA}, timeout=20)
        if resp.status_code != 200:
            return None
    except Exception as e:
        return None

    html = resp.text

    # Extract JSON-LD blocks
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>',
        html, re.DOTALL
    )

    json_ld = None
    for block in blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "Event":
                        json_ld = item
                        break
            elif isinstance(data, dict) and data.get("@type") == "Event":
                json_ld = data
            if json_ld:
                break
        except json.JSONDecodeError:
            continue

    if json_ld:
        # Extract full description from HTML (richer than JSON-LD summary)
        desc_match = re.search(
            r'<div\s+class="event-description-html">\s*(.*?)\s*</div>',
            html, re.DOTALL
        )
        if desc_match:
            full_desc = strip_html(desc_match.group(1))
            if len(full_desc) > len(json_ld.get("description", "")):
                json_ld["_full_description"] = full_desc

        return json_ld

    # Fallback: try to extract from HTML meta tags
    meta = {}
    for tag in ["og:title", "og:description", "og:image"]:
        m = re.search(rf'<meta\s+property="{tag}"\s+content="([^"]*)"', html)
        if m:
            meta[tag] = m.group(1)

    if meta.get("og:title"):
        return {"_from_meta": True, **meta}

    return None


def process_event(card: dict, city: dict) -> dict | None:
    """Fetch event details and build an event record."""
    event_url = card["link"]
    ae_id = card["ae_id"]
    name = card["name"]

    details = fetch_event_details(event_url)
    if not details:
        return None

    if details.get("_from_meta"):
        # Sparse fallback from meta tags
        title = details.get("og:title", name)
        date_str = None
        time_str = None
        venue_name = ""
        description = details.get("og:description", "")
        image_url = details.get("og:image", "")
        lat, lon = None, None
        end_date_str = None
        street_address = ""
        zip_code = ""
        full_description = description
        addr_city = city["display"]
        addr_state = city["state"]
    else:
        # Rich JSON-LD data
        title = details.get("name", name)
        date_str, time_str = parse_iso_date(details.get("startDate"))
        _, _ = parse_iso_date(details.get("endDate"))
        end_date_str, _ = parse_iso_date(details.get("endDate"))

        location = details.get("location", {})
        venue_name = location.get("name", "") if isinstance(location, dict) else ""
        address = location.get("address", {}) if isinstance(location, dict) else {}
        geo = location.get("geo", {}) if isinstance(location, dict) else {}

        description = details.get("description", "")
        image_url = details.get("image", "")

        lat = float(geo.get("latitude")) if geo.get("latitude") else None
        lon = float(geo.get("longitude")) if geo.get("longitude") else None

        # Extract street address and zip from JSON-LD (PostalAddress)
        street_address = ""
        zip_code = ""
        if isinstance(address, dict):
            addr_city = address.get("addressLocality", city["display"])
            addr_state = address.get("addressRegion", city["state"])
            street_address = address.get("streetAddress", "")
            zip_code = address.get("postalCode", "")
        else:
            addr_city = city["display"]
            addr_state = city["state"]

        # Use full HTML description if available (richer than JSON-LD summary)
        full_description = details.get("_full_description", "")
        if not full_description or len(full_description) < len(description):
            full_description = description

    if not date_str:
        return None

    # Skip past events
    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if event_date < datetime.now().date():
            return None
    except:
        return None

    event_city = addr_city
    event_state = addr_state

    fp = content_fingerprint(title, date_str, event_city)

    return {
        "title": title,
        "date": date_str,
        "end_date": end_date_str if end_date_str else None,
        "time": time_str or "",
        "venue_name": venue_name,
        "city": event_city,
        "state": event_state,
        "category": categorize(title, full_description),
        "description": description[:500] if description else title,
        "long_description": full_description[:2000] if full_description else None,
        "image_url": image_url,
        "ticket_url": event_url,
        "source": "allevents",
        "source_id": f"allevents_{ae_id}",
        "organizer": "",
        "slug": make_slug(title, date_str),
        "latitude": lat,
        "longitude": lon,
        "content_fingerprint": fp,
        "street_address": street_address[:300] if street_address else None,
        "zip_code": zip_code[:20] if zip_code else None,
    }


# ---------------------------------------------------------------------------
# Deduplication — uses shared cross-source module
# ---------------------------------------------------------------------------

from event_dedup import content_fingerprint, get_all_fingerprints


def get_existing_events() -> tuple:
    existing_ids = set()
    existing_title_dates = set()

    try:
        resp = requests.get(
            f"{REST}/events?select=source_id,title,date&limit=5000",
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

    # Cross-source fingerprints via shared module (uses curl)
    existing_fingerprints = get_all_fingerprints()

    return existing_ids, existing_title_dates, existing_fingerprints


def normalize_title(title: str) -> str:
    """Normalize title for fuzzy dedup."""
    t = title.lower().strip()
    t = re.sub(r'&amp;', '&', t)
    t = re.sub(r'[^a-z0-9 ]', '', t)
    t = re.sub(r'\b(jan|feb|mar|apr|may|june?|july?|aug|sept?|oct|nov|dec)\b', '', t)
    t = re.sub(r'\b\d+\b', '', t)
    t = re.sub(r'\bfree\b', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def is_duplicate(event: dict, existing_ids: set, existing_title_dates: set, existing_fingerprints: set) -> bool:
    if event["source_id"] in existing_ids:
        return True
    t = re.sub(r'[^a-z0-9]', '', event["title"].lower())
    if (t, event["date"]) in existing_title_dates:
        return True
    # Cross-source content fingerprint (unified: title+date+city)
    fp = content_fingerprint(
        event["title"],
        event["date"],
        event.get("city", "")
    )
    if fp in existing_fingerprints:
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
                # Try one at a time
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
                    except:
                        pass
        except Exception as e:
            print(f"  ⚠ Upsert error: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape AllEvents.in for Indian diaspora events")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--city", type=str, default=None, help="Single city slug (e.g. 'houston')")
    parser.add_argument("--batch", type=str, default=None, choices=["a", "b", "c", "d"], help="Legacy batches (prefer --day)")
    parser.add_argument("--day", type=int, choices=range(7), default=None,
                        help="Day-of-week batch (0=Mon..6=Sun). Full cycle = 1 week.")
    args = parser.parse_args()

    if not args.dry_run and (not SB_URL or not SB_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    cities = CITIES
    if args.city:
        cities = [c for c in CITIES if c["ae"] == args.city]
        if not cities:
            print(f"Unknown city: {args.city}. Available: {', '.join(c['ae'] for c in CITIES)}")
            sys.exit(1)
    elif args.day is not None:
        cities = [c for i, c in enumerate(CITIES) if i % 7 == args.day]
        print(f"📅 Day {args.day} batch: {', '.join(c['display'] for c in cities)} ({len(cities)} cities)")
    elif args.batch:
        cities = [c for c in CITIES if c.get("batch") == args.batch]
        print(f"📦 Running batch {args.batch.upper()}: {len(cities)} cities")

    # Get existing events for dedup
    existing_ids, existing_title_dates = set(), set()
    if not args.dry_run:
        print("📋 Fetching existing events for deduplication...")
        existing_ids, existing_title_dates, existing_fingerprints = get_existing_events()
        print(f"   Found {len(existing_ids)} existing source_ids, {len(existing_title_dates)} title+date combos, {len(existing_fingerprints)} content fingerprints")

    all_events = []
    seen_source_ids = set()
    seen_batch_keys = set()

    print(f"\n🔍 Scraping AllEvents.in ({len(cities)} cities × {len(KEYWORDS)} keywords)...\n")

    for city in cities:
        city_events = []
        city_cards_seen = set()  # Avoid duplicate detail fetches within a city

        for keyword in KEYWORDS:
            print(f"  📍 {city['display']}: \"{keyword}\"...", end=" ", flush=True)

            cards = scrape_listing_page(city, keyword)
            new_cards = [c for c in cards if c["ae_id"] not in city_cards_seen]

            relevant_count = 0
            for card in new_cards:
                city_cards_seen.add(card["ae_id"])

                # Quick relevance check on name before fetching details
                name = card.get("name", "")
                if is_false_positive(name):
                    continue

                # Fetch full details
                event = process_event(card, city)
                if not event:
                    continue

                # Check relevance with full description
                if not is_relevant(event["title"], event.get("description", "")):
                    continue

                # Dedup check
                if event["source_id"] in seen_source_ids:
                    continue
                batch_key = normalize_title(event["title"])[:25] + "|" + event["date"]
                if batch_key in seen_batch_keys:
                    continue
                if not args.dry_run and is_duplicate(event, existing_ids, existing_title_dates, existing_fingerprints):
                    continue

                seen_source_ids.add(event["source_id"])
                seen_batch_keys.add(batch_key)
                city_events.append(event)
                relevant_count += 1

                # Rate limit — be nice to AllEvents
                time.sleep(0.8)

            print(f"{len(cards)} cards, {len(new_cards)} new, {relevant_count} relevant")

            # Rate limit between listing pages
            time.sleep(1.0)

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
