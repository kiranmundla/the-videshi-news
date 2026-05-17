#!/usr/bin/env python3
"""
events-ingest.py — Scrape Indian diaspora events from Eventbrite + Ticketmaster
and upsert them into the Supabase `events` table.

Usage:
    python3 events-ingest.py                # Full scrape of all keywords × cities
    python3 events-ingest.py --source eb    # Eventbrite only
    python3 events-ingest.py --source tm    # Ticketmaster only
    python3 events-ingest.py --city "ca--san-jose"  # Single city (Eventbrite format)
"""

import json
import os
import re
import subprocess
import sys
import time
import hashlib
import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

EVENTBRITE_KEYWORDS = [
    "indian", "bollywood", "telugu", "tamil", "garba", "diwali", "desi",
    "hindi", "punjabi", "bhangra", "cricket", "biryani", "carnatic",
    "bharatanatyam", "kathak", "holi", "navratri", "pongal", "onam",
    "sikh", "gurdwara", "eid", "iftar", "mehndi", "sangeet",
]

TICKETMASTER_KEYWORDS = [
    "Diljit", "Bollywood", "Garba", "Indian", "Desi", "Bhangra",
    "Telugu", "Punjabi", "Navratri",
]

# Eventbrite URL format: /d/{state}--{city}/{keyword}/
CITIES = [
    {"eb": "ca--san-francisco",  "tm_state": "CA", "display": "San Francisco",  "state": "CA"},
    {"eb": "ca--san-jose",       "tm_state": "CA", "display": "San Jose",       "state": "CA"},
    {"eb": "ny--new-york",       "tm_state": "NY", "display": "New York",       "state": "NY"},
    {"eb": "nj--edison",         "tm_state": "NJ", "display": "Edison",         "state": "NJ"},
    {"eb": "tx--dallas",         "tm_state": "TX", "display": "Dallas",         "state": "TX"},
    {"eb": "tx--houston",        "tm_state": "TX", "display": "Houston",        "state": "TX"},
    {"eb": "il--chicago",        "tm_state": "IL", "display": "Chicago",        "state": "IL"},
    {"eb": "wa--seattle",        "tm_state": "WA", "display": "Seattle",        "state": "WA"},
    {"eb": "ga--atlanta",        "tm_state": "GA", "display": "Atlanta",        "state": "GA"},
    {"eb": "dc--washington",     "tm_state": "DC", "display": "Washington",     "state": "DC"},
    {"eb": "ca--los-angeles",    "tm_state": "CA", "display": "Los Angeles",    "state": "CA"},
    {"eb": "mi--detroit",        "tm_state": "MI", "display": "Detroit",        "state": "MI"},
    {"eb": "nc--charlotte",      "tm_state": "NC", "display": "Charlotte",      "state": "NC"},
    {"eb": "pa--philadelphia",   "tm_state": "PA", "display": "Philadelphia",   "state": "PA"},
]

# Category auto-detection keywords
CATEGORY_RULES = [
    ("Music",     ["concert", "music", "live band", "singer", "dj ", "dj night", "bollywood night", "bhangra night", "carnatic", "classical music", "ghazal", "qawwali"]),
    ("Dance",     ["dance", "bharatanatyam", "kathak", "garba", "dandiya", "bhangra class", "salsa"]),
    ("Food",      ["food", "cook", "biryani", "culinary", "taste", "dinner", "brunch", "lunch", "feast", "iftar", "potluck"]),
    ("Comedy",    ["comedy", "standup", "stand-up", "comedian", "laugh", "open mic"]),
    ("Sports",    ["cricket", "kabaddi", "badminton", "sport", "tournament", "marathon", "run ", "5k ", "10k "]),
    ("Religious", ["temple", "gurdwara", "mosque", "church", "puja", "pooja", "havan", "kirtan", "bhajan", "aarti", "satsang", "prayer", "kalyanam", "ram navami"]),
    ("Festival",  ["diwali", "holi", "navratri", "pongal", "onam", "eid", "vaisakhi", "baisakhi", "ugadi", "makar sankranti", "lohri", "festival", "mela", "dussehra", "ganesh"]),
    ("Community", ["convention", "conference", "meetup", "networking", "association", "tana", "ata ", "tta ", "nata", "mata", "diaspora", "community", "gala", "fundraiser", "charity"]),
    ("Cultural",  ["cultural", "art", "exhibit", "gallery", "heritage", "history", "lecture", "seminar", "workshop", "yoga", "meditation", "ayurveda"]),
]

# False-positive filters: event titles matching these regexes are likely NOT Indian events
FALSE_POSITIVE_PATTERNS = [
    r"(?i)indian wells",           # Tennis tournament
    r"(?i)cleveland indians?(?:\s|$)",
    r"(?i)indian motorcycle",
    r"(?i)native\s+(american\s+)?indian",
    r"(?i)candy crafting at cricket",  # Saw this in Ticketmaster results
    r"(?i)west indian day parade",     # Caribbean, not South Asian
]

# ---------------------------------------------------------------------------
# Supabase
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def categorize(title: str, description: str = "") -> str:
    """Auto-detect event category from title/description."""
    text = f"{title} {description}".lower()
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return cat
    return "Other"


def is_false_positive(title: str) -> bool:
    """Check if event title is a false positive (not actually an Indian event)."""
    for pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(pattern, title):
            return True
    return False


def make_source_id(source: str, raw_id: str) -> str:
    """Create a stable source_id."""
    return f"{source}_{raw_id}"


# ---------------------------------------------------------------------------
# Eventbrite scraper
# ---------------------------------------------------------------------------

def scrape_eventbrite(city_config: dict, keyword: str) -> list:
    """Scrape Eventbrite search page for a city+keyword combo."""
    eb_city = city_config["eb"]
    url = f"https://www.eventbrite.com/d/{eb_city}/{quote(keyword)}/?page=1"

    try:
        resp = requests.get(url, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=15)
        if resp.status_code != 200:
            return []
    except Exception as e:
        print(f"  ⚠ Eventbrite request failed for {eb_city}/{keyword}: {e}")
        return []

    # Extract __SERVER_DATA__ JSON
    match = re.search(r'window\.__SERVER_DATA__\s*=\s*(\{.*?\});', resp.text, re.DOTALL)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    results = data.get("search_data", {}).get("events", {}).get("results", [])
    events = []

    for evt in results:
        title = evt.get("name", "").strip()
        if not title or is_false_positive(title):
            continue

        # Extract venue info
        venue = evt.get("primary_venue", {}) or {}
        venue_name = venue.get("name", "")
        address = venue.get("address", {}) or {}
        city = address.get("city", city_config["display"])
        state = address.get("region", city_config["state"])
        # Normalize state to 2-letter code
        if state and len(state) > 2:
            state = city_config["state"]

        # Date/time
        start_date = evt.get("start_date", "")
        start_time = evt.get("start_time", "")
        end_date = evt.get("end_date", "")

        # Format time nicely
        time_display = ""
        if start_time:
            try:
                t = datetime.strptime(start_time, "%H:%M")
                time_display = t.strftime("%-I:%M %p")
            except:
                time_display = start_time

        # Image
        image = evt.get("image", {}) or {}
        image_url = image.get("url", "")

        # Organizer
        org = evt.get("primary_organizer", {}) or {}
        organizer = org.get("name", "")

        # Ticket URL
        ticket_url = evt.get("tickets_url", "") or evt.get("url", "")

        # Price
        price = ""
        ticket_avail = evt.get("ticket_availability", {}) or {}
        if ticket_avail.get("is_free"):
            price = "Free"
        elif ticket_avail.get("minimum_ticket_price", {}).get("display"):
            min_p = ticket_avail["minimum_ticket_price"]["display"]
            max_p = (ticket_avail.get("maximum_ticket_price", {}) or {}).get("display", "")
            if max_p and max_p != min_p:
                price = f"{min_p}–{max_p}"
            else:
                price = f"From {min_p}"

        # Summary/description
        description = evt.get("summary", "") or ""

        # Event ID from Eventbrite
        eb_id = str(evt.get("id", ""))
        if not eb_id:
            eb_id = hashlib.md5(f"{title}_{start_date}_{city}".encode()).hexdigest()[:16]

        events.append({
            "title": title,
            "date": start_date,
            "time": time_display,
            "end_date": end_date if end_date != start_date else None,
            "venue_name": venue_name,
            "city": city,
            "state": state[:2] if state else None,
            "category": categorize(title, description),
            "description": description[:500] if description else None,
            "image_url": image_url or None,
            "ticket_url": ticket_url or None,
            "source": "eventbrite",
            "source_id": f"eb_{eb_id}",
            "price_range": price or None,
            "organizer": organizer or None,
        })

    return events


# ---------------------------------------------------------------------------
# Ticketmaster fetcher
# ---------------------------------------------------------------------------

def fetch_ticketmaster(keyword: str, state_code: str) -> list:
    """Use ticketmaster CLI to search events."""
    try:
        result = subprocess.run(
            ["ticketmaster", "search-events",
             "--keyword", keyword,
             "--state-code", state_code,
             "--size", "20",
             "--sort", "date,asc"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"  ⚠ Ticketmaster failed for {keyword}/{state_code}: {e}")
        return []

    events = []
    for evt in data.get("events", []):
        title = evt.get("name", "").strip()
        if not title or is_false_positive(title):
            continue

        city = evt.get("city", "")
        state = evt.get("state", state_code)
        date = evt.get("date", "")
        tm_time = evt.get("time", "")
        venue = evt.get("venue", "")
        ticket_url = evt.get("url", "")
        price = evt.get("price_range", "")
        tm_id = evt.get("id", "") or evt.get("hex_id", "")

        if not tm_id:
            tm_id = hashlib.md5(f"{title}_{date}_{city}".encode()).hexdigest()[:16]

        # Format time
        time_display = ""
        if tm_time:
            try:
                t = datetime.strptime(tm_time, "%H:%M:%S")
                time_display = t.strftime("%-I:%M %p")
            except:
                time_display = tm_time

        events.append({
            "title": title,
            "date": date,
            "time": time_display,
            "end_date": None,
            "venue_name": venue,
            "city": city,
            "state": state[:2] if state else None,
            "category": categorize(title),
            "description": None,
            "image_url": None,
            "ticket_url": ticket_url or None,
            "source": "ticketmaster",
            "source_id": f"tm_{tm_id}",
            "price_range": price or None,
            "organizer": None,
        })

    return events


# ---------------------------------------------------------------------------
# Supabase upsert
# ---------------------------------------------------------------------------

def upsert_events(events: list) -> int:
    """Upsert events to Supabase. Returns count of upserted rows."""
    if not events:
        return 0

    # Deduplicate by source_id
    seen = set()
    unique = []
    for e in events:
        sid = e["source_id"]
        if sid not in seen:
            seen.add(sid)
            # Filter out past events
            try:
                event_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
                if event_date < datetime.now().date():
                    continue
            except:
                pass
            # Add updated_at
            e["updated_at"] = datetime.now(timezone.utc).isoformat()
            unique.append(e)

    if not unique:
        return 0

    # Batch upsert (Supabase limit is ~1000 rows)
    batch_size = 100
    total = 0
    for i in range(0, len(unique), batch_size):
        batch = unique[i:i + batch_size]
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
                print(f"  ⚠ Upsert failed ({resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            print(f"  ⚠ Upsert error: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ingest Indian diaspora events")
    parser.add_argument("--source", choices=["eb", "tm", "all"], default="all",
                        help="Source to scrape: eb=Eventbrite, tm=Ticketmaster, all=both")
    parser.add_argument("--city", type=str, default=None,
                        help="Single city to scrape (Eventbrite format, e.g. 'ca--san-jose')")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print events without upserting")
    args = parser.parse_args()

    cities = CITIES
    if args.city:
        cities = [c for c in CITIES if c["eb"] == args.city]
        if not cities:
            print(f"Unknown city: {args.city}")
            sys.exit(1)

    all_events = []

    # === Eventbrite ===
    if args.source in ("eb", "all"):
        print(f"🔍 Scraping Eventbrite ({len(cities)} cities × {len(EVENTBRITE_KEYWORDS)} keywords)...")
        eb_count = 0
        for city in cities:
            for kw in EVENTBRITE_KEYWORDS:
                events = scrape_eventbrite(city, kw)
                if events:
                    print(f"  ✓ {city['eb']}/{kw}: {len(events)} events")
                    all_events.extend(events)
                    eb_count += len(events)
                time.sleep(2)  # Rate limit
        print(f"  Eventbrite total (raw): {eb_count}")

    # === Ticketmaster ===
    if args.source in ("tm", "all"):
        print(f"\n🎫 Fetching Ticketmaster...")
        tm_count = 0
        seen_states = set()
        for city in cities:
            st = city["tm_state"]
            if st in seen_states:
                continue
            seen_states.add(st)
            for kw in TICKETMASTER_KEYWORDS:
                events = fetch_ticketmaster(kw, st)
                if events:
                    print(f"  ✓ {kw}/{st}: {len(events)} events")
                    all_events.extend(events)
                    tm_count += len(events)
                time.sleep(0.5)
        print(f"  Ticketmaster total (raw): {tm_count}")

    # Deduplicate
    seen = {}
    deduped = []
    for e in all_events:
        key = e["source_id"]
        if key not in seen:
            seen[key] = True
            deduped.append(e)

    print(f"\n📊 Total unique events: {len(deduped)}")

    if args.dry_run:
        for e in deduped[:20]:
            print(f"  {e['date']} | {e['title'][:55]} | {e['city']}, {e['state']} | {e['category']} | {e['source']}")
        if len(deduped) > 20:
            print(f"  ... and {len(deduped) - 20} more")
        return

    # Upsert to Supabase
    print("\n💾 Upserting to Supabase...")
    count = upsert_events(deduped)
    print(f"✅ Done! Upserted {count} events.")


if __name__ == "__main__":
    main()
