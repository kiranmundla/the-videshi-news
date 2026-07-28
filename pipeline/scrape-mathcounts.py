#!/usr/bin/env python3
"""
Scrape MATHCOUNTS (mathcounts.org) for state competition dates.
Populates kids_deadlines table linked to MATHCOUNTS program entry.

Fetches the competition search pages (paginated, ~18 pages) and extracts
state-level competitions only (chapter competitions are too numerous/noisy).
"""

import subprocess
import json
import re
import os
import sys
from datetime import datetime, date

# ── Config ──────────────────────────────────────────────────────────────────
MC_PROGRAM_ID = 'a25b5926-dbae-4b37-9083-116654224603'
SUPABASE_PROJECT_REF = 'lboecaekpynbpyijrbfz'
SOURCE = 'scraper-mathcounts'
BASE_URL = 'https://www.mathcounts.org/programs/chapter-state-competition-search'
MAX_PAGES = 20  # safety limit


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


def parse_mc_date(date_str):
    """Parse MATHCOUNTS date format 'MM-DD-YYYY' into 'YYYY-MM-DD'."""
    if not date_str or date_str.strip().upper() == 'TBD':
        return None
    date_str = date_str.strip()
    m = re.match(r'(\d{2})-(\d{2})-(\d{4})', date_str)
    if m:
        return f'{m.group(3)}-{m.group(1)}-{m.group(2)}'
    return None


def extract_competitions(html):
    """Extract competition rows from a MATHCOUNTS search results page."""
    competitions = []
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
    if not tables:
        return competitions

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tables[0], re.DOTALL)
    for row in rows[1:]:  # skip header
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        if len(clean) >= 5:
            competitions.append({
                'name': clean[0],
                'state': clean[1],
                'chapter': clean[2],
                'date': clean[3],
                'type': clean[4],
            })
    return competitions


def get_max_page(html):
    """Extract the maximum page number from pagination links."""
    pages = re.findall(r'page=(\d+)', html)
    if pages:
        return max(int(p) for p in pages)
    return 0


def fetch_all_state_competitions():
    """Fetch all pages and extract state-level competitions."""
    all_state_comps = []
    seen_names = set()

    log('Fetching MATHCOUNTS competition pages...')

    # Fetch page 0 to determine total pages
    html = fetch_url(f'{BASE_URL}?page=0')
    if not html:
        log('  FAILED to fetch first page')
        return all_state_comps

    max_page = get_max_page(html)
    log(f'  Found {max_page + 1} pages of competitions')

    for page_num in range(0, min(max_page + 1, MAX_PAGES)):
        if page_num == 0:
            page_html = html  # reuse first fetch
        else:
            page_html = fetch_url(f'{BASE_URL}?page={page_num}')
            if not page_html:
                log(f'  FAILED to fetch page {page_num}, skipping')
                continue

        comps = extract_competitions(page_html)
        state_comps = [c for c in comps if c['type'] == 'State']

        for sc in state_comps:
            # Deduplicate (page 0 and page 1 sometimes overlap)
            if sc['name'] not in seen_names:
                seen_names.add(sc['name'])
                all_state_comps.append(sc)

        total_on_page = len(comps)
        states_on_page = len(state_comps)
        new_states = len([c for c in state_comps if c['name'] in seen_names])
        log(f'  Page {page_num}: {total_on_page} total, {states_on_page} state comps')

    return all_state_comps


def build_deadlines(state_comps):
    """Convert state competitions into deadline entries."""
    deadlines = []

    for comp in state_comps:
        parsed_date = parse_mc_date(comp['date'])
        state_code = comp['state']
        comp_name = comp['name']

        # Determine the season year
        if parsed_date:
            year = parsed_date[:4]
            season_label = f'{int(year) - 1}-{year[2:]}'
        else:
            # For TBD dates, assume next season (2026-2027)
            today = date.today()
            if today.month >= 8:
                season_label = f'{today.year}-{str(today.year + 1)[2:]}'
            else:
                season_label = f'{today.year - 1}-{str(today.year)[2:]}'

        source_id = f'mathcounts-state-{state_code.lower()}-{season_label}'

        deadline = {
            'title': f'MATHCOUNTS {comp_name}',
            'deadline_type': 'competition',
            'source_id': source_id,
            'registration_url': 'https://www.mathcounts.org/programs/chapter-state-competition-search',
            'location': f'{state_code}, USA',
            'grade_min': 6,
            'grade_max': 8,
            'cost': '',
            'description': f'MATHCOUNTS {season_label} State Competition for {state_code}. Grades 6-8 math competition.',
        }

        if parsed_date:
            deadline['deadline_date'] = parsed_date
            deadline['event_date'] = parsed_date
        else:
            # Use a placeholder date of March 15 for TBD state comps
            # (most state competitions run in March)
            if today.month >= 8:
                placeholder_year = today.year + 1
            else:
                placeholder_year = today.year
            deadline['deadline_date'] = f'{placeholder_year}-03-15'
            deadline['description'] += ' Date TBD.'

        deadlines.append(deadline)

    return deadlines


def upsert_deadlines(deadlines):
    """Insert or update deadlines in kids_deadlines table."""
    inserted = 0
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
                '{MC_PROGRAM_ID}',
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
            inserted += 1
        else:
            errors += 1
            log(f'  ERROR upserting: {d["title"]}')

    return inserted, errors


def main():
    log('=== MATHCOUNTS Scraper Start ===')
    load_env()

    # Also add the known national competition date
    # MATHCOUNTS National Competition is typically in May
    today = date.today()
    if today.month >= 8:
        national_year = today.year + 1
    else:
        national_year = today.year

    # 1. Fetch all state competitions
    state_comps = fetch_all_state_competitions()
    log(f'Found {len(state_comps)} unique state competitions')

    dated = [c for c in state_comps if c['date'] and c['date'] != 'TBD']
    tbd = [c for c in state_comps if not c['date'] or c['date'] == 'TBD']
    log(f'  With dates: {len(dated)}')
    log(f'  TBD: {len(tbd)}')

    # 2. Build deadline entries
    deadlines = build_deadlines(state_comps)

    # 3. Add MATHCOUNTS National Competition entry
    deadlines.append({
        'title': f'MATHCOUNTS National Competition {national_year}',
        'deadline_date': f'{national_year}-05-11',  # Typically mid-May
        'deadline_type': 'competition',
        'event_date': f'{national_year}-05-11',
        'source_id': f'mathcounts-national-{national_year}',
        'registration_url': 'https://www.mathcounts.org',
        'location': 'Washington, DC area',
        'grade_min': 6,
        'grade_max': 8,
        'cost': '',
        'description': f'MATHCOUNTS {national_year} National Competition. Top mathletes from each state compete for the national title.',
    })

    # 4. Add MATHCOUNTS registration deadline (typically October for schools)
    reg_year = national_year
    deadlines.append({
        'title': f'MATHCOUNTS {reg_year} School Registration Deadline',
        'deadline_date': f'{reg_year - 1}-11-15',  # Typical mid-November deadline
        'deadline_type': 'registration_close',
        'source_id': f'mathcounts-registration-{reg_year}',
        'registration_url': 'https://www.mathcounts.org',
        'location': 'Nationwide',
        'grade_min': 6,
        'grade_max': 8,
        'cost': '',
        'description': f'Deadline for schools to register teams for MATHCOUNTS {reg_year} competition season. Check mathcounts.org for exact date.',
    })

    log(f'Total deadlines to upsert: {len(deadlines)}')

    # 5. Upsert
    inserted, errors = upsert_deadlines(deadlines)

    # Summary
    log('=== MATHCOUNTS Scraper Summary ===')
    log(f'  State competitions found: {len(state_comps)}')
    log(f'    With dates: {len(dated)}')
    log(f'    TBD: {len(tbd)}')
    log(f'  Total deadlines upserted: {inserted}')
    log(f'  Errors: {errors}')

    # Show all dated state competitions
    if dated:
        log('  Dated state competitions:')
        for c in dated:
            log(f'    {c["state"]:4s} | {c["date"]:12s} | {c["name"]}')

    log('=== MATHCOUNTS Scraper Done ===')


if __name__ == '__main__':
    main()
