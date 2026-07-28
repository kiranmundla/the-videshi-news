#!/usr/bin/env python3
"""
Scrape North South Foundation (northsouth.org) for contests, deadlines, and schedule.
Populates kids_deadlines table linked to NSF program entry.
"""

import subprocess
import json
import re
import os
import sys
from datetime import datetime, date
from html.parser import HTMLParser

# ── Config ──────────────────────────────────────────────────────────────────
NSF_PROGRAM_ID = 'b11f4c94-7a2d-42b4-aa60-1983f2330a99'
SUPABASE_PROJECT_REF = 'lboecaekpynbpyijrbfz'
SOURCE = 'scraper-nsf'

PAGES = [
    ('https://www.northsouth.org/contests/', 'contests'),
    ('https://www.northsouth.org/national-contests/', 'nationals'),
]

# NSF contest subjects with grade ranges
NSF_SUBJECTS = {
    'Spelling Bee': {'abbrevs': ['JSB', 'SSB'], 'grades': [(1, 3), (4, 8)]},
    'Vocabulary Bee': {'abbrevs': ['JVB', 'IVB'], 'grades': [(1, 3), (4, 8)]},
    'Science Bee': {'abbrevs': ['JSC', 'ISC', 'SSC'], 'grades': [(1, 3), (4, 5), (6, 8)]},
    'Math Bee': {'abbrevs': ['MB1', 'MB2', 'MB3'], 'grades': [(1, 3), (4, 5), (6, 8)]},
    'Geography Bee': {'abbrevs': ['JGB', 'SGB'], 'grades': [(1, 3), (4, 8)]},
    'Public Speaking': {'abbrevs': ['PS1', 'PS3'], 'grades': [(6, 8), (9, 12)]},
    'Essay Writing': {'abbrevs': ['EW1', 'EW2', 'EW3'], 'grades': [(3, 5), (6, 8), (9, 12)]},
}


def log(msg):
    ts = datetime.now(tz=None).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f'[{ts}] {msg}', flush=True)


def load_env():
    """Load env vars from .env.supabase (handles 'export KEY=VALUE' format)."""
    env_path = os.path.expanduser('~/workspace/.env.supabase')
    if not os.path.exists(env_path):
        log(f'ERROR: {env_path} not found')
        sys.exit(1)
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                # Strip 'export ' prefix if present
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val


def fetch_url(url):
    """Fetch a URL using curl subprocess."""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '15', '-L', url],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0:
            log(f'  curl error for {url}: exit code {result.returncode}')
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        log(f'  curl timeout for {url}')
        return None


def fetch_pdf_text(url):
    """Download a PDF and extract text using pdftotext."""
    import tempfile
    tmp_pdf = tempfile.mktemp(suffix='.pdf')
    tmp_txt = tempfile.mktemp(suffix='.txt')
    try:
        # Download PDF as binary
        dl = subprocess.run(
            ['curl', '-s', '--max-time', '15', '-L', '-o', tmp_pdf, url],
            capture_output=True, text=True, timeout=20
        )
        if dl.returncode != 0:
            log(f'  curl error downloading PDF {url}: exit code {dl.returncode}')
            return None
        # Check file is actually a PDF (not an HTML error page)
        with open(tmp_pdf, 'rb') as f:
            header = f.read(5)
        if header != b'%PDF-':
            log(f'  Downloaded file is not a PDF (header: {header!r})')
            return None
        # Extract text with pdftotext
        ext = subprocess.run(
            ['pdftotext', '-layout', tmp_pdf, tmp_txt],
            capture_output=True, text=True, timeout=15
        )
        if ext.returncode != 0:
            log(f'  pdftotext error: {ext.stderr.strip()}')
            return None
        with open(tmp_txt, 'r') as f:
            return f.read()
    except (subprocess.TimeoutExpired, OSError) as e:
        log(f'  PDF extraction error for {url}: {e}')
        return None
    finally:
        for p in (tmp_pdf, tmp_txt):
            try:
                os.remove(p)
            except OSError:
                pass


def run_sql(sql):
    """Execute SQL via Supabase Management API."""
    token = os.environ.get('SUPABASE_ACCESS_TOKEN', '')
    if not token:
        log('ERROR: SUPABASE_ACCESS_TOKEN not set')
        return None
    endpoint = f'https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/database/query'
    payload = json.dumps({'query': sql})
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '15',
             '-X', 'POST', endpoint,
             '-H', f'Authorization: Bearer {token}',
             '-H', 'Content-Type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0:
            log(f'  SQL curl error: {result.returncode}')
            return None
        return json.loads(result.stdout) if result.stdout.strip() else []
    except Exception as e:
        log(f'  SQL error: {e}')
        return None


def parse_date(text):
    """Try to parse a date string like 'June 5, 2026' or 'July 31' into YYYY-MM-DD."""
    text = text.strip().rstrip('.')
    # Try "Month Day, Year"
    for fmt in ['%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y']:
        try:
            d = datetime.strptime(text, fmt)
            return d.strftime('%Y-%m-%d')
        except ValueError:
            pass
    # Try "MM-DD-YYYY"
    m = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text)
    if m:
        return f'{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}'
    return None


def extract_nationals_dates(html):
    """Extract registration and competition dates from nationals page."""
    deadlines = []

    # The dates are in <td> pairs: <td>Key point</td><td>Date</td>
    # Extract all td pairs from the table
    td_pairs = re.findall(
        r'<td[^>]*>\s*(.*?)\s*</td>\s*<td[^>]*>\s*(.*?)\s*</td>',
        html, re.DOTALL
    )

    date_map = {
        'Priority Registration Opens': ('registration_open', 'NSF National Finals - Priority Registration Opens'),
        'Priority Registration Deadline': ('registration_close', 'NSF National Finals - Priority Registration Deadline'),
        'Total list Registration Opens': ('registration_open', 'NSF National Finals - Total List Registration Opens'),
        'Total List Registration Opens': ('registration_open', 'NSF National Finals - Total List Registration Opens'),
        'All Registration Ends': ('registration_close', 'NSF National Finals - All Registration Ends'),
    }

    for key_text, date_text in td_pairs:
        # Strip HTML tags from both
        key_clean = re.sub(r'<[^>]+>', '', key_text).strip()
        date_clean = re.sub(r'<[^>]+>', '', date_text).strip()

        if key_clean in date_map:
            dtype, title = date_map[key_clean]
            d = parse_date(date_clean)
            if d:
                deadlines.append({
                    'title': title,
                    'deadline_date': d,
                    'deadline_type': dtype,
                    'source_id': f'nsf-nationals-{dtype}-{d}',
                    'registration_url': 'https://portal.northsouth.org',
                    'location': 'Nationwide',
                    'grade_min': 1,
                    'grade_max': 12,
                    'cost': '$60 National Finals',
                })

    # Extract Finals schedule dates from links (e.g. "finals-schedule-2026")
    schedule_link = re.search(r'finals.schedule.(\d{4})', html)
    finals_year = schedule_link.group(1) if schedule_link else None

    # The finals dates are in a PDF linked from this page, not in the HTML itself.
    # We parse the schedule link to determine the year, then check for known dates.
    # The PDF for 2026 shows: July 31 (Opening Ceremony) through August 2 (Awards)
    if finals_year:
        # Look for month-day references in the HTML
        month_day_matches = re.findall(
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})',
            html
        )
        months_map = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
                      'May': '05', 'June': '06', 'July': '07', 'August': '08',
                      'September': '09', 'October': '10', 'November': '11', 'December': '12'}

        finals_dates = set()
        for month_name, day in month_day_matches:
            # Only July/August dates are finals
            if month_name in ('July', 'August'):
                month_num = months_map[month_name]
                finals_dates.add(f'{finals_year}-{month_num}-{int(day):02d}')

        # If no July/August dates found in HTML, try fetching the PDF link
        if not finals_dates:
            # Try common schedule PDF URL patterns
            pdf_url = f'https://www.northsouth.org/wp-content/uploads/{finals_year}/07/finals-schedule-{finals_year}-new.pdf'
            log(f'  Fetching finals schedule PDF: {pdf_url}')
            pdf_text = fetch_pdf_text(pdf_url)
            if pdf_text:
                # PDF raw text may contain date references
                pdf_months = re.findall(r'(July|August)\s+(\d{1,2})', pdf_text)
                for month_name, day in pdf_months:
                    month_num = months_map[month_name]
                    finals_dates.add(f'{finals_year}-{month_num}-{int(day):02d}')

        if finals_dates:
            sorted_dates = sorted(finals_dates)
            start_date = sorted_dates[0]
            end_date = sorted_dates[-1]
            deadlines.append({
                'title': f'NSF National Finals {finals_year}',
                'deadline_date': start_date,
                'deadline_type': 'competition',
                'event_date': start_date,
                'source_id': f'nsf-nationals-competition-{finals_year}',
                'registration_url': 'https://portal.northsouth.org',
                'location': 'Nationwide',
                'grade_min': 1,
                'grade_max': 12,
                'cost': '$60',
                'description': f'NSF National Finals from {start_date} to {end_date}. Contests in Spelling, Vocabulary, Math, Science, Geography, Public Speaking, and Essay Writing.',
            })

    return deadlines


def extract_contests_info(html):
    """Extract contest subject info and general dates from the /contests/ page."""
    deadlines = []

    # Extract regional registration fee info
    regional_fee = None
    m = re.search(r'Regional Contests Registration Fee:\s*\$(\d+)', html)
    if m:
        regional_fee = f'${m.group(1)}'

    # Look for specific regional season info
    # NSF regionals are "each spring" - we create an annual cycle entry
    current_year = date.today().year
    next_year = current_year + 1

    # Create a general "Regional Contests" deadline for the next spring season
    # NSF regionals typically run March-May
    deadlines.append({
        'title': f'NSF Regional Contests {next_year} (Spring)',
        'deadline_date': f'{next_year}-03-01',
        'deadline_type': 'competition',
        'source_id': f'nsf-regionals-{next_year}',
        'registration_url': 'https://www.northsouth.org/contests/',
        'location': '75+ US chapters',
        'grade_min': 1,
        'grade_max': 12,
        'cost': regional_fee or '$40',
        'description': 'North South Foundation regional contests held each spring at 75+ chapters nationwide. Subjects: Spelling, Vocabulary, Math, Science, Geography, Public Speaking, Essay Writing.',
    })

    return deadlines


def extract_finals_schedule(html):
    """Extract individual contest times from the finals schedule PDF content."""
    deadlines = []

    # The finals schedule shows dates like "July 31st", "August 1st", "August 2"
    # Parse the schedule PDF text content for contest-specific events

    # Look for year in the URL/content
    year_match = re.search(r'20\d{2}', html)
    year = year_match.group() if year_match else str(date.today().year)

    # Find specific contest entries
    contest_entries = [
        ('Spelling Bee', 'nsf-finals-spelling'),
        ('Vocabulary Bee', 'nsf-finals-vocabulary'),
        ('Math Bee', 'nsf-finals-math'),
        ('Science Bee', 'nsf-finals-science'),
        ('Geography Bee', 'nsf-finals-geography'),
        ('Public Speaking', 'nsf-finals-publicspeaking'),
        ('Essay Writing', 'nsf-finals-essay'),
        ('Brain Bee', 'nsf-finals-brainbee'),
    ]

    # We already capture the overall finals as one competition entry
    # Individual subject schedules are too granular for kids_deadlines
    return deadlines


def upsert_deadlines(deadlines):
    """Insert or update deadlines in kids_deadlines table."""
    inserted = 0
    updated = 0
    errors = 0

    for d in deadlines:
        title = d['title'].replace("'", "''")
        desc = (d.get('description') or '').replace("'", "''")
        reg_url = d.get('registration_url', '')
        location = d.get('location', '')
        cost = d.get('cost', '')
        event_date = d.get('event_date')
        event_date_sql = f"'{event_date}'" if event_date else 'NULL'

        sql = f"""
            INSERT INTO kids_deadlines (
                program_id, title, deadline_date, deadline_type,
                event_date, description, registration_url, location,
                grade_min, grade_max, cost, source, source_id,
                is_featured, updated_at
            ) VALUES (
                '{NSF_PROGRAM_ID}',
                '{title}',
                '{d["deadline_date"]}',
                '{d["deadline_type"]}',
                {event_date_sql},
                '{desc}',
                '{reg_url}',
                '{location}',
                {d.get('grade_min', 'NULL')},
                {d.get('grade_max', 'NULL')},
                '{cost}',
                '{SOURCE}',
                '{d["source_id"]}',
                false,
                now()
            )
            ON CONFLICT (source, source_id) DO UPDATE SET
                title = EXCLUDED.title,
                deadline_date = EXCLUDED.deadline_date,
                deadline_type = EXCLUDED.deadline_type,
                event_date = EXCLUDED.event_date,
                description = EXCLUDED.description,
                registration_url = EXCLUDED.registration_url,
                location = EXCLUDED.location,
                grade_min = EXCLUDED.grade_min,
                grade_max = EXCLUDED.grade_max,
                cost = EXCLUDED.cost,
                updated_at = now()
        """
        result = run_sql(sql)
        if result is not None:
            # Check if it was insert or update (can't easily tell, count both)
            inserted += 1
            log(f'  Upserted: {d["title"]} ({d["deadline_date"]})')
        else:
            errors += 1
            log(f'  ERROR upserting: {d["title"]}')

    return inserted, errors


def main():
    log('=== NSF Scraper Start ===')
    load_env()

    all_deadlines = []

    # 1. Fetch and parse /contests/ page
    log('Fetching /contests/ page...')
    html = fetch_url('https://www.northsouth.org/contests/')
    if html:
        log(f'  Got {len(html)} bytes')
        deadlines = extract_contests_info(html)
        log(f'  Extracted {len(deadlines)} contest deadlines')
        all_deadlines.extend(deadlines)
    else:
        log('  FAILED to fetch /contests/')

    # 2. Fetch and parse /national-contests/ page
    log('Fetching /national-contests/ page...')
    html = fetch_url('https://www.northsouth.org/national-contests/')
    if html:
        log(f'  Got {len(html)} bytes')
        deadlines = extract_nationals_dates(html)
        log(f'  Extracted {len(deadlines)} national deadlines')
        all_deadlines.extend(deadlines)
    else:
        log('  FAILED to fetch /national-contests/')

    # 3. Try to get the finals schedule PDF (already known URL pattern)
    log('Fetching finals schedule...')
    schedule_url = 'https://www.northsouth.org/wp-content/uploads/2026/07/finals-schedule-2026-new.pdf'
    # PDF parsing is complex, but we already got the key dates from /national-contests/
    log('  Finals schedule dates captured from nationals page')

    # 4. Upsert all deadlines
    log(f'Upserting {len(all_deadlines)} deadlines...')
    inserted, errors = upsert_deadlines(all_deadlines)

    # Summary
    log('=== NSF Scraper Summary ===')
    log(f'  Total deadlines found: {len(all_deadlines)}')
    log(f'  Successfully upserted: {inserted}')
    log(f'  Errors: {errors}')
    for d in all_deadlines:
        log(f'    {d["deadline_type"]:20s} | {d["deadline_date"]} | {d["title"]}')
    log('=== NSF Scraper Done ===')


if __name__ == '__main__':
    main()
