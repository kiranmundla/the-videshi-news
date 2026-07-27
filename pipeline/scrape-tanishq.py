#!/usr/bin/env python3
"""
scrape-tanishq.py — Scrape Tanishq US trunk show events from tanishq.com
and upsert into the Supabase `events` table.

Tanishq (Tata Group) does traveling trunk shows across US cities. Each show
gets its own page at tanishq.com/trunk-show-{city}.html with venue, dates,
and RSVP. We probe a known list of US city slugs to find active shows.

Usage:
    python3 -u scrape-tanishq.py              # Full scrape + insert
    python3 -u scrape-tanishq.py --dry-run    # Preview only
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

SOURCE = "tanishq"
BASE_URL = "https://www.tanishq.com"
CURRENT_YEAR = datetime.now().year

# Tanishq uses predictable URL slugs. We maintain a list of known US cities
# they've done trunk shows in. The scraper tries each and picks up active ones.
# URL pattern: /trunk-show-{slug}.html or /{slug}-trunk-show.html
CITY_SLUGS = [
    # Primary format: trunk-show-{city}
    "trunk-show-houston", "trunk-show-dallas", "trunk-show-austin",
    "trunk-show-san-antonio", "trunk-show-san-jose", "trunk-show-sacramento",
    "trunk-show-los-angeles", "trunk-show-la", "trunk-show-san-diego",
    "trunk-show-seattle", "trunk-show-portland", "trunk-show-denver",
    "trunk-show-phoenix", "trunk-show-atlanta", "trunk-show-orlando",
    "trunk-show-miami", "trunk-show-tampa", "trunk-show-fort-lauderdale",
    "trunk-show-charlotte", "trunk-show-raleigh", "trunk-show-nashville",
    "trunk-show-washington-dc", "trunk-show-philadelphia", "trunk-show-baltimore",
    "trunk-show-new-york", "trunk-show-new-jersey", "trunk-show-edison",
    "trunk-show-boston", "trunk-show-chicago", "trunk-show-schaumburg",
    "trunk-show-detroit", "trunk-show-minneapolis", "trunk-show-cleveland",
    "trunk-show-columbus", "trunk-show-st-louis", "trunk-show-milwaukee",
    "trunk-show-indianapolis", "trunk-show-pittsburgh", "trunk-show-cincinnati",
    "trunk-show-fremont", "trunk-show-irvine", "trunk-show-sunnyvale",
    "trunk-show-plano", "trunk-show-cary", "trunk-show-redmond",
    "trunk-show-bellevue", "trunk-show-bloomington",
    "trunk-show-boca-raton", "trunk-show-coral-springs",
    # Alternate format: {city}-trunk-show
    "houston-trunk-show", "dallas-trunk-show", "austin-trunk-show",
    "san-jose-trunk-show", "sacramento-trunk-show", "seattle-trunk-show",
    "denver-trunk-show", "atlanta-trunk-show", "raleigh-trunk-show",
    "chicago-trunk-show", "boston-trunk-show", "dublin-trunk-show",
    "new-york-trunk-show", "new-jersey-trunk-show",
    "fort-lauderdale-trunk-show", "milwaukee-trunk-show",
    "st-louis-trunk-show", "minneapolis-trunk-show",
    "phoenix-trunk-show", "tampa-trunk-show",
    "charlotte-trunk-show", "nashville-trunk-show",
    "washington-dc-trunk-show", "philadelphia-trunk-show",
    "detroit-trunk-show", "cleveland-trunk-show",
    "san-antonio-trunk-show", "portland-trunk-show",
    "orlando-trunk-show", "miami-trunk-show",
    "pittsburgh-trunk-show", "cincinnati-trunk-show",
]

# City name → (state, lat, lng)
CITY_GEO = {
    "houston": ("TX", 29.7604, -95.3698),
    "dallas": ("TX", 32.7767, -96.7970),
    "austin": ("TX", 30.2672, -97.7431),
    "san antonio": ("TX", 29.4241, -98.4936),
    "plano": ("TX", 33.0198, -96.6989),
    "san jose": ("CA", 37.3382, -121.8863),
    "sacramento": ("CA", 38.5816, -121.4944),
    "los angeles": ("CA", 34.0522, -118.2437),
    "la": ("CA", 34.0522, -118.2437),
    "san diego": ("CA", 32.7157, -117.1611),
    "irvine": ("CA", 33.6846, -117.8265),
    "fremont": ("CA", 37.5485, -121.9886),
    "sunnyvale": ("CA", 37.3688, -122.0363),
    "seattle": ("WA", 47.6062, -122.3321),
    "redmond": ("WA", 47.6740, -122.1215),
    "bellevue": ("WA", 47.6101, -122.2015),
    "portland": ("OR", 45.5152, -122.6784),
    "denver": ("CO", 39.7392, -104.9903),
    "phoenix": ("AZ", 33.4484, -112.0740),
    "atlanta": ("GA", 33.7490, -84.3880),
    "orlando": ("FL", 28.5383, -81.3792),
    "miami": ("FL", 25.7617, -80.1918),
    "tampa": ("FL", 27.9506, -82.4572),
    "fort lauderdale": ("FL", 26.1224, -80.1373),
    "coral springs": ("FL", 26.2712, -80.2706),
    "boca raton": ("FL", 26.3584, -80.0831),
    "charlotte": ("NC", 35.2271, -80.8431),
    "raleigh": ("NC", 35.7796, -78.6382),
    "cary": ("NC", 35.7915, -78.7811),
    "nashville": ("TN", 36.1627, -86.7816),
    "washington dc": ("DC", 38.9072, -77.0369),
    "washington-dc": ("DC", 38.9072, -77.0369),
    "philadelphia": ("PA", 39.9526, -75.1652),
    "pittsburgh": ("PA", 40.4406, -79.9959),
    "baltimore": ("MD", 39.2904, -76.6122),
    "new york": ("NY", 40.7128, -74.0060),
    "new jersey": ("NJ", 40.5187, -74.4121),
    "edison": ("NJ", 40.5187, -74.4121),
    "boston": ("MA", 42.3601, -71.0589),
    "chicago": ("IL", 41.8781, -87.6298),
    "schaumburg": ("IL", 42.0334, -88.0834),
    "detroit": ("MI", 42.3314, -83.0458),
    "minneapolis": ("MN", 44.9778, -93.2650),
    "bloomington": ("MN", 44.8408, -93.2983),
    "cleveland": ("OH", 41.4993, -81.6944),
    "columbus": ("OH", 39.9612, -82.9988),
    "dublin": ("OH", 40.0992, -83.1141),
    "cincinnati": ("OH", 39.1031, -84.5120),
    "st louis": ("MO", 38.6270, -90.1994),
    "st-louis": ("MO", 38.6270, -90.1994),
    "milwaukee": ("WI", 43.0389, -87.9065),
    "indianapolis": ("IN", 39.7684, -86.1581),
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


def extract_city_from_slug(slug: str) -> str:
    """Convert 'trunk-show-st-louis' to 'st louis'."""
    city = slug.replace("trunk-show-", "").replace("-trunk-show", "")
    return city.replace("-", " ")


MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}


def parse_tanishq_dates(text: str) -> list:
    """Parse date strings like 'July 25th - 26th, 2026' or 'May 9th - 10th, 2026'.
    Returns list of (date_str, date_str) tuples for start/end dates.
    """
    # Pattern: Month DDth - DDth, YYYY  or  Month DDth, YYYY
    m = re.search(
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+'
        r'(\d{1,2})(?:st|nd|rd|th)?\s*'
        r'(?:-\s*(\d{1,2})(?:st|nd|rd|th)?)?\s*,?\s*'
        r'(\d{4})',
        text, re.I
    )
    if not m:
        return []

    month = MONTHS[m.group(1).lower()]
    start_day = int(m.group(2))
    end_day = int(m.group(3)) if m.group(3) else start_day
    year = int(m.group(4))

    start_date = f"{year}-{month:02d}-{start_day:02d}"
    end_date = f"{year}-{month:02d}-{end_day:02d}" if end_day != start_day else None

    return start_date, end_date


def parse_time(text: str) -> str | None:
    """Extract start time from strings like '11:00 AM – 7:30 PM' or '11am to 8:00pm'."""
    m = re.search(r'(\d{1,2}):?(\d{2})?\s*(AM|PM)', text, re.I)
    if m:
        h = int(m.group(1)) % 12 + (12 if m.group(3).upper() == "PM" else 0)
        mi = m.group(2) or "00"
        return f"{h:02d}:{mi}"
    return None


# ---------------------------------------------------------------------------
# Fetch and parse
# ---------------------------------------------------------------------------

def fetch_trunk_show_page(slug: str) -> str | None:
    """Fetch a Tanishq trunk show page via curl."""
    url = f"{BASE_URL}/{slug}.html"
    for attempt in range(2):
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "-o", "-", "-w", "\n%{http_code}",
                 "-A", HEADERS["User-Agent"], "--connect-timeout", "10", url],
                capture_output=True, text=True, timeout=20
            )
            body = result.stdout
            # Extract HTTP status code from the last line
            lines = body.strip().rsplit('\n', 1)
            if len(lines) == 2:
                content, status = lines[0], lines[1].strip()
                if status == "200" and len(content) > 500:
                    return content
                elif status == "404":
                    return None  # Page doesn't exist, no retry
            elif result.returncode == 0 and len(body) > 500:
                return body
        except Exception:
            pass
        if attempt == 0:
            import time
            time.sleep(1)
    return None


def parse_trunk_show(html: str, slug: str) -> dict | None:
    """Parse a Tanishq trunk show page into an event dict."""
    if not html or len(html) < 200:
        return None

    # Check it's not a 404 or redirect to homepage
    if "Page Not Found" in html or "404" in html[:500]:
        return None

    city_name = extract_city_from_slug(slug)

    # The HTML structure is:
    # <div class="trunk-info-label">Venue:</div>
    # <div class="trunk-info-content"><span>Hotel Name</span><span>Address</span></div>
    
    # Extract venue
    venue = ""
    venue_m = re.search(
        r'Venue:\s*</div>\s*<div[^>]*class="trunk-info-content"[^>]*>(.*?)</div>',
        html, re.I | re.DOTALL
    )
    if venue_m:
        venue = re.sub(r'<[^>]+>', ' ', venue_m.group(1)).strip()
        venue = re.sub(r'\s+', ' ', venue).strip()
    else:
        # Fallback: broader match
        venue_m = re.search(r'Venue:\s*(?:<[^>]+>)*\s*(.+?)(?:<|$)', html, re.I)
        if venue_m:
            venue = re.sub(r'<[^>]+>', ' ', venue_m.group(1)).strip()
            venue = re.sub(r'\s+', ' ', venue).strip()

    # Extract dates
    dates_text = ""
    dates_m = re.search(
        r'Dates?:\s*</div>\s*<div[^>]*class="trunk-info-content"[^>]*>(.*?)</div>',
        html, re.I | re.DOTALL
    )
    if dates_m:
        dates_text = re.sub(r'<[^>]+>', ' ', dates_m.group(1)).strip()
        dates_text = re.sub(r'\s+', ' ', dates_text)
    else:
        dates_m = re.search(r'Dates?:\s*(?:<[^>]+>)*\s*(.+?)(?:<|Phone|Contact|$)', html, re.I | re.DOTALL)
        if dates_m:
            dates_text = re.sub(r'<[^>]+>', ' ', dates_m.group(1)).strip()
            dates_text = re.sub(r'\s+', ' ', dates_text)

    if not dates_text:
        return None

    result = parse_tanishq_dates(dates_text)
    if not result:
        return None

    start_date, end_date = result

    # Check the event is current or future (allow events ending today)
    try:
        check_date = end_date or start_date
        event_dt = datetime.strptime(check_date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if event_dt < today:
            return None  # Past event
    except (ValueError, TypeError):
        pass

    # Extract timings
    time_text = ""
    time_m = re.search(
        r'Timings?:\s*</div>\s*<div[^>]*class="trunk-info-content"[^>]*>(.*?)</div>',
        html, re.I | re.DOTALL
    )
    if time_m:
        time_text = re.sub(r'<[^>]+>', ' ', time_m.group(1)).strip()
    else:
        time_m = re.search(r'Timings?:\s*(?:<[^>]+>)*\s*(.+?)(?:<|Phone|Contact|$)', html, re.I | re.DOTALL)
        if time_m:
            time_text = re.sub(r'<[^>]+>', ' ', time_m.group(1)).strip()

    start_time = parse_time(time_text) if time_text else None

    # Extract phone
    phone = ""
    phone_m = re.search(r'Phone:\s*(?:<[^>]+>)*\s*([\d-]+)', html, re.I)
    if phone_m:
        phone = phone_m.group(1).strip()

    # Get geo
    geo = CITY_GEO.get(city_name, CITY_GEO.get(city_name.replace(" ", "-"), None))
    state = geo[0] if geo else ""
    lat = geo[1] if geo else None
    lng = geo[2] if geo else None

    city_display = city_name.title()
    # Special case corrections
    if city_display == "St Louis":
        city_display = "St. Louis"
    if city_display == "Washington Dc":
        city_display = "Washington D.C."

    description = f"Tanishq Trunk Show in {city_display}. Exclusive preview of fine Indian jewelry collection."
    if venue:
        description += f" Venue: {venue}."

    page_url = f"{BASE_URL}/{slug}.html"
    fp = content_fingerprint(f"Tanishq Trunk Show — {city_display}", start_date, city_display)
    slug_hash = hashlib.md5(f"{slug}|{start_date}".encode()).hexdigest()[:6]
    event_slug = slugify(f"tanishq-trunk-show-{city_display}-{start_date}-{slug_hash}")

    return {
        "title": f"Tanishq Trunk Show — {city_display}",
        "description": description[:200],
        "date": start_date,
        "time": start_time,
        "end_date": end_date,
        "city": city_display,
        "state": state,
        "venue_name": venue,
        "latitude": lat,
        "longitude": lng,
        "category": "Shopping",
        "source": SOURCE,
        "source_id": page_url,
        "image_url": None,
        "ticket_url": page_url,
        "price_range": "Free",
        "organizer": "Tanishq",
        "slug": event_slug,
        "content_fingerprint": fp,
    }


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def sb_curl(method: str, endpoint: str, data=None, params: str = "") -> tuple:
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
    if not events:
        return 0
    total = 0
    for ev in events:
        try:
            rc, out = sb_curl("POST", "events", data=ev)
            if rc == 0 and '"code"' not in out[:50]:
                total += 1
            else:
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
    parser = argparse.ArgumentParser(description="Scrape Tanishq US trunk shows")
    parser.add_argument("--dry-run", action="store_true", help="Preview without inserting")
    args = parser.parse_args()

    if not args.dry_run and (not SB_URL or not SB_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)

    print(f"🔍 Probing {len(CITY_SLUGS)} Tanishq trunk show URLs...")

    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    events = []
    seen_dates = set()

    def probe_slug(slug):
        """Probe a single Tanishq trunk show URL and return event or None."""
        html = fetch_trunk_show_page(slug)
        if not html:
            return None
        return parse_trunk_show(html, slug)

    # Probe all URLs concurrently (polite: 3 threads max, with small delay)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(probe_slug, slug): slug for slug in CITY_SLUGS}
        for future in as_completed(futures):
            slug = futures[future]
            try:
                ev = future.result()
                if ev:
                    key = (ev["date"], ev["city"])
                    if key not in seen_dates:
                        seen_dates.add(key)
                        events.append(ev)
                        print(f"  ✅ {ev['title']} | {ev['date']} to {ev.get('end_date', ev['date'])} | {ev['venue_name'][:40]}")
            except Exception as e:
                print(f"  ⚠ Error probing {slug}: {e}")

    print(f"\n📊 Found {len(events)} active/upcoming trunk shows")

    if not events:
        print("ℹ️ No current trunk shows found")
        sys.exit(0)

    # Dedup against DB
    existing_urls, existing_fps = set(), set()
    if not args.dry_run:
        existing_urls, existing_fps = get_existing()
        print(f"📊 Existing: {len(existing_urls)} URLs, {len(existing_fps)} fingerprints")

    new_events = []
    skipped = 0
    for ev in events:
        if ev["source_id"] in existing_urls:
            skipped += 1
            continue
        if ev.get("content_fingerprint") and ev["content_fingerprint"] in existing_fps:
            skipped += 1
            continue
        new_events.append(ev)
        existing_urls.add(ev["source_id"])

    print(f"📊 New: {len(new_events)} | Skipped: {skipped}")

    if args.dry_run:
        for ev in new_events:
            print(f"  💎 {ev['title'][:55]} | {ev['date']} | {ev['venue_name'][:40]}")
        print(f"\n🏁 Dry run — {len(new_events)} events would be inserted")
    else:
        inserted = upsert_events(new_events)
        print(f"\n✅ Inserted {inserted}/{len(new_events)} Tanishq trunk shows")


if __name__ == "__main__":
    main()
