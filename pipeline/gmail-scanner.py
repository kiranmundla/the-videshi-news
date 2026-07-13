#!/usr/bin/env python3
"""
gmail-scanner.py — Scan signals@thevideshi.com for newsletter emails,
extract them into the email_signals Supabase table for processing by
email-signal-ingest.py.

Uses Gmail API via OAuth2 refresh token (no Hatch connector needed).

Usage:
    python3 pipeline/gmail-scanner.py [--dry-run] [--limit N]
"""

import os, sys, json, subprocess, base64, re, hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# ── Load env ──────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/workspace/.env.gmail'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))

GMAIL_CLIENT_ID = os.environ.get('GMAIL_CLIENT_ID', '')
GMAIL_CLIENT_SECRET = os.environ.get('GMAIL_CLIENT_SECRET', '')
GMAIL_REFRESH_TOKEN = os.environ.get('GMAIL_REFRESH_TOKEN', '')

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

STATE_FILE = os.path.join(os.path.dirname(__file__), 'gmail-scanner-state.json')

# ── Gmail API helpers ─────────────────────────────────────────────────
def get_access_token():
    """Get a fresh access token using the refresh token."""
    result = subprocess.run([
        'curl', '-s', '-X', 'POST', 'https://oauth2.googleapis.com/token',
        '-d', f'client_id={GMAIL_CLIENT_ID}',
        '-d', f'client_secret={GMAIL_CLIENT_SECRET}',
        '-d', f'refresh_token={GMAIL_REFRESH_TOKEN}',
        '-d', 'grant_type=refresh_token',
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    if 'access_token' not in data:
        print(f"❌ Failed to get access token: {data}", file=sys.stderr)
        sys.exit(1)
    return data['access_token']

def gmail_get(access_token, endpoint):
    """GET from Gmail API."""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {access_token}',
        f'https://gmail.googleapis.com/gmail/v1/users/me/{endpoint}',
    ], capture_output=True, text=True)
    return json.loads(result.stdout) if result.stdout else {}

def gmail_list_messages(access_token, query='', max_results=50):
    """List messages matching a query."""
    endpoint = f'messages?maxResults={max_results}'
    if query:
        import urllib.parse
        endpoint += f'&q={urllib.parse.quote(query)}'
    return gmail_get(access_token, endpoint)

def gmail_get_message(access_token, msg_id):
    """Get a full message by ID."""
    return gmail_get(access_token, f'messages/{msg_id}?format=full')

# ── Message parsing ───────────────────────────────────────────────────
def get_header(msg, name):
    """Extract a header value from a Gmail message."""
    headers = msg.get('payload', {}).get('headers', [])
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ''

def get_body_text(msg):
    """Extract plain text body from a Gmail message."""
    payload = msg.get('payload', {})

    # Simple single-part message
    if payload.get('mimeType') == 'text/plain' and payload.get('body', {}).get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')

    # Multipart — search parts
    parts = payload.get('parts', [])
    for part in parts:
        if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
        # Nested multipart
        for subpart in part.get('parts', []):
            if subpart.get('mimeType') == 'text/plain' and subpart.get('body', {}).get('data'):
                return base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8', errors='replace')

    return ''

def get_body_html(msg):
    """Extract HTML body from a Gmail message."""
    payload = msg.get('payload', {})

    if payload.get('mimeType') == 'text/html' and payload.get('body', {}).get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')

    parts = payload.get('parts', [])
    for part in parts:
        if part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
        for subpart in part.get('parts', []):
            if subpart.get('mimeType') == 'text/html' and subpart.get('body', {}).get('data'):
                return base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8', errors='replace')

    return ''

def extract_source_company(from_addr, subject):
    """Try to identify the source company/org from sender."""
    # Extract domain from email
    match = re.search(r'@([\w.-]+)', from_addr)
    if not match:
        return ''
    domain = match.group(1).lower()

    # Strip common email service domains
    generic_domains = {'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
                       'mail.com', 'protonmail.com', 'icloud.com'}
    if domain in generic_domains:
        # Try to extract name from the display name portion
        name_match = re.match(r'^([^<]+)', from_addr)
        return name_match.group(1).strip().strip('"') if name_match else ''

    # Use domain as company name, strip common prefixes
    company = domain.split('.')[0]
    for prefix in ['mail', 'email', 'news', 'newsletter', 'updates', 'info', 'noreply']:
        if company == prefix and '.' in domain:
            parts = domain.split('.')
            company = parts[1] if len(parts) > 1 else parts[0]

    return company.title()

# ── Supabase helpers ──────────────────────────────────────────────────
def sb_post(table, data):
    """Insert a row into Supabase."""
    result = subprocess.run([
        'curl', '-s', '-w', '\n%{http_code}',
        f'{SUPABASE_URL}/rest/v1/{table}',
        '-X', 'POST',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', json.dumps(data),
    ], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    status = int(lines[-1]) if lines else 0
    body = '\n'.join(lines[:-1])
    return status, body

def check_already_processed(email_id):
    """Check if this email_id is already in the table."""
    result = subprocess.run([
        'curl', '-s',
        f'{SUPABASE_URL}/rest/v1/email_signals?email_id=eq.{email_id}&select=id',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
    ], capture_output=True, text=True)
    try:
        rows = json.loads(result.stdout)
        return len(rows) > 0
    except:
        return False

# ── State management ──────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'last_history_id': None, 'last_run': None, 'processed_count': 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# ── Main ──────────────────────────────────────────────────────────────
def main():
    dry_run = '--dry-run' in sys.argv
    limit = 20
    for i, arg in enumerate(sys.argv):
        if arg == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    if not all([GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN]):
        print("❌ Missing Gmail credentials in .env.gmail", file=sys.stderr)
        sys.exit(1)

    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("❌ Missing Supabase credentials in .env.supabase", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    print(f"📧 Gmail Scanner — scanning signals@thevideshi.com")
    print(f"   Last run: {state.get('last_run', 'never')}")
    print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    # Get access token
    access_token = get_access_token()

    # List recent messages (unread or all recent)
    # Use 'newer_than:1d' for first run, then use history for incremental
    query = 'newer_than:1d'
    if state.get('last_run'):
        # Scan last 2 days to catch stragglers
        query = 'newer_than:2d'

    result = gmail_list_messages(access_token, query=query, max_results=limit)
    messages = result.get('messages', [])

    if not messages:
        print("   No new messages found.")
        state['last_run'] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    print(f"   Found {len(messages)} messages to process")

    inserted = 0
    skipped = 0
    errors = 0

    for msg_stub in messages:
        msg_id = msg_stub['id']

        # Check if already in DB
        if check_already_processed(msg_id):
            skipped += 1
            continue

        # Fetch full message
        msg = gmail_get_message(access_token, msg_id)
        if not msg or 'payload' not in msg:
            errors += 1
            continue

        from_addr = get_header(msg, 'From')
        to_addr = get_header(msg, 'To')
        subject = get_header(msg, 'Subject')
        date_str = get_header(msg, 'Date')

        # Parse received date
        received_at = None
        if date_str:
            try:
                received_at = parsedate_to_datetime(date_str).isoformat()
            except:
                received_at = datetime.now(timezone.utc).isoformat()
        else:
            received_at = datetime.now(timezone.utc).isoformat()

        body_text = get_body_text(msg)
        body_html = get_body_html(msg)
        source_company = extract_source_company(from_addr, subject)

        # Truncate body to avoid giant payloads
        body_text = body_text[:10000] if body_text else ''
        body_html = body_html[:20000] if body_html else ''

        print(f"   📩 {subject[:80]}")
        print(f"      From: {from_addr[:60]}  Source: {source_company}")

        if dry_run:
            inserted += 1
            continue

        # Insert into email_signals table
        row = {
            'email_id': msg_id,
            'from_address': from_addr[:500],
            'to_address': to_addr[:500],
            'subject': subject[:1000],
            'body_text': body_text,
            'body_html': body_html,
            'received_at': received_at,
            'processed': False,
            'source_company': source_company[:200],
        }

        status, body = sb_post('email_signals', row)
        if 200 <= status < 300:
            inserted += 1
        else:
            # Might be duplicate (unique constraint on email_id)
            if 'duplicate' in body.lower() or '23505' in body:
                skipped += 1
            else:
                print(f"      ⚠️ Insert failed ({status}): {body[:200]}", file=sys.stderr)
                errors += 1

    # Update state
    state['last_run'] = datetime.now(timezone.utc).isoformat()
    state['processed_count'] = state.get('processed_count', 0) + inserted
    save_state(state)

    print(f"\n📊 Summary: {inserted} inserted, {skipped} skipped (already seen), {errors} errors")

if __name__ == '__main__':
    main()
