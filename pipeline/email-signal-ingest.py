#!/usr/bin/env python3
"""
email-signal-ingest.py — Process incoming email signals from company blogs/newsletters
into topics for the article pipeline.

Reads unprocessed rows from `email_signals` table, extracts key information,
and creates topics in `p2_topics` for the writer pipeline to pick up.

Usage:
    python3 pipeline/email-signal-ingest.py [--dry-run] [--limit N]
"""

import os, sys, json, subprocess, re, hashlib
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.openai'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

def sb_get(path):
    """GET from Supabase REST API."""
    result = subprocess.run([
        'curl', '-s', f'{SUPABASE_URL}/rest/v1/{path}',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
    ], capture_output=True, text=True)
    return json.loads(result.stdout) if result.stdout else []

def sb_patch(table, match_col, match_val, data):
    """PATCH a row in Supabase."""
    subprocess.run([
        'curl', '-s', '-X', 'PATCH',
        f'{SUPABASE_URL}/rest/v1/{table}?{match_col}=eq.{match_val}',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=minimal',
        '-d', json.dumps(data),
    ], capture_output=True, text=True)

def sb_post(table, data):
    """POST a row to Supabase, return response."""
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
    code = lines[-1] if lines else '000'
    body = '\n'.join(lines[:-1])
    return code, body

def extract_text_from_html(html):
    """Simple HTML to text."""
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:3000]  # Cap length

def classify_email(subject, body_text, source_company):
    """Use GPT-4o-mini to classify email content and extract a topic."""
    prompt = f"""You are a news editor for an Indian diaspora news site. Analyze this email from a company blog/newsletter and determine:
1. Is this newsworthy for the Indian diaspora? (yes/no)
2. If yes, what's the headline angle with a diaspora spin?
3. Category: technology, immigration, markets-finance, entertainment, news, sports, nri-world
4. Keywords (5-8 tags)
5. A 2-sentence summary of what happened

Email subject: {subject}
Source company: {source_company or 'Unknown'}
Email content (first 2000 chars): {body_text[:2000]}

Respond in JSON:
{{"newsworthy": true/false, "headline": "...", "category": "...", "keywords": ["..."], "summary": "...", "urgency": "high|medium|low"}}"""

    result = subprocess.run([
        'curl', '-s', 'https://api.openai.com/v1/chat/completions',
        '-H', f'Authorization: Bearer {OPENAI_API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'model': 'gpt-4o-mini',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.2,
            'response_format': {'type': 'json_object'},
        }),
    ], capture_output=True, text=True)

    try:
        resp = json.loads(result.stdout)
        content = resp['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"  ⚠ GPT classification failed: {e}")
        return None

def main():
    dry_run = '--dry-run' in sys.argv
    limit = 20
    for i, arg in enumerate(sys.argv):
        if arg == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    # Fetch unprocessed email signals
    emails = sb_get(f'email_signals?processed=eq.false&order=received_at.asc&limit={limit}')

    if not emails:
        print("No unprocessed email signals.")
        return

    print(f"Processing {len(emails)} email signal(s)...\n")

    created = 0
    skipped = 0

    for email in emails:
        subject = email.get('subject', '')
        body_text = email.get('body_text', '')
        body_html = email.get('body_html', '')
        source = email.get('source_company', '')
        email_id = email.get('email_id', '')

        # Get text content
        text = body_text or extract_text_from_html(body_html) if body_html else ''
        if not text and not subject:
            print(f"  ⏭ Skipping empty email {email_id}")
            if not dry_run:
                sb_patch('email_signals', 'email_id', email_id, {
                    'processed': True, 'processed_at': datetime.now(timezone.utc).isoformat()
                })
            skipped += 1
            continue

        print(f"  📧 {source or 'Unknown'}: {subject[:80]}")

        # Classify with GPT
        classification = classify_email(subject, text, source)

        if not classification or not classification.get('newsworthy'):
            print(f"    → Not newsworthy, skipping")
            if not dry_run:
                sb_patch('email_signals', 'email_id', email_id, {
                    'processed': True, 'processed_at': datetime.now(timezone.utc).isoformat()
                })
            skipped += 1
            continue

        headline = classification.get('headline', subject)
        category = classification.get('category', 'technology')
        keywords = classification.get('keywords', [])
        summary = classification.get('summary', '')
        urgency = classification.get('urgency', 'medium')

        print(f"    → {headline}")
        print(f"    → Category: {category}, Urgency: {urgency}")

        if dry_run:
            print(f"    → [DRY RUN] Would create topic")
            continue

        # Create topic in p2_topics
        topic_id = hashlib.md5(f"email:{email_id}".encode()).hexdigest()[:8]
        topic = {
            'canonical_title': headline,
            'vertical': category,
            'category': category,
            'urgency': urgency,
            'score_diaspora': 7 if urgency == 'high' else 5,
            'score_significance': 8 if urgency == 'high' else 6,
            'score_recency': 9,
            'score_source_avail': 8,
            'score_total': 32 if urgency == 'high' else 28,
            'signal_count': 1,
            'keywords': keywords,
            'status': 'approved',
        }

        code, body = sb_post('p2_topics', topic)
        if code == '201':
            print(f"    ✅ Topic created")
            created += 1
        else:
            print(f"    ❌ Topic creation failed: {code}")

        # Mark email as processed
        sb_patch('email_signals', 'email_id', email_id, {
            'processed': True,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'source_company': source or classification.get('source_company'),
        })

    print(f"\nDone: {created} topics created, {skipped} skipped")

if __name__ == '__main__':
    main()
