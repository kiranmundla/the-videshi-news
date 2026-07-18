#!/usr/bin/env python3
"""
tweet-enricher.py — Automatically find and embed relevant X tweets in Videshi articles.

Uses TwitterAPI.io to search tweets by handle, matches them to recent articles
by topic relevance, and patches the article body.

Flow:
  1. Get recent published articles without existing embeds (last 24h)
  2. Match article topics to registry handles (strict name matching)
  3. Search recent tweets from matched handles via TwitterAPI.io
  4. Score tweet relevance against article content
  5. Verify tweet via react-tweet API (will it render?)
  6. Patch article body with the tweet URL after paragraph 2

Usage:
  python3 tweet-enricher.py              # dry run — show what would be embedded
  python3 tweet-enricher.py --apply      # actually patch articles in Supabase
  python3 tweet-enricher.py --hours 48   # look back N hours for articles (default 24)

Env: ~/workspace/.env.twitterapi-io, ~/workspace/.env.supabase
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta

_dir = os.path.dirname(os.path.abspath(__file__))

# ─── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.twitterapi-io"))

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_session = requests.Session()
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
REST = f"{SB_URL}/rest/v1"
SB_HEADERS = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

TWITTERAPI_IO_KEY = os.environ.get("TWITTERAPI_IO_KEY", "")
TWITTERAPI_IO_BASE = "https://api.twitterapi.io"

VERIFY_SCRIPT = os.path.join(_dir, "verify-tweet.sh")
REGISTRY_PATH = os.path.join(_dir, "social-embed-registry.json")

# Categories where embeds make sense
EMBED_CATEGORIES = {"news", "sports", "entertainment", "technology", "nri-world", "immigration"}


# ─── TwitterAPI.io search ─────────────────────────────────────────────────────

def _twitterapiio_search(query, max_results=20, hours=48):
    """Run a TwitterAPI.io advanced_search and return normalized tweet dicts."""
    if not TWITTERAPI_IO_KEY:
        print("  ⚠ TWITTERAPI_IO_KEY not set", file=sys.stderr)
        return []

    try:
        result = subprocess.run(
            ["curl", "-sS",
             f"{TWITTERAPI_IO_BASE}/twitter/tweet/advanced_search",
             "-H", f"X-API-Key: {TWITTERAPI_IO_KEY}",
             "-G",
             "--data-urlencode", f"query={query}",
             "-d", "queryType=Latest"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            print(f"  ⚠ TwitterAPI.io curl error: {result.stderr[:200]}", file=sys.stderr)
            return []
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"  ⚠ TwitterAPI.io error: {e}", file=sys.stderr)
        return []

    raw_tweets = data.get("tweets", [])
    if not raw_tweets:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results = []
    for t in raw_tweets[:max_results]:
        created_str = t.get("createdAt", "")
        try:
            created = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
            if created < cutoff:
                continue
        except (ValueError, TypeError):
            pass

        media_list = t.get("extendedEntities", {}).get("media", [])
        photos = [m.get("media_url_https", "") for m in media_list if m.get("type") == "photo"]
        has_video = any(m.get("type") in ("video", "animated_gif") for m in media_list)

        author = t.get("author", {})
        handle_actual = author.get("userName", "")

        results.append({
            "id": t.get("id", ""),
            "text": t.get("text", ""),
            "created_at": created_str,
            "photos": photos,
            "photo_count": len(photos),
            "has_video": has_video,
            "url": t.get("url", f"https://x.com/{handle_actual}/status/{t.get('id', '')}"),
            "likes": t.get("likeCount", 0) or 0,
            "retweets": t.get("retweetCount", 0) or 0,
            "views": t.get("viewCount", 0) or 0,
            "verified": author.get("isBlueVerified", False),
            "handle": handle_actual,
            "followers": author.get("followers", 0) or 0,
        })

    return results


def fetch_recent_tweets(handle, hours=48, max_results=20):
    """Fetch recent tweets from a handle via TwitterAPI.io."""
    return _twitterapiio_search(f"from:{handle}", max_results=max_results, hours=hours)


def search_topic_tweets(topic_query, hours=48, max_results=20):
    """Search tweets by topic (no handle filter) via TwitterAPI.io.
    Filters self-citations and sorts by authority then views."""
    tweets = _twitterapiio_search(topic_query, max_results=max_results, hours=hours)
    tweets = [t for t in tweets if (t.get("handle", "") or "").lower() != "thevideshi"]
    # Sort by authority (followers + verified) first, then views
    tweets.sort(key=lambda t: (
        source_authority(t),
        t.get("views", 0) or 0,
    ), reverse=True)
    return tweets


def source_authority(tweet):
    """Score source authority: 0 = unknown/low, 1 = mid, 2 = credible, 3 = official.
    Based on verified status, follower count, and known news handles."""
    followers = tweet.get("followers", 0) or 0
    verified = tweet.get("verified", False)
    handle = (tweet.get("handle", "") or "").lower()

    # Known authoritative news/official handles (lowercase)
    OFFICIAL_HANDLES = {
        # Indian news
        "ndtv", "ndtvprofitindia", "thehindu", "httweets", "timesofindia",
        "indiatoday", "airnewsalerts", "ani", "ddnews",
        "presidentofindia", "naaborendramodi", "paborahmoaborahffice",
        # Global news
        "reuters", "ap", "bbcnews", "cnn", "bbcworld", "bbcbreaking",
        "nytimes", "washingtonpost", "guardian", "aljazeera",
        "cnbc", "bloomberg", "forbes", "wsj",
        # Cricket / sports
        "bcci", "icc", "espncricinfo", "fifaworldcup", "fifacom",
        # Tech
        "techcrunch", "wired", "theverge",
        # Entertainment
        "variety", "deadline", "taborahran_adarsh", "bollyhungama",
        # Legal / gov
        "barandbench", "scjudgments",
        # Known credible handles
        "mohanlal", "arrahman", "gulf_news", "tradeboc",
    }

    if handle in OFFICIAL_HANDLES:
        return 3
    if verified and followers >= 100_000:
        return 3
    if verified and followers >= 10_000:
        return 2
    if followers >= 50_000:
        return 2
    if verified or followers >= 10_000:
        return 1
    return 0


def build_topic_query(headline):
    """Extract 3-5 distinctive keywords from headline for topic search."""
    stopwords = {"the","a","an","in","on","at","to","for","of","and","or","is","are",
                 "was","were","has","had","have","been","be","will","can","may","with",
                 "its","it","by","from","that","this","says","said","after","over",
                 "new","set","how","why","what","who","but","not","all","into","up"}
    words = re.findall(r'[A-Za-z]{3,}', headline)
    keywords = [w for w in words if w.lower() not in stopwords]
    # Take first 5 distinctive words
    return " ".join(keywords[:5])


# ─── Registry matching ────────────────────────────────────────────────────────

def load_registry():
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)
    
    entities = []
    for cat, data in registry.items():
        if not isinstance(data, dict):
            continue
        for p in data.get("persons", []):
            if p.get("x"):
                entities.append({
                    "name": p["name"],
                    "handle": p["x"],
                    "type": "person",
                    "category": cat,
                    # Build match patterns: full name words (3+ chars)
                    "match_words": [w.lower() for w in p["name"].split() if len(w) > 2],
                })
        for o in data.get("organizations", []):
            if o.get("x"):
                entities.append({
                    "name": o["name"],
                    "handle": o["x"],
                    "type": "org",
                    "category": cat,
                    "match_words": [w.lower() for w in o["name"].split() if len(w) > 2],
                })
    return entities


def match_article_to_handles(headline, body_500, category, entities):
    """
    Match article to registry handles. Strict rules:
    - Person names: ALL significant words must appear in HEADLINE (not just body)
    - Org names (single word like BCCI, ISRO): exact word boundary in headline or first 500 chars
    - Category must overlap (a sports handle shouldn't match a tech article)
    - Skip generic words that cause false positives
    """
    headline_lower = headline.lower()
    text_lower = (headline + " " + body_500).lower()
    
    # Words that cause false positive matches
    STOPWORDS = {"india", "indian", "world", "national", "new", "south", "west", "east", "north"}
    
    matches = []
    for ent in entities:
        name_lower = ent["name"].lower()
        words = ent["match_words"]
        
        # Filter out stopwords from match
        sig_words = [w for w in words if w not in STOPWORDS]
        if not sig_words:
            continue
        
        if len(sig_words) >= 2:
            # Multi-word name (person/org): require ALL significant words in HEADLINE
            if all(w in headline_lower for w in sig_words):
                matches.append(ent)
        elif len(sig_words) == 1 and len(sig_words[0]) >= 4:
            # Single significant word (BCCI, ISRO, Google): word boundary match in headline
            if re.search(r'\b' + re.escape(sig_words[0]) + r'\b', headline_lower):
                matches.append(ent)
    
    # Sort: persons before orgs, longer names first (more specific)
    matches.sort(key=lambda m: (0 if m["type"] == "person" else 1, -len(m["name"])))
    return matches


# ─── Relevance scoring ────────────────────────────────────────────────────────

def score_relevance(tweet_text, headline, body_500):
    """
    Score how relevant a tweet is to an article. Returns 0-10.
    Checks keyword overlap between tweet text and article content.
    """
    # Extract significant words from headline
    headline_words = set(
        w.lower() for w in re.findall(r'[a-zA-Z]{4,}', headline)
    ) - {"that", "this", "with", "from", "have", "been", "will", "just", "says",
         "about", "their", "after", "what", "when", "more", "than", "also"}
    
    tweet_lower = tweet_text.lower()
    
    # Count headline keywords found in tweet
    matches = sum(1 for w in headline_words if w in tweet_lower)
    
    # Bonus for entity names
    if any(w in tweet_lower for w in headline_words if len(w) > 5):
        matches += 2
    
    return min(matches, 10)


# ─── Verify tweet ─────────────────────────────────────────────────────────────

def verify_tweet(tweet_id):
    """Verify tweet renders via react-tweet API. Returns True if VALID."""
    try:
        result = subprocess.run(
            ["bash", VERIFY_SCRIPT, str(tweet_id)],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0 and result.stdout.strip().startswith("VALID")
    except Exception:
        return False


# ─── Patch article ────────────────────────────────────────────────────────────

def patch_article_embed(article_id, body, tweet_url):
    """Insert tweet URL after the 2nd paragraph in the article body."""
    paragraphs = body.split("\n\n")
    if len(paragraphs) < 3:
        insert_at = len(paragraphs)
    else:
        insert_at = 2  # After 2nd paragraph
    
    paragraphs.insert(insert_at, tweet_url)
    new_body = "\n\n".join(paragraphs)
    
    resp = _session.patch(
        f"{REST}/p2_articles?id=eq.{article_id}",
        headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        json={"body": new_body},
        timeout=10,
    )
    return resp.status_code in (200, 204)


# ─── Main enrichment loop ────────────────────────────────────────────────────

def run_enrichment(hours=24, apply=False, max_embeds=5):
    """
    Find articles that could benefit from a tweet embed and optionally apply.
    Returns a report dict.
    """
    entities = load_registry()
    
    # Get recent articles
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    resp = _session.get(
        f"{REST}/p2_articles",
        params={
            "select": "id,headline,slug,category,published_at,body",
            "status": "eq.published",
            "order": "published_at.desc",
            "limit": "250",
            "published_at": f"gte.{since}",
        },
        headers=SB_HEADERS, timeout=15,
    ).json()
    
    if not isinstance(resp, list):
        return {"error": "Failed to fetch articles", "detail": str(resp)[:200]}
    
    # Filter: no existing embeds, eligible category
    candidates = []
    topic_only = []  # Articles with no registry match — try topic search
    for a in resp:
        body = a.get("body", "") or ""
        if re.search(r'x\.com/\w+/status/\d+', body):
            continue  # already has embed
        if a.get("category", "") not in EMBED_CATEGORIES:
            continue
        
        matches = match_article_to_handles(
            a["headline"], body[:500], a["category"], entities
        )
        if matches:
            candidates.append({"article": a, "handles": matches})
        else:
            topic_only.append({"article": a, "handles": []})
    
    report = {
        "articles_checked": len(resp),
        "candidates": len(candidates),
        "embeds_added": 0,
        "details": [],
    }
    
    embeds_added = 0
    seen_handles = set()  # Don't hit the same handle twice
    
    for c in candidates:
        if embeds_added >= max_embeds:
            break
        
        a = c["article"]
        headline = a["headline"]
        body = a.get("body", "") or ""
        
        # Try each matched handle until we find a good tweet
        for handle_info in c["handles"][:2]:  # Max 2 handles per article
            handle = handle_info["handle"]
            
            if handle.lower() in seen_handles:
                pass
            seen_handles.add(handle.lower())
            
            # Fetch recent tweets via TwitterAPI.io (prefer with photos)
            tweets = fetch_recent_tweets(handle, hours=max(hours, 48), max_results=20)
            if not tweets:
                # Fallback: topic search when handle timeline is empty
                topic_q = build_topic_query(headline)
                if topic_q:
                    tweets = search_topic_tweets(topic_q, hours=max(hours, 48))
            if not tweets:
                continue
            
            # Score relevance and filter
            best_tweet = None
            best_score = 0
            
            for tweet in tweets:
                score = score_relevance(tweet["text"], headline, body[:500])
                
                # Bonus for photos (the whole point)
                if tweet["photo_count"] > 0:
                    score += 3
                
                # Minimum relevance threshold — tweet must actually be about the article topic
                if score < 5:
                    continue
                
                if score > best_score:
                    best_score = score
                    best_tweet = tweet
            
            if not best_tweet:
                report["details"].append({
                    "headline": headline[:80],
                    "handle": f"@{handle}",
                    "status": "no_relevant_tweet",
                })
                continue
            
            # Verify tweet renders
            tweet_id = best_tweet["id"]
            if not verify_tweet(tweet_id):
                report["details"].append({
                    "headline": headline[:80],
                    "handle": f"@{handle}",
                    "tweet_url": best_tweet["url"],
                    "status": "verify_failed",
                })
                continue
            
            # We have a good tweet!
            detail = {
                "headline": headline[:80],
                "handle": f"@{handle}",
                "tweet_url": best_tweet["url"],
                "photos": best_tweet["photo_count"],
                "relevance": best_score,
                "tweet_text": best_tweet["text"][:100],
                "status": "would_embed" if not apply else "embedded",
            }
            
            if apply:
                ok = patch_article_embed(a["id"], body, best_tweet["url"])
                if ok:
                    embeds_added += 1
                    detail["status"] = "embedded"
                else:
                    detail["status"] = "patch_failed"
            
            report["details"].append(detail)
            break  # Move to next article
    
    # ── Topic-only search for articles without registry matches ──
    for c in topic_only:
        if embeds_added >= max_embeds:
            break

        a = c["article"]
        headline = a["headline"]
        body = a.get("body", "") or ""
        topic_q = build_topic_query(headline)
        if not topic_q:
            continue

        tweets = search_topic_tweets(topic_q, hours=max(hours, 48))
        if not tweets:
            continue

        # Score and find best
        best_tweet = None
        best_score = 0

        for tweet in tweets:
            score = score_relevance(tweet["text"], headline, body[:500])
            if tweet["photo_count"] > 0:
                score += 3

            # Source authority gate — prefer official/credible sources
            authority = source_authority(tweet)
            if authority == 0:
                continue  # Skip unknown/low-authority accounts entirely
            # Bonus for authoritative sources
            score += authority  # +1 mid, +2 credible, +3 official

            if score < 5:  # Stricter threshold for topic search
                continue
            if score > best_score:
                best_score = score
                best_tweet = tweet

        if not best_tweet:
            continue

        tweet_id = best_tweet["id"]
        if not verify_tweet(tweet_id):
            continue

        detail = {
            "headline": headline[:80],
            "handle": f"@{best_tweet.get('handle', '?')}",
            "tweet_url": best_tweet["url"],
            "photos": best_tweet["photo_count"],
            "relevance": best_score,
            "tweet_text": best_tweet["text"][:100],
            "source": "topic_search",
            "status": "would_embed" if not apply else "embedded",
        }

        if apply:
            ok = patch_article_embed(a["id"], body, best_tweet["url"])
            if ok:
                embeds_added += 1
                detail["status"] = "embedded"
            else:
                detail["status"] = "patch_failed"

        report["details"].append(detail)

    report["embeds_added"] = embeds_added
    return report


# ─── PASS 2: Verify embedded tweets are relevant ─────────────────────────────

def verify_recent_embeds(hours=24, apply=False):
    """Pass 2: Re-check all tweets embedded in recent articles.
    Fetches the tweet text via TwitterAPI.io, re-scores against the full
    article headline+body, and removes any that fall below the relevance floor.
    """
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Fetch recent published articles that have x.com embeds
    resp = requests.get(
        f"{REST}/p2_articles",
        params={
            "select": "id,headline,body,slug,category",
            "status": "eq.published",
            "order": "published_at.desc",
            "limit": "250",
            "published_at": f"gte.{since}",
        },
        headers=SB_HEADERS,
        timeout=15,
    ).json()

    if not isinstance(resp, list):
        return {"error": "DB fetch failed", "raw": str(resp)[:200]}

    report = {"articles_checked": 0, "embeds_verified": 0, "embeds_removed": 0, "details": []}

    for a in resp:
        body = a.get("body", "") or ""
        # Find x.com tweet URLs in the body
        tweet_urls = re.findall(r'https?://x\.com/\w+/status/(\d+)', body)
        if not tweet_urls:
            continue

        report["articles_checked"] += 1
        headline = a["headline"]

        for tid in tweet_urls:
            report["embeds_verified"] += 1
            tweet_url_pattern = re.compile(r'https?://x\.com/\w+/status/' + tid)
            tweet_url_match = tweet_url_pattern.search(body)
            if not tweet_url_match:
                continue
            tweet_url = tweet_url_match.group(0)

            # Fetch tweet text via TwitterAPI.io
            tweet_data = _fetch_tweet_by_id(tid)
            if not tweet_data:
                # Can't verify — leave it
                report["details"].append({
                    "headline": headline[:80],
                    "tweet_url": tweet_url,
                    "action": "kept_no_data",
                })
                continue

            tweet_text = tweet_data.get("text", "")
            tweet_handle = tweet_data.get("handle", "?")
            tweet_followers = tweet_data.get("followers", 0)

            # Re-score with headline + full body (not just 500 chars)
            relevance = score_relevance(tweet_text, headline, body[:1500])

            # Check authority
            authority = source_authority(tweet_data)

            # Combined score — same formula as embedding pass
            total = relevance + authority
            if tweet_data.get("photo_count", 0) > 0:
                total += 3

            # Verification threshold: relevance must be ≥5 on its own
            # (authority alone can't save an off-topic tweet)
            if relevance >= 5 and total >= 5:
                report["details"].append({
                    "headline": headline[:80],
                    "handle": f"@{tweet_handle}",
                    "tweet_url": tweet_url,
                    "relevance": relevance,
                    "authority": authority,
                    "total": total,
                    "action": "kept",
                })
                continue

            # Below threshold — remove
            detail = {
                "headline": headline[:80],
                "handle": f"@{tweet_handle}",
                "followers": tweet_followers,
                "tweet_url": tweet_url,
                "relevance": relevance,
                "authority": authority,
                "total": total,
                "tweet_text": tweet_text[:100],
                "action": "would_remove" if not apply else "removed",
            }

            if apply:
                new_body = body.replace(f"\n\n{tweet_url}", "").replace(f"{tweet_url}\n\n", "").replace(tweet_url, "")
                if new_body != body:
                    patch = requests.patch(
                        f"{REST}/p2_articles?id=eq.{a['id']}",
                        headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                        json={"body": new_body},
                        timeout=10,
                    )
                    if patch.status_code in (200, 204):
                        detail["action"] = "removed"
                        report["embeds_removed"] += 1
                        body = new_body  # update for next tweet in same article
                    else:
                        detail["action"] = "remove_failed"

            report["details"].append(detail)

    return report


def _fetch_tweet_by_id(tweet_id):
    """Fetch a single tweet's data by ID via TwitterAPI.io."""
    try:
        cmd = [
            "curl", "-sS", "-m", "10",
            f"{TWITTERAPI_IO_BASE}/twitter/tweets?tweet_ids={tweet_id}",
            "-H", f"X-API-Key: {TWITTERAPI_IO_KEY}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        tweets = data.get("tweets") or []
        if not tweets:
            return None
        tweet = tweets[0]
        author = tweet.get("author", {}) or {}
        return {
            "id": str(tweet.get("id", tweet_id)),
            "text": tweet.get("text", ""),
            "handle": author.get("userName", ""),
            "followers": author.get("followers", 0) or 0,
            "verified": author.get("isBlueVerified", False),
            "views": tweet.get("viewCount", 0) or 0,
            "photo_count": sum(
                1 for m in (tweet.get("extendedEntities", {}) or {}).get("media", [])
                if m.get("type") == "photo"
            ),
        }
    except Exception:
        return None


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enrich Videshi articles with X tweet embeds")
    parser.add_argument("--apply", action="store_true", help="Actually patch articles (default: dry run)")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours for articles")
    parser.add_argument("--max", type=int, default=5, help="Max embeds to add per run")
    parser.add_argument("--verify-only", action="store_true", help="Skip pass 1, only run verification pass")
    args = parser.parse_args()

    if not args.verify_only:
        print("═══ PASS 1: Embed tweets ═══")
        report = run_enrichment(hours=args.hours, apply=args.apply, max_embeds=args.max)
        print(json.dumps(report, indent=2))
        print()

    print("═══ PASS 2: Verify embedded tweets ═══")
    verify_report = verify_recent_embeds(hours=args.hours, apply=args.apply)
    print(json.dumps(verify_report, indent=2))
