#!/usr/bin/env python3
"""
scrape-meetup.py — Scrape Indian/desi community events from Meetup.com
and upsert them into the Supabase `events` table.

Searches by US state (all 50 + DC) for full national coverage.
Meetup uses Next.js with Apollo cache. We fetch search pages and
extract event data from the __NEXT_DATA__ / __APOLLO_STATE__ JSON embedded
in the HTML. No API key needed.

Usage:
    python3 pipeline/scrape-meetup.py              # Today's rotation (~8 states)
    python3 pipeline/scrape-meetup.py --day 0       # Explicit rotation day
    python3 pipeline/scrape-meetup.py --all         # All 51 states (full sweep)
    python3 pipeline/scrape-meetup.py --state tx    # Single state (by code)
    python3 pipeline/scrape-meetup.py --dry-run     # Print events without inserting
"""

import hashlib
import json
import os
import re
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta, date
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
    "tech meetup indian", "startup desi", "networking south asian",
    "professional indian", "yoga",
]

# ── 50 US states + DC ─────────────────────────────────────────────────────
# Meetup location param format: us--{state_code_lower}
STATES = [
    {"location": "us--al", "display": "Alabama",              "abbr": "AL", "slug": "alabama"},
    {"location": "us--ak", "display": "Alaska",               "abbr": "AK", "slug": "alaska"},
    {"location": "us--az", "display": "Arizona",              "abbr": "AZ", "slug": "arizona"},
    {"location": "us--ar", "display": "Arkansas",             "abbr": "AR", "slug": "arkansas"},
    {"location": "us--ca", "display": "California",           "abbr": "CA", "slug": "california"},
    {"location": "us--co", "display": "Colorado",             "abbr": "CO", "slug": "colorado"},
    {"location": "us--ct", "display": "Connecticut",          "abbr": "CT", "slug": "connecticut"},
    {"location": "us--de", "display": "Delaware",             "abbr": "DE", "slug": "delaware"},
    {"location": "us--fl", "display": "Florida",              "abbr": "FL", "slug": "florida"},
    {"location": "us--ga", "display": "Georgia",              "abbr": "GA", "slug": "georgia"},
    {"location": "us--hi", "display": "Hawaii",               "abbr": "HI", "slug": "hawaii"},
    {"location": "us--id", "display": "Idaho",                "abbr": "ID", "slug": "idaho"},
    {"location": "us--il", "display": "Illinois",             "abbr": "IL", "slug": "illinois"},
    {"location": "us--in", "display": "Indiana",              "abbr": "IN", "slug": "indiana"},
    {"location": "us--ia", "display": "Iowa",                 "abbr": "IA", "slug": "iowa"},
    {"location": "us--ks", "display": "Kansas",               "abbr": "KS", "slug": "kansas"},
    {"location": "us--ky", "display": "Kentucky",             "abbr": "KY", "slug": "kentucky"},
    {"location": "us--la", "display": "Louisiana",            "abbr": "LA", "slug": "louisiana"},
    {"location": "us--me", "display": "Maine",                "abbr": "ME", "slug": "maine"},
    {"location": "us--md", "display": "Maryland",             "abbr": "MD", "slug": "maryland"},
    {"location": "us--ma", "display": "Massachusetts",        "abbr": "MA", "slug": "massachusetts"},
    {"location": "us--mi", "display": "Michigan",             "abbr": "MI", "slug": "michigan"},
    {"location": "us--mn", "display": "Minnesota",            "abbr": "MN", "slug": "minnesota"},
    {"location": "us--ms", "display": "Mississippi",          "abbr": "MS", "slug": "mississippi"},
    {"location": "us--mo", "display": "Missouri",             "abbr": "MO", "slug": "missouri"},
    {"location": "us--mt", "display": "Montana",              "abbr": "MT", "slug": "montana"},
    {"location": "us--ne", "display": "Nebraska",             "abbr": "NE", "slug": "nebraska"},
    {"location": "us--nv", "display": "Nevada",               "abbr": "NV", "slug": "nevada"},
    {"location": "us--nh", "display": "New Hampshire",        "abbr": "NH", "slug": "new-hampshire"},
    {"location": "us--nj", "display": "New Jersey",           "abbr": "NJ", "slug": "new-jersey"},
    {"location": "us--nm", "display": "New Mexico",           "abbr": "NM", "slug": "new-mexico"},
    {"location": "us--ny", "display": "New York",             "abbr": "NY", "slug": "new-york"},
    {"location": "us--nc", "display": "North Carolina",       "abbr": "NC", "slug": "north-carolina"},
    {"location": "us--nd", "display": "North Dakota",         "abbr": "ND", "slug": "north-dakota"},
    {"location": "us--oh", "display": "Ohio",                 "abbr": "OH", "slug": "ohio"},
    {"location": "us--ok", "display": "Oklahoma",             "abbr": "OK", "slug": "oklahoma"},
    {"location": "us--or", "display": "Oregon",               "abbr": "OR", "slug": "oregon"},
    {"location": "us--pa", "display": "Pennsylvania",         "abbr": "PA", "slug": "pennsylvania"},
    {"location": "us--ri", "display": "Rhode Island",         "abbr": "RI", "slug": "rhode-island"},
    {"location": "us--sc", "display": "South Carolina",       "abbr": "SC", "slug": "south-carolina"},
    {"location": "us--sd", "display": "South Dakota",         "abbr": "SD", "slug": "south-dakota"},
    {"location": "us--tn", "display": "Tennessee",            "abbr": "TN", "slug": "tennessee"},
    {"location": "us--tx", "display": "Texas",                "abbr": "TX", "slug": "texas"},
    {"location": "us--ut", "display": "Utah",                 "abbr": "UT", "slug": "utah"},
    {"location": "us--vt", "display": "Vermont",              "abbr": "VT", "slug": "vermont"},
    {"location": "us--va", "display": "Virginia",             "abbr": "VA", "slug": "virginia"},
    {"location": "us--wa", "display": "Washington",           "abbr": "WA", "slug": "washington"},
    {"location": "us--wv", "display": "West Virginia",        "abbr": "WV", "slug": "west-virginia"},
    {"location": "us--wi", "display": "Wisconsin",            "abbr": "WI", "slug": "wisconsin"},
    {"location": "us--wy", "display": "Wyoming",              "abbr": "WY", "slug": "wyoming"},
    {"location": "us--dc", "display": "District of Columbia", "abbr": "DC", "slug": "district-of-columbia"},
]

# Category rules (same as events-ingest.py)
CATEGORY_RULES = [
    # Spiritual/Religious FIRST — these should never fall through to Education
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
                     "robotics competition", "coding competition", "debate tournament",
                     "hackathon", "competition", "contest", "tournament"]),
    # Entertainment / Music / Dance BEFORE Education
    ("Entertainment", ["bollywood night", "bollywood festive", "bollywood singing",
                       "bollyx", "dj party", "afterparty", "after party",
                       "cruise party", "rooftop party", "yacht party",
                       "bollywood rock"]),
    ("Music",       ["concert", "live music", "live band", "singer", "dj night",
                     "bhangra night", "carnatic", "classical music",
                     "ghazal", "qawwali", "raagas"]),
    ("Dance",       ["dance", "bharatanatyam", "kathak", "garba", "dandiya",
                     "bhangra class", "salsa", "nritya", "bachata", "cha-cha",
                     "forró", "bollyx"]),
    ("Comedy",      ["comedy", "standup", "stand-up", "comedian", "laugh", "open mic"]),
    ("Food",        ["food", "cook", "biryani", "culinary", "taste", "dinner", "brunch",
                     "lunch", "feast", "potluck", "tasting", "chai", "restaurant",
                     "cuisine", "wine", "foodie"]),
    ("Sports",      ["cricket", "kabaddi", "badminton", "sport", "marathon", "run ",
                     "5k ", "10k ", "carrom"]),
    # Education LAST — only if nothing else matched
    ("Education",   ["school", "certification", "study group",
                     "seminar", "webinar", "course"]),
    ("Cultural",    ["cultural", "art", "exhibit", "gallery", "heritage", "history"]),
    ("Community",   ["convention", "conference", "meetup", "networking", "association",
                     "community", "gala", "fundraiser", "charity", "social",
                     "workshop", "class", "training", "lecture", "learning"]),
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
    "yoga", "chai", "rangoli", "kolam",
    "tech meetup", "startup", "networking", "professional",
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

def fetch_meetup_events(state: dict, keyword: str) -> list:
    """Fetch events from Meetup search page for a state+keyword combo."""
    url = "https://www.meetup.com/find/"
    params = {
        "keywords": keyword,
        "source": "EVENTS",
        "eventType": "inPerson",
        "location": state["location"],
    }

    try:
        resp = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=12)
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

        # Get venue info — city/state come from the event venue, not the search scope
        venue = v.get("venue", {}) or {}
        venue_name = ""
        venue_city = ""
        venue_state = state["abbr"]
        street_address = ""
        lat = None
        lon = None

        if isinstance(venue, dict) and venue.get("__typename") == "Venue":
            venue_name = venue.get("name", "")
            venue_city = venue.get("city", "") or ""
            venue_state = venue.get("state", state["abbr"]) or state["abbr"]
            street_address = venue.get("address", "") or ""
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
        group_city = ""
        group_ref = v.get("group")
        if isinstance(group_ref, dict) and "__ref" in group_ref:
            group_data = group_map.get(group_ref["__ref"], {})
            organizer = group_data.get("name", "")
            group_city = group_data.get("city", "") or ""

        # Get event URL
        event_url = v.get("eventUrl", "")
        event_id = v.get("id", "")

        _lat = float(lat) if lat else None
        _lon = float(lon) if lon else None
        fp = content_fingerprint(title, date_str, venue_city or group_city or "")

        events.append({
            "title": title,
            "date": date_str,
            "time": time_str or "",
            "venue_name": venue_name,
            "city": venue_city or group_city or "",
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
            "latitude": _lat,
            "longitude": _lon,
            "content_fingerprint": fp,
            "street_address": street_address[:300] if street_address else None,
        })

    return events


# ---------------------------------------------------------------------------
# Cross-source content fingerprint — use shared module
# ---------------------------------------------------------------------------

from event_dedup import content_fingerprint, get_all_fingerprints


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def get_existing_events() -> tuple:
    """Get set of existing source_ids, (title_lower, date) tuples, and content_fingerprints for dedup."""
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
    """Normalize title for fuzzy dedup: lowercase, strip punctuation, dates, 'free', etc."""
    t = title.lower().strip()
    t = re.sub(r'&amp;', '&', t)
    t = re.sub(r'[^a-z0-9 ]', '', t)
    t = re.sub(r'\b(jan|feb|mar|apr|may|june?|july?|aug|sept?|oct|nov|dec)\b', '', t)
    t = re.sub(r'\b\d+\b', '', t)
    t = re.sub(r'\bfree\b', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def normalize_title_from_stripped(stripped: str) -> str:
    """Normalize an already-stripped (alphanumeric only) title for prefix matching."""
    return stripped[:25]


def is_duplicate(event: dict, existing_ids: set, existing_title_dates: set, existing_fingerprints: set = set()) -> bool:
    """Check if event already exists (by source_id, fuzzy title+date, or content fingerprint)."""
    if event["source_id"] in existing_ids:
        return True
    # Exact alphanumeric match
    t = re.sub(r'[^a-z0-9]', '', event["title"].lower())
    if (t, event["date"]) in existing_title_dates:
        return True
    # Cross-source content fingerprint (unified: title+date+city)
    if existing_fingerprints:
        fp = content_fingerprint(
            event["title"],
            event["date"],
            event.get("city", "")
        )
        if fp in existing_fingerprints:
            return True
    # Fuzzy prefix match (first 25 normalized chars + same date)
    tn = normalize_title(event["title"])[:25]
    for (et, ed) in existing_title_dates:
        if ed == event["date"]:
            en = normalize_title_from_stripped(et)[:25]
            if tn and en and tn == en:
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
    parser = argparse.ArgumentParser(description="Scrape Meetup events for Indian diaspora (state-level)")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--state", type=str, default=None,
                        help="Single state by code (e.g. 'tx', 'ca') or slug (e.g. 'texas')")
    parser.add_argument("--day", type=int, choices=range(7), default=None,
                        help="Day-of-week rotation (0-6). Splits 51 states into 7 daily slices of ~8 each.")
    parser.add_argument("--all", action="store_true", help="Scrape all 51 states")
    args = parser.parse_args()

    if not args.dry_run and (not SB_URL or not SB_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    states = STATES
    if args.state:
        key = args.state.lower()
        states = [s for s in STATES if s["abbr"].lower() == key or s["slug"] == key]
        if not states:
            print(f"Unknown state: {args.state}. Use code (tx) or slug (texas).")
            sys.exit(1)
    elif args.all:
        states = STATES
    elif args.day is not None:
        # Daily rotation: split all states into 7 slices
        states = [s for i, s in enumerate(STATES) if i % 7 == args.day]
        print(f"📅 Day {args.day} batch: {', '.join(s['abbr'] for s in states)} ({len(states)} states)")
    else:
        # Auto-detect rotation day
        rotation_day = date.today().toordinal() % 7
        states = [s for i, s in enumerate(STATES) if i % 7 == rotation_day]
        print(f"📅 Auto day {rotation_day}: {', '.join(s['abbr'] for s in states)} ({len(states)} states)")

    # Get existing events for dedup
    existing_ids, existing_title_dates, existing_fingerprints = set(), set(), set()
    if not args.dry_run:
        print("📋 Fetching existing events for deduplication...")
        existing_ids, existing_title_dates, existing_fingerprints = get_existing_events()
        print(f"   Found {len(existing_ids)} existing source_ids, {len(existing_title_dates)} title+date combos, {len(existing_fingerprints)} content fingerprints")

    all_events = []
    seen_source_ids = set()
    seen_batch_keys = set()

    print(f"\n🔍 Scraping Meetup ({len(states)} states × {len(KEYWORDS)} keywords)...\n")

    for state in states:
        state_events = []
        for keyword in KEYWORDS:
            print(f"  📍 {state['display']} ({state['abbr']}): \"{keyword}\"...", end=" ", flush=True)
            events = fetch_meetup_events(state, keyword)

            # Filter for relevance
            relevant = []
            for e in events:
                if is_false_positive(e["title"]):
                    continue
                if not is_relevant(e["title"], e.get("description", "")):
                    continue
                if e["source_id"] in seen_source_ids:
                    continue
                # Within-batch fuzzy dedup (same event from different keywords)
                batch_key = normalize_title(e["title"])[:25] + "|" + e["date"]
                if batch_key in seen_batch_keys:
                    continue
                if not args.dry_run and is_duplicate(e, existing_ids, existing_title_dates, existing_fingerprints):
                    continue
                seen_source_ids.add(e["source_id"])
                seen_batch_keys.add(batch_key)
                relevant.append(e)

            state_events.extend(relevant)
            print(f"{len(events)} found, {len(relevant)} relevant")

            # Rate limit — be nice to Meetup
            time.sleep(1.5)

        all_events.extend(state_events)
        if state_events:
            print(f"  ✅ {state['display']}: {len(state_events)} new relevant events\n")
        else:
            print(f"  ⚪ {state['display']}: no new events\n")

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
