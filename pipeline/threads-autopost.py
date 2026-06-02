#!/usr/bin/env python3
"""Post recent Videshi articles to Threads (@the.videshi)."""

import json, os, sys, time, requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
MAX_POSTS = 3

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                key = key.replace('export ', '').strip()
                env[key] = val.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

# Category emoji mapping
CATEGORY_EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏",
    "travel": "✈️", "lifestyle-health": "🧘", "markets-finance": "📈",
    "technology": "💻", "sports": "🏏", "entertainment": "🎬", "food": "🍛"
}

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# --- Fetch recent articles ---
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "order": "published_at.desc",
        "limit": "10",
        "select": "id,slug,headline,subheadline,category,image_url,body"
    },
    headers=headers
)
resp.raise_for_status()
articles = resp.json()
print(f"Fetched {len(articles)} recent articles")

# Filter: not yet posted, has image
candidates = []
for a in articles:
    aid = str(a["id"])
    if aid in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  Skipping {a['slug']} — no image_url")
        continue
    candidates.append(a)

candidates = candidates[:MAX_POSTS]
print(f"Candidates to post: {len(candidates)}")

if not candidates:
    print("Nothing to post.")
    sys.exit(0)

# --- Compose and post ---
def compose_post(article):
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article["slug"]
    headline = article["headline"]
    body = article.get("body", "") or ""

    # Extract first meaningful sentences from body for summary
    # Clean markdown
    import re
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body)  # links
    clean = re.sub(r'[#*_>`]', '', clean)  # markdown chars
    clean = re.sub(r'\n+', ' ', clean).strip()
    
    # Get first 2 sentences
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    summary_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) > 30:  # skip short fragments
            summary_sentences.append(s)
            if len(summary_sentences) >= 2:
                break
    summary = ' '.join(summary_sentences)

    url = f"📰 thevideshi.com/articles/{slug}"
    separator = "━━━━━━━━━━━━━━━━━━━━"
    header = f"{emoji} {cat_label} | The Videshi"

    # Make headline punchy and ALL CAPS
    punchy_headline = headline.upper()
    # Trim if too long
    if len(punchy_headline) > 100:
        punchy_headline = punchy_headline[:97] + "..."

    post = f"{header}\n\n{separator}\n\n{punchy_headline}\n\n{summary}\n\n{url}"

    # Trim summary to fit 500 chars
    while len(post) > 500 and summary:
        # Remove last word from summary
        summary = summary.rsplit(' ', 1)[0]
        if not summary.endswith('.'):
            summary = summary.rstrip('.,;:!? ') + '.'
        post = f"{header}\n\n{separator}\n\n{punchy_headline}\n\n{summary}\n\n{url}"

    return post

posted = 0
errors = []

for i, article in enumerate(candidates):
    slug = article["slug"]
    aid = str(article["id"])
    print(f"\n--- Posting [{i+1}/{len(candidates)}]: {slug} ---")

    post_text = compose_post(article)
    print(f"Post text ({len(post_text)} chars):\n{post_text[:200]}...")

    # Step 1: Create media container with image
    image_url = article["image_url"]
    container_data = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": post_text,
        "access_token": THREADS_ACCESS_TOKEN
    }

    try:
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data=container_data,
            timeout=30
        )
        resp_json = resp.json()
        print(f"Container response: {resp_json}")

        if "error" in resp_json or "id" not in resp_json:
            print(f"Image container failed, falling back to TEXT")
            container_data = {
                "media_type": "TEXT",
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN
            }
            resp = requests.post(
                f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                data=container_data,
                timeout=30
            )
            resp_json = resp.json()
            print(f"Text container response: {resp_json}")

        if "id" not in resp_json:
            errors.append(f"{slug}: container creation failed: {resp_json}")
            continue

        container_id = resp_json["id"]

        # Step 2: Wait for processing then publish
        time.sleep(12)
        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN
            },
            timeout=30
        )
        pub_json = pub_resp.json()
        print(f"Publish response: {pub_json}")

        if "id" not in pub_json:
            errors.append(f"{slug}: publish failed: {pub_json}")
            continue

        post_id = str(pub_json["id"])
        print(f"✅ Posted: {slug} -> {post_id}")

        # Update log
        threads_log[aid] = {
            "slug": slug,
            "threads_post_id": post_id,
            "posted_at": datetime.utcnow().isoformat() + "Z"
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(threads_log, f, indent=2)

        posted += 1

        # Wait between posts
        if i < len(candidates) - 1:
            print("Waiting 10s before next post...")
            time.sleep(10)

    except Exception as e:
        errors.append(f"{slug}: {str(e)}")
        print(f"❌ Error: {e}")

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: {posted}/{len(candidates)} posted to Threads")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("No errors.")
