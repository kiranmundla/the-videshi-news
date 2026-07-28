#!/usr/bin/env python3
"""
Eventbrite event scraper for The Videshi.
Scrapes Eventbrite search results via __SERVER_DATA__ embedded JSON.
Searches by US state (all 50 + DC) for full national coverage.

Usage:
  python3 scrape-eventbrite.py              # Today's rotation (~8 states)
  python3 scrape-eventbrite.py --day 0      # Explicit rotation day
  python3 scrape-eventbrite.py --all        # All 51 states (full sweep)
  python3 scrape-eventbrite.py --state texas # Single state test
  python3 scrape-eventbrite.py --dry-run    # Don't insert into DB
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
    url = f"{SUPABASE_URL}/rest/v1/{table}?on_conflict=source,source_id"
    payload = json.dumps(rows)
    cmd = [
        "curl", "-s", "-w", "\nHTTP_CODE: %{http_code}",
        "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal,resolution=ignore-duplicates",
        "-d", payload,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    out = r.stdout.strip()
    # Extract HTTP status code from the tail "HTTP_CODE: NNN"
    code = ""
    if "HTTP_CODE: " in out:
        code = out.split("HTTP_CODE: ")[-1].strip()
    if code not in ("200", "201"):
        # Log the response body (everything before the HTTP_CODE line)
        body = out.split("\nHTTP_CODE:")[0].strip() if "\nHTTP_CODE:" in out else out
        print(f"    ⚠ Insert returned HTTP {code}: {body[:200]}", flush=True)
    return code in ("200", "201")

def get_existing_fingerprints():
    """Fetch ALL content_fingerprints from events table (cross-source)."""
    from event_dedup import get_all_fingerprints
    return get_all_fingerprints()

# ── 50 US states + DC ─────────────────────────────────────────────────────
STATES = [
    {"slug": "alabama", "abbr": "AL"},
    {"slug": "alaska", "abbr": "AK"},
    {"slug": "arizona", "abbr": "AZ"},
    {"slug": "arkansas", "abbr": "AR"},
    {"slug": "california", "abbr": "CA"},
    {"slug": "colorado", "abbr": "CO"},
    {"slug": "connecticut", "abbr": "CT"},
    {"slug": "delaware", "abbr": "DE"},
    {"slug": "florida", "abbr": "FL"},
    {"slug": "georgia", "abbr": "GA"},
    {"slug": "hawaii", "abbr": "HI"},
    {"slug": "idaho", "abbr": "ID"},
    {"slug": "illinois", "abbr": "IL"},
    {"slug": "indiana", "abbr": "IN"},
    {"slug": "iowa", "abbr": "IA"},
    {"slug": "kansas", "abbr": "KS"},
    {"slug": "kentucky", "abbr": "KY"},
    {"slug": "louisiana", "abbr": "LA"},
    {"slug": "maine", "abbr": "ME"},
    {"slug": "maryland", "abbr": "MD"},
    {"slug": "massachusetts", "abbr": "MA"},
    {"slug": "michigan", "abbr": "MI"},
    {"slug": "minnesota", "abbr": "MN"},
    {"slug": "mississippi", "abbr": "MS"},
    {"slug": "missouri", "abbr": "MO"},
    {"slug": "montana", "abbr": "MT"},
    {"slug": "nebraska", "abbr": "NE"},
    {"slug": "nevada", "abbr": "NV"},
    {"slug": "new-hampshire", "abbr": "NH"},
    {"slug": "new-jersey", "abbr": "NJ"},
    {"slug": "new-mexico", "abbr": "NM"},
    {"slug": "new-york", "abbr": "NY"},
    {"slug": "north-carolina", "abbr": "NC"},
    {"slug": "north-dakota", "abbr": "ND"},
    {"slug": "ohio", "abbr": "OH"},
    {"slug": "oklahoma", "abbr": "OK"},
    {"slug": "oregon", "abbr": "OR"},
    {"slug": "pennsylvania", "abbr": "PA"},
    {"slug": "rhode-island", "abbr": "RI"},
    {"slug": "south-carolina", "abbr": "SC"},
    {"slug": "south-dakota", "abbr": "SD"},
    {"slug": "tennessee", "abbr": "TN"},
    {"slug": "texas", "abbr": "TX"},
    {"slug": "utah", "abbr": "UT"},
    {"slug": "vermont", "abbr": "VT"},
    {"slug": "virginia", "abbr": "VA"},
    {"slug": "washington", "abbr": "WA"},
    {"slug": "west-virginia", "abbr": "WV"},
    {"slug": "wisconsin", "abbr": "WI"},
    {"slug": "wyoming", "abbr": "WY"},
    {"slug": "district-of-columbia", "abbr": "DC"},
]

# Search terms — "indian" is primary, "desi" and "bollywood" catch party/cultural events
SEARCH_TERMS = ["indian", "desi", "bollywood"]

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


def fetch_page(state_slug: str, term: str, page: int = 1) -> tuple:
    """Fetch one page of Eventbrite search results for a state.
    Returns (events_list, total_count, page_count).
    """
    import subprocess

    # URL term mapping
    if term == "indian":
        url_term = "indian-events"
    elif term == "desi":
        url_term = "desi-events"
    elif term == "bollywood":
        url_term = "bollywood"
    else:
        url_term = f"{term}-events"

    url = f"https://www.eventbrite.com/d/united-states--{state_slug}/{url_term}/"
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


from event_dedup import content_fingerprint


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


def parse_event(e: dict, state_abbr: str) -> dict | None:
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
    if not start_date:
        return None  # date is NOT NULL in DB; skip dateless events
    start_time = e.get("start_time", "")
    end_date = e.get("end_date", "")

    # Venue
    venue = e.get("primary_venue") or {}
    venue_name = venue.get("name", "")
    addr = venue.get("address", {}) or {}
    address_1 = addr.get("address_1", "")
    # Include street address in venue_name: "Santana Row, 377 Santana Row"
    if address_1 and address_1 not in venue_name:
        venue_name = f"{venue_name}, {address_1}" if venue_name else address_1
    event_city = addr.get("city", "")
    event_state = addr.get("region", state_abbr)
    lat = addr.get("latitude")
    lng = addr.get("longitude")

    # Image
    image = e.get("image") or {}
    image_url = ""
    if image:
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

    slug = make_slug(name, event_city or "unknown", start_date, event_id)
    fp = content_fingerprint(name, start_date, event_city or "unknown")
    category = map_category(e.get("tags", []))

    # Full description from search data (often empty; backfill script enriches later)
    full_desc = (e.get("full_description") or "").strip()

    row = {
        "title": name[:300],
        "date": start_date or None,
        "time": start_time or None,
        "end_date": end_date or None,
        "venue_name": venue_name[:300] if venue_name else None,
        "city": event_city or None,
        "state": event_state or None,
        "category": category,
        "description": summary[:2000] if summary else None,
        "long_description": full_desc[:5000] if full_desc else None,
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


def scrape_state(state: dict, existing_fps: set) -> list:
    """Scrape all Indian/desi/bollywood events for one US state."""
    state_slug = state["slug"]
    state_abbr = state["abbr"]

    seen_ids = set()  # Dedupe across search terms
    all_events = []

    for term in SEARCH_TERMS:
        # Fetch page 1
        results, total, page_count = fetch_page(state_slug, term)
        if not results:
            time.sleep(0.5)
            continue

        for e in results:
            eid = str(e.get("id", ""))
            if eid in seen_ids:
                continue
            seen_ids.add(eid)
            row = parse_event(e, state_abbr)
            if row and row["content_fingerprint"] not in existing_fps:
                all_events.append(row)

        # Fetch remaining pages (max 5 pages = 100 events per term)
        for pg in range(2, min(page_count + 1, 6)):
            time.sleep(1.0)
            results, _, _ = fetch_page(state_slug, term, page=pg)
            for e in results:
                eid = str(e.get("id", ""))
                if eid in seen_ids:
                    continue
                seen_ids.add(eid)
                row = parse_event(e, state_abbr)
                if row and row["content_fingerprint"] not in existing_fps:
                    all_events.append(row)

        time.sleep(1.0)  # Rate limit between terms

    return all_events


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape Eventbrite for Indian diaspora events (state-level)")
    parser.add_argument("--day", type=int, default=None, help="Rotation day (0-6)")
    parser.add_argument("--all", action="store_true", help="Scrape all 51 states")
    parser.add_argument("--state", type=str, default=None, help="Single state slug (e.g. texas, new-york)")
    parser.add_argument("--dry-run", action="store_true", help="Don't insert into DB")
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)

    # Determine which states to scrape
    if args.state:
        states = [s for s in STATES if s["slug"] == args.state]
        if not states:
            print(f"ERROR: State '{args.state}' not found. Available: {', '.join(s['slug'] for s in STATES)}")
            sys.exit(1)
    elif args.all:
        states = STATES
    else:
        # Daily rotation: ~8 states per day, full cycle in 7 days
        rotation_day = args.day if args.day is not None else date.today().toordinal() % 7
        chunk_size = len(STATES) // 7  # 51 // 7 = 7
        start_idx = rotation_day * chunk_size
        end_idx = start_idx + chunk_size if rotation_day < 6 else len(STATES)
        states = STATES[start_idx:end_idx]
        print(f"Rotation day {rotation_day}: states {start_idx}-{end_idx-1} ({len(states)} states)")

    # Fetch existing fingerprints to avoid duplicates
    existing_fps = get_existing_fingerprints()
    print(f"Existing Eventbrite fingerprints: {len(existing_fps)}")

    total_found = 0
    total_new = 0
    total_inserted = 0
    errors = []

    for state in states:
        try:
            events = scrape_state(state, existing_fps)
            total_found_state = len(events)
            total_found += total_found_state

            if events and not args.dry_run:
                # Insert in batches of 20
                for i in range(0, len(events), 20):
                    batch = events[i : i + 20]
                    ok = supabase_post("events", batch)
                    if ok:
                        total_inserted += len(batch)
                        # Add fingerprints to avoid cross-state dupes
                        for ev in batch:
                            existing_fps.add(ev["content_fingerprint"])
                    else:
                        errors.append(f"{state['abbr']}: batch insert failed")

                total_new += total_found_state
                print(f"  ✅ {state['abbr']} ({state['slug']}): {total_found_state} new events inserted")
            elif events and args.dry_run:
                total_new += total_found_state
                print(f"  🔍 {state['abbr']} ({state['slug']}): {total_found_state} new events (dry-run)")
                for ev in events[:3]:
                    print(f"      → {ev['title'][:50]} | {ev['date']} | {ev['city']}, {ev['state']}")
            else:
                print(f"  ⬚ {state['abbr']} ({state['slug']}): no new events")

            time.sleep(1.5)  # Rate limit between states

        except Exception as ex:
            errors.append(f"{state['abbr']}: {ex}")
            print(f"  ❌ {state['abbr']} ({state['slug']}): {ex}")
            traceback.print_exc()

    # Summary
    print(f"\n{'='*50}")
    print(f"Eventbrite scrape complete")
    print(f"  States scraped: {len(states)}")
    print(f"  New events found: {total_new}")
    print(f"  Events inserted: {total_inserted}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors:
            print(f"    - {e}")


if __name__ == "__main__":
    main()
