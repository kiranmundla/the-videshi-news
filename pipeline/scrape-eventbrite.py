#!/usr/bin/env python3
"""
Eventbrite event scraper for The Videshi.
Scrapes Eventbrite search results via __SERVER_DATA__ embedded JSON.
Uses the same 50-city rotation as Meetup/AllEvents/Sulekha scrapers.

Usage:
  python3 scrape-eventbrite.py              # Today's rotation (7 cities)
  python3 scrape-eventbrite.py --day 0      # Explicit rotation day
  python3 scrape-eventbrite.py --all        # All 50 cities (full sweep)
  python3 scrape-eventbrite.py --city austin # Single city test
"""

import os, sys, json, re, time, hashlib, argparse, traceback
from datetime import datetime, date
from urllib.parse import quote

# ── Supabase ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

def supabase_post(table, rows):
    """Insert rows, skip conflicts on slug."""
    import subprocess
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = supabase_headers()
    headers["Prefer"] = "return=minimal,resolution=ignore-duplicates"
    payload = json.dumps(rows)
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal,resolution=ignore-duplicates",
        "-d", payload,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    code = r.stdout.strip()
    return code in ("200", "201")

def get_existing_fingerprints():
    """Fetch existing content_fingerprints from events table."""
    import subprocess
    url = f"{SUPABASE_URL}/rest/v1/events?select=content_fingerprint&source=eq.eventbrite&limit=5000"
    cmd = [
        "curl", "-s", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        rows = json.loads(r.stdout)
        return {row["content_fingerprint"] for row in rows if row.get("content_fingerprint")}
    except:
        return set()

# ── 50 cities ─────────────────────────────────────────────────────────────
CITIES = [
    # Original 14
    {"slug": "san-francisco", "display": "San Francisco", "state": "ca"},
    {"slug": "san-jose", "display": "San Jose", "state": "ca"},
    {"slug": "new-york", "display": "New York", "state": "ny"},
    {"slug": "edison", "display": "Edison", "state": "nj"},
    {"slug": "chicago", "display": "Chicago", "state": "il"},
    {"slug": "houston", "display": "Houston", "state": "tx"},
    {"slug": "dallas", "display": "Dallas", "state": "tx"},
    {"slug": "los-angeles", "display": "Los Angeles", "state": "ca"},
    {"slug": "seattle", "display": "Seattle", "state": "wa"},
    {"slug": "washington", "display": "Washington", "state": "dc"},
    {"slug": "boston", "display": "Boston", "state": "ma"},
    {"slug": "atlanta", "display": "Atlanta", "state": "ga"},
    {"slug": "philadelphia", "display": "Philadelphia", "state": "pa"},
    {"slug": "detroit", "display": "Detroit", "state": "mi"},
    # Expansion 18
    {"slug": "austin", "display": "Austin", "state": "tx"},
    {"slug": "miami", "display": "Miami", "state": "fl"},
    {"slug": "phoenix", "display": "Phoenix", "state": "az"},
    {"slug": "denver", "display": "Denver", "state": "co"},
    {"slug": "san-diego", "display": "San Diego", "state": "ca"},
    {"slug": "portland", "display": "Portland", "state": "or"},
    {"slug": "minneapolis", "display": "Minneapolis", "state": "mn"},
    {"slug": "tampa", "display": "Tampa", "state": "fl"},
    {"slug": "charlotte", "display": "Charlotte", "state": "nc"},
    {"slug": "raleigh", "display": "Raleigh", "state": "nc"},
    {"slug": "columbus", "display": "Columbus", "state": "oh"},
    {"slug": "indianapolis", "display": "Indianapolis", "state": "in"},
    {"slug": "nashville", "display": "Nashville", "state": "tn"},
    {"slug": "sacramento", "display": "Sacramento", "state": "ca"},
    {"slug": "irvine", "display": "Irvine", "state": "ca"},
    {"slug": "plano", "display": "Plano", "state": "tx"},
    {"slug": "fremont", "display": "Fremont", "state": "ca"},
    {"slug": "sunnyvale", "display": "Sunnyvale", "state": "ca"},
    # Tier 2 (18)
    {"slug": "cary", "display": "Cary", "state": "nc"},
    {"slug": "durham", "display": "Durham", "state": "nc"},
    {"slug": "pittsburgh", "display": "Pittsburgh", "state": "pa"},
    {"slug": "orlando", "display": "Orlando", "state": "fl"},
    {"slug": "baltimore", "display": "Baltimore", "state": "md"},
    {"slug": "stamford", "display": "Stamford", "state": "ct"},
    {"slug": "ann-arbor", "display": "Ann Arbor", "state": "mi"},
    {"slug": "san-antonio", "display": "San Antonio", "state": "tx"},
    {"slug": "salt-lake-city", "display": "Salt Lake City", "state": "ut"},
    {"slug": "cincinnati", "display": "Cincinnati", "state": "oh"},
    {"slug": "cleveland", "display": "Cleveland", "state": "oh"},
    {"slug": "kansas-city", "display": "Kansas City", "state": "mo"},
    {"slug": "st-louis", "display": "St Louis", "state": "mo"},
    {"slug": "las-vegas", "display": "Las Vegas", "state": "nv"},
    {"slug": "richmond", "display": "Richmond", "state": "va"},
    {"slug": "jacksonville", "display": "Jacksonville", "state": "fl"},
    {"slug": "hartford", "display": "Hartford", "state": "ct"},
    {"slug": "milwaukee", "display": "Milwaukee", "state": "wi"},
]

# Search terms — "indian" is primary, "desi" and "bollywood" catch party/cultural events
SEARCH_TERMS = ["indian", "desi", "bollywood"]

# ── State code mapping ────────────────────────────────────────────────────
STATE_MAP = {
    "ca": "CA", "ny": "NY", "nj": "NJ", "il": "IL", "tx": "TX",
    "wa": "WA", "dc": "DC", "ma": "MA", "ga": "GA", "pa": "PA",
    "mi": "MI", "fl": "FL", "az": "AZ", "co": "CO", "or": "OR",
    "mn": "MN", "nc": "NC", "oh": "OH", "in": "IN", "tn": "TN",
    "ct": "CT", "md": "MD", "ut": "UT", "mo": "MO", "nv": "NV",
    "va": "VA", "wi": "WI",
}

# ── Relevance filter ─────────────────────────────────────────────────────
# Events matching these keywords in title are likely Indian/South Asian diaspora
RELEVANCE_KEYWORDS = {
    "indian", "india", "bollywood", "desi", "hindi", "tamil", "telugu",
    "bengali", "gujarati", "punjabi", "marathi", "kannada", "malayalam",
    "south asian", "bhangra", "garba", "dandiya", "navratri", "diwali",
    "holi", "ganesh", "durga", "puja", "pongal", "onam", "eid",
    "biryani", "curry", "naan", "chapati", "samosa", "chai",
    "yoga", "meditation", "ayurveda", "vedic", "mandir", "temple",
    "sitar", "tabla", "raga", "carnatic", "hindustani", "kathak",
    "bharatanatyam", "kuchipudi", "odissi", "classical dance",
    "cricket", "kabaddi", "ipl",
    "diaspora", "nri", "dosa", "idli", "masala",
    "rangoli", "mehndi", "henna", "sangeet", "mehendi",
    "independence day", "republic day",
    "ghoshal", "pathak", "kumar", "khan", "sharma", "patel",
    "arijit", "atif", "badshah", "neha kakkar", "shreya",
    "chinmaya", "isha", "art of living", "iskcon", "baps",
    "swami", "guru", "pandit", "kirtan", "bhajan",
}

def is_relevant(event_name: str, event_summary: str = "") -> bool:
    """Check if event is likely Indian/South Asian diaspora related."""
    text = (event_name + " " + (event_summary or "")).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


# ── HTML parsing ──────────────────────────────────────────────────────────

def extract_server_data(html: str) -> dict:
    """Extract __SERVER_DATA__ JSON from Eventbrite page HTML."""
    start = html.find("window.__SERVER_DATA__")
    if start < 0:
        return {}
    eq_pos = html.find("=", start)
    brace_start = html.find("{", eq_pos)
    if brace_start < 0:
        return {}
    # Balanced brace counting
    depth = 0
    end = brace_start
    for i in range(brace_start, len(html)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
        if depth == 0:
            end = i
            break
    try:
        return json.loads(html[brace_start : end + 1])
    except json.JSONDecodeError:
        return {}


def fetch_page(city_slug: str, state: str, term: str, page: int = 1) -> tuple:
    """Fetch one page of Eventbrite search results.
    Returns (events_list, total_count, page_count).
    """
    import subprocess

    # URL pattern: /d/{state}--{city}/{term}-events/ (or just /{term}/)
    if term == "indian":
        url_term = "indian-events"
    elif term == "desi":
        url_term = "desi-events"
    elif term == "bollywood":
        url_term = "bollywood"
    else:
        url_term = f"{term}-events"

    url = f"https://www.eventbrite.com/d/{state}--{city_slug}/{url_term}/"
    if page > 1:
        url += f"?page={page}"

    cmd = [
        "curl", "-s", "-L", "--max-time", "20",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "-H", "Accept: text/html,application/xhtml+xml",
        "-H", "Accept-Language: en-US,en;q=0.9",
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0 or not r.stdout:
        return [], 0, 0

    data = extract_server_data(r.stdout)
    if not data:
        return [], 0, 0

    search_data = data.get("search_data", {})
    events_data = search_data.get("events", {})
    pagination = events_data.get("pagination", {})
    results = events_data.get("results", [])

    total = pagination.get("object_count", 0)
    page_count = pagination.get("page_count", 0)

    return results, total, page_count


def make_slug(title: str, city: str, start_date: str, event_id: str) -> str:
    """Generate a unique slug for the event."""
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    city_slug = re.sub(r"[^a-z0-9]+", "-", city.lower()).strip("-")
    # Append date + last 6 of event_id for uniqueness
    date_part = start_date.replace("-", "") if start_date else ""
    id_suffix = event_id[-6:] if event_id else ""
    slug = f"{base}-{city_slug}-{date_part}-{id_suffix}".strip("-")
    return slug[:120]


def content_fingerprint(title: str, start_date: str, city: str) -> str:
    """Same fingerprint formula as other scrapers."""
    raw = f"{title.lower().strip()}|{start_date}|{city.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


def map_category(tags: list) -> str:
    """Map Eventbrite tags to our event categories.
    Allowed DB values: Comedy, Community, Competition, Cultural, Dance,
    Festival, Food, Music, Religious, Sports, Entertainment, Education, Other
    """
    tag_names = {t.get("display_name", "").lower() for t in (tags or [])}
    if tag_names & {"music", "concert", "performing arts", "dj / dance"}:
        return "Music"
    if tag_names & {"food & drink", "food"}:
        return "Food"
    if tag_names & {"community & culture", "community", "historic"}:
        return "Community"
    if tag_names & {"religion & spirituality", "spirituality"}:
        return "Religious"
    if tag_names & {"health & wellness", "yoga", "fitness"}:
        return "Cultural"
    if tag_names & {"business", "professional", "networking", "career"}:
        return "Community"
    if tag_names & {"family & education", "family", "kids", "education"}:
        return "Education"
    if tag_names & {"arts", "film & media", "visual arts"}:
        return "Entertainment"
    if tag_names & {"science & technology", "tech"}:
        return "Education"
    if tag_names & {"sports & fitness", "sports"}:
        return "Sports"
    if tag_names & {"charity & causes", "charity"}:
        return "Community"
    if tag_names & {"comedy"}:
        return "Comedy"
    if tag_names & {"dance"}:
        return "Dance"
    if tag_names & {"festival"}:
        return "Festival"
    return "Cultural"  # default for Indian events


def parse_event(e: dict, city_display: str, state_upper: str) -> dict | None:
    """Convert an Eventbrite event object to our events table row."""
    name = e.get("name", "").strip()
    if not name:
        return None

    summary = e.get("summary", "") or ""
    event_id = str(e.get("id", ""))

    # Relevance check
    if not is_relevant(name, summary):
        return None

    start_date = e.get("start_date", "")
    start_time = e.get("start_time", "")
    end_date = e.get("end_date", "")
    end_time_val = e.get("end_time", "")

    # Venue
    venue = e.get("primary_venue") or {}
    venue_name = venue.get("name", "")
    addr = venue.get("address", {}) or {}
    event_city = addr.get("city", city_display)
    event_state = addr.get("region", state_upper)
    lat = addr.get("latitude")
    lng = addr.get("longitude")

    # Image
    image = e.get("image") or {}
    image_url = ""
    if image:
        # Prefer medium size
        sizes = image.get("image_sizes", {})
        image_url = sizes.get("medium") or sizes.get("small") or image.get("url", "")

    # URL
    url = e.get("url", "")

    # Price
    is_free = e.get("is_free")
    price_range = "Free" if is_free else ""

    # Organizer
    organizer = ""
    primary_org = e.get("primary_organizer") or {}
    if primary_org:
        organizer = primary_org.get("name", "")

    slug = make_slug(name, event_city, start_date, event_id)
    fp = content_fingerprint(name, start_date, event_city)
    category = map_category(e.get("tags", []))

    row = {
        "title": name[:300],
        "date": start_date or None,
        "time": start_time or None,
        "end_date": end_date or None,
        "venue_name": venue_name[:300] if venue_name else None,
        "city": event_city,
        "state": event_state,
        "category": category,
        "description": summary[:2000] if summary else None,
        "image_url": image_url or None,
        "ticket_url": url or None,
        "source": "eventbrite",
        "source_id": event_id,
        "price_range": price_range or None,
        "organizer": organizer[:300] if organizer else None,
        "slug": slug,
        "latitude": float(lat) if lat else None,
        "longitude": float(lng) if lng else None,
        "content_fingerprint": fp,
    }
    return row


def scrape_city(city: dict, existing_fps: set) -> list:
    """Scrape all Indian/desi/bollywood events for one city."""
    city_slug = city["slug"]
    state = city["state"]
    state_upper = STATE_MAP.get(state, state.upper())
    city_display = city["display"]

    seen_ids = set()  # Dedupe across search terms
    all_events = []

    for term in SEARCH_TERMS:
        # Fetch page 1
        results, total, page_count = fetch_page(city_slug, state, term)
        if not results:
            time.sleep(0.5)
            continue

        for e in results:
            eid = str(e.get("id", ""))
            if eid in seen_ids:
                continue
            seen_ids.add(eid)
            row = parse_event(e, city_display, state_upper)
            if row and row["content_fingerprint"] not in existing_fps:
                all_events.append(row)

        # Fetch remaining pages (max 5 pages = 100 events per term, plenty)
        for pg in range(2, min(page_count + 1, 6)):
            time.sleep(1.0)
            results, _, _ = fetch_page(city_slug, state, term, page=pg)
            for e in results:
                eid = str(e.get("id", ""))
                if eid in seen_ids:
                    continue
                seen_ids.add(eid)
                row = parse_event(e, city_display, state_upper)
                if row and row["content_fingerprint"] not in existing_fps:
                    all_events.append(row)

        time.sleep(1.0)  # Rate limit between terms

    return all_events


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape Eventbrite for Indian diaspora events")
    parser.add_argument("--day", type=int, default=None, help="Rotation day (0-6)")
    parser.add_argument("--all", action="store_true", help="Scrape all 50 cities")
    parser.add_argument("--city", type=str, default=None, help="Single city slug to test")
    parser.add_argument("--dry-run", action="store_true", help="Don't insert into DB")
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)

    # Determine which cities to scrape
    if args.city:
        cities = [c for c in CITIES if c["slug"] == args.city]
        if not cities:
            print(f"ERROR: City '{args.city}' not found")
            sys.exit(1)
    elif args.all:
        cities = CITIES
    else:
        # Daily rotation: 7-8 cities per day
        rotation_day = args.day if args.day is not None else date.today().toordinal() % 7
        chunk_size = len(CITIES) // 7
        start_idx = rotation_day * chunk_size
        end_idx = start_idx + chunk_size if rotation_day < 6 else len(CITIES)
        cities = CITIES[start_idx:end_idx]
        print(f"Rotation day {rotation_day}: cities {start_idx}-{end_idx-1} ({len(cities)} cities)")

    # Fetch existing fingerprints to avoid duplicates
    existing_fps = get_existing_fingerprints()
    print(f"Existing Eventbrite fingerprints: {len(existing_fps)}")

    total_found = 0
    total_new = 0
    total_inserted = 0
    errors = []

    for city in cities:
        try:
            events = scrape_city(city, existing_fps)
            total_found_city = len(events)
            total_found += total_found_city

            if events and not args.dry_run:
                # Insert in batches of 20
                for i in range(0, len(events), 20):
                    batch = events[i : i + 20]
                    ok = supabase_post("events", batch)
                    if ok:
                        total_inserted += len(batch)
                        # Add fingerprints to avoid cross-city dupes
                        for ev in batch:
                            existing_fps.add(ev["content_fingerprint"])
                    else:
                        errors.append(f"{city['display']}: batch insert failed")

                total_new += total_found_city
                print(f"  ✅ {city['display']}: {total_found_city} new events inserted")
            elif events and args.dry_run:
                total_new += total_found_city
                print(f"  🔍 {city['display']}: {total_found_city} new events (dry-run)")
                for ev in events[:3]:
                    print(f"      → {ev['title'][:50]} | {ev['date']} | {ev['city']}")
            else:
                print(f"  ⬚ {city['display']}: no new events")

            time.sleep(1.5)  # Rate limit between cities

        except Exception as ex:
            errors.append(f"{city['display']}: {ex}")
            print(f"  ❌ {city['display']}: {ex}")
            traceback.print_exc()

    # Summary
    print(f"\n{'='*50}")
    print(f"Eventbrite scrape complete")
    print(f"  Cities scraped: {len(cities)}")
    print(f"  New events found: {total_new}")
    print(f"  Events inserted: {total_inserted}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors:
            print(f"    - {e}")


if __name__ == "__main__":
    main()
