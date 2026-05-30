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
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

# Category emoji mapping
EMOJI_MAP = {
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

# --- Step 1: Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w') as f:
        json.dump(threads_log, f)

print(f"Threads log has {len(threads_log)} entries")

# --- Step 2: Fetch recent articles ---
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

# --- Step 3: Filter to unposted articles with images ---
candidates = []
for a in articles:
    aid = str(a["id"])
    if aid in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  Skipping {aid} ({a.get('headline','?')[:50]}) — no image")
        continue
    candidates.append(a)

candidates = candidates[:MAX_POSTS]
print(f"Will post {len(candidates)} articles")

if not candidates:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Step 4: Compose and post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = EMOJI_MAP.get(cat, "📰")
    cat_display = cat.upper().replace("-", " ")
    slug = article.get("slug", "")
    headline = article.get("headline", "").strip()
    body = article.get("body", "") or ""

    # Extract first substantive sentences from body for summary
    # Strip markdown formatting
    import re
    clean = re.sub(r'[#*>\[\]`_]', '', body)
    clean = re.sub(r'\!\[.*?\]\(.*?\)', '', clean)
    clean = re.sub(r'\(https?://[^\)]+\)', '', clean)
    clean = re.sub(r'https?://\S+', '', clean)
    sentences = re.split(r'(?<=[.!?])\s+', clean.strip())
    # Skip very short or header-like sentences
    good = [s.strip() for s in sentences if len(s.strip()) > 40 and not s.strip().startswith('|')]

    summary = ""
    if good:
        summary = good[0]
        if len(good) > 1 and len(summary) < 180:
            combined = summary + " " + good[1]
            if len(combined) < 250:
                summary = combined

    # Build post
    url_line = f"📰 thevideshi.com/articles/{slug}"
    separator = "━━━━━━━━━━━━━━━━━━━━"

    post = f"{emoji} {cat_display} | The Videshi\n\n{separator}\n\n{headline.upper()}\n\n{summary}\n\n{url_line}"

    # Trim if over 500 chars
    if len(post) > 500:
        # Shorten summary
        avail = 500 - len(post) + len(summary)
        if avail > 30:
            summary = summary[:avail-3].rsplit(' ', 1)[0] + "..."
        else:
            summary = ""
        post = f"{emoji} {cat_display} | The Videshi\n\n{separator}\n\n{headline.upper()}\n\n{summary}\n\n{url_line}"

    if len(post) > 500:
        post = post[:497] + "..."

    return post

posted = 0
errors = []

for i, article in enumerate(candidates):
    aid = str(article["id"])
    headline = article.get("headline", "?")
    print(f"\n--- Posting {i+1}/{len(candidates)}: {headline[:60]} ---")

    post_text = compose_post(article)
    print(f"Post text ({len(post_text)} chars):\n{post_text}\n")

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
        resp_json = resp.json()
        print(f"Container response: {resp.status_code} {resp_json}")

        if "id" not in resp_json:
            # Image might have failed — fall back to TEXT
            print(f"Image container failed, falling back to TEXT-only")
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
            resp_json = resp.json()
            print(f"Text container response: {resp.status_code} {resp_json}")

        if "id" not in resp_json:
            errors.append(f"{aid}: container creation failed: {resp_json}")
            continue

        container_id = resp_json["id"]

        # Step 2: Wait for processing then publish
        print(f"Waiting 10s for media processing...")
        time.sleep(10)

        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN,
            },
            timeout=30,
        )
        pub_json = resp.json()
        print(f"Publish response: {resp.status_code} {pub_json}")

        if "id" not in pub_json:
            errors.append(f"{aid}: publish failed: {pub_json}")
            continue

        post_id = str(pub_json["id"])

        # Update log
        threads_log[aid] = {
            "slug": article.get("slug", ""),
            "threads_post_id": post_id,
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(threads_log, f, indent=2)

        posted += 1
        print(f"✅ Posted successfully! Post ID: {post_id}")

    except Exception as e:
        errors.append(f"{aid}: exception: {str(e)}")
        print(f"❌ Error: {e}")

    # Wait between posts
    if i < len(candidates) - 1:
        print("Waiting 10s before next post...")
        time.sleep(10)

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: Posted {posted}/{len(candidates)} articles to Threads")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"Total entries in threads-log.json: {len(threads_log)}")
