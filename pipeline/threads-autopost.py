#!/usr/bin/env python3
"""Auto-post recent Videshi articles to Threads."""

import json
import os
import re
import sys
import time
import requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
MAX_FETCH = 10
MAX_POST = 3

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supabase_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

# Category emoji map
CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle-health": "🧘",
    "markets-finance": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

def load_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}

def save_log(log):
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def fetch_articles():
    """Fetch recent published articles from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    params = {
        "status": "eq.published",
        "order": "published_at.desc",
        "limit": str(MAX_FETCH),
        "select": "id,slug,headline,subheadline,category,image_url,body"
    }
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()

def compose_post(article):
    """Compose a Threads post matching the X post format."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_display = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "").strip()
    # Make it punchy ALL CAPS
    headline_caps = headline.upper()
    
    # Extract a sharp 1-2 sentence summary from the body
    body = article.get("body") or ""
    summary = extract_summary(body, headline)
    
    slug = article.get("slug", "")
    url_line = f"📰 thevideshi.com/articles/{slug}"
    
    separator = "━━━━━━━━━━━━━━━━━━━━"
    
    post = f"""{emoji} {cat_display} | The Videshi

{separator}

{headline_caps}

{summary}

{url_line}"""
    
    # Trim to 500 chars if needed
    if len(post) > 500:
        # Shorten summary
        overhead = len(post) - 500
        if len(summary) > overhead + 20:
            summary = summary[:len(summary) - overhead - 3].rsplit(' ', 1)[0] + "..."
            post = f"""{emoji} {cat_display} | The Videshi

{separator}

{headline_caps}

{summary}

{url_line}"""
        else:
            # Drop summary entirely
            post = f"""{emoji} {cat_display} | The Videshi

{separator}

{headline_caps}

{url_line}"""
    
    # Final safety check
    if len(post) > 500:
        post = post[:497] + "..."
    
    return post

def extract_summary(body, headline):
    """Extract 1-2 sharp sentences from the article body."""
    # Strip markdown formatting
    text = re.sub(r'#{1,6}\s+', '', body)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Filter out very short or formatting-only lines
    good = [s.strip() for s in sentences if len(s.strip()) > 30 and not s.strip().startswith('|')]
    
    if not good:
        return ""
    
    # Take first 1-2 meaningful sentences (skip if too similar to headline)
    headline_words = set(headline.lower().split())
    result = []
    for s in good[:5]:
        s_words = set(s.lower().split())
        overlap = len(headline_words & s_words) / max(len(headline_words), 1)
        if overlap < 0.6:
            result.append(s)
            if len(result) >= 2:
                break
    
    if not result and good:
        result = good[:1]
    
    summary = ' '.join(result)
    # Cap summary length
    if len(summary) > 250:
        summary = summary[:247].rsplit(' ', 1)[0] + "..."
    
    return summary

def post_to_threads(post_text, image_url=None):
    """Post to Threads using the two-step API."""
    # Step 1: Create media container
    container_data = {
        "text": post_text,
        "access_token": THREADS_ACCESS_TOKEN
    }
    
    use_image = False
    if image_url:
        container_data["media_type"] = "IMAGE"
        container_data["image_url"] = image_url
        use_image = True
    else:
        container_data["media_type"] = "TEXT"
    
    resp = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
        data=container_data
    )
    
    result = resp.json()
    
    # Check for image errors, fall back to text
    if use_image and ("error" in result or resp.status_code != 200):
        print(f"  ⚠️  Image failed ({result.get('error', {}).get('message', 'unknown')}), falling back to text-only")
        container_data.pop("image_url", None)
        container_data["media_type"] = "TEXT"
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data=container_data
        )
        result = resp.json()
    
    if "id" not in result:
        raise Exception(f"Container creation failed: {result}")
    
    container_id = result["id"]
    
    # Step 2: Wait then publish
    wait_time = 15 if use_image else 5
    print(f"  ⏳ Waiting {wait_time}s for processing...")
    time.sleep(wait_time)
    
    resp = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
        data={
            "creation_id": container_id,
            "access_token": THREADS_ACCESS_TOKEN
        }
    )
    
    pub_result = resp.json()
    if "id" not in pub_result:
        raise Exception(f"Publish failed: {pub_result}")
    
    return pub_result["id"]


def main():
    print("=== Threads Auto-Post ===")
    print(f"Time: {datetime.utcnow().isoformat()}Z\n")
    
    # Fetch articles
    articles = fetch_articles()
    print(f"Fetched {len(articles)} recent articles")
    
    # Load log
    threads_log = load_log()
    print(f"Already posted: {len(threads_log)} articles\n")
    
    # Filter unposted articles with images
    to_post = []
    for a in articles:
        aid = str(a["id"])
        if aid in threads_log:
            continue
        if not a.get("image_url"):
            print(f"  Skipping (no image): {a.get('slug', 'unknown')}")
            continue
        to_post.append(a)
        if len(to_post) >= MAX_POST:
            break
    
    if not to_post:
        print("✅ No new articles to post.")
        return
    
    print(f"Will post {len(to_post)} articles:\n")
    
    posted = 0
    errors = 0
    
    for i, article in enumerate(to_post):
        aid = str(article["id"])
        slug = article.get("slug", "unknown")
        print(f"--- [{i+1}/{len(to_post)}] {slug} ---")
        
        try:
            post_text = compose_post(article)
            print(f"  Post ({len(post_text)} chars):")
            print(f"  {post_text[:100]}...")
            
            post_id = post_to_threads(post_text, article.get("image_url"))
            print(f"  ✅ Posted! ID: {post_id}")
            
            # Update log
            threads_log[aid] = {
                "slug": slug,
                "threads_post_id": str(post_id),
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            save_log(threads_log)
            posted += 1
            
            # Wait between posts
            if i < len(to_post) - 1:
                print("  ⏳ Waiting 10s before next post...")
                time.sleep(10)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1
    
    print(f"\n=== Summary ===")
    print(f"Posted: {posted}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()
