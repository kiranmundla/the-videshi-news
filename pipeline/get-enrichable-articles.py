#!/usr/bin/env python3
"""
Fetches recently published articles that could benefit from an X embed.
Outputs JSON array for the enricher cron task to process.
"""

import json, os, re
from datetime import datetime, timezone, timedelta
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
}
REGISTRY_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/social-embed-registry.json')

EMBED_CATEGORIES = ['news', 'sports', 'entertainment', 'technology', 'nri-world']

def load_registry():
    with open(REGISTRY_PATH) as f:
        data = json.load(f)
    lookup = {}
    for cat, entries in data.items():
        if cat.startswith('_') or not isinstance(entries, dict):
            continue
        for person in entries.get('persons', []):
            if person.get('x'):
                lookup[person['name'].lower()] = person['x']
        for org in entries.get('organizations', []):
            if org.get('x'):
                lookup[org['name'].lower()] = org['x']
    return lookup

def main():
    hours_back = int(os.environ.get('HOURS_BACK', '6'))
    since = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    url = (f"{SUPABASE_URL}/rest/v1/p2_articles"
           f"?select=id,headline,subheadline,category,slug"
           f"&status=eq.published"
           f"&published_at=gte.{since}"
           f"&order=published_at.desc"
           f"&limit=20")
    
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    articles = r.json()
    
    # Need to check body for existing embeds separately (body is large)
    enrichable = []
    for a in articles:
        if a['category'] not in EMBED_CATEGORIES:
            continue
        # Check if article body already has an embed
        body_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{a['id']}&select=body",
            headers=HEADERS, timeout=10
        ).json()
        body = body_check[0].get('body', '') if body_check else ''
        if re.search(r'^https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/\d+', body, re.MULTILINE):
            continue
        enrichable.append(a)
    
    # Match handles from registry
    registry = load_registry()
    for a in enrichable:
        text = f"{a['headline']} {a.get('subheadline', '')}".lower()
        handles = []
        for name, handle in registry.items():
            if name in text:
                handles.append({'name': name, 'handle': handle})
        a['matched_handles'] = handles
    
    print(json.dumps(enrichable, indent=2))

if __name__ == '__main__':
    main()
