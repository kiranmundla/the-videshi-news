#!/usr/bin/env python3
"""
tweet-enricher.py — Automatically find and embed relevant X tweets in Videshi articles.

Uses the X API v2 to fetch recent tweets from handles in social-embed-registry.json,
matches them to recent articles by topic relevance, and patches the article body.

Flow:
  1. Get recent published articles without existing embeds (last 24h)
  2. Match article topics to registry handles (strict name matching)
  3. Fetch recent tweets from matched handles via X API
  4. Score tweet relevance against article content
  5. Verify tweet via react-tweet API (will it render?)
  6. Patch article body with the tweet URL after paragraph 2

Usage:
  python3 tweet-enricher.py              # dry run — show what would be embedded
  python3 tweet-enricher.py --apply      # actually patch articles in Supabase
  python3 tweet-enricher.py --hours 48   # look back N hours for articles (default 24)

Env: ~/workspace/.env.twitter, ~/workspace/.env.supabase
"""

import os
import sys
import json
import re
import subprocess
import importlib.util
from datetime import datetime, timezone, timedelta

# Load fetch-tweets module
_dir = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ft", os.path.join(_dir, "fetch-tweets.py"))
ft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ft)

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
load_env(os.path.expanduser("~/workspace/.env.twitter"))

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

VERIFY_SCRIPT = os.path.join(_dir, "verify-tweet.sh")
REGISTRY_PATH = os.path.join(_dir, "social-embed-registry.json")

# Categories where embeds make sense
EMBED_CATEGORIES = {"news", "sports", "entertainment", "technology", "nri-world", "immigration"}


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
            "limit": "50",
            "published_at": f"gte.{since}",
        },
        headers=SB_HEADERS, timeout=15,
    ).json()
    
    if not isinstance(resp, list):
        return {"error": "Failed to fetch articles", "detail": str(resp)[:200]}
    
    # Filter: no existing embeds, eligible category
    candidates = []
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
                # Already fetched this handle's timeline, use cached result
                pass
            seen_handles.add(handle.lower())
            
            # Fetch recent tweets (prefer with photos)
            tweets = ft.fetch_recent_tweets(handle, hours=max(hours, 48), max_results=10)
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
                
                # Minimum relevance threshold
                if score < 3:
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
    
    report["embeds_added"] = embeds_added
    return report


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enrich Videshi articles with X tweet embeds")
    parser.add_argument("--apply", action="store_true", help="Actually patch articles (default: dry run)")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours for articles")
    parser.add_argument("--max", type=int, default=5, help="Max embeds to add per run")
    args = parser.parse_args()
    
    report = run_enrichment(hours=args.hours, apply=args.apply, max_embeds=args.max)
    print(json.dumps(report, indent=2))
