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

# Load X API credentials (OAuth1 user-context) so we can use the same X-search
# path the reel pipeline uses, instead of scraping DuckDuckGo (now bot-blocked).
load_env(os.path.expanduser('~/workspace/.env.twitter'))

# --- Import the shared X-search module (pipeline/fetch-tweets.py) ---
_FETCH_TWEETS_MOD = None
def _fetch_tweets():
    """Import the hyphenated fetch-tweets.py once; cache the module.
    Returns the module, or None if it can't be loaded."""
    global _FETCH_TWEETS_MOD
    if _FETCH_TWEETS_MOD is not None:
        return _FETCH_TWEETS_MOD
    try:
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fetch-tweets.py')
        spec = importlib.util.spec_from_file_location('videshi_fetch_tweets', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _FETCH_TWEETS_MOD = mod
    except Exception as e:
        print(f"  ⚠ Could not load fetch-tweets module: {e}")
        _FETCH_TWEETS_MOD = False
    return _FETCH_TWEETS_MOD or None


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
        # Skip malformed top-level entries (e.g. a stray "Name": "@handle"
        # written at the root instead of inside a category's persons array).
        if not isinstance(entries, dict):
            print(f"  ⚠ Skipping malformed registry entry '{cat}' (expected object, got {type(entries).__name__})")
            continue
        for person in entries.get('persons', []):
            if person.get('x'):
                lookup[person['name'].lower()] = person['x'].lstrip('@')
        for org in entries.get('organizations', []):
            if org.get('x'):
                lookup[org['name'].lower()] = org['x'].lstrip('@')
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
_STOPWORDS = {
    'a','an','the','and','or','but','of','to','in','on','for','with','as','at',
    'by','from','is','are','was','were','be','been','it','its','this','that',
    'these','those','his','her','their','they','them','who','what','when','now',
    'has','have','had','will','just','not','no','than','then','into','out','up',
    'down','over','under','about','after','before','more','most','first','last',
    'big','bigger','clean','seals','refuses','tried','trap','wants','showed',
}

def build_search_query(headline, max_terms=5):
    """Turn a headline into a tight X search query. The recent-search endpoint
    rejects full sentences ('Ambiguous use of operators'), so we keep only
    high-signal terms: proper nouns (capitalized words) first, then other
    content words, dropping stopwords/numbers/punctuation.
    """
    # Split on the first sentence-ending punctuation so we focus on the main
    # clause. NOTE: do not split on '-' — it would chop hyphenated words like
    # "Emergency-Room" down to a useless single token.
    head = re.split(r'[.\u2014:;!?]', headline)[0]
    words = re.findall(r"[A-Za-z']+", head.replace('-', ' '))
    proper, other = [], []
    for w in words:
        wl = w.lower()
        if wl in _STOPWORDS or len(w) < 3:
            continue
        if w[0].isupper():
            proper.append(w)
        else:
            other.append(w)
    # Proper nouns carry the topic; pad with content words if we have room.
    terms, seen = [], set()
    for w in proper + other:
        k = w.lower()
        if k not in seen:
            seen.add(k); terms.append(w)
        if len(terms) >= max_terms:
            break
    return ' '.join(terms)

def search_tweet(query, handle=None):
    """Find a relevant, embeddable tweet via the X API (the same recent-search
    path the reel pipeline uses), then verify it renders through react-tweet.
    Returns (tweet_url, tweet_id, verify_output) or (None, None, None).

    NOTE: the old implementation scraped DuckDuckGo for `site:x.com` links,
    which DDG now blocks as bot traffic (returns an anomaly page) — it found
    zero tweets. This uses fetch-tweets.search_topic_posts() instead.
    """
    ft = _fetch_tweets()
    if not ft:
        return None, None, None

    # Relevance keywords from the query (drop tiny stopword-ish tokens).
    kw = [w for w in re.findall(r'\w+', query) if len(w) > 2]

    # Gather candidates. When we have a known handle, bias to that author first
    # (from:handle), then fall back to a topic-wide search.
    candidates = []
    try:
        if handle:
            candidates = ft.search_topic_posts(
                f"from:{handle} ({query})", hours=48,
                max_results=20, verified_only=False, min_likes=0,
                require_media=False)
        if not candidates:
            candidates = ft.search_topic_posts(
                query, hours=48, max_results=30,
                verified_only=True, min_likes=50,
                require_media=False)
    except Exception as e:
        print(f"  ⚠ X search error: {e}")
        return None, None, None

    if not candidates:
        return None, None, None

    # Rank: keyword relevance, then verified, then reach.
    def _rel(p):
        text_l = (p.get('text', '') or '').lower()
        return sum(1 for k in kw if k.lower() in text_l)
    def _score(p):
        return (_rel(p), 1 if p.get('verified') else 0,
                p.get('impressions', 0) or 0, p.get('likes', 0) or 0)
    candidates.sort(key=_score, reverse=True)

    # Relevance floor: avoid embedding a tweet that merely shares one generic
    # word with the headline (e.g. "Emergency" matching an unrelated post).
    # Require >=2 keyword hits, or all of them when the query is very short.
    min_hits = 1 if len(kw) <= 1 else 2

    # Verify each candidate renders through react-tweet; return the first valid.
    for p in candidates[:5]:
        if _rel(p) < min_hits:
            continue
        tweet_id = p.get('id')
        if not tweet_id:
            continue
        try:
            verify = subprocess.run(
                ['bash', VERIFY_SCRIPT, tweet_id],
                capture_output=True, text=True, timeout=10
            )
        except Exception as e:
            print(f"  ⚠ Verify error for {tweet_id}: {e}")
            continue
        if verify.returncode == 0 and verify.stdout.strip().startswith('VALID'):
            tweet_url = p.get('url') or f"https://x.com/i/status/{tweet_id}"
            return tweet_url, tweet_id, verify.stdout.strip()

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
                keywords = build_search_query(headline)
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
            keywords = build_search_query(headline)
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
