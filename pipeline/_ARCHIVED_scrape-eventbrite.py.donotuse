#!/usr/bin/env python3
"""
scrape-eventbrite.py — Scrape Indian/desi events from Eventbrite
and upsert them into the Supabase `events` table.

Approach: Eventbrite search pages embed structured JSON in window.__SERVER_DATA__
with full event details including geo coordinates, venue, dates, and descriptions.

Usage:
    python3 pipeline/scrape-eventbrite.py              # Full scrape (today's day slice)
    python3 pipeline/scrape-eventbrite.py --dry-run     # Print events without inserting
    python3 pipeline/scrape-eventbrite.py --city houston # Single city
    python3 pipeline/scrape-eventbrite.py --day 0       # Specific day (0=Mon..6=Sun)
"""

import json
import hashlib
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
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

USER_AGENT = "Mozilla/5.0 (compatible; TheVideshi/1.0; +https://thevideshi.com)"

KEYWORDS = [
    "indian", "bollywood", "desi", "tamil", "telugu", "punjabi",
    "hindi", "gujarati", "south-asian", "bengali", "garba", "bhangra",
    "tech-meetup-indian", "startup-desi", "networking-south-asian",
    "professional-indian", "yoga",
]

# 50 cities — same as other scrapers
CITIES = [
    {"eb": "san-francisco", "display": "San Francisco", "state": "CA"},
    {"eb": "san-jose", "display": "San Jose", "state": "CA"},
    {"eb": "new-york", "display": "New York", "state": "NY"},
    {"eb": "edison--nj", "display": "Edison", "state": "NJ"},
    {"eb": "chicago", "display": "Chicago", "state": "IL"},
    {"eb": "houston", "display": "Houston", "state": "TX"},
    {"eb": "dallas", "display": "Dallas", "state": "TX"},
    {"eb": "los-angeles", "display": "Los Angeles", "state": "CA"},
    {"eb": "seattle", "display": "Seattle", "state": "WA"},
    {"eb": "washington", "display": "Washington", "state": "DC"},
    {"eb": "boston", "display": "Boston", "state": "MA"},
    {"eb": "atlanta", "display": "Atlanta", "state": "GA"},
    {"eb": "philadelphia", "display": "Philadelphia", "state": "PA"},
    {"eb": "detroit", "display": "Detroit", "state": "MI"},
    {"eb": "austin", "display": "Austin", "state": "TX"},
    {"eb": "miami", "display": "Miami", "state": "FL"},
    {"eb": "phoenix", "display": "Phoenix", "state": "AZ"},
    {"eb": "denver", "display": "Denver", "state": "CO"},
    {"eb": "san-diego", "display": "San Diego", "state": "CA"},
    {"eb": "portland", "display": "Portland", "state": "OR"},
    {"eb": "minneapolis", "display": "Minneapolis", "state": "MN"},
    {"eb": "tampa", "display": "Tampa", "state": "FL"},
    {"eb": "charlotte", "display": "Charlotte", "state": "NC"},
    {"eb": "raleigh", "display": "Raleigh", "state": "NC"},
    {"eb": "columbus", "display": "Columbus", "state": "OH"},
    {"eb": "indianapolis", "display": "Indianapolis", "state": "IN"},
    {"eb": "nashville", "display": "Nashville", "state": "TN"},
    {"eb": "sacramento", "display": "Sacramento", "state": "CA"},
    {"eb": "irvine", "display": "Irvine", "state": "CA"},
    {"eb": "plano", "display": "Plano", "state": "TX"},
    {"eb": "fremont", "display": "Fremont", "state": "CA"},
    {"eb": "sunnyvale", "display": "Sunnyvale", "state": "CA"},
    {"eb": "cary--nc", "display": "Cary", "state": "NC"},
    {"eb": "durham", "display": "Durham", "state": "NC"},
    {"eb": "pittsburgh", "display": "Pittsburgh", "state": "PA"},
    {"eb": "orlando", "display": "Orlando", "state": "FL"},
    {"eb": "baltimore", "display": "Baltimore", "state": "MD"},
    {"eb": "stamford", "display": "Stamford", "state": "CT"},
    {"eb": "ann-arbor", "display": "Ann Arbor", "state": "MI"},
    {"eb": "san-antonio", "display": "San Antonio", "state": "TX"},
    {"eb": "salt-lake-city", "display": "Salt Lake City", "state": "UT"},
    {"eb": "cincinnati", "display": "Cincinnati", "state": "OH"},
    {"eb": "cleveland", "display": "Cleveland", "state": "OH"},
    {"eb": "kansas-city", "display": "Kansas City", "state": "MO"},
    {"eb": "st-louis", "display": "St Louis", "state": "MO"},
    {"eb": "las-vegas", "display": "Las Vegas", "state": "NV"},
    {"eb": "richmond", "display": "Richmond", "state": "VA"},
    {"eb": "jacksonville", "display": "Jacksonville", "state": "FL"},
    {"eb": "hartford", "display": "Hartford", "state": "CT"},
    {"eb": "milwaukee", "display": "Milwaukee", "state": "WI"},
]

CATEGORY_RULES = [
    ("Religious",   ["temple", "gurdwara", "mosque", "puja", "pooja", "havan",
                     "kirtan", "bhajan", "aarti", "satsang", "prayer",
                     "yoga", "meditation", "sound bath", "sound healing",
                     "pranayama", "dhyana", "mantra", "bhakti", "vedic",
                     "ayurveda", "kundalini", "reiki", "chakra", "inner engineering",
                     "sadhguru", "devotional", "sacred", "chanting", "sufi",
                     "mindfulness", "spiritual"]),
    ("Festival",    ["diwali", "holi", "navratri", "pongal", "onam", "eid", "vaisakhi",
                     "festival", "mela", "dussehra", "ganesh"]),
    ("Competition", ["spelling bee", "math olympiad", "chess tournament",
                     "hackathon", "competition", "contest", "tournament"]),
    ("Entertainment", ["bollywood night", "bollywood festive", "bollywood singing",
                       "bollywood party", "bollywood dance party",
                       "comedy", "stand-up", "standup", "open mic",
                       "movie night", "film screening", "karaoke"]),
    ("Dance",       ["bollywood dance", "garba", "dandiya", "bhangra",
                     "kathak", "bharatanatyam", "kuchipudi", "salsa",
                     "dance class", "dance workshop"]),
    ("Music",       ["concert", "live music", "carnatic", "hindustani",
                     "classical music", "raga", "tabla", "sitar", "veena",
                     "music festival", "dj night", "sufi night"]),
    ("Food",        ["food festival", "cooking class", "biryani", "curry",
                     "chai", "food tasting", "potluck", "dinner"]),
    ("Education",   ["workshop", "seminar", "lecture", "webinar",
                     "class", "course", "training", "conference"]),
    ("Cultural",    ["cultural", "heritage", "rangoli", "mehndi", "sangeet",
                     "art exhibition", "theater", "drama"]),
    ("Community",   []),
]

RELEVANCE_KEYWORDS = [
    "indian", "india", "bollywood", "telugu", "tamil", "hindi", "punjabi",
    "bengali", "gujarati", "marathi", "malayalam", "kannada", "desi",
    "south asian", "garba", "dandiya", "bhangra", "diwali", "holi",
    "navratri", "pongal", "onam", "eid", "iftar", "sikh", "gurdwara",
    "carnatic", "hindustani", "bharatanatyam", "kathak",
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
    r"(?i)indian island",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def categorize(title, description=""):
    text = f"{title} {description}".lower()
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return cat
    return "Community"


def is_relevant(title, description=""):
    text = f"{title} {description}".lower()
    for pat in FALSE_POSITIVE_PATTERNS:
        if re.search(pat, f"{title} {description}"):
            return False
    for kw in RELEVANCE_KEYWORDS:
        if kw in text:
            return True
    return False


def make_slug(title, date_str):
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80]
    if date_str:
        slug += f"-{date_str}"
    return slug


def content_fingerprint(date_str, time_str="", lat=None, lon=None, venue=""):
    lat_r = round(float(lat), 3) if lat else 0
    lng_r = round(float(lon), 3) if lon else 0
    norm_venue = re.sub(r'[^a-z0-9]', '', (venue or '').lower())
    time_norm = (time_str or '00:00')[:5]
    raw = f"{date_str}|{time_norm}|{lat_r}|{lng_r}|{norm_venue}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def fetch_eventbrite_search(city, keyword):
    """Fetch events from Eventbrite search via __SERVER_DATA__."""
    url = f"https://www.eventbrite.com/d/united-states--{city['eb']}/{keyword}/"

    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        if resp.status_code != 200:
            return []
    except Exception as e:
        print(f"    ⚠ Request failed: {e}")
        return []

    m = re.search(r'window\.__SERVER_DATA__\s*=\s*(\{.*?\});', resp.text, re.DOTALL)
    if not m:
        return []

    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    results = data.get("search_data", {}).get("events", {}).get("results", [])
    events = []

    for ev in results:
        try:
            title = ev.get("name", "").strip()
            if not title or ev.get("is_online_event"):
                continue

            summary = ev.get("summary", "")
            if not is_relevant(title, summary):
                continue

            start_date = ev.get("start_date", "")
            start_time = ev.get("start_time", "")
            end_date = ev.get("end_date", "")
            if not start_date:
                continue

            try:
                if datetime.strptime(start_date, "%Y-%m-%d").date() < datetime.now().date():
                    continue
            except ValueError:
                pass

            venue = ev.get("primary_venue") or {}
            venue_name = venue.get("name", "")
            addr = venue.get("address", {})
            event_city = addr.get("city", city["display"])
            event_state = addr.get("region", city["state"])
            lat = addr.get("latitude")
            lon = addr.get("longitude")
            lat_f = float(lat) if lat else None
            lon_f = float(lon) if lon else None

            time_display = ""
            if start_time:
                try:
                    t = datetime.strptime(start_time, "%H:%M")
                    time_display = t.strftime("%-I:%M %p")
                except ValueError:
                    time_display = start_time

            image_sizes = ev.get("image", {}).get("image_sizes", {})
            image_url = image_sizes.get("large") or image_sizes.get("medium") or ev.get("image", {}).get("url", "")

            desc = (summary or title)[:200]
            event_url = ev.get("url", "")
            eid = ev.get("eid", ev.get("id", ""))

            fp = content_fingerprint(start_date, time_display, lat_f, lon_f, venue_name)

            events.append({
                "title": title,
                "date": start_date,
                "end_date": end_date or None,
                "time": time_display,
                "venue_name": venue_name,
                "city": event_city,
                "state": event_state,
                "category": categorize(title, summary),
                "description": desc,
                "long_description": summary[:2000] if summary else None,
                "image_url": image_url,
                "ticket_url": event_url,
                "source": "eventbrite",
                "source_id": f"eventbrite_{eid}",
                "organizer": "",
                "slug": make_slug(title, start_date),
                "latitude": lat_f,
                "longitude": lon_f,
                "content_fingerprint": fp,
            })
        except Exception as e:
            print(f"    ⚠ Error parsing event: {e}")

    return events


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def get_existing_events():
    existing_ids = set()
    existing_title_dates = set()
    existing_fingerprints = set()

    try:
        resp = requests.get(
            f"{REST}/events?select=source_id,title,date,content_fingerprint&limit=5000",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        if resp.status_code == 200:
            for e in resp.json():
                if e.get("source_id"):
                    existing_ids.add(e["source_id"])
                if e.get("title") and e.get("date"):
                    t = re.sub(r'[^a-z0-9]', '', e["title"].lower())
                    existing_title_dates.add((t, e["date"]))
                if e.get("content_fingerprint"):
                    existing_fingerprints.add(e["content_fingerprint"])
    except Exception as e:
        print(f"  ⚠ Could not fetch existing events: {e}")

    return existing_ids, existing_title_dates, existing_fingerprints


def is_duplicate(event, existing_ids, existing_title_dates, existing_fingerprints):
    if event["source_id"] in existing_ids:
        return True
    t = re.sub(r'[^a-z0-9]', '', event["title"].lower())
    if (t, event["date"]) in existing_title_dates:
        return True
    if event.get("content_fingerprint") and event["content_fingerprint"] in existing_fingerprints:
        return True
    return False


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_events(events):
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
                print(f"  ⚠ Upsert batch error {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"  ⚠ Upsert exception: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Eventbrite events")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--city", type=str, default=None, help="Single city eb slug")
    parser.add_argument("--day", type=int, default=None, choices=range(7),
                        help="Day of week (0=Mon..6=Sun). Default: today. ~7 cities/day.")
    args = parser.parse_args()

    if not args.dry_run and (not SB_URL or not SB_KEY):
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    print(f"🎟️  Eventbrite Scraper for The Videshi")
    print(f"   {len(CITIES)} cities × {len(KEYWORDS)} keywords\n")

    cities = CITIES
    if args.city:
        cities = [c for c in CITIES if c["eb"] == args.city]
        if not cities:
            print(f"Unknown city: {args.city}. Available: {', '.join(c['eb'] for c in CITIES)}")
            sys.exit(1)
    else:
        # Daily rotation: split 50 cities across 7 days
        day = args.day if args.day is not None else datetime.now().weekday()
        n = len(CITIES)
        chunk = n // 7
        start = day * chunk
        end = start + chunk if day < 6 else n
        cities = CITIES[start:end]
        print(f"📅 Day {day} ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day]}): {len(cities)} cities")

    existing_ids, existing_title_dates, existing_fingerprints = set(), set(), set()
    if not args.dry_run:
        print("📋 Fetching existing events for deduplication...")
        existing_ids, existing_title_dates, existing_fingerprints = get_existing_events()
        print(f"   Found {len(existing_ids)} existing source_ids, {len(existing_title_dates)} title+date combos, {len(existing_fingerprints)} content fingerprints")

    all_events = []
    seen_source_ids = set()

    print(f"\n🔍 Scraping Eventbrite ({len(cities)} cities × {len(KEYWORDS)} keywords)...\n")

    for city in cities:
        city_events = []
        for keyword in KEYWORDS:
            print(f"  📍 {city['display']} / {keyword}...", end=" ", flush=True)
            events = fetch_eventbrite_search(city, keyword)
            relevant_count = 0

            for event in events:
                if event["source_id"] in seen_source_ids:
                    continue
                if not args.dry_run and is_duplicate(event, existing_ids, existing_title_dates, existing_fingerprints):
                    continue

                seen_source_ids.add(event["source_id"])
                city_events.append(event)
                relevant_count += 1

            print(f"{relevant_count} new" if relevant_count else "—")
            time.sleep(1.5)

        if city_events:
            print(f"  ✅ {city['display']}: {len(city_events)} events")
            all_events.extend(city_events)

    print(f"\n{'='*60}")
    print(f"Total new events found: {len(all_events)}")

    if args.dry_run:
        for e in all_events[:10]:
            print(f"\n  📅 {e['date']} {e['time']}")
            print(f"     {e['title']}")
            print(f"     📍 {e['venue_name']}, {e['city']}, {e['state']}")
            if e.get("latitude"):
                print(f"     🌐 {e['latitude']:.4f}, {e['longitude']:.4f}")
            print(f"     🏷️  {e['category']}")
            print(f"     🔗 {e['ticket_url']}")
        if len(all_events) > 10:
            print(f"\n  ... and {len(all_events) - 10} more")
    elif all_events:
        inserted = upsert_events(all_events)
        print(f"✅ Inserted {inserted} events into Supabase")
    else:
        print("ℹ️  No new events to insert")
