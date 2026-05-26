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
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
MAX_ARTICLES = 3
POST_DELAY = 10  # seconds between posts

# Load env files
def load_env(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        print(f"ERROR: {path} not found")
        sys.exit(1)
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env.get("THREADS_ACCESS_TOKEN")
SUPABASE_URL = supa_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = supa_env.get("SUPABASE_SERVICE_ROLE_KEY")

if not THREADS_ACCESS_TOKEN:
    print("ERROR: THREADS_ACCESS_TOKEN not found"); sys.exit(1)
if not SUPABASE_KEY:
    print("ERROR: SUPABASE_SERVICE_ROLE_KEY not found"); sys.exit(1)

# Category emoji mapping
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

# --- 1. Load threads log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w') as f:
        json.dump(threads_log, f, indent=2)

print(f"Threads log has {len(threads_log)} existing entries.")

# --- 2. Fetch recent published articles ---
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
        "select": "id,slug,headline,subheadline,category,image_url",
    },
    headers=headers,
)

if resp.status_code != 200:
    print(f"ERROR: Supabase fetch failed: {resp.status_code} {resp.text}")
    sys.exit(1)

articles = resp.json()
print(f"Fetched {len(articles)} recent articles from Supabase.")

# --- 3. Filter out already-posted ---
unposted = [a for a in articles if str(a['id']) not in threads_log]
print(f"Found {len(unposted)} unposted articles.")

to_post = unposted[:MAX_ARTICLES]
if not to_post:
    print("No new articles to post. Done.")
    sys.exit(0)

print(f"Will post {len(to_post)} articles.\n")

# --- 4. Post each article ---
posted_count = 0
errors = []

for i, article in enumerate(to_post):
    slug = article.get('slug', '')
    headline = article.get('headline', 'Untitled')
    subheadline = article.get('subheadline', '')
    category = (article.get('category') or 'news').lower().strip()
    emoji = CATEGORY_EMOJI.get(category, "📰")

    # Build the post text
    link = f"thevideshi.com/articles/{slug}"

    # Use subheadline as summary, fallback to headline
    summary = subheadline if subheadline else headline

    post_text = f"{emoji} {headline}\n\n{summary}\n\n🔗 {link}"

    # Truncate if over 500 chars
    if len(post_text) > 500:
        # Shorten summary to fit
        max_summary = 500 - len(f"{emoji} {headline}\n\n\n\n🔗 {link}") - 3
        if max_summary > 20:
            summary = summary[:max_summary] + "..."
            post_text = f"{emoji} {headline}\n\n{summary}\n\n🔗 {link}"
        else:
            post_text = post_text[:497] + "..."

    print(f"--- Article {i+1}/{len(to_post)} ---")
    print(f"ID: {article['id']}")
    print(f"Headline: {headline}")
    print(f"Category: {category}")
    print(f"Post ({len(post_text)} chars):\n{post_text}\n")

    try:
        # Step 1: Create media container
        create_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data={
                "media_type": "TEXT",
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN,
            },
        )

        if create_resp.status_code != 200:
            err = f"Create container failed for {article['id']}: {create_resp.status_code} {create_resp.text}"
            print(f"ERROR: {err}")
            errors.append(err)
            continue

        container_id = create_resp.json().get("id")
        if not container_id:
            err = f"No container ID returned for {article['id']}: {create_resp.text}"
            print(f"ERROR: {err}")
            errors.append(err)
            continue

        print(f"Container created: {container_id}")

        # Wait for processing
        time.sleep(3)

        # Step 2: Publish
        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN,
            },
        )

        if pub_resp.status_code != 200:
            err = f"Publish failed for {article['id']}: {pub_resp.status_code} {pub_resp.text}"
            print(f"ERROR: {err}")
            errors.append(err)
            continue

        post_id = pub_resp.json().get("id")
        if not post_id:
            err = f"No post ID returned for {article['id']}: {pub_resp.text}"
            print(f"ERROR: {err}")
            errors.append(err)
            continue

        print(f"Published! Post ID: {post_id}")

        # Update log
        threads_log[str(article['id'])] = {
            "slug": slug,
            "threads_post_id": str(post_id),
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(threads_log, f, indent=2)

        posted_count += 1
        print(f"Logged successfully.\n")

    except Exception as e:
        err = f"Exception posting {article['id']}: {str(e)}"
        print(f"ERROR: {err}")
        errors.append(err)

    # Rate limit delay (skip after last post)
    if i < len(to_post) - 1:
        print(f"Waiting {POST_DELAY}s before next post...")
        time.sleep(POST_DELAY)

# --- Summary ---
print("\n=== SUMMARY ===")
print(f"Posted: {posted_count}/{len(to_post)}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("No errors.")
print("Done.")
