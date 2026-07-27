#!/usr/bin/env python3
"""
scrape-spiritual-events.py — Scrape US events from spiritual organizations
and upsert to Supabase events table.

Sources:
  1. Isha Foundation (Sadhguru) - per-city pages + special tours
  2. Art of Living (Sri Sri Ravi Shankar) - tour schedule
  3. Amma (Mata Amritanandamayi) - NA tour page
  4. Satsang Foundation (Sri M) - events page
  5. Brahma Kumaris / BK Shivani - US events
  6. Vipassana (dhamma.org) - US center schedules

Uses GPT-4o-mini to extract structured event data from HTML,
making the parser robust across different site layouts.

Category: 'Spiritual'
Source: 'spiritual-scraper'
Featured: set when a major teacher personally visits the US
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, date
from html.parser import HTMLParser
from urllib.parse import quote

# ── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.openai'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
OPENAI_KEY = os.environ.get('OPENAI_API_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
    sys.exit(1)
if not OPENAI_KEY:
    print("ERROR: Missing OPENAI_API_KEY", file=sys.stderr)
    sys.exit(1)

# Normalize URL
SB_HOST = SUPABASE_URL if not SUPABASE_URL.startswith('https://') else SUPABASE_URL[len('https://'):]

# ── HTML text extraction ─────────────────────────────────────────────────────

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.skip = True
        if tag in ('br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'td', 'th'):
            self.text.append('\n')
        # Preserve link URLs so the LLM can find ticket/registration links
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            if href and href.startswith('http'):
                self.text.append(f' [link: {href}] ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.skip = False

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.text.append(data.strip())

def html_to_text(html):
    t = TextExtractor()
    t.feed(html)
    raw = ' '.join(t.text)
    # Collapse whitespace but keep newlines
    lines = [re.sub(r'\s+', ' ', l).strip() for l in raw.split('\n')]
    return '\n'.join(l for l in lines if l)

# ── Source definitions ───────────────────────────────────────────────────────

# Each source: (url, organization, teacher_name, teacher_is_featured)
# teacher_is_featured: True means events from this page typically involve
# the teacher personally (e.g., tour pages). False = regular local programs.

ISHA_CITIES = [
    'losangeles', 'sanfrancisco', 'seattle', 'newyork', 'dallas',
    'atlanta', 'houston', 'chicago', 'dc', 'boston', 'denver',
    'austin', 'nashville', 'phoenix', 'detroit', 'philadelphia',
    'newjersey', 'miami'
]

SOURCES = []

# Isha per-city pages (regular programs by instructors — not featured)
for city in ISHA_CITIES:
    SOURCES.append({
        'url': f'https://innerengineering.sadhguru.org/{city}',
        'org': 'Isha Foundation',
        'teacher': 'Sadhguru',
        'featured': False,
        'country_filter': 'US',
    })

# Isha special events / tours (Sadhguru personal — featured)
SOURCES.append({
    'url': 'https://isha.sadhguru.org/global/en/events/special-events/north-america-tour',
    'org': 'Isha Foundation',
    'teacher': 'Sadhguru',
    'featured': True,
    'country_filter': 'US',
})

# Art of Living / Gurudev tour schedule
SOURCES.append({
    'url': 'https://gurudev.artofliving.org/tour-schedule/list/',
    'org': 'Art of Living Foundation',
    'teacher': 'Sri Sri Ravi Shankar',
    'featured': True,  # Tour schedule = Gurudev personal
    'country_filter': 'US',
})

# Amma NA tour (Swami Amritaswarupananda 2026 — senior disciple, not featured)
SOURCES.append({
    'url': 'https://na.amma.org/news/swami-amritaswarupanandas-usa-tour-2026',
    'org': 'Amma (MA Center)',
    'teacher': 'Amma',
    'featured': False,  # Swami tour, not Amma personally
    'country_filter': 'US',
})

# Sri M / Satsang Foundation events
SOURCES.append({
    'url': 'https://satsang-foundation.org/category/events/',
    'org': 'The Satsang Foundation',
    'teacher': 'Sri M',
    'featured': True,  # Sri M's events are personal
    'country_filter': 'US',
})

# Brahma Kumaris LA (as a representative US page)
SOURCES.append({
    'url': 'https://bklosangeles.org/events/list/',
    'org': 'Brahma Kumaris',
    'teacher': 'BK Shivani',
    'featured': False,
    'country_filter': 'US',
})

# Vipassana US centers
VIPASSANA_CENTERS = [
    ('https://www.dhamma.org/en-US/schedules/schdhara', 'Dhamma Dhara, Shelburne Falls, MA'),
    ('https://www.dhamma.org/en-US/schedules/noncenter/ny.us', 'New York Vipassana'),
    ('https://www.dhamma.org/en-US/schedules/schsela', 'Dhamma Sela, Colorado'),
    ('https://www.dhamma.org/en-US/schedules/schpasava', 'Dhamma Pasava, Idaho'),
]
for url, center in VIPASSANA_CENTERS:
    SOURCES.append({
        'url': url,
        'org': f'Vipassana ({center})',
        'teacher': 'S.N. Goenka tradition',
        'featured': False,
        'country_filter': 'US',
    })

# ── Fetch page ───────────────────────────────────────────────────────────────

def fetch_page(url):
    """Fetch URL with curl, return text content."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-L', '-A', 'TheVideshi/1.0 (thevideshi.com)',
             '--max-time', '20', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  curl error for {url}: {result.stderr[:200]}", file=sys.stderr)
            return None
        html = result.stdout
        if not html or len(html) < 100:
            print(f"  Empty/tiny response from {url}", file=sys.stderr)
            return None
        text = html_to_text(html)
        # Truncate to ~6000 chars to stay within LLM context budget
        if len(text) > 6000:
            text = text[:6000]
        return text
    except Exception as e:
        print(f"  Exception fetching {url}: {e}", file=sys.stderr)
        return None

# ── LLM extraction ───────────────────────────────────────────────────────────

EXTRACT_PROMPT = """You are an event data extractor. Given text from a spiritual organization's event page, extract ALL upcoming events as a JSON array.

RULES:
- Only include events in the UNITED STATES (US) or CANADA. Skip events in India, Europe, Portugal, etc.
- Only include events with dates in 2026 or 2027. Skip past events.
- For each event, extract:
  - title: Event name (e.g., "Inner Engineering In-Person", "The Journey Within with Gurudev")
  - date: Start date as YYYY-MM-DD
  - end_date: End date as YYYY-MM-DD (same as date if single-day, null if unknown)
  - time: Start time if mentioned (e.g., "7:00 PM"), null if not
  - venue_name: Venue/location name
  - city: City name
  - state: US state abbreviation (CA, NY, TX, etc.) or Canadian province
  - description: 1-2 sentence description of the event
  - ticket_url: Registration/ticket URL if found, null otherwise
  - price_range: Price info if found (e.g., "Free", "$330", "$375"), null otherwise
  - is_major_teacher_appearance: true if the page text indicates the main spiritual teacher/guru is personally present at this event (not just regular instructors or local teachers). false for regular classes/programs taught by local staff.

Return ONLY a valid JSON array. If no qualifying events found, return [].

ORGANIZATION: {org}
TEACHER: {teacher}

PAGE TEXT:
{text}"""

def extract_events_with_llm(text, org, teacher):
    """Use GPT-4o-mini to extract structured events from page text."""
    prompt = EXTRACT_PROMPT.format(org=org, teacher=teacher, text=text)

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You extract event data into clean JSON. Return only a JSON array, no markdown fences."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 3000,
        "response_format": {"type": "json_object"}
    })

    try:
        result = subprocess.run(
            ['curl', '-sS', '-X', 'POST', 'https://api.openai.com/v1/chat/completions',
             '-H', f'Authorization: Bearer {OPENAI_KEY}',
             '-H', 'Content-Type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=60
        )
        resp = json.loads(result.stdout)
        if 'error' in resp:
            print(f"  OpenAI error: {resp['error']}", file=sys.stderr)
            return []

        content = resp['choices'][0]['message']['content']
        data = json.loads(content)

        # Handle both {"events": [...]} and [...] formats
        if isinstance(data, dict):
            events = data.get('events', data.get('results', []))
        elif isinstance(data, list):
            events = data
        else:
            events = []

        return events
    except Exception as e:
        print(f"  LLM extraction error: {e}", file=sys.stderr)
        return []

# ── Supabase upsert ──────────────────────────────────────────────────────────

def make_source_id(org, title, date_str):
    """Create a stable, unique source_id from org + title + date."""
    raw = f"{org}|{title}|{date_str}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def make_slug(title, city, date_str):
    """Create a URL-friendly slug."""
    raw = f"{title} {city} {date_str}"
    slug = re.sub(r'[^a-z0-9]+', '-', raw.lower()).strip('-')
    return slug[:120]

def upsert_event(event, org, teacher, is_featured_source, source_url=None):
    """Upsert a single event to Supabase."""
    title = event.get('title', '').strip()
    date_str = event.get('date', '')
    if not title or not date_str:
        return False

    # Validate date format
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        # Skip past events
        if dt.date() < date.today():
            return False
    except ValueError:
        print(f"  Bad date '{date_str}' for '{title}'", file=sys.stderr)
        return False

    sid = make_source_id(org, title, date_str)
    slug = make_slug(title, event.get('city', ''), date_str)

    # Featured = source says featured AND LLM confirms teacher is personally present
    is_featured = is_featured_source and event.get('is_major_teacher_appearance', False)

    # Use LLM-extracted ticket_url, fall back to source page URL
    ticket_url = event.get('ticket_url') or source_url

    record = {
        'title': title,
        'date': date_str,
        'time': event.get('time'),
        'end_date': event.get('end_date'),
        'venue_name': event.get('venue_name'),
        'city': event.get('city', ''),
        'state': event.get('state'),
        'category': 'Spiritual',
        'description': event.get('description'),
        'ticket_url': ticket_url,
        'price_range': event.get('price_range'),
        'organizer': org,
        'artist_info': teacher,
        'source': 'spiritual-scraper',
        'source_id': sid,
        'slug': slug,
        'is_featured': is_featured,
    }

    # Remove None values
    record = {k: v for k, v in record.items() if v is not None}

    payload = json.dumps(record)

    # Upsert using source+source_id as the conflict key
    # Since there's no unique constraint on source+source_id, use the REST API
    # with on_conflict on source_id (which should be unique for our source)
    for attempt in range(2):
        try:
            result = subprocess.run(
                ['curl', '-sS', '-X', 'POST',
                 f'https://{SB_HOST}/rest/v1/events',
                 '-H', f'apikey: {SUPABASE_KEY}',
                 '-H', f'Authorization: Bearer {SUPABASE_KEY}',
                 '-H', 'Content-Type: application/json',
                 '-H', 'Prefer: resolution=merge-duplicates',
                 '-d', payload],
                capture_output=True, text=True, timeout=30
            )
            break
        except subprocess.TimeoutExpired:
            if attempt == 0:
                print(f"  Timeout on upsert for '{title}', retrying...", file=sys.stderr)
                time.sleep(2)
                continue
            print(f"  Timeout on upsert for '{title}' (gave up)", file=sys.stderr)
            return False

    stdout = result.stdout.strip()
    # Detect Supabase error responses: JSON with "code" + "message" keys, or curl failure
    is_error = result.returncode != 0 or ('"code"' in stdout and '"message"' in stdout) or ('error' in stdout.lower())
    if is_error and 'duplicate' not in stdout.lower():
        print(f"  Upsert failed for '{title}': {stdout[:200]}", file=sys.stderr)
        return False

    return True

# ── Check existing events ────────────────────────────────────────────────────

def get_existing_source_ids():
    """Get all existing source_ids from spiritual-scraper."""
    result = subprocess.run(
        ['curl', '-sS',
         f'https://{SB_HOST}/rest/v1/events?source=eq.spiritual-scraper&select=source_id',
         '-H', f'apikey: {SUPABASE_KEY}',
         '-H', f'Authorization: Bearer {SUPABASE_KEY}'],
        capture_output=True, text=True, timeout=15
    )
    try:
        rows = json.loads(result.stdout)
        return {r['source_id'] for r in rows if r.get('source_id')}
    except:
        return set()

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"Spiritual Events Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    existing_ids = get_existing_source_ids()
    print(f"Existing spiritual events in DB: {len(existing_ids)}")

    total_new = 0
    total_updated = 0
    total_skipped = 0
    total_sources = len(SOURCES)
    featured_events = []

    for i, src in enumerate(SOURCES):
        url = src['url']
        org = src['org']
        teacher = src['teacher']
        is_featured = src['featured']

        print(f"\n[{i+1}/{total_sources}] {org} — {url}")

        # Fetch page
        text = fetch_page(url)
        if not text:
            print(f"  ⚠ Could not fetch page, skipping")
            continue

        if len(text) < 50:
            print(f"  ⚠ Page too short ({len(text)} chars), skipping")
            continue

        print(f"  Fetched {len(text)} chars")

        # Extract events with LLM
        events = extract_events_with_llm(text, org, teacher)
        print(f"  Extracted {len(events)} events")

        if not events:
            continue

        # Upsert each event
        for ev in events:
            sid = make_source_id(org, ev.get('title', ''), ev.get('date', ''))

            is_new = sid not in existing_ids
            ok = upsert_event(ev, org, teacher, is_featured, source_url=url)

            if ok:
                if is_new:
                    total_new += 1
                    existing_ids.add(sid)
                else:
                    total_updated += 1

                # Track featured events for summary
                if is_featured and ev.get('is_major_teacher_appearance'):
                    featured_events.append({
                        'title': ev.get('title'),
                        'teacher': teacher,
                        'city': ev.get('city'),
                        'state': ev.get('state'),
                        'date': ev.get('date'),
                    })
            else:
                total_skipped += 1

        # Rate limit — don't hammer OpenAI
        time.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS: {total_new} new, {total_updated} updated, {total_skipped} skipped")
    print(f"Total spiritual events in DB: {len(existing_ids)}")

    if featured_events:
        print(f"\n🌟 FEATURED EVENTS (major teacher visits):")
        for fe in featured_events:
            print(f"  ★ {fe['teacher']} — {fe['title']} — {fe['city']}, {fe['state']} — {fe['date']}")

    print(f"\nDone at {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == '__main__':
    main()
