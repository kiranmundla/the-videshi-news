#!/usr/bin/env python3
"""Post recent Videshi articles to Threads (@the.videshi)."""

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
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

# Category emoji mapping
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

# Load tracking log
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}

# Fetch recent articles
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

# Filter: not yet posted, has image_url
candidates = []
for a in articles:
    aid = str(a["id"])
    if aid in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  Skipping {aid} ({a.get('slug','?')}) — no image_url")
        continue
    candidates.append(a)

print(f"Candidates not yet posted: {len(candidates)}")
to_post = candidates[:MAX_POSTS]

if not to_post:
    print("Nothing new to post. Done.")
    sys.exit(0)

def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article.get("slug", "")
    headline = (article.get("headline") or "").strip()
    body = (article.get("body") or "")

    # Extract first 2 meaningful sentences from body for summary
    import re
    # Remove markdown formatting
    clean = re.sub(r'[#*_`>\[\]()]', '', body)
    clean = re.sub(r'\n+', ' ', clean).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    # Get first 2 non-trivial sentences
    summary_parts = []
    for s in sentences:
        s = s.strip()
        if len(s) > 30:
            summary_parts.append(s)
        if len(summary_parts) >= 2:
            break
    summary = ' '.join(summary_parts)

    # Build the post
    url = f"📰 thevideshi.com/articles/{slug}"
    separator = "━━━━━━━━━━━━━━━━━━━━"

    # Rewrite headline: ALL CAPS, punchy
    headline_caps = headline.upper()

    post = f"""{emoji} {cat_label} | The Videshi

{separator}

{headline_caps}

{summary}

{url}"""

    # Trim if over 500 chars — shorten summary
    if len(post) > 500:
        # Try with just 1 sentence
        summary = summary_parts[0] if summary_parts else ""
        post = f"""{emoji} {cat_label} | The Videshi

{separator}

{headline_caps}

{summary}

{url}"""

    if len(post) > 500:
        # Truncate summary to fit
        overhead = len(post) - len(summary)
        max_summary = 500 - overhead - 3
        summary = summary[:max_summary].rsplit(' ', 1)[0] + "..."
        post = f"""{emoji} {cat_label} | The Videshi

{separator}

{headline_caps}

{summary}

{url}"""

    return post

posted = 0
errors = []

for i, article in enumerate(to_post):
    aid = str(article["id"])
    slug = article.get("slug", "?")
    print(f"\n--- Posting {i+1}/{len(to_post)}: {slug} ---")

    post_text = compose_post(article)
    print(f"Post text ({len(post_text)} chars):")
    print(post_text[:200] + "..." if len(post_text) > 200 else post_text)

    # Step 1: Create media container WITH IMAGE
    container_data = {
        "media_type": "IMAGE",
        "image_url": article["image_url"],
        "text": post_text,
        "access_token": THREADS_ACCESS_TOKEN,
    }

    try:
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data=container_data,
        )
        resp_json = resp.json()
        print(f"Container response: {resp.status_code} {resp_json}")

        if "id" not in resp_json:
            # Image might have failed, try TEXT-only fallback
            print("Image container failed, falling back to TEXT-only...")
            container_data_text = {
                "media_type": "TEXT",
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN,
            }
            resp = requests.post(
                f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                data=container_data_text,
            )
            resp_json = resp.json()
            print(f"Text container response: {resp.status_code} {resp_json}")

        if "id" not in resp_json:
            err = f"Failed to create container for {slug}: {resp_json}"
            print(err)
            errors.append(err)
            continue

        container_id = resp_json["id"]

        # Step 2: Wait for processing then publish
        print("Waiting 10s for processing...")
        time.sleep(10)

        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN,
            },
        )
        pub_json = resp.json()
        print(f"Publish response: {resp.status_code} {pub_json}")

        if "id" not in pub_json:
            err = f"Failed to publish {slug}: {pub_json}"
            print(err)
            errors.append(err)
            continue

        post_id = pub_json["id"]
        print(f"✅ Published: post_id={post_id}")

        # Update log
        threads_log[aid] = {
            "slug": slug,
            "threads_post_id": str(post_id),
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, "w") as f:
            json.dump(threads_log, f, indent=2)

        posted += 1

        # Wait between posts
        if i < len(to_post) - 1:
            print("Waiting 10s before next post...")
            time.sleep(10)

    except Exception as e:
        err = f"Exception posting {slug}: {e}"
        print(err)
        errors.append(err)

print(f"\n=== Summary ===")
print(f"Posted: {posted}/{len(to_post)}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("No errors.")
