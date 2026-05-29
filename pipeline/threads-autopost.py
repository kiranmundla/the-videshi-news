#!/usr/bin/env python3
"""Post recent Videshi articles to Threads (@the.videshi)."""

import json, os, sys, time, requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# Load creds
def load_env(path):
    d = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                d[k.strip()] = v.strip()
    return d

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")

CATEGORY_EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏",
    "travel": "✈️", "lifestyle-health": "🧘", "markets-finance": "📈",
    "technology": "💻", "sports": "🏏", "entertainment": "🎬", "food": "🍛",
}

# --- Fetch articles ---
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
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
print(f"Fetched {len(articles)} recent published articles")

# --- Load log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# --- Filter unposted ---
unposted = [a for a in articles if str(a["id"]) not in threads_log and a.get("image_url")]
print(f"Unposted with images: {len(unposted)}")

to_post = unposted[:3]
if not to_post:
    print("Nothing new to post. Done.")
    sys.exit(0)

# --- Compose & post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")

    headline = article["headline"].upper()
    # Trim headline if too long
    if len(headline) > 120:
        headline = headline[:117] + "..."

    # Extract summary from body
    body = article.get("body") or article.get("subheadline") or ""
    # Get first meaningful paragraph from body
    summary = ""
    if body:
        paragraphs = [p.strip() for p in body.split("\n") if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("!") and len(p.strip()) > 40]
        if paragraphs:
            summary = paragraphs[0]
            # Clean markdown
            import re
            summary = re.sub(r'\*\*([^*]+)\*\*', r'\1', summary)
            summary = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', summary)
            summary = re.sub(r'<[^>]+>', '', summary)
            # Trim to ~200 chars max
            if len(summary) > 200:
                summary = summary[:197].rsplit(' ', 1)[0] + "..."

    slug = article["slug"]
    url = f"📰 thevideshi.com/articles/{slug}"

    post = f"{emoji} {cat_label} | The Videshi\n\n━━━━━━━━━━━━━━━━━━━━\n\n{headline}\n\n{summary}\n\n{url}"

    # Ensure under 500 chars
    if len(post) > 500:
        # Trim summary
        over = len(post) - 500
        if summary and len(summary) > over + 20:
            summary = summary[:len(summary) - over - 3].rsplit(' ', 1)[0] + "..."
            post = f"{emoji} {cat_label} | The Videshi\n\n━━━━━━━━━━━━━━━━━━━━\n\n{headline}\n\n{summary}\n\n{url}"
        else:
            # Drop summary
            post = f"{emoji} {cat_label} | The Videshi\n\n━━━━━━━━━━━━━━━━━━━━\n\n{headline}\n\n{url}"

    if len(post) > 500:
        post = post[:500]

    return post


posted = 0
errors = []

for i, article in enumerate(to_post):
    post_text = compose_post(article)
    print(f"\n--- Article {i+1}: {article['headline'][:60]}... ---")
    print(f"Post text ({len(post_text)} chars):\n{post_text}\n")

    # Step 1: Create container with image
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
            timeout=30
        )
        cresp = resp.json()
        print(f"Container response: {cresp}")

        if "id" not in cresp:
            # Image failed - fall back to text
            print("Image container failed, falling back to TEXT...")
            container_data = {
                "media_type": "TEXT",
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN,
            }
            resp = requests.post(
                f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                data=container_data,
                timeout=30
            )
            cresp = resp.json()
            print(f"Text container response: {cresp}")
            if "id" not in cresp:
                errors.append(f"{article['id']}: container creation failed: {cresp}")
                continue

        container_id = cresp["id"]

        # Step 2: Wait then publish
        print("Waiting 12s for processing...")
        time.sleep(12)

        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN,
            },
            timeout=30
        )
        pub_data = pub_resp.json()
        print(f"Publish response: {pub_data}")

        if "id" in pub_data:
            post_id = pub_data["id"]
            threads_log[str(article["id"])] = {
                "slug": article["slug"],
                "threads_post_id": str(post_id),
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            with open(LOG_PATH, 'w') as f:
                json.dump(threads_log, f, indent=2)
            posted += 1
            print(f"✅ Posted! ID: {post_id}")
        else:
            errors.append(f"{article['id']}: publish failed: {pub_data}")
            print(f"❌ Publish failed")

    except Exception as e:
        errors.append(f"{article['id']}: {str(e)}")
        print(f"❌ Error: {e}")

    # Wait between posts
    if i < len(to_post) - 1:
        print("Waiting 10s before next post...")
        time.sleep(10)

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: {posted}/{len(to_post)} articles posted to Threads")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("No errors.")
