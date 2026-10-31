#!/usr/bin/env python3
"""
temple-events-scraper.py — Scrape events from Hindu temple websites.

Reads pipeline/temple-directory.json for the temple list. Each temple has a
parser_type that determines the extraction strategy:
- static_html: parse event listings from server-rendered HTML
- json_ld: extract schema.org/Event blocks
- google_calendar: extract embedded Google Calendar
- angular_spa: JS-rendered, API discovery needed (currently skipped)
- rss: parse RSS/Atom feed
- hindutemples_info: scrape Upcoming Festivals from hindutemples.info temple page

Usage:
    python3 pipeline/temple-events-scraper.py              # Full scrape
    python3 pipeline/temple-events-scraper.py --dry-run     # Print only
    python3 pipeline/temple-events-scraper.py --temple "Sunnyvale"
"""

import json
import os
import re
import sys
import subprocess
import hashlib
import argparse
from datetime import datetime, timezone

sys.stdout.reconfigure(line_buffering=True)

UA = "TheVideshi/1.0 (thevideshi.com; events)"

ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")
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
}

DIR_FILE = os.path.join(os.path.dirname(__file__), "temple-directory.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from event_geocode import geocode_venue


def curl_get(url, timeout=25):
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "-A", UA,
           "-w", "\n%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout + 10)
        out = r.stdout
        if "\n" in out:
            body, code = out.rsplit("\n", 1)
            try:
                return int(code.strip()), body
            except ValueError:
                pass
        return 0, ""
    except Exception:
        return 0, ""


def curl_post(url, data, timeout=30):
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-X", "POST",
           "-w", "\n%{http_code}", url]
    for k, v in HEADERS.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["-d", json.dumps(data)])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout + 10)
        out = r.stdout
        if "\n" in out:
            body, code = out.rsplit("\n", 1)
            try:
                return int(code.strip()), body
            except ValueError:
                pass
        return 0, ""
    except Exception:
        return 0, ""


STATE_NAME_TO_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
}


def extract_page_city_state(html):
    """hindutemples.info pages state the temple's real city in their
    og:description: '<Name> in <City>, <State Name>. Address: ...'.
    Many directory entries (41-city expansion, 2026-10-10) carry no
    city/state fields — without this, their events insert with empty
    city/state and are invisible to every city feed. Returns
    (city, state_abbr) or ('', '')."""
    # Temple names can themselves contain " in <City>" ("Sri
    # Guruvayurappan Temple in Dallas in Carrollton, Texas. Address:")
    # — a greedy name group makes the LAST " in " the city boundary.
    tag = re.search(
        r'property="og:description"\s+content="([^"]+)"', html)
    if not tag:
        return "", ""
    m = re.match(
        r"(.+) in ([A-Z][A-Za-z .-]+),\s+([A-Z][A-Za-z ]+)\.\s+Address:",
        tag.group(1),
    )
    if not m:
        return "", ""
    city, state_name = m.group(2), m.group(3)
    abbr = STATE_NAME_TO_ABBR.get(state_name.strip(), "")
    return (city.strip(), abbr) if abbr else ("", "")


VALID_STATE_ABBRS = set(STATE_NAME_TO_ABBR.values())
_NON_CITY_TOKENS = {"mandir", "temple", "church", "mosque", "gurudwara",
                    "gurdwara", "center", "centre", "hall"}


def city_state_valid(city, state):
    """True only when state is a real US abbreviation and city is a
    plausible city name. The 41-city expansion (2026-10-10) produced a
    garbled entry (BAPS Orlando: city='Mandir', state='Orlando' — the
    venue string split on the wrong token) whose non-empty fields sailed
    past both the page-recovery check and the empty-field insert guard,
    publishing events under a nonsense city. Validity, not non-emptiness,
    is the bar (2026-10-30)."""
    if not city or not state:
        return False
    if state.strip().upper() not in VALID_STATE_ABBRS:
        return False
    if city.strip().lower() in _NON_CITY_TOKENS:
        return False
    return True


def slugify(text):
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s[:80].strip("-")


def parse_json_ld_events(html, temple):
    """Extract schema.org/Event blocks from HTML."""
    events = []
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>',
        html, re.DOTALL
    )
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("@type") != "Event":
                continue
            name = item.get("name", "").strip()
            if not name:
                continue
            start = item.get("startDate", "")
            date = start[:10] if len(start) >= 10 else ""
            loc = item.get("location", {})
            if isinstance(loc, dict):
                venue = loc.get("name", temple["name"])
                addr = loc.get("address", {})
                if isinstance(addr, dict):
                    city = addr.get("addressLocality", temple["city"])
                else:
                    city = temple["city"]
            else:
                venue, city = temple["name"], temple["city"]
            url = item.get("url", temple["events_url"])
            events.append({
                "title": name,
                "date": date,
                "venue_name": venue,
                "city": city,
                "state": temple["state"],
                "ticket_url": url,
                "source": "temple",
                "source_id": f"temple_{hashlib.md5(f'{name}_{date}_{city}'.encode()).hexdigest()[:16]}",
                "slug": slugify(f"{name}-{city}-{date}"),
                "category": "Spiritual",
            })
    return events


def parse_static_html_events(html, temple):
    """Best-effort parse of event listings from static HTML.
    Looks for common patterns: event titles in headings with dates nearby."""
    events = []
    # Pattern 1: <a> tags with event-like text and date patterns nearby
    # This is intentionally conservative — only picks up clear event listings
    seen = set()
    # Find date patterns (MM/DD/YYYY, Month DD, YYYY, etc.)
    date_pat = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,?\s+\d{4})?|\d{1,2}/\d{1,2}/\d{2,4})"
    for m in re.finditer(
        r"<(?:h[1-4]|a)[^>]*>([^<>]{10,120})</(?:h[1-4]|a)>", html
    ):
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        if len(title) < 10 or title in seen:
            continue
        # Check if it looks like an event (not nav/menu)
        t = title.lower()
        if any(x in t for x in ["home", "about", "contact", "donate", "login",
                                 "menu", "search", "subscribe"]):
            continue
        # Look for a date within 500 chars after the title
        context = html[m.end():m.end() + 500]
        dm = re.search(date_pat, context, re.IGNORECASE)
        if dm:
            seen.add(title)
            events.append({
                "title": title,
                "date": dm.group(1),
                "venue_name": temple["name"],
                "city": temple["city"],
                "state": temple["state"],
                "ticket_url": temple["events_url"],
                "source": "temple",
                "source_id": f"temple_{hashlib.md5(f'{title}_{dm.group(1)}'.encode()).hexdigest()[:16]}",
                "slug": slugify(f"{title}-{temple['city']}-{dm.group(1)}"),
                "category": "Spiritual",
            })
    return events


def parse_hindutemples_info_events(html, temple):
    """Extract Upcoming Festivals from hindutemples.info temple page.

    Each festival is in <li class="list-group-item"> with:
    - <strong>Festival Name</strong>
    - optional <div class="small text-muted">description</div>
    - <div class="text-end">Date or Start – End</div>
    Only major festivals/homams/cultural events — this source lists
    festivals only, no weekly pujas, matching Kiran's bar.
    """
    events = []
    idx = html.find("Upcoming Festivals")
    if idx < 0:
        return events
    section = html[idx:idx + 12000]
    items = re.findall(
        r'<li class="list-group-item[^"]*">(.*?)</li>',
        section, re.DOTALL
    )
    for item in items:
        nm = re.search(r"<strong>([^<]+)</strong>", item)
        if not nm:
            continue
        name = nm.group(1).strip()
        if not name or len(name) < 2:
            continue
        dm = re.search(
            r'<div class="small text-muted[^"]*">(.*?)</div>',
            item, re.DOTALL
        )
        desc = re.sub(r"\s+", " ", dm.group(1)).strip() if dm else ""
        dtm = re.search(
            r'<div class="text-end[^"]*">(.*?)</div>', item, re.DOTALL
        )
        if not dtm:
            continue
        date_raw = re.sub(r"\s+", " ", dtm.group(1)).strip()
        dates = [d.strip() for d in re.split(r"\s*[–-]\s*", date_raw)]
        start_date = ""
        for fmt in ("%b %d, %Y", "%B %d, %Y"):
            try:
                start_date = datetime.strptime(dates[0], fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        if not start_date:
            continue
        # Skip past events
        if start_date < datetime.now(timezone.utc).strftime("%Y-%m-%d"):
            continue
        # Temple name MUST be part of the id: festival+date+city alone
        # collides across temples in the same city (Houston's Jalaram and
        # Guruvayurappan temples share every festival sid, so whichever
        # temple scraped first permanently blocked the other's events).
        sid = hashlib.md5(
            f"hindutemples_{temple['name']}_{name}_{start_date}_"
            f"{temple['city']}".encode()
        ).hexdigest()[:16]
        events.append({
            "title": f"{name} at {temple['name']}",
            "date": start_date,
            "venue_name": temple["name"],
            "city": temple["city"],
            "state": temple["state"],
            "ticket_url": temple.get("website") or temple.get("events_url"),
            "source": "temple",
            "source_id": f"temple_{sid}",
            "slug": slugify(
                f"{name}-{temple['name']}-{temple['city']}-{start_date}"),
            "category": "Spiritual",
            "description": desc,
        })
    return events


def scrape_temple(temple):
    """Scrape a single temple's events page."""
    parser = temple.get("parser_type", "static_html")
    url = temple.get("events_url") or temple.get("website")

    if parser == "angular_spa":
        print(f"  ⏭ {temple['name']}: SPA - needs API discovery, skipping")
        return []

    if parser == "hindutemples_info":
        status, html = curl_get(url)
        if status != 200 or not html:
            print(f"  ⚠ {temple['name']}: fetch failed ({status})")
            return []
        # Directory entries without city/state: recover both from the
        # page itself (og:description states the temple's real city).
        # Invalid (garbled/swapped) fields get the same recovery chance.
        if not city_state_valid(temple.get("city", ""), temple.get("state", "")):
            city, state = extract_page_city_state(html)
            if city and state:
                temple = {**temple, "city": city, "state": state}
                print(f"     (city/state from page: {city}, {state})")
        events = parse_hindutemples_info_events(html, temple)
        print(f"  ✓ {temple['name']}: {len(events)} festivals")
        return events

    if not url:
        print(f"  ⏭ {temple['name']}: no events URL")
        return []

    status, html = curl_get(url)
    if status != 200 or not html:
        print(f"  ⚠ {temple['name']}: fetch failed ({status})")
        return []

    events = []
    # Always try JSON-LD first (most reliable)
    events.extend(parse_json_ld_events(html, temple))
    # Fall back to static HTML parsing
    if not events and parser == "static_html":
        events.extend(parse_static_html_events(html, temple))

    print(f"  ✓ {temple['name']}: {len(events)} events")
    return events


def get_existing_source_ids():
    status, body = curl_get(
        f"{REST}/events?select=source_id&source=eq.temple&limit=5000",
        timeout=15,
    )
    # curl_get doesn't send auth headers; use direct curl for Supabase
    cmd = ["curl", "-sS", "--max-time", "15",
           f"{REST}/events?select=source_id&source=eq.temple&limit=5000",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        rows = json.loads(r.stdout)
        return {e["source_id"] for e in rows if e.get("source_id")}
    except Exception:
        return set()


def insert_events(events):
    if not events:
        return 0
    # Geocode at insert time: coord-less events are invisible to the site's
    # ZIP / near-me radius search. One Nominatim lookup per unique venue
    # (cached in event_geocode); failures stay NULL and are logged.
    venues = {(ev.get("venue_name", ""), ev.get("city", ""), ev.get("state", ""))
              for ev in events}
    coords = {}
    for venue, city, state in sorted(venues):
        lat, lon, level = geocode_venue(venue, city, state)
        if lat is not None:
            coords[(venue, city, state)] = (lat, lon)
            print(f"    📍 {venue} ({city}, {state}): {level} → {lat:.4f},{lon:.4f}")
        else:
            print(f"    ⚠ Could not geocode venue: {venue} ({city}, {state}) — event coords stay NULL")
    for ev in events:
        c = coords.get((ev.get("venue_name", ""), ev.get("city", ""), ev.get("state", "")))
        if c:
            ev["latitude"], ev["longitude"] = c
    inserted = 0
    for ev in events:
        ev["updated_at"] = datetime.now(timezone.utc).isoformat()
        status, body = curl_post(f"{REST}/events", [ev])
        if status in (200, 201):
            inserted += 1
        else:
            print(f"    ⚠ Insert failed for '{ev['title'][:40]}' ({status})")
    return inserted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--temple", type=str, default=None,
                    help="Filter to temple name substring")
    args = ap.parse_args()

    with open(DIR_FILE) as f:
        directory = json.load(f)

    temples = directory["temples"]
    if args.temple:
        temples = [t for t in temples
                   if args.temple.lower() in t["name"].lower()]

    print(f"🛕 Scraping {len(temples)} temples...\n")

    all_events = []
    for temple in temples:
        all_events.extend(scrape_temple(temple))

    # Deduplicate by source_id
    seen = set()
    unique = []
    for ev in all_events:
        if ev["source_id"] not in seen:
            seen.add(ev["source_id"])
            unique.append(ev)

    print(f"\n📊 {len(unique)} unique temple events found")

    if args.dry_run:
        for ev in unique[:20]:
            print(f"  - {ev['title'][:60]} | {ev['date']} | "
                  f"{ev['city']}, {ev['state']}")
        return

    existing = get_existing_source_ids()
    new = [e for e in unique if e["source_id"] not in existing]

    # Secondary dedupe on title+date+city: the hindutemples source_id
    # hash gained the temple name (2026-10-18), so events inserted
    # under the old colliding hash look "new" by id — never re-insert
    # a row the table already carries under another id.
    cmd = ["curl", "-sS", "--max-time", "20",
           f"{REST}/events?select=title,date,city&source=eq.temple"
           "&limit=5000",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        existing_tdc = {
            (e["title"].strip().lower(), e["date"],
             (e.get("city") or "").strip().lower())
            for e in json.loads(r.stdout)
        }
    except Exception:
        existing_tdc = set()
    before = len(new)
    new = [e for e in new
           if (e["title"].strip().lower(), e["date"],
               (e.get("city") or "").strip().lower()) not in existing_tdc]
    if before != len(new):
        print(f"  Title+date+city dedupe skipped {before - len(new)} more")

    # Never insert an event with empty or invalid city/state: it is
    # invisible to every city feed and pollutes the table. (Invalid =
    # state not a US abbreviation or city a venue word like 'Mandir' —
    # the BAPS Orlando garble, 2026-10-30.)
    located = [e for e in new
               if city_state_valid(e.get("city", ""), e.get("state", ""))]
    if len(located) != len(new):
        print(f"  ⚠ Dropped {len(new) - len(located)} events with "
              "empty/invalid city/state")
    new = located
    print(f"  New: {len(new)} (skipping {len(unique) - len(new)} existing)")

    inserted = insert_events(new)
    print(f"✅ Inserted {inserted} temple events")

    # Feed rebuild so new events reach the site's static feeds (festivals hub,
    # Your Hub read /data/events.json). Guarded: skip when nothing was inserted.
    if inserted > 0:
        try:
            prebuild = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "prebuild-feeds.py")
            r = subprocess.run([sys.executable, "-u", prebuild],
                               capture_output=True, text=True, timeout=900)
            print(r.stdout[-1500:] if r.stdout else "")
            if r.returncode != 0:
                print(f"⚠ prebuild-feeds.py failed (rc={r.returncode}): "
                      f"{(r.stderr or '')[-500:]}")
            else:
                print("✅ Feeds rebuilt — new temple events will go out with the next push")
        except Exception as e:
            print(f"⚠ Feed rebuild skipped: {e}")


if __name__ == "__main__":
    main()
