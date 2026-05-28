#!/usr/bin/env python3
"""Post recently published Videshi articles to Threads (@the.videshi)."""

import json
import os
import sys
import time
import requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
MAX_POSTS = 3

# Load credentials
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supabase_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

# Category emoji mapping
EMOJI = {
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

# --- Step 1: Fetch recent published articles ---
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "order": "published_at.desc",
        "limit": "10",
        "select": "id,slug,headline,subheadline,category,image_url,body",
    },
    headers=headers,
)
resp.raise_for_status()
articles = resp.json()
print(f"Fetched {len(articles)} recent published articles")

# --- Step 2: Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# --- Step 3: Filter to unposted articles with images ---
to_post = []
for a in articles:
    aid = str(a["id"])
    if aid in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  Skipping {a['slug']} — no image_url")
        continue
    to_post.append(a)
    if len(to_post) >= MAX_POSTS:
        break

print(f"Articles to post: {len(to_post)}")
if not to_post:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Step 4: Compose and post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article["slug"]
    headline = article["headline"].upper()
    
    # Extract a sharp summary from the body
    body = article.get("body") or article.get("subheadline") or ""
    # Get first meaningful paragraph from body for summary
    summary = ""
    if body:
        # Try to get first 1-2 sentences that aren't just the headline
        paragraphs = [p.strip() for p in body.split("\n") if p.strip() and len(p.strip()) > 30]
        # Skip markdown headers
        paragraphs = [p for p in paragraphs if not p.startswith("#") and not p.startswith("![")]
        # Clean markdown formatting
        for p in paragraphs[:3]:
            clean = p.replace("**", "").replace("*", "").replace("`", "").strip()
            # Skip if it's basically the headline
            if clean.upper()[:30] == headline[:30]:
                continue
            summary = clean
            break
    
    if not summary and article.get("subheadline"):
        summary = article["subheadline"]
    
    # Truncate summary if needed
    if len(summary) > 200:
        summary = summary[:197].rsplit(" ", 1)[0] + "..."
    
    url = f"thevideshi.com/articles/{slug}"
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}

📰 {url}"""
    
    # Ensure within 500 chars
    if len(post) > 500:
        # Trim summary more aggressively
        avail = 500 - len(post) + len(summary)
        if avail > 20:
            summary = summary[:avail - 3].rsplit(" ", 1)[0] + "..."
            post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}

📰 {url}"""
        else:
            # Drop summary entirely
            post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━

{headline}

📰 {url}"""
    
    return post[:500]

posted = 0
errors = []

for i, article in enumerate(to_post):
    slug = article["slug"]
    post_text = compose_post(article)
    print(f"\n--- Posting {i+1}/{len(to_post)}: {slug} ---")
    print(f"Text ({len(post_text)} chars):\n{post_text}\n")
    
    # Step 1: Create media container with image
    image_url = article["image_url"]
    container_data = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": post_text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    
    try:
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data=container_data,
            timeout=30,
        )
        container_resp = resp.json()
        print(f"Container response: {container_resp}")
        
        if "id" not in container_resp:
            # Image failed — fallback to text-only
            print(f"  Image container failed, falling back to TEXT")
            container_data = {
                "media_type": "TEXT",
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN,
            }
            resp = requests.post(
                f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                data=container_data,
                timeout=30,
            )
            container_resp = resp.json()
            print(f"  Text container response: {container_resp}")
            if "id" not in container_resp:
                errors.append(f"{slug}: container creation failed — {container_resp}")
                continue
        
        container_id = container_resp["id"]
        
        # Step 2: Wait for processing then publish
        print(f"  Waiting 12s for media processing...")
        time.sleep(12)
        
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN,
            },
            timeout=30,
        )
        publish_resp = resp.json()
        print(f"  Publish response: {publish_resp}")
        
        if "id" not in publish_resp:
            errors.append(f"{slug}: publish failed — {publish_resp}")
            continue
        
        post_id = publish_resp["id"]
        print(f"  ✅ Published! Post ID: {post_id}")
        
        # Update log
        threads_log[str(article["id"])] = {
            "slug": slug,
            "threads_post_id": str(post_id),
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, "w") as f:
            json.dump(threads_log, f, indent=2)
        
        posted += 1
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  Waiting 10s before next post...")
            time.sleep(10)
    
    except Exception as e:
        errors.append(f"{slug}: {str(e)}")
        print(f"  ❌ Error: {e}")

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: {posted}/{len(to_post)} articles posted to Threads")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"Total in threads-log.json: {len(threads_log)}")
