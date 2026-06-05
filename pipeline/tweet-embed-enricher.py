#!/usr/bin/env python3
"""
Tweet Embed Enricher for The Videshi
Post-processing step: finds recently published articles that could benefit from
an X/Twitter embed, searches for relevant tweets, verifies them, and patches
the article body.

Runs as a cron job every 2 hours. Only enriches articles from the last 6 hours
that don't already have an embed.

Categories eligible: news, sports, entertainment, technology, nri-world
Categories skipped: travel, food, lifestyle (rarely tweet-worthy)
"""

import json, os, sys, re, time, subprocess
from datetime import datetime, timezone, timedelta
import requests

# --- ENV ---
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
VERIFY_SCRIPT = os.path.expanduser('~/workspace/the-videshi-news/pipeline/verify-tweet.sh')
REGISTRY_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/social-embed-registry.json')

# Categories worth embedding
EMBED_CATEGORIES = ['news', 'sports', 'entertainment', 'technology', 'nri-world']

# Max embeds to add per run (rate-limit friendly)
MAX_ENRICHMENTS_PER_RUN = 5

# --- Load handle registry ---
def load_registry():
    with open(REGISTRY_PATH) as f:
        data = json.load(f)
    # Build a flat lookup: name -> handle
    lookup = {}
    for cat, entries in data.items():
        if cat.startswith('_'):
            continue
        for person in entries.get('persons', []):
            if person.get('x'):
                lookup[person['name'].lower()] = person['x']
        for org in entries.get('organizations', []):
            if org.get('x'):
                lookup[org['name'].lower()] = org['x']
    return lookup

# --- Fetch recent articles without embeds ---
def fetch_enrichable_articles(hours_back=6):
    """Get recent published articles in embed-eligible categories that don't have an embed yet."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Fetch recent articles
    url = (f"{SUPABASE_URL}/rest/v1/p2_articles"
           f"?select=id,headline,subheadline,body,category,slug"
           f"&status=eq.published"
           f"&published_at=gte.{since}"
           f"&order=published_at.desc"
           f"&limit=20")
    
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    articles = r.json()
    
    # Filter: eligible category + no existing embed
    enrichable = []
    for a in articles:
        if a['category'] not in EMBED_CATEGORIES:
            continue
        body = a.get('body', '') or ''
        # Skip if already has an X embed (bare URL on its own line)
        if re.search(r'^https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/\d+', body, re.MULTILINE):
            continue
        enrichable.append(a)
    
    return enrichable

# --- Extract key entities from article ---
def extract_entities(article):
    """Pull out person names, org names, and key topics from headline + subheadline."""
    text = f"{article['headline']} {article.get('subheadline', '')}"
    # Return the combined text for search — the registry lookup + web search will do the matching
    return text

# --- Search for a tweet ---
def search_tweet(query, handle=None):
    """Search for a relevant tweet using web search via the verify pipeline.
    Returns (tweet_url, tweet_id, verify_output) or (None, None, None).
    """
    # Build search query
    if handle:
        search_q = f"site:x.com @{handle} {query}"
    else:
        search_q = f"site:x.com {query}"
    
    # Use curl to search via DuckDuckGo lite (no API key needed)
    try:
        result = subprocess.run(
            ['curl', '-sS', '-L', '-A', 'Mozilla/5.0',
             f'https://lite.duckduckgo.com/lite/?q={requests.utils.quote(search_q)}'],
            capture_output=True, text=True, timeout=15
        )
        html = result.stdout
        
        # Extract x.com/twitter.com status URLs from results
        urls = re.findall(r'https?://(?:www\.)?(?:twitter|x)\.com/(\w+)/status/(\d+)', html)
        
        if not urls:
            return None, None, None
        
        # Try each found tweet (up to 3)
        for handle_found, tweet_id in urls[:3]:
            verify = subprocess.run(
                ['bash', VERIFY_SCRIPT, tweet_id],
                capture_output=True, text=True, timeout=10
            )
            if verify.returncode == 0 and verify.stdout.strip().startswith('VALID'):
                tweet_url = f"https://x.com/{handle_found}/status/{tweet_id}"
                return tweet_url, tweet_id, verify.stdout.strip()
        
        return None, None, None
    except Exception as e:
        print(f"  ⚠ Search error: {e}")
        return None, None, None

# --- Find matching handle from registry ---
def find_handle(article_text, registry):
    """Check if any registry person/org is mentioned in the article."""
    text_lower = article_text.lower()
    matches = []
    for name, handle in registry.items():
        # Check if name appears in headline/subheadline
        if name in text_lower:
            matches.append((name, handle))
    return matches

# --- Patch article body with tweet embed ---
def patch_article_body(article_id, body, tweet_url):
    """Insert the tweet URL into the article body at a good location."""
    paragraphs = body.split('\n\n')
    
    # Insert after the 2nd or 3rd paragraph (after the lede + context)
    insert_after = min(2, len(paragraphs) - 1)
    
    # Build the enriched body
    new_paragraphs = paragraphs[:insert_after + 1]
    new_paragraphs.append(tweet_url)  # Bare URL on its own line
    new_paragraphs.extend(paragraphs[insert_after + 1:])
    
    new_body = '\n\n'.join(new_paragraphs)
    
    # Patch in Supabase
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={**HEADERS, 'Prefer': 'return=minimal'},
        json={'body': new_body},
        timeout=15
    )
    r.raise_for_status()
    return True

# --- Main ---
def main():
    print(f"🐦 Tweet Embed Enricher — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Eligible categories: {', '.join(EMBED_CATEGORIES)}")
    
    registry = load_registry()
    print(f"   Registry: {len(registry)} handles loaded")
    
    articles = fetch_enrichable_articles(hours_back=6)
    print(f"   Found {len(articles)} enrichable articles (last 6h, no existing embed)")
    
    if not articles:
        print("   Nothing to enrich. Done.")
        return
    
    enriched = 0
    for article in articles:
        if enriched >= MAX_ENRICHMENTS_PER_RUN:
            print(f"   Hit max enrichments ({MAX_ENRICHMENTS_PER_RUN}) for this run")
            break
        
        headline = article['headline']
        article_text = extract_entities(article)
        print(f"\n   📰 [{article['category']}] {headline[:80]}...")
        
        # Step 1: Check registry for known handles
        matches = find_handle(article_text, registry)
        
        tweet_url = None
        if matches:
            # Try each matched person/org
            for name, handle in matches[:2]:
                print(f"      🔍 Searching @{handle} ({name})...")
                # Search with handle + headline keywords
                keywords = re.sub(r'[^\w\s]', '', headline)[:60]
                tweet_url, tweet_id, verify_out = search_tweet(keywords, handle=handle)
                if tweet_url:
                    print(f"      ✅ Found: {tweet_url}")
                    print(f"         {verify_out}")
                    break
                else:
                    print(f"      ❌ No matching tweet from @{handle}")
                time.sleep(1)  # Rate limit
        
        if not tweet_url:
            # Step 2: Generic search with headline
            print(f"      🔍 Generic search...")
            keywords = re.sub(r'[^\w\s]', '', headline)[:60]
            tweet_url, tweet_id, verify_out = search_tweet(keywords)
            if tweet_url:
                print(f"      ✅ Found: {tweet_url}")
                print(f"         {verify_out}")
            else:
                print(f"      ❌ No relevant tweet found — skipping")
                continue
        
        # Step 3: Patch the article
        try:
            patch_article_body(article['id'], article['body'], tweet_url)
            print(f"      📝 Embedded in article body")
            enriched += 1
        except Exception as e:
            print(f"      ⚠ Patch failed: {e}")
        
        time.sleep(2)  # Rate limit between articles
    
    print(f"\n   ✨ Done — enriched {enriched}/{len(articles)} articles")

if __name__ == '__main__':
    main()
