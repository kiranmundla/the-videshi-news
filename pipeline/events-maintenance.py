#!/usr/bin/env python3
"""
events-maintenance.py — Periodic maintenance for The Videshi events table.
1. Delete past events (date < today)
2. Refresh Ticketmaster events for Indian/South Asian artists and shows
3. Geocode events missing latitude/longitude via Nominatim
"""

import json
import os
import subprocess
import sys
import time
import re
from datetime import datetime, timezone

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

# Ticketmaster API key (consumer key)
TM_KEY = os.environ.get("TICKETMASTER_API_KEY", "7elxdku9GGG5k8j0Xm8KWdANDgecHMV0")

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def curl_supabase(method, path, json_data=None, prefer=None):
    """Make a Supabase REST call via curl (avoids proxy issues with requests)."""
    url = f"{REST}{path}"
    cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method.upper(), url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if json_data is not None:
        cmd += ["-d", json.dumps(json_data)]
    cmd += ["--max-time", "15"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    output = result.stdout.strip()
    lines = output.rsplit("\n", 1)
    body = lines[0] if len(lines) > 1 else ""
    status = int(lines[-1]) if lines[-1].isdigit() else 0
    return status, body


# ---------------------------------------------------------------------------
# Ticketmaster search configs
# ---------------------------------------------------------------------------

# Artist-specific searches (keyword + optional classificationName)
TM_ARTIST_SEARCHES = [
    {"keyword": "Diljit Dosanjh"},
    {"keyword": "Shreya Ghoshal"},
    {"keyword": "Sonu Nigam"},
    {"keyword": "Arijit Singh"},
    {"keyword": "Vishal Shekhar"},
    {"keyword": "Kumar Sanu"},
    {"keyword": "AR Rahman"},
    {"keyword": "Atif Aslam"},
    {"keyword": "Neha Kakkar"},
    {"keyword": "Badshah"},
    {"keyword": "AP Dhillon"},
    {"keyword": "Karan Aujla"},
    {"keyword": "Armaan Malik"},
    {"keyword": "Shankar Ehsaan Loy"},
    {"keyword": "Amit Trivedi"},
    {"keyword": "Sunidhi Chauhan"},
    {"keyword": "Asha Bhosle"},
    {"keyword": "Lucky Ali"},
    {"keyword": "Nucleya"},
    {"keyword": "Divine rapper"},
    {"keyword": "Raftaar"},
    {"keyword": "Pritam"},
    {"keyword": "Jubin Nautiyal"},
    {"keyword": "Darshan Raval"},
]

# State codes to search
TM_STATES = [
    "CA", "TX", "NY", "NJ", "IL", "GA", "WA", "MA",
    "PA", "VA", "MD", "NC", "FL", "OH", "MI", "CT",
    "AZ", "CO", "MN", "OR",
]

def slugify(text):
    """Create a URL-friendly slug from text."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:80].strip('-')

def categorize_event(title, desc=""):
    """Categorize event based on title and description."""
    t = (title + " " + (desc or "")).lower()

    # Spiritual/Religious first
    spiritual_kw = ["temple", "mandir", "gurudwara", "gurdwara", "kirtan", "bhajan",
                     "puja", "pooja", "satsang", "meditation", "yoga", "vedic",
                     "bhakti", "spiritual", "prayer", "dharma", "gita", "iskcon",
                     "baps", "swami", "guru", "ashram", "havan", "aarti", "diwali",
                     "navratri", "holi", "ganesh", "durga", "ram navami", "janmashtami"]
    if any(kw in t for kw in spiritual_kw):
        return "Spiritual"

    # Entertainment
    ent_kw = ["concert", "bollywood", "music", "dance", "comedy", "show",
              "performance", "festival", "mela", "bhangra", "garba",
              "dandiya", "dj ", "party", "night ", "live music", "standup",
              "singer", "band", "tour"]
    if any(kw in t for kw in ent_kw):
        return "Entertainment"

    # Sports
    sport_kw = ["cricket", "kabaddi", "badminton", "soccer", "run ",
                "marathon", "5k", "10k", "volleyball", "sports", "tournament",
                "match", "league", "fitness"]
    if any(kw in t for kw in sport_kw):
        return "Sports & Fitness"

    # Education
    edu_kw = ["workshop", "class", "seminar", "lecture", "webinar",
              "conference", "summit", "talk", "panel", "hackathon",
              "bootcamp", "training", "course", "learn"]
    if any(kw in t for kw in edu_kw):
        return "Education"

    # Community (default for desi events)
    return "Community"

def search_ticketmaster(keyword, state_code=None):
    """Search Ticketmaster Discovery API for events."""
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": TM_KEY,
        "keyword": keyword,
        "countryCode": "US",
        "size": 50,
        "sort": "date,asc",
        "startDateTime": f"{TODAY}T00:00:00Z",
    }
    if state_code:
        params["stateCode"] = state_code

    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            print(f"  Rate limited, waiting 2s...")
            time.sleep(2)
            r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()
        events = data.get("_embedded", {}).get("events", [])
        return events
    except Exception as e:
        print(f"  Error searching TM for {keyword}: {e}")
        return []

def tm_event_to_row(ev):
    """Convert a Ticketmaster event to a Supabase row."""
    title = ev.get("name", "")
    eid = ev.get("id", "")

    # Date/time
    dates = ev.get("dates", {}).get("start", {})
    date_str = dates.get("localDate", "")
    time_str = dates.get("localTime", "")

    # Venue
    venues = ev.get("_embedded", {}).get("venues", [{}])
    venue = venues[0] if venues else {}
    venue_name = venue.get("name", "")
    city = venue.get("city", {}).get("name", "")
    state = venue.get("state", {}).get("stateCode", "")

    # Location
    loc = venue.get("location", {})
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    if lat:
        try:
            lat = float(lat)
        except:
            lat = None
    if lon:
        try:
            lon = float(lon)
        except:
            lon = None

    # Image
    images = ev.get("images", [])
    image_url = ""
    if images:
        # Prefer 16:9 ratio, larger
        best = sorted(images, key=lambda i: i.get("width", 0), reverse=True)
        image_url = best[0].get("url", "") if best else ""

    # Ticket URL
    ticket_url = ev.get("url", "")

    # Price
    price_ranges = ev.get("priceRanges", [])
    price_range = ""
    if price_ranges:
        pr = price_ranges[0]
        mn = pr.get("min", "")
        mx = pr.get("max", "")
        currency = pr.get("currency", "USD")
        if mn and mx:
            price_range = f"${mn:.0f} - ${mx:.0f}"
        elif mn:
            price_range = f"From ${mn:.0f}"

    # Seatmap
    seatmap = ev.get("seatmap", {})
    seatmap_url = seatmap.get("staticUrl", "") if seatmap else ""

    # Description
    desc = ev.get("info", "") or ev.get("pleaseNote", "") or ""

    slug = slugify(f"{title}-{city}-{date_str}")
    category = categorize_event(title, desc)

    row = {
        "title": title,
        "date": date_str,
        "time": time_str or None,
        "venue_name": venue_name,
        "city": city,
        "state": state,
        "category": category,
        "description": desc[:500] if desc else None,
        "image_url": image_url,
        "ticket_url": ticket_url,
        "source": "ticketmaster",
        "source_id": f"tm-{eid}",
        "price_range": price_range or None,
        "slug": slug,
        "latitude": lat,
        "longitude": lon,
    }
    if seatmap_url:
        row["seatmap_url"] = seatmap_url

    return row

def upsert_events(rows):
    """Upsert events into Supabase."""
    if not rows:
        return 0
    # Batch in groups of 50
    total = 0
    for i in range(0, len(rows), 50):
        batch = rows[i:i+50]
        r = requests.post(
            f"{REST}/events",
            headers={**HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"},
            json=batch,
            timeout=30,
        )
        if r.status_code in (200, 201):
            result = r.json()
            count = len(result) if isinstance(result, list) else 1
            total += count
        else:
            print(f"  Upsert error: {r.status_code} {r.text[:200]}")
    return total

def _curl_nominatim(query):
    """Hit Nominatim via curl subprocess (requests hangs through proxy)."""
    from urllib.parse import urlencode
    params = urlencode({"q": query, "format": "json", "limit": 1, "countrycodes": "us"})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}", url,
        "-H", "User-Agent: TheVideshi/1.0 (events geocoder)",
        "--max-time", "10",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    output = result.stdout.strip()
    lines = output.rsplit("\n", 1)
    body = lines[0] if len(lines) > 1 else ""
    status = int(lines[-1]) if lines[-1].isdigit() else 0
    if status == 200 and body:
        results = json.loads(body)
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    return None, None


def geocode_nominatim(venue, city, state=""):
    """Geocode an address using Nominatim (free, no API key)."""
    query = f"{venue}, {city}"
    if state:
        query += f", {state}"
    query += ", USA"

    try:
        lat, lon = _curl_nominatim(query)
        if lat and lon:
            return lat, lon
        # Try with just city
        fallback = f"{city}, {state}, USA" if state else f"{city}, USA"
        return _curl_nominatim(fallback)
    except Exception as e:
        print(f"  Geocode error for {venue}, {city}: {e}")
    return None, None

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"=== Events Maintenance — {TODAY} ===\n")

    # 1. Delete past events
    print("--- Step 1: Delete past events ---")
    r = requests.get(
        f"{REST}/events?select=id&date=lt.{TODAY}",
        headers=HEADERS,
        timeout=15,
    )
    past_events = r.json() if r.status_code == 200 else []
    if past_events and isinstance(past_events, list) and len(past_events) > 0:
        # Delete them
        dr = requests.delete(
            f"{REST}/events?date=lt.{TODAY}",
            headers={**HEADERS, "Prefer": "return=representation"},
            timeout=15,
        )
        if dr.status_code in (200, 204):
            deleted = dr.json() if dr.status_code == 200 else []
            count = len(deleted) if isinstance(deleted, list) else 0
            print(f"  Deleted {count} past events")
        else:
            print(f"  Delete error: {dr.status_code}")
    else:
        print("  No past events to delete")

    # 2. Ticketmaster refresh
    print("\n--- Step 2: Ticketmaster artist search ---")
    all_tm_rows = []
    seen_source_ids = set()

    for search in TM_ARTIST_SEARCHES:
        kw = search["keyword"]
        events = search_ticketmaster(kw)
        new_count = 0
        for ev in events:
            row = tm_event_to_row(ev)
            if row["source_id"] not in seen_source_ids:
                seen_source_ids.add(row["source_id"])
                all_tm_rows.append(row)
                new_count += 1
        if new_count > 0:
            print(f"  {kw}: {new_count} events")
        time.sleep(0.25)  # Rate limit courtesy

    # Also search by state for broader Indian events
    print("\n--- Step 2b: Ticketmaster state searches ---")
    state_keywords = ["bollywood", "indian", "desi", "bhangra"]
    for state in TM_STATES:
        for kw in state_keywords:
            events = search_ticketmaster(kw, state_code=state)
            new_count = 0
            for ev in events:
                row = tm_event_to_row(ev)
                if row["source_id"] not in seen_source_ids:
                    seen_source_ids.add(row["source_id"])
                    all_tm_rows.append(row)
                    new_count += 1
            if new_count > 0:
                print(f"  {state}/{kw}: {new_count} events")
            time.sleep(0.2)

    print(f"\n  Total Ticketmaster events to upsert: {len(all_tm_rows)}")
    if all_tm_rows:
        upserted = upsert_events(all_tm_rows)
        print(f"  Upserted: {upserted}")

    # 3. Geocode events missing coordinates
    print("\n--- Step 3: Geocode events missing coordinates ---")
    r = requests.get(
        f"{REST}/events?select=id,title,venue_name,city,state&latitude=is.null&longitude=is.null",
        headers=HEADERS,
        timeout=15,
    )
    if r.status_code != 200:
        print(f"  Error fetching ungeolocated events: {r.status_code}")
        return

    missing = r.json()
    if not isinstance(missing, list):
        print(f"  Unexpected response: {str(missing)[:200]}")
        return

    # Cap geocoding to 75 per run to stay within cron timeout (Nominatim: 1 req/sec)
    GEOCODE_BATCH = 75
    total_missing = len(missing)
    if total_missing > GEOCODE_BATCH:
        print(f"  {total_missing} events need geocoding, processing batch of {GEOCODE_BATCH}")
        missing = missing[:GEOCODE_BATCH]
    else:
        print(f"  {total_missing} events need geocoding")
    geocoded = 0
    failed = 0

    for ev in missing:
        eid = ev["id"]
        venue = ev.get("venue_name", "")
        city = ev.get("city", "")
        state = ev.get("state", "")

        lat, lon = geocode_nominatim(venue, city, state)
        if lat and lon:
            # Update via curl (requests.patch fails through proxy)
            try:
                status, _ = curl_supabase(
                    "PATCH",
                    f"/events?id=eq.{eid}",
                    json_data={"latitude": lat, "longitude": lon},
                    prefer="return=minimal",
                )
                if status in (200, 204):
                    geocoded += 1
                else:
                    print(f"  Update error for {eid}: HTTP {status}")
                    failed += 1
            except Exception as e:
                print(f"  Curl error for {eid}: {e}")
                failed += 1
        else:
            failed += 1
            print(f"  Could not geocode: {ev.get('title', '?')[:50]} | {venue} | {city}")

        time.sleep(1.1)  # Nominatim rate limit: 1 req/sec

    print(f"  Geocoded: {geocoded}, Failed: {failed}")

    # 4. Final count
    try:
        status, body = curl_supabase("GET", f"/events?select=id&date=gte.{TODAY}")
        if status == 200:
            data = json.loads(body)
            total = len(data) if isinstance(data, list) else "?"
        else:
            total = "?"
    except Exception:
        total = "?"
    print(f"\n=== Done. Total active events: {total} ===")

if __name__ == "__main__":
    main()
