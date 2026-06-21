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
load_env(os.path.expanduser('~/workspace/.env.openai'))
load_env(os.path.expanduser('~/workspace/.env.google-ai'))
OPENAI_KEY = os.environ.get('OPENAI_API_KEY', '')
GEMINI_KEY = os.environ.get('GOOGLE_AI_API_KEY', '')

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

# Generic geo/political/topic tokens that are too common to anchor relevance on
# their own. A candidate tweet matching ONLY these (e.g. 'india'+'uk') is a
# keyword collision, not a real topical match — the floor requires at least one
# hit on a DISTINCTIVE entity (named person/org/specific term) outside this set.
_GENERIC_TOKENS = {
    'india','indian','indians','uk','britain','british','us','usa','america',
    'american','china','chinese','pakistan','europe','european','eu','world',
    'global','nation','national','country','government','govt','state','states',
    'pm','president','minister','ministry','official','officials','leader',
    'leaders','trade','deal','talks','summit','meeting','market','markets',
    'economy','economic','political','politics','policy','news','report',
    'update','latest','breaking','says','said','new','plan','plans',
}

def _heuristic_query(headline, max_terms=5):
    """Fallback when GPT is unavailable: keep only high-signal terms from the
    headline (proper nouns first), dropping stopwords/numbers/punctuation.
    The recent-search endpoint rejects full sentences ('Ambiguous use of
    operators'), so we must reduce to plain keywords.
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

def _gpt_query(headline, subheadline='', body=''):
    """Ask GPT to read the article and return the best X search keywords.
    GPT understands the actual entities/event far better than stopword-stripping
    a headline (which mangles things like 'Emergency-Room Doctor' -> 'Emergency').
    Returns a query string, or '' on any failure (caller falls back).
    """
    snippet = (body or '')[:1200]
    prompt = (
        "You are helping search X (Twitter) for a post relevant to a news "
        "article. Read the article and return the BEST short search query to "
        "find a relevant tweet on X.\n\n"
        "Rules:\n"
        "- 2 to 5 words, only the most distinctive terms (people, orgs, places, "
        "the specific event). Use the actual proper names.\n"
        "- NO operators, hashtags, quotes, punctuation, or boolean words — just "
        "plain keywords separated by spaces.\n"
        "- Prefer specific named entities over generic words.\n\n"
        f"HEADLINE: {headline}\n"
        f"SUBHEADLINE: {subheadline}\n"
        f"ARTICLE: {snippet}\n\n"
        'Respond in JSON: {"query": "the search keywords"}'
    )
    # OpenAI first.
    if OPENAI_KEY:
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini",
                      "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.2,
                      "response_format": {"type": "json_object"}},
                timeout=30,
            )
            if r.status_code == 200:
                q = json.loads(r.json()["choices"][0]["message"]["content"]).get("query", "")
                q = re.sub(r'[^\w\s]', ' ', q).strip()
                if q:
                    return ' '.join(q.split()[:6])
            else:
                print(f"  ⚠ GPT query {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"  ⚠ GPT query error: {e}")
    # Gemini fallback (thinkingBudget:0 — see AGENTS.md note on JSON truncation).
    if GEMINI_KEY:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"responseMimeType": "application/json",
                                            "temperature": 0.2,
                                            "thinkingConfig": {"thinkingBudget": 0}}},
                timeout=30,
            )
            if r.status_code == 200:
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                q = json.loads(txt).get("query", "")
                q = re.sub(r'[^\w\s]', ' ', q).strip()
                if q:
                    return ' '.join(q.split()[:6])
        except Exception as e:
            print(f"  ⚠ Gemini query error: {e}")
    return ''

def _sanitize_query(q):
    """X recent-search rejects a query whose first/last bare token is a boolean
    operator (and/or/not) — 'ambiguous use of <op> as a keyword' → HTTP 400.
    Strip leading/trailing operator and stopword tokens so a trailing 'and'
    (from a truncated headline) doesn't skip the article."""
    if not q:
        return q
    _OPS = {'and', 'or', 'not'}
    toks = q.split()
    # Trim from both ends while the edge token is an operator or a stopword.
    while toks and (toks[0].lower() in _OPS or toks[0].lower() in _STOPWORDS):
        toks.pop(0)
    while toks and (toks[-1].lower() in _OPS or toks[-1].lower() in _STOPWORDS):
        toks.pop()
    return ' '.join(toks).strip()

def build_search_query(headline, subheadline='', body='', max_terms=5):
    """Best X search query for an article: GPT reads it and picks the entities;
    if GPT is unavailable, fall back to a headline keyword heuristic."""
    q = _gpt_query(headline, subheadline, body)
    if not q:
        q = _heuristic_query(headline, max_terms=max_terms)
    return _sanitize_query(q)

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

    # Distinctive keywords = query terms minus generic geo/political tokens.
    # Defined up-front because _distinct_rel/_score (used in candidates.sort)
    # close over it; defining it after the sort raised a NameError.
    distinct_kw = [k for k in kw if k.lower() not in _GENERIC_TOKENS]

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

    # Don't cite ourselves — embedding @thevideshi's own tweet in a Videshi
    # article is circular. Drop our own handle from candidates.
    candidates = [p for p in candidates
                  if (p.get('handle', '') or '').lower() != 'thevideshi']
    if not candidates:
        return None, None, None

    def _rel(p):
        text_l = (p.get('text', '') or '').lower()
        return sum(1 for k in kw if k.lower() in text_l)
    def _distinct_rel(p):
        """Count hits on DISTINCTIVE keywords only (named people/orgs/specific
        terms), excluding generic geo/political tokens. A tweet that matches
        only 'india'+'uk' has 0 distinctive hits and must be rejected."""
        text_l = (p.get('text', '') or '').lower()
        return sum(1 for k in distinct_kw if k.lower() in text_l)
    def _score(p):
        return (_distinct_rel(p), _rel(p), 1 if p.get('verified') else 0,
                p.get('impressions', 0) or 0, p.get('likes', 0) or 0)
    candidates.sort(key=_score, reverse=True)

    # Relevance floor: avoid embedding a tweet that merely shares generic
    # country/political words with the headline (e.g. an "India rejects OIC on
    # J&K" tweet matching an India-UK-trade article only on 'india'+'uk').
    # distinct_kw (query terms minus generic geo/political tokens) is defined
    # at the top of this function.
    # Require >=2 total keyword hits AND >=1 hit on a distinctive entity.
    # When the query is all-generic (no distinctive terms) or a single term,
    # fall back to the old total-hits floor so legitimately generic stories
    # are not over-filtered.
    min_hits = 1 if len(kw) <= 1 else 2

    # Verify each candidate renders through react-tweet; return the first valid.
    for p in candidates[:5]:
        if _rel(p) < min_hits:
            continue
        # When the article HAS distinctive entities, the matched tweet must
        # hit at least one of them — generic geo-token collisions are rejected.
        if distinct_kw and _distinct_rel(p) < 1:
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

        # Build the X search query once (GPT reads the article; heuristic fallback)
        keywords = build_search_query(
            headline,
            subheadline=article.get('subheadline', ''),
            body=article.get('body', ''),
        )
        print(f"      🔑 query: {keywords!r}")

        # Step 1: Check registry for known handles
        matches = find_handle(article_text, registry)
        
        tweet_url = None
        if matches:
            # Try each matched person/org
            for name, handle in matches[:2]:
                print(f"      🔍 Searching @{handle} ({name})...")
                tweet_url, tweet_id, verify_out = search_tweet(keywords, handle=handle)
                if tweet_url:
                    print(f"      ✅ Found: {tweet_url}")
                    print(f"         {verify_out}")
                    break
                else:
                    print(f"      ❌ No matching tweet from @{handle}")
                time.sleep(1)  # Rate limit
        
        if not tweet_url:
            # Step 2: Generic topic search
            print(f"      🔍 Generic search...")
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
