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

DIR_FILE = os.path.join(os.path.dirname(__file__), "temple-directory.json")


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


def scrape_temple(temple):
    """Scrape a single temple's events page."""
    parser = temple.get("parser_type", "static_html")
    url = temple.get("events_url") or temple.get("website")

    if parser == "angular_spa":
        print(f"  ⏭ {temple['name']}: SPA - needs API discovery, skipping")
        return []

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
    print(f"  New: {len(new)} (skipping {len(unique) - len(new)} existing)")

    inserted = insert_events(new)
    print(f"✅ Inserted {inserted} temple events")


if __name__ == "__main__":
    main()
