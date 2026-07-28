#!/usr/bin/env python3
"""
scrape-temples.py — Scrape events from Hindu temple websites and upsert
them into the Supabase `events` table.

Sources are read from the `event_sources` table so adding a new temple
is just inserting a row — no code changes needed.

Parser types:
  baps           – BAPS center Upcoming-Events.aspx pages
  iskcon-wp      – WordPress-based ISKCON sites (/events/list/)
  iskcon-generic – Other ISKCON temple pages
  generic        – Standalone Hindu temple sites

Usage:
    python3 scrape-temples.py                 # Full scrape
    python3 scrape-temples.py --dry-run       # Print events without inserting
    python3 scrape-temples.py --parser baps   # Only scrape BAPS sources
    python3 scrape-temples.py --limit 5       # Limit to 5 sources (testing)
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, date, timezone

sys.stdout.reconfigure(line_buffering=True)

# ── Env ──────────────────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
    sys.exit(1)

# SUPABASE_URL already has https:// — strip it for curl
SB_HOST = SUPABASE_URL.replace("https://", "").replace("http://", "")
UA = "TheVideshi/1.0 (thevideshi.com; diaspora event aggregator)"

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def curl_text(url, timeout=20):
    """Fetch a URL and return the response text. Returns None on failure."""
    try:
        r = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-A", UA, url],
            capture_output=True, text=True, timeout=timeout + 10
        )
        if r.returncode != 0:
            print(f"  ⚠ curl error for {url}: {r.stderr[:200]}")
            return None
        return r.stdout
    except subprocess.TimeoutExpired:
        print(f"  ⚠ timeout fetching {url}")
        return None
    except Exception as e:
        print(f"  ⚠ fetch error for {url}: {e}")
        return None


def content_fingerprint(title, date_str, city):
    """Unified cross-source fingerprint: normalized title + date + city."""
    norm_title = re.sub(r"[^a-z0-9 ]", "", (title or "").lower().strip())[:60]
    norm_city = re.sub(r"[^a-z0-9]", "", (city or "").lower().strip())
    raw = f"{norm_title}|{date_str}|{norm_city}"
    return hashlib.md5(raw.encode()).hexdigest()


def make_slug(title, city, date_str):
    """Generate a URL-safe slug."""
    parts = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")[:50]
    city_slug = re.sub(r"[^a-z0-9]+", "-", (city or "").lower()).strip("-")[:15]
    return f"{parts}-{city_slug}-{date_str}" if city_slug else f"{parts}-{date_str}"


def parse_date_english(text):
    """Parse dates like 'Sunday, September 06, 2026 - 3:00 PM' or
    'Saturday, August 01, 2026 - 4:00 pm to 7:00 pm'.
    Returns (date_str YYYY-MM-DD, time_str HH:MM or None, end_time or None)."""
    text = text.strip()

    # Try: Day, Month DD, YYYY - H:MM AM/PM [to H:MM AM/PM]
    m = re.match(
        r"(?:\w+,?\s+)?(\w+)\s+(\d{1,2}),?\s+(\d{4})"
        r"(?:\s*[-–]\s*(\d{1,2}[:.]\d{2}\s*[AaPp][Mm]))?",
        text
    )
    if not m:
        return None, None, None

    month_name = m.group(1).lower()
    day = int(m.group(2))
    year = int(m.group(3))
    time_raw = m.group(4)

    month = MONTH_MAP.get(month_name)
    if not month:
        return None, None, None

    date_str = f"{year}-{month:02d}-{day:02d}"

    time_str = None
    if time_raw:
        time_str = normalize_time(time_raw)

    # Check for end time: "to H:MM AM/PM"
    end_time = None
    end_m = re.search(r"to\s+(\d{1,2}[:.]\d{2}\s*[AaPp][Mm])", text)
    if end_m:
        end_time = normalize_time(end_m.group(1))

    return date_str, time_str, end_time


def normalize_time(raw):
    """Convert '3:00 PM' or '4.00 pm' to '15:00'."""
    raw = raw.strip().replace(".", ":")
    m = re.match(r"(\d{1,2}):(\d{2})\s*([AaPp][Mm])", raw)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    ampm = m.group(3).upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


# ── DB operations ────────────────────────────────────────────────────────────

def fetch_event_sources(parser_filter=None):
    """Fetch enabled rows from event_sources table."""
    url = f"https://{SB_HOST}/rest/v1/event_sources?enabled=eq.true&select=*"
    if parser_filter:
        url += f"&parser=eq.{parser_filter}"
    url += "&order=parser,name"

    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse event_sources response: {r.stdout[:200]}")
        return []


def fetch_existing_fingerprints():
    """Fetch all existing content_fingerprints from the events table."""
    url = (f"https://{SB_HOST}/rest/v1/events"
           f"?select=content_fingerprint"
           f"&content_fingerprint=not.is.null"
           f"&date=gte.{date.today().isoformat()}"
           f"&limit=10000")
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    try:
        rows = json.loads(r.stdout)
        return {row["content_fingerprint"] for row in rows if row.get("content_fingerprint")}
    except:
        return set()


def upsert_event(record):
    """Upsert a single event to Supabase. Returns True on success."""
    payload = json.dumps(record)
    url = f"https://{SB_HOST}/rest/v1/events?on_conflict=source,source_id"

    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: resolution=merge-duplicates,return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )

    out = r.stdout.strip()
    if r.returncode != 0 or ('"code"' in out and '"message"' in out):
        if "duplicate" not in out.lower():
            print(f"    ⚠ Upsert failed for '{record.get('title', '?')[:40]}': {out[:200]}")
            return False
    return True


def update_last_scraped(source_id):
    """Update last_scraped_at timestamp for an event source."""
    now = datetime.now(timezone.utc).isoformat()
    payload = json.dumps({"last_scraped_at": now})
    url = f"https://{SB_HOST}/rest/v1/event_sources?id=eq.{source_id}"

    subprocess.run(
        ["curl", "-sS", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=15
    )


# ── BAPS Parser ──────────────────────────────────────────────────────────────

def parse_baps(html, source_row):
    """Parse a BAPS center Upcoming-Events.aspx page.

    Actual structure (confirmed from live pages):
      - Section is between 'Upcoming Events</h1>' and 'Latest News'
      - Each event lives inside a div.paddingLR10 containing:
          <h2><a title=" Event Name"> Event Name</a></h2>
          <div class="description borderbottom">
            Day, Month DD, YYYY - HH:MM AM/PM
          </div>
      - Some events have images in a sibling/parent col div
      - Some pages have no paddingLR10 (empty event list) — that's fine
    """
    events = []

    # Extract the events section
    match = re.search(r"Upcoming Events</h1>(.*?)Latest News", html, re.DOTALL)
    if not match:
        match = re.search(r"Upcoming Events</h1>(.*?)(?:<footer|</body)", html, re.DOTALL)
    if not match:
        return events

    section = match.group(1)

    # Find all paddingLR10 blocks — each one is an event
    blocks = list(re.finditer(
        r'paddingLR10[^>]*>(.*?)</div>\s*</div>',
        section, re.DOTALL
    ))
    if not blocks:
        # Fallback: split by h2 tags if no paddingLR10 blocks
        blocks = list(re.finditer(r'(<h2[^>]*>.*?</h2>.*?(?=<h2|$))', section, re.DOTALL))

    for block_match in blocks:
        block = block_match.group(1) if hasattr(block_match, 'group') else block_match

        # Extract title from <h2><a title="..."> or <h2> text
        title = None
        title_m = re.search(r'<a\s+title=["\']([^"\']+)["\']', block)
        if title_m:
            title = title_m.group(1).strip()
        else:
            title_m = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
            if title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()

        if not title or len(title) < 3:
            continue

        # Skip non-event lines (closures, notices)
        title_lower = title.lower()
        if any(skip in title_lower for skip in [
            "mandir is closed", "center closed", "no activities",
            "closed for", "holiday closure",
        ]):
            continue

        # Extract date from the description div or plain text
        date_text = None
        desc_m = re.search(r'class="description[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        if desc_m:
            date_text = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()
        else:
            # Fallback: find any date-like text
            dt_m = re.search(
                r"((?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)"
                r",?\s+(?:January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\s+\d{1,2},?\s+\d{4}"
                r"[^<\n]*)",
                block
            )
            if dt_m:
                date_text = dt_m.group(1).strip()

        if not date_text:
            continue

        # Handle multi-day events: "From Friday, October 02 to Sunday, October 04"
        multi_m = re.match(r"From\s+\w+,\s+(\w+\s+\d{1,2})\s+to\s+\w+,\s+(\w+\s+\d{1,2})", date_text)
        if multi_m:
            # Use the start date as the main date, and end date too
            start_text = multi_m.group(1) + f", {date.today().year}"
            end_text = multi_m.group(2) + f", {date.today().year}"
            date_str, time_str, _ = parse_date_english(start_text)
            end_date_str, _, _ = parse_date_english(end_text)
        else:
            date_str, time_str, _ = parse_date_english(date_text)
            end_date_str = None

        if not date_str:
            continue

        # Skip past events
        try:
            if datetime.strptime(date_str, "%Y-%m-%d").date() < date.today():
                continue
        except ValueError:
            continue

        # Look for image in nearby HTML (scan a window around this block)
        block_start = block_match.start()
        window = section[max(0, block_start - 500):block_start + len(block_match.group(0)) + 200]
        img_match = re.search(r'src=["\']([^"\']*(?:upcomingevents|eventimages|UpcomingEvents)[^"\']*)["\']', window, re.IGNORECASE)
        image_url = None
        if img_match:
            img_path = img_match.group(1)
            if not img_path.startswith("http"):
                img_path = f"https://www.baps.org{img_path}"
            image_url = img_path

        city = source_row.get("city") or ""
        state = source_row.get("state") or ""
        venue = source_row.get("name", "")

        event = {
            "title": title,
            "date": date_str,
            "time": time_str,
            "venue_name": venue,
            "city": city,
            "state": state,
            "category": "Spiritual",
            "ticket_url": source_row["url"],
            "organizer": "BAPS Swaminarayan Sanstha",
            "source": source_row.get("source", "baps"),
            "source_id": f"baps_{re.sub(r'[^a-z0-9]', '', city.lower())}_{hashlib.md5((title + date_str).encode()).hexdigest()[:8]}",
            "content_fingerprint": content_fingerprint(title, date_str, city),
            "slug": make_slug(title, city, date_str),
        }
        if image_url:
            event["image_url"] = image_url
        if end_date_str:
            event["end_date"] = end_date_str

        events.append(event)

    return events


# ── ISKCON WordPress Parser ──────────────────────────────────────────────────

def parse_iskcon_wp(html, source_row):
    """Parse WordPress-based ISKCON event pages (The Events Calendar plugin).

    Actual structure (confirmed from iskconnyc.com):
      - Events are in <article class="... post-NNNN tribe_events ...">
      - Title in <a> with event-url or event-title class
      - Date in <time datetime="YYYY-MM-DD">
      - Description in event-description div
      - Event URL in the title link
    """
    events = []

    # Find all <article> event blocks
    for m in re.finditer(r'<article[^>]*(?:post-\d+|tribe_events)[^>]*>(.*?)</article>', html, re.DOTALL):
        block = m.group(1)

        # Extract title from event-url/event-title link, then h3
        title = None
        for pattern in [
            r'<a[^>]*class="[^"]*event-(?:url|title)[^"]*"[^>]*>(.*?)</a>',
            r'<a[^>]*href="[^"]*event[^"]*"[^>]*>(.*?)</a>',
            r'<h3[^>]*>(.*?)</h3>',
        ]:
            title_m = re.search(pattern, block, re.DOTALL)
            if title_m:
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
                # Decode HTML entities
                title = title.replace("&#8211;", "–").replace("&#8212;", "—")
                title = title.replace("&amp;", "&").replace("&#039;", "'")
                break

        if not title or len(title) < 3:
            continue

        # Extract date from datetime attribute
        date_str = None
        time_str = None
        dt_m = re.search(r'datetime="(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}))?', block)
        if dt_m:
            date_str = dt_m.group(1)
            time_str = dt_m.group(2)

        if not date_str:
            # Fallback: find text date
            txt_m = re.search(
                r"((?:January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?)",
                block
            )
            if txt_m:
                date_str, time_str, _ = parse_date_english(txt_m.group(1))

        if not date_str:
            continue

        # Skip past events
        try:
            if datetime.strptime(date_str, "%Y-%m-%d").date() < date.today():
                continue
        except ValueError:
            continue

        # Extract time if not found yet
        if not time_str:
            time_m = re.search(r'(\d{1,2}:\d{2}\s*[AaPp][Mm])', block)
            if time_m:
                time_str = normalize_time(time_m.group(1))

        # Extract description
        description = None
        desc_m = re.search(r'description[^>]*>(.*?)</div>', block, re.DOTALL)
        if desc_m:
            description = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()
            description = re.sub(r'\s+', ' ', description)
            if len(description) > 500:
                description = description[:497] + "..."

        # Extract event URL
        link_m = re.search(r'href="(https?://[^"]*event[^"]*)"', block)
        ticket_url = link_m.group(1) if link_m else source_row["url"]

        # Extract image
        img_m = re.search(r'<img[^>]*src="(https?://[^"]+)"', block)
        image_url = img_m.group(1) if img_m else None

        city = source_row.get("city") or ""
        state = source_row.get("state") or ""
        venue = source_row.get("name", "")
        src = source_row.get("source", "iskcon")

        event = {
            "title": title,
            "date": date_str,
            "time": time_str,
            "venue_name": venue,
            "city": city,
            "state": state,
            "category": "Spiritual",
            "description": description,
            "ticket_url": ticket_url,
            "organizer": "ISKCON",
            "source": src,
            "source_id": f"iskcon_{re.sub(r'[^a-z0-9]', '', city.lower())}_{hashlib.md5((title + date_str).encode()).hexdigest()[:8]}",
            "content_fingerprint": content_fingerprint(title, date_str, city),
            "slug": make_slug(title, city, date_str),
        }
        if image_url:
            event["image_url"] = image_url

        events.append(event)

    return events


# ── ISKCON Generic Parser ────────────────────────────────────────────────────

def parse_iskcon_generic(html, source_row):
    """Parse various ISKCON temple pages — festival schedules, event lists.

    Looks for date patterns and event names in less structured pages.
    """
    events = []

    # Strategy: find all date-like strings and extract nearby event text
    # ISKCON festival schedules often list: "Date - Festival Name" or
    # "Festival Name\nDate"

    # Pattern: Month Day - Event Name (common in festival schedules)
    for m in re.finditer(
        r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?"
        r",?\s*((?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?)"
        r"\s*[-–:]\s*([^\n<]{5,100})",
        html
    ):
        date_text = m.group(1)
        event_text = re.sub(r"<[^>]+>", "", m.group(2)).strip()

        # If no year in date, assume current/next occurrence
        if not re.search(r"\d{4}", date_text):
            date_text = date_text.rstrip(",") + f", {date.today().year}"

        date_str, time_str, _ = parse_date_english(date_text)
        if not date_str:
            continue

        # Skip past events
        try:
            ev_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if ev_date < date.today():
                # Try next year
                next_year = f"{date.today().year + 1}-{date_str[5:]}"
                try:
                    if datetime.strptime(next_year, "%Y-%m-%d").date() >= date.today():
                        date_str = next_year
                    else:
                        continue
                except:
                    continue
        except ValueError:
            continue

        # Clean up event text
        title = re.sub(r"\(.*?\)", "", event_text).strip()
        title = re.sub(r"\s+", " ", title)
        if not title or len(title) < 5:
            continue
        # Skip garbage: titles that are mostly digits/punctuation or look like date fragments
        if re.match(r"^[\d,\s./\-]+$", title):
            continue
        # Skip non-event lines
        if any(skip in title.lower() for skip in ["break fast", "ekadasi", "fast till"]):
            continue

        city = source_row.get("city") or ""
        state = source_row.get("state") or ""
        venue = source_row.get("name", "")
        src = source_row.get("source", "iskcon")

        events.append({
            "title": title,
            "date": date_str,
            "time": time_str,
            "venue_name": venue,
            "city": city,
            "state": state,
            "category": "Spiritual",
            "ticket_url": source_row["url"],
            "organizer": "ISKCON",
            "source": src,
            "source_id": f"iskcon_{re.sub(r'[^a-z0-9]', '', city.lower())}_{hashlib.md5((title + date_str).encode()).hexdigest()[:8]}",
            "content_fingerprint": content_fingerprint(title, date_str, city),
            "slug": make_slug(title, city, date_str),
        })

    return events


# ── Generic Temple Parser ────────────────────────────────────────────────────

def parse_generic(html, source_row):
    """Best-effort parser for standalone temple websites.

    Searches for any recognizable event patterns:
    - Dates with event names
    - Calendar listings
    - Festival schedules
    """
    events = []

    # Strategy 1: Look for structured event data (JSON-LD)
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(m.group(1))
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") in ("Event", "SocialEvent", "MusicEvent", "Festival"):
                    title = item.get("name", "")
                    start = item.get("startDate", "")
                    if title and start:
                        date_str = start[:10]
                        time_str = None
                        if len(start) > 10 and "T" in start:
                            t = start.split("T")[1][:5]
                            time_str = t if re.match(r"\d{2}:\d{2}", t) else None

                        city = source_row.get("city") or ""
                        state = source_row.get("state") or ""

                        events.append({
                            "title": title,
                            "date": date_str,
                            "time": time_str,
                            "venue_name": source_row.get("name", ""),
                            "city": city,
                            "state": state,
                            "category": "Spiritual",
                            "ticket_url": item.get("url") or source_row["url"],
                            "organizer": source_row.get("name", ""),
                            "source": source_row.get("source", "temple"),
                            "source_id": f"temple_{re.sub(r'[^a-z0-9]', '', city.lower())}_{hashlib.md5((title + date_str).encode()).hexdigest()[:8]}",
                            "content_fingerprint": content_fingerprint(title, date_str, city),
                            "slug": make_slug(title, city, date_str),
                        })
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    # If JSON-LD found events, return those (more reliable)
    if events:
        return [e for e in events if e["date"] >= date.today().isoformat()]

    # Strategy 2: Same heuristic as iskcon-generic — date + event name
    for m in re.finditer(
        r"((?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?)"
        r"\s*[-–:,]\s*([^\n<]{5,120})",
        html
    ):
        date_text = m.group(1)
        event_text = re.sub(r"<[^>]+>", "", m.group(2)).strip()

        if not re.search(r"\d{4}", date_text):
            date_text = date_text.rstrip(",") + f", {date.today().year}"

        date_str, time_str, _ = parse_date_english(date_text)
        if not date_str:
            continue

        try:
            ev_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if ev_date < date.today():
                next_year = f"{date.today().year + 1}-{date_str[5:]}"
                try:
                    if datetime.strptime(next_year, "%Y-%m-%d").date() >= date.today():
                        date_str = next_year
                    else:
                        continue
                except:
                    continue
        except ValueError:
            continue

        title = re.sub(r"\s+", " ", event_text).strip()
        if not title or len(title) < 4:
            continue

        city = source_row.get("city") or ""
        state = source_row.get("state") or ""

        events.append({
            "title": title,
            "date": date_str,
            "time": time_str,
            "venue_name": source_row.get("name", ""),
            "city": city,
            "state": state,
            "category": "Spiritual",
            "ticket_url": source_row["url"],
            "organizer": source_row.get("name", ""),
            "source": source_row.get("source", "temple"),
            "source_id": f"temple_{re.sub(r'[^a-z0-9]', '', city.lower())}_{hashlib.md5((title + date_str).encode()).hexdigest()[:8]}",
            "content_fingerprint": content_fingerprint(title, date_str, city),
            "slug": make_slug(title, city, date_str),
        })

    return events


# ── Parser dispatch ──────────────────────────────────────────────────────────

PARSERS = {
    "baps": parse_baps,
    "iskcon-wp": parse_iskcon_wp,
    "iskcon-generic": parse_iskcon_generic,
    "generic": parse_generic,
}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape temple events")
    parser.add_argument("--dry-run", action="store_true", help="Print events without inserting")
    parser.add_argument("--parser", type=str, default=None, help="Only scrape sources with this parser type")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of sources to scrape")
    args = parser.parse_args()

    print(f"[{ts()}] Temple events scraper starting")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    if args.parser:
        print(f"  Parser filter: {args.parser}")

    # 1. Fetch sources from event_sources table
    sources = fetch_event_sources(args.parser)
    if not sources:
        print("  No enabled sources found.")
        return

    if args.limit:
        sources = sources[:args.limit]

    print(f"  Sources to scrape: {len(sources)}")

    # 2. Fetch existing fingerprints for cross-source dedup
    existing_fps = set()
    if not args.dry_run:
        existing_fps = fetch_existing_fingerprints()
        print(f"  Existing fingerprints loaded: {len(existing_fps)}")

    # 3. Scrape each source
    total_found = 0
    total_inserted = 0
    total_skipped_dup = 0
    total_skipped_past = 0
    sources_ok = 0
    sources_fail = 0

    for src in sources:
        name = src["name"]
        url = src["url"]
        parser_type = src["parser"]

        print(f"\n  📍 {name} [{parser_type}]")
        print(f"     {url}")

        parse_fn = PARSERS.get(parser_type)
        if not parse_fn:
            print(f"     ⚠ Unknown parser type: {parser_type}")
            sources_fail += 1
            continue

        # Fetch the page
        html = curl_text(url)
        if not html:
            print(f"     ⚠ Could not fetch page")
            sources_fail += 1
            continue

        if len(html) < 200:
            print(f"     ⚠ Page too short ({len(html)} bytes), skipping")
            sources_fail += 1
            continue

        # Extract og:image as fallback for events without per-event images
        og_image = None
        og_m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not og_m:
            og_m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.IGNORECASE)
        if og_m:
            og_image = og_m.group(1).strip()

        # Parse events
        try:
            events = parse_fn(html, src)
        except Exception as e:
            print(f"     ⚠ Parser error: {e}")
            sources_fail += 1
            continue

        print(f"     Found {len(events)} events")
        total_found += len(events)

        if not events:
            sources_ok += 1
            # Still update last_scraped_at even if no events found
            if not args.dry_run:
                update_last_scraped(src["id"])
            continue

        # Insert events
        inserted = 0
        for ev in events:
            fp = ev.get("content_fingerprint", "")

            if fp in existing_fps:
                total_skipped_dup += 1
                continue

            # Use og:image as fallback if no per-event image
            if not ev.get("image_url") and og_image:
                ev["image_url"] = og_image

            if args.dry_run:
                print(f"     → {ev['date']} | {ev['title'][:50]}")
                inserted += 1
            else:
                # Remove None values before upserting
                record = {k: v for k, v in ev.items() if v is not None}
                if upsert_event(record):
                    existing_fps.add(fp)
                    inserted += 1

        total_inserted += inserted
        sources_ok += 1
        print(f"     Inserted: {inserted}")

        # Update last_scraped_at
        if not args.dry_run:
            update_last_scraped(src["id"])

        # Small delay between sources to be polite
        time.sleep(0.5)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"[{ts()}] Temple events scraper done")
    print(f"  Sources OK: {sources_ok}, Failed: {sources_fail}")
    print(f"  Events found: {total_found}")
    print(f"  Events inserted: {total_inserted}")
    print(f"  Skipped (cross-source dup): {total_skipped_dup}")


if __name__ == "__main__":
    main()
