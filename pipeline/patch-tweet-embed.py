#!/usr/bin/env python3
"""
Patches an article body with a tweet embed URL.
Usage: patch-tweet-embed.py ARTICLE_ID TWEET_URL
Inserts the URL after the 2nd-3rd paragraph.
"""

import json, os, sys, re
import requests

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.replace('export ', '').strip()
                os.environ[key] = val.strip()

load_env(os.path.expanduser('~/workspace/.env.supabase'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

def main():
    if len(sys.argv) < 3:
        print("Usage: patch-tweet-embed.py ARTICLE_ID TWEET_URL", file=sys.stderr)
        sys.exit(1)
    
    article_id = sys.argv[1]
    tweet_url = sys.argv[2]
    
    # Fetch current body
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}&select=body",
        headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'},
        timeout=10
    )
    body = r.json()[0]['body']
    
    # Check if already has this embed
    if tweet_url in body:
        print(f"Already has this embed — skipping")
        return
    
    # Insert after 2nd or 3rd paragraph
    paragraphs = body.split('\n\n')
    insert_after = min(2, len(paragraphs) - 1)
    
    new_paragraphs = paragraphs[:insert_after + 1]
    new_paragraphs.append(tweet_url)
    new_paragraphs.extend(paragraphs[insert_after + 1:])
    new_body = '\n\n'.join(new_paragraphs)
    
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={**HEADERS, 'Prefer': 'return=minimal'},
        json={'body': new_body},
        timeout=15
    )
    r.raise_for_status()
    print(f"✅ Embedded {tweet_url} in article {article_id}")

if __name__ == '__main__':
    main()
