#!/usr/bin/env python3
"""
scrape-znfashions.py — Scrape South-Asian clothing & jewelry exhibitions
from ZN Fashions (znfashions.com) and upsert into the Supabase `events` table.

ZN Fashions organises 1,000+ exhibitions across 50+ US cities — exactly the
saree/jewelry pop-up events that other platforms miss.

Usage:
    python3 -u scrape-znfashions.py              # Full scrape + insert
    python3 -u scrape-znfashions.py --dry-run    # Preview only
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import argparse
from datetime import datetime, timezone

sys.stdout.reconfigure(line_buffering=True)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")
REST = f"{SB_URL}/rest/v1"

HEADERS = {
    "User-Agent": "TheVideshi/1.0 (thevideshi.com; diaspora event aggregator)"
}

SOURCE = "znfashions"
ZN_URL = "https://znfashions.com/"

# City → (state_abbrev, state_full, lat, lng)
# ZN Fashions uses short city names; map to state and approximate coords
CITY_GEO = {
    "dallas": ("TX", "Texas", 32.7767, -96.7970),
    "plano": ("TX", "Texas", 33.0198, -96.6989),
    "houston": ("TX", "Texas", 29.7604, -95.3698),
    "austin": ("TX", "Texas", 30.2672, -97.7431),
    "san antonio": ("TX", "Texas", 29.4241, -98.4936),
    "phoenix": ("AZ", "Arizona", 33.4484, -112.0740),
    "los angeles": ("CA", "California", 34.0522, -118.2437),
    "san jose": ("CA", "California", 37.3382, -121.8863),
    "seattle": ("WA", "Washington", 47.6062, -122.3321),
    "denver": ("CO", "Colorado", 39.7392, -104.9903),
    "atlanta": ("GA", "Georgia", 33.7490, -84.3880),
    "orlando": ("FL", "Florida", 28.5383, -81.3792),
    "tampa": ("FL", "Florida", 27.9506, -82.4572),
    "fort lauderdale": ("FL", "Florida", 26.1224, -80.1373),
    "charlotte": ("NC", "North Carolina", 35.2271, -80.8431),
    "raleigh": ("NC", "North Carolina", 35.7796, -78.6382),
    "nashville": ("TN", "Tennessee", 36.1627, -86.7816),
    "washington d.c.": ("DC", "District of Columbia", 38.9072, -77.0369),
    "washington": ("DC", "District of Columbia", 38.9072, -77.0369),
    "philadelphia": ("PA", "Pennsylvania", 39.9526, -75.1652),
    "baltimore": ("MD", "Maryland", 39.2904, -76.6122),
    "new york": ("NY", "New York", 40.7128, -74.0060),
    "new jersey": ("NJ", "New Jersey", 40.5187, -74.4121),
    "boston": ("MA", "Massachusetts", 42.3601, -71.0589),
    "chicago": ("IL", "Illinois", 41.8781, -87.6298),
    "schaumburg": ("IL", "Illinois", 42.0334, -88.0834),
    "detroit": ("MI", "Michigan", 42.3314, -83.0458),
    "troy": ("MI", "Michigan", 42.6064, -83.1498),
    "livonia": ("MI", "Michigan", 42.3684, -83.3527),
    "michigan": ("MI", "Michigan", 42.3314, -83.0458),
    "minneapolis": ("MN", "Minnesota", 44.9778, -93.2650),
    "cleveland": ("OH", "Ohio", 41.4993, -81.6944),
    "columbus": ("OH", "Ohio", 39.9612, -82.9988),
    "oklahoma": ("OK", "Oklahoma", 35.4676, -97.5164),
    "oklahoma city": ("OK", "Oklahoma", 35.4676, -97.5164),
    "st. louis": ("MO", "Missouri", 38.6270, -90.1994),
    "st louis": ("MO", "Missouri", 38.6270, -90.1994),
    "wisconsin": ("WI", "Wisconsin", 43.0389, -87.9065),
    "milwaukee": ("WI", "Wisconsin", 43.0389, -87.9065),
    "hoover": ("AL", "Alabama", 33.4054, -86.8114),
    "alabama": ("AL", "Alabama", 33.4054, -86.8114),
    "southlake": ("TX", "Texas", 32.9412, -97.1342),
    "sugar land": ("TX", "Texas", 29.6197, -95.6349),
    "clear lake": ("TX", "Texas", 29.5494, -95.1151),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def content_fingerprint(title: str, date_str: str, city: str) -> str:
    """Cross-source dedup fingerprint — delegates to shared module."""
    from event_dedup import content_fingerprint as _fp
    return _fp(title, date_str, city)


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-')[:120]


def resolve_city(title: str, venue: str) -> tuple:
    """Extract city/state/coords from the event title or venue name."""
    # ZN titles are like "Dallas Wedding Exhibition", "Chicago/Schaumburg Autumn Exhibition"
    # Try to find the city from the title
    title_lower = title.lower()

    # Handle compound city names like "Dallas/Southlake", "Michigan/Troy", "Houston/Clear Lake"
    for city_key, geo in sorted(CITY_GEO.items(), key=lambda x: -len(x[0])):
        if city_key in title_lower:
            return city_key.title(), geo[0], geo[1], geo[2], geo[3]

    # Fallback — try venue name
    venue_lower = (venue or "").lower()
    for city_key, geo in sorted(CITY_GEO.items(), key=lambda x: -len(x[0])):
        if city_key in venue_lower:
            return city_key.title(), geo[0], geo[1], geo[2], geo[3]

    return "", "", "", None, None


def parse_time_range(time_str: str) -> tuple:
    """Parse '11AM – 8PM' into ('11:00', '20:00')."""
    m = re.match(r'(\d{1,2})(AM|PM)\s*[–-]\s*(\d{1,2})(AM|PM)', time_str, re.I)
    if not m:
        return None, None
    sh, sp, eh, ep = m.group(1), m.group(2).upper(), m.group(3), m.group(4).upper()
    start_h = int(sh) % 12 + (12 if sp == "PM" else 0)
    end_h = int(eh) % 12 + (12 if ep == "PM" else 0)
    return f"{start_h:02d}:00", f"{end_h:02d}:00"


# ---------------------------------------------------------------------------
# Fetch and parse
# ---------------------------------------------------------------------------

def fetch_page() -> str:
    """Fetch znfashions.com HTML via curl (requests may fail through proxy)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-A", HEADERS["User-Agent"], ZN_URL],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and len(result.stdout) > 500:
            return result.stdout
    except Exception as e:
        print(f"⚠ curl failed: {e}")

    # Fallback to requests
    try:
        import requests
        r = requests.get(ZN_URL, headers=HEADERS, timeout=15)
        return r.text
    except Exception as e:
        print(f"⚠ requests also failed: {e}")
        return ""


def parse_events(html: str) -> list:
    """Parse ZN Fashions HTML for event listings.

    The page structure (from browser_open output) shows:
    - Month headers like "### August 2026", "### September 2026"
    - Date lines like "22 Sat", "23 Sun 2 events"
    - Event titles in h4: "#### Cleveland Summer Exhibition"
    - Details: "11AM – 6PM · Wyndham Independence"
    - Next exhibition block with full date "Sunday, August 09, 2026 11AM – 9PM ..."

    We parse from the raw HTML, looking for the calendar section.
    """
    events = []

    # ZN Fashions is a Next.js site that embeds a @graph JSON-LD with all events.
    # Primary strategy: extract the @graph from the script tag.
    graph_match = re.search(
        r'"application/ld\+json"[^>]*>(\{"@context":"https://schema\.org","@graph":\[.*?\]\})',
        html, re.S
    )
    if graph_match:
        try:
            graph_data = json.loads(graph_match.group(1))
            items = [e for e in graph_data.get("@graph", []) if e.get("@type") == "Event"]
            for item in items:
                ev = parse_jsonld_event(item)
                if ev:
                    events.append(ev)
            if events:
                print(f"  ✅ Found {len(events)} events via JSON-LD @graph")
                return events
        except json.JSONDecodeError as ex:
            print(f"  ⚠ JSON-LD @graph parse error: {ex}")

    # Fallback: try individual ld+json script blocks
    ld_matches = re.findall(
        r'<script\s+type="application/ld\+json">\s*([\s\S]*?)\s*</script>',
        html, re.IGNORECASE
    )
    for ld_text in ld_matches:
        try:
            ld_data = json.loads(ld_text)
            items = ld_data if isinstance(ld_data, list) else [ld_data]
            for item in items:
                if item.get("@type") == "Event":
                    ev = parse_jsonld_event(item)
                    if ev:
                        events.append(ev)
        except json.JSONDecodeError:
            continue

    if events:
        print(f"  ✅ Found {len(events)} events via JSON-LD script blocks")

    return events


def parse_text_calendar(text: str) -> list:
    """Parse the text-rendered calendar from ZN Fashions page."""
    events = []

    # Find all month+year markers
    month_re = re.compile(
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
        re.I
    )
    MONTHS = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    lines = text.split('\n')
    current_month = None
    current_year = None
    current_day = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for month header
        mm = month_re.search(line)
        if mm:
            current_month = MONTHS[mm.group(1).lower()]
            current_year = int(mm.group(2))
            i += 1
            continue

        # Check for date marker: "22 Sat" or "23 Sun 2 events"
        dm = re.match(r'^(\d{1,2})\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', line, re.I)
        if dm:
            current_day = int(dm.group(1))
            i += 1
            continue

        # Check for "Next exhibition" block with full date
        # "Sunday, August 09, 2026 11AM – 9PM Marriott Dallas Plano Dallas, TX"
        full_date = re.match(
            r'(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday),?\s+'
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+'
            r'(\d{1,2}),?\s+(\d{4})\s+'
            r'(\d{1,2}(?:AM|PM)\s*[–-]\s*\d{1,2}(?:AM|PM))',
            line, re.I
        )
        if full_date:
            fd_month = MONTHS[full_date.group(1).lower()]
            fd_day = int(full_date.group(2))
            fd_year = int(full_date.group(3))
            current_month = fd_month
            current_year = fd_year
            current_day = fd_day
            # Time range is in the same line
            time_range = full_date.group(4)
            # Look back for title (should be the previous non-empty line)
            title = None
            for j in range(i - 1, max(i - 5, 0), -1):
                candidate = lines[j].strip()
                if candidate and 'exhibition' in candidate.lower():
                    title = candidate.lstrip('#').strip()
                    break
            if not title:
                # Look forward
                for j in range(i + 1, min(i + 3, len(lines))):
                    candidate = lines[j].strip()
                    if candidate and 'exhibition' in candidate.lower():
                        title = candidate.lstrip('#').strip()
                        break

            if title and current_month and current_year and current_day:
                venue = ""
                # Rest of line after time range might have venue info
                rest = line[full_date.end():].strip()
                if rest:
                    # Extract venue — typically before the bold city
                    venue = re.sub(r'\*\*.*?\*\*', '', rest).strip().rstrip(',').strip()
                    if not venue:
                        venue = rest

                ev = build_event(title, current_year, current_month, current_day, time_range, venue)
                if ev:
                    events.append(ev)

            i += 1
            continue

        # Check for event title — contains "Exhibition"
        if 'exhibition' in line.lower() and current_month and current_year and current_day:
            title = line.lstrip('#').strip()
            # Next line should have time · venue
            time_range = ""
            venue = ""
            for j in range(i + 1, min(i + 4, len(lines))):
                detail = lines[j].strip()
                tm = re.match(r'(\d{1,2}(?:AM|PM)\s*[–-]\s*\d{1,2}(?:AM|PM))\s*[·•]\s*(.*)', detail, re.I)
                if tm:
                    time_range = tm.group(1)
                    venue = tm.group(2).strip()
                    break

            ev = build_event(title, current_year, current_month, current_day, time_range, venue)
            if ev:
                events.append(ev)

        i += 1

    return events


def build_event(title: str, year: int, month: int, day: int, time_range: str, venue: str) -> dict | None:
    """Build a standardised event dict."""
    try:
        date_str = f"{year}-{month:02d}-{day:02d}"
    except (ValueError, TypeError):
        return None

    start_time, end_time = parse_time_range(time_range) if time_range else (None, None)
    city, state, state_full, lat, lng = resolve_city(title, venue)

    if not city:
        # Try to extract from venue
        city, state, state_full, lat, lng = resolve_city(venue, "")

    description = f"ZN Fashions {title}. South-Asian clothing and jewelry exhibition."
    if venue:
        description += f" Venue: {venue}."

    slug_hash = hashlib.md5(f"{title}|{date_str}".encode()).hexdigest()[:6]
    slug = slugify(f"zn-{title}-{city}-{date_str}-{slug_hash}")

    fp = content_fingerprint(f"ZN Fashions: {title}", date_str, city)

    source_id = f"znfashions_{slugify(title)}_{date_str}"

    return {
        "title": f"ZN Fashions: {title}",
        "description": description[:200],
        "date": date_str,
        "time": start_time,
        "end_date": None,
        "city": city,
        "state": state,
        "venue_name": venue,
        "latitude": lat,
        "longitude": lng,
        "category": "Shopping",
        "source": SOURCE,
        "source_id": source_id,
        "image_url": None,
        "ticket_url": ZN_URL,
        "price_range": "Free",
        "organizer": "ZN Fashions",
        "slug": slug,
        "content_fingerprint": fp,
    }


def parse_jsonld_event(item: dict) -> dict | None:
    """Parse a JSON-LD Event item."""
    title = (item.get("name") or "").strip()
    if not title:
        return None

    start = item.get("startDate", "")
    date_str = start[:10] if start else None
    time_str = None
    if start and "T" in start:
        time_str = start.split("T")[1][:5]

    if not date_str:
        return None

    location = item.get("location", {})
    venue_name = location.get("name", "")
    address_obj = location.get("address", {})
    locality = address_obj.get("addressLocality", "")
    region = address_obj.get("addressRegion", "")

    geo = location.get("geo", {})
    lat = geo.get("latitude")
    lon = geo.get("longitude")

    desc = (item.get("description") or title)[:200]
    image_url = None
    images = item.get("image", [])
    if isinstance(images, list) and images:
        image_url = images[0]
    elif isinstance(images, str):
        image_url = images

    ticket_url = item.get("url", ZN_URL)
    source_url = item.get("url", "")
    organizer_obj = item.get("organizer", {})
    organizer = organizer_obj.get("name", "ZN Fashions")

    slug_hash = hashlib.md5((source_url or title).encode()).hexdigest()[:6]
    slug = slugify(f"zn-{title}-{locality}-{date_str}-{slug_hash}")
    fp = content_fingerprint(title, date_str, locality)

    city = locality
    state = region
    # ZN uses full state names like "Texas" → convert to abbreviation
    STATE_ABBREV = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
        "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
        "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
        "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
        "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
        "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
        "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
        "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
        "new mexico": "NM", "new york": "NY", "north carolina": "NC",
        "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
        "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
        "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
        "vermont": "VT", "virginia": "VA", "washington": "WA",
        "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
        "district of columbia": "DC",
    }
    if state and state.lower() in STATE_ABBREV:
        state = STATE_ABBREV[state.lower()]
    if not city:
        city, state, _, lat, lon = resolve_city(title, venue_name)

    return {
        "title": f"ZN Fashions: {title}" if "ZN" not in title else title,
        "description": desc,
        "date": date_str,
        "time": time_str,
        "end_date": None,
        "city": city,
        "state": state,
        "venue_name": venue_name,
        "latitude": lat,
        "longitude": lon,
        "category": "Shopping",
        "source": SOURCE,
        "source_id": source_url or f"znfashions_{slug_hash}",
        "image_url": image_url,
        "ticket_url": ticket_url or ZN_URL,
        "price_range": "Free",
        "organizer": organizer,
        "slug": slug,
        "content_fingerprint": fp,
    }


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def sb_curl(method: str, endpoint: str, data=None, params: str = "") -> tuple:
    """Make Supabase REST call via curl (proxy-safe)."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if params:
        url += f"?{params}"

    cmd = [
        "curl", "-s", "-X", method, url,
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
    ]
    if method == "POST":
        cmd += ["-H", "Prefer: resolution=merge-duplicates"]
    if data is not None:
        cmd += ["-d", json.dumps(data)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.returncode, result.stdout


def get_existing():
    """Fetch existing source_ids and content_fingerprints for dedup."""
    existing_urls = set()
    if not SB_URL or not SB_KEY:
        return existing_urls, set()

    try:
        rc, out = sb_curl("GET", "events", params="select=source_id&limit=10000")
        if rc == 0 and out.strip().startswith("["):
            for e in json.loads(out):
                if e.get("source_id"):
                    existing_urls.add(e["source_id"])
    except Exception as e:
        print(f"⚠ Failed to fetch existing events: {e}")

    # Cross-source fingerprints via shared module (uses curl)
    from event_dedup import get_all_fingerprints
    existing_fps = get_all_fingerprints()

    return existing_urls, existing_fps


def upsert_events(events: list) -> int:
    """Upsert events into Supabase via curl."""
    if not events:
        return 0

    total = 0
    for ev in events:
        try:
            rc, out = sb_curl("POST", "events", data=ev)
            if rc == 0 and '"code"' not in out[:50]:
                total += 1
            else:
                # Try plain insert without merge-duplicates
                cmd = [
                    "curl", "-s", "-X", "POST",
                    f"{SB_URL}/rest/v1/events",
                    "-H", f"apikey: {SB_KEY}",
                    "-H", f"Authorization: Bearer {SB_KEY}",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(ev),
                ]
                r2 = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if r2.returncode == 0 and '"code"' not in r2.stdout[:50]:
                    total += 1
                else:
                    print(f"    ⚠ Upsert failed for '{ev['title'][:40]}': {r2.stdout[:150]}")
        except Exception as e:
            print(f"    ⚠ Upsert error: {e}")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape ZN Fashions exhibitions")
    parser.add_argument("--dry-run", action="store_true", help="Preview without inserting")
    args = parser.parse_args()

    if not args.dry_run and (not SB_URL or not SB_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    print("🔍 Fetching ZN Fashions calendar...")
    html = fetch_page()
    if not html:
        print("❌ Could not fetch znfashions.com")
        sys.exit(1)

    print(f"  📄 Fetched {len(html)} bytes")

    events = parse_events(html)
    print(f"  📊 Parsed {len(events)} events")

    if not events:
        print("❌ No events found — page structure may have changed")
        sys.exit(0)

    # Dedup
    existing_urls, existing_fps = set(), set()
    if not args.dry_run:
        existing_urls, existing_fps = get_existing()
        print(f"📊 Existing: {len(existing_urls)} URLs, {len(existing_fps)} fingerprints")

    new_events = []
    skipped_url = 0
    skipped_fp = 0

    for ev in events:
        if ev["source_id"] in existing_urls:
            skipped_url += 1
            continue
        if ev.get("content_fingerprint") and ev["content_fingerprint"] in existing_fps:
            skipped_fp += 1
            continue
        new_events.append(ev)
        existing_urls.add(ev["source_id"])
        if ev.get("content_fingerprint"):
            existing_fps.add(ev["content_fingerprint"])

    print(f"\n📊 New: {len(new_events)} | Skipped (URL): {skipped_url} | Skipped (FP): {skipped_fp}")

    if args.dry_run:
        for ev in new_events:
            print(f"  🛍️ {ev['title'][:55]} | {ev['date']} | {ev['city']}, {ev['state']} | {ev['venue_name'][:30]}")
        print(f"\n🏁 Dry run — {len(new_events)} events would be inserted")
    else:
        inserted = upsert_events(new_events)
        print(f"\n✅ Inserted {inserted}/{len(new_events)} ZN Fashions events")


if __name__ == "__main__":
    main()
