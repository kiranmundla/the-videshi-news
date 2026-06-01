#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
from datetime import datetime, timezone

import requests
import tweepy

# --- Load env files ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                env[key] = val
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env.get("X_CONSUMER_KEY") or twitter_env.get("TWITTER_CONSUMER_KEY") or twitter_env.get("API_KEY")
CONSUMER_SECRET = twitter_env.get("X_CONSUMER_SECRET") or twitter_env.get("TWITTER_CONSUMER_SECRET") or twitter_env.get("API_SECRET")
ACCESS_TOKEN = twitter_env.get("X_ACCESS_TOKEN") or twitter_env.get("TWITTER_ACCESS_TOKEN") or twitter_env.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = twitter_env.get("X_ACCESS_TOKEN_SECRET") or twitter_env.get("TWITTER_ACCESS_TOKEN_SECRET") or twitter_env.get("ACCESS_TOKEN_SECRET")
SUPABASE_SERVICE_ROLE_KEY = supabase_env.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# Verify keys loaded
for name, val in [("CONSUMER_KEY", CONSUMER_KEY), ("CONSUMER_SECRET", CONSUMER_SECRET),
                   ("ACCESS_TOKEN", ACCESS_TOKEN), ("ACCESS_TOKEN_SECRET", ACCESS_TOKEN_SECRET),
                   ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_SERVICE_ROLE_KEY)]:
    if not val:
        print(f"ERROR: {name} not found in env files")
        sys.exit(1)

print("✓ All keys loaded")

# --- Fetch untweeted articles ---
headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    headers=headers,
    timeout=30
)
resp.raise_for_status()
articles = resp.json()
print(f"✓ Found {len(articles)} untweeted articles")

# Filter out articles with no image_url and take up to 4
eligible = [a for a in articles if a.get("image_url")]
selected = eligible[:4]
print(f"✓ Selected {len(selected)} articles to post (out of {len(eligible)} with images)")

if not selected:
    print("No articles to post. Done.")
    sys.exit(0)

# --- Category emoji mapping ---
CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

def compose_post(article):
    """Compose a long-form X post from an article. Returns the text."""
    cat = (article.get("category") or "news").lower().strip()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body (strip markdown formatting for plain text)
    body_clean = body.replace("##", "").replace("**", "").replace("*", "").replace("`", "")
    # Get first ~800 chars of body for context
    body_excerpt = body_clean[:2000]
    
    # Build the post - will be filled by the LLM caller
    # For now, create a structured template
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{subheadline}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

# --- Setup tweepy ---
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# --- Tweet log ---
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = {}
if os.path.exists(log_path):
    with open(log_path) as f:
        tweet_log = json.load(f)

# --- Output articles data for LLM to compose posts ---
print("\n=== ARTICLES DATA ===")
for i, article in enumerate(selected):
    print(f"\n--- ARTICLE {i+1} ---")
    print(f"ID: {article['id']}")
    print(f"SLUG: {article['slug']}")
    print(f"HEADLINE: {article['headline']}")
    print(f"SUBHEADLINE: {article.get('subheadline', 'N/A')}")
    print(f"CATEGORY: {article.get('category', 'news')}")
    print(f"IMAGE_URL: {article.get('image_url', 'N/A')}")
    body = (article.get('body') or '')[:1500]
    print(f"BODY_EXCERPT: {body}")
    print(f"--- END ARTICLE {i+1} ---")

print("\n=== END ARTICLES DATA ===")
