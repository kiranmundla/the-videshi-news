#!/usr/bin/env python3
"""
events-tm-refresh-v2.py — Refresh Ticketmaster events using CLI tool.
Checks existing source_ids first, inserts only truly new events.
"""

import json
import os
import sys
import re
import subprocess
import time
import hashlib
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

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
}

ARTIST_KEYWORDS = [
    "Diljit Dosanjh", "Shreya Ghoshal", "Sonu Nigam", "Arijit Singh",
    "AR Rahman", "Atif Aslam", "Neha Kakkar", "Badshah", "AP Dhillon",
    "Karan Aujla", "Armaan Malik", "Amit Trivedi", "Sunidhi Chauhan",
    "Jubin Nautiyal", "Darshan Raval", "Nucleya", "Pritam",
    "Vishal Shekhar", "Kumar Sanu", "Lucky Ali",
]

STATE_KEYWORDS = ["bollywood", "indian", "desi", "bhangra", "garba"]
STATES = ["CA", "TX", "NY", "NJ", "IL", "GA", "WA", "MA", "PA", "VA",
          "MD", "NC", "FL", "OH", "MI", "CT", "AZ", "CO", "MN", "OR"]

FALSE_POSITIVE_PATTERNS = [
    r"\bcasino\b", r"\bslot\b", r"\bpoker\b",
    r"\bindian wells\b", r"\bindianapolis\b", r"\bindian motorcycle\b",
    r"\bindian rocks\b", r"\bindian trail\b", r"\bindian river\b",
    r"\bindian head\b", r"\bindian lake\b", r"\bindian mound\b",
]

def is_false_positive(title):
    t = title.lower()
    for pat in FALSE_POSITIVE_PATTERNS:
        if re.search(pat, t):
            return True
    return False

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:80].strip('-')

def categorize(title):
    t = title.lower()
    spiritual_kw = ["temple", "mandir", "kirtan", "bhajan", "puja", "satsang",
                     "meditation", "yoga", "vedic", "bhakti", "spiritual", "dharma",
                     "gita", "iskcon", "baps", "guru", "havan", "aarti"]
    if any(kw in t for kw in spiritual_kw):
        return "Spiritual"
    ent_kw = ["concert", "bollywood", "music", "dance", "comedy", "show",
              "tour", "festival", "mela", "bhangra", "garba", "dandiya",
              "dj ", "party", "night", "live", "singer"]
    if any(kw in t for kw in ent_kw):
        return "Entertainment"
    sport_kw = ["cricket", "kabaddi", "badminton", "marathon", "run ",
                "volleyball", "sports", "tournament"]
    if any(kw in t for kw in sport_kw):
        return "Sports & Fitness"
    return "Community"

def fetch_tm(keyword, state_code=None, size=20):
    cmd = ["ticketmaster", "search-events",
           "--keyword", keyword, "--size", str(size), "--sort", "date,asc"]
    if state_code:
        cmd += ["--state-code", state_code]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        return data.get("events", [])
    except Exception as e:
        print(f"  Error: {keyword}/{state_code}: {e}")
        return []

def event_to_row(evt):
    title = evt.get("name", "").strip()
    city = evt.get("city", "")
    state = evt.get("state", "")
    date = evt.get("date", "")
    tm_time = evt.get("time", "")
    venue = evt.get("venue", "")
    ticket_url = evt.get("url", "")
    price = evt.get("price_range", "")
    tm_id = evt.get("id", "") or evt.get("hex_id", "")

    if not tm_id:
        tm_id = hashlib.md5(f"{title}_{date}_{city}".encode()).hexdigest()[:16]

    time_display = ""
    if tm_time:
        try:
            t = datetime.strptime(tm_time, "%H:%M:%S")
            time_display = t.strftime("%-I:%M %p")
        except:
            time_display = tm_time

    slug = slugify(f"{title}-{city}-{date}")
    category = categorize(title)

    return {
        "title": title,
        "date": date,
        "time": time_display or None,
        "venue_name": venue,
        "city": city,
        "state": state,
        "category": category,
        "source": "ticketmaster",
        "source_id": f"tm_{tm_id}",  # underscore to match existing convention
        "ticket_url": ticket_url,
        "price_range": price or None,
        "slug": slug,
    }

def get_existing_source_ids():
    """Get all existing TM source_ids."""
    r = requests.get(
        f"{REST}/events?select=source_id&source=eq.ticketmaster",
        headers=HEADERS, timeout=15,
    )
    if r.status_code == 200:
        return {e["source_id"] for e in r.json()}
    return set()

def get_existing_slugs():
    """Get all existing slugs."""
    r = requests.get(
        f"{REST}/events?select=slug",
        headers=HEADERS, timeout=15,
    )
    if r.status_code == 200:
        return {e["slug"] for e in r.json() if e.get("slug")}
    return set()

def insert_events(rows, existing_slugs):
    """Insert events one batch at a time, handling slug conflicts."""
    if not rows:
        return 0

    inserted = 0
    # Deduplicate slugs within the batch
    used_slugs = set(existing_slugs)
    for row in rows:
        slug = row["slug"]
        if slug in used_slugs:
            # Append a short hash to make unique
            suffix = hashlib.md5(row["source_id"].encode()).hexdigest()[:6]
            row["slug"] = f"{slug[:73]}-{suffix}"
        used_slugs.add(row["slug"])

    # Insert in batches of 20
    for i in range(0, len(rows), 20):
        batch = rows[i:i+20]
        r = requests.post(
            f"{REST}/events",
            headers={**HEADERS, "Prefer": "return=representation"},
            json=batch, timeout=30,
        )
        if r.status_code in (200, 201):
            result = r.json()
            count = len(result) if isinstance(result, list) else 1
            inserted += count
        else:
            # Try one by one
            for row in batch:
                r2 = requests.post(
                    f"{REST}/events",
                    headers={**HEADERS, "Prefer": "return=minimal"},
                    json=row, timeout=15,
                )
                if r2.status_code in (200, 201):
                    inserted += 1
                else:
                    print(f"  Skip: {row['title'][:40]} ({r2.status_code})")
    return inserted

def update_existing_events(rows, existing_source_ids):
    """Update existing TM events (refresh dates, prices, URLs)."""
    updated = 0
    for row in rows:
        if row["source_id"] in existing_source_ids:
            # Update mutable fields
            patch = {
                "date": row["date"],
                "time": row["time"],
                "ticket_url": row["ticket_url"],
                "price_range": row["price_range"],
            }
            r = requests.patch(
                f"{REST}/events?source_id=eq.{row['source_id']}",
                headers={**HEADERS, "Prefer": "return=minimal"},
                json=patch, timeout=10,
            )
            if r.status_code in (200, 204):
                updated += 1
    return updated

def main():
    print("=== Ticketmaster Refresh v2 ===\n")

    existing_source_ids = get_existing_source_ids()
    existing_slugs = get_existing_slugs()
    print(f"Existing TM events: {len(existing_source_ids)}")
    print(f"Existing slugs: {len(existing_slugs)}")

    all_rows = []
    seen = set()

    # Artist searches
    print("\n--- Artist searches ---")
    for kw in ARTIST_KEYWORDS:
        events = fetch_tm(kw, size=50)
        new = 0
        for evt in events:
            title = evt.get("name", "")
            if is_false_positive(title):
                continue
            row = event_to_row(evt)
            if row["source_id"] not in seen:
                seen.add(row["source_id"])
                all_rows.append(row)
                new += 1
        if new > 0:
            print(f"  {kw}: {new} events")
        time.sleep(0.15)

    # State keyword searches
    print("\n--- State keyword searches ---")
    for state in STATES:
        for kw in STATE_KEYWORDS:
            events = fetch_tm(kw, state_code=state, size=20)
            new = 0
            for evt in events:
                title = evt.get("name", "")
                if is_false_positive(title):
                    continue
                row = event_to_row(evt)
                if row["source_id"] not in seen:
                    seen.add(row["source_id"])
                    all_rows.append(row)
                    new += 1
            if new > 0:
                print(f"  {state}/{kw}: {new} events")
            time.sleep(0.1)

    print(f"\nTotal unique TM events found: {len(all_rows)}")

    # Split into new vs existing
    new_rows = [r for r in all_rows if r["source_id"] not in existing_source_ids]
    update_rows = [r for r in all_rows if r["source_id"] in existing_source_ids]

    print(f"  New events to insert: {len(new_rows)}")
    print(f"  Existing events to update: {len(update_rows)}")

    if new_rows:
        inserted = insert_events(new_rows, existing_slugs)
        print(f"  Inserted: {inserted}")

    if update_rows:
        updated = update_existing_events(update_rows, existing_source_ids)
        print(f"  Updated: {updated}")

    # Final count
    r = requests.get(
        f"{REST}/events?select=id",
        headers=HEADERS, timeout=15,
    )
    total = len(r.json()) if r.status_code == 200 else "?"
    print(f"\nTotal events in DB: {total}")

if __name__ == "__main__":
    main()
