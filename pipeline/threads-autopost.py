#!/usr/bin/env python3
"""Auto-post recent Videshi articles to Threads (@the.videshi)."""

import json, os, time, sys, requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            env[key.strip()] = val.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_SERVICE_ROLE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

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

# --- Load tracking log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}

# --- Fetch recent published articles ---
headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
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

# Filter: not already posted, has image_url
candidates = []
for a in articles:
    aid = str(a["id"])
    if aid in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  Skipping (no image): {a.get('headline','?')[:60]}")
        continue
    candidates.append(a)

print(f"Candidates after filtering: {len(candidates)}")
to_post = candidates[:3]

if not to_post:
    print("Nothing new to post. Done.")
    sys.exit(0)

# --- Compose & post ---
def compose_post(article):
    cat = article.get("category", "news") or "news"
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article.get("slug", "")

    # Rewrite headline: punchy ALL CAPS
    headline = article.get("headline", "").strip()
    headline_caps = headline.upper()

    # Extract summary from body (first meaningful paragraph)
    body = article.get("body", "") or ""
    subheadline = article.get("subheadline", "") or ""
    summary = subheadline.strip()
    if not summary:
        # Try to grab first paragraph from body
        for para in body.split("\n"):
            para = para.strip()
            if len(para) > 40 and not para.startswith("#") and not para.startswith("!"):
                summary = para[:200]
                break

    # Build the post
    url = f"📰 thevideshi.com/articles/{slug}"
    header = f"{emoji} {cat_label} | The Videshi"
    separator = "━━━━━━━━━━━━━━━━━━━━"

    post = f"{header}\n\n{separator}\n\n{headline_caps}\n\n{summary}\n\n{url}"

    # Trim to 500 chars if needed
    if len(post) > 500:
        # Shorten summary
        available = 500 - len(header) - len(separator) - len(headline_caps) - len(url) - 10  # newlines
        if available > 20:
            summary = summary[:available-3].rsplit(" ", 1)[0] + "..."
        else:
            summary = ""
        post = f"{header}\n\n{separator}\n\n{headline_caps}\n\n{summary}\n\n{url}" if summary else f"{header}\n\n{separator}\n\n{headline_caps}\n\n{url}"

    return post[:500]

posted = 0
errors = 0

for i, article in enumerate(to_post):
    post_text = compose_post(article)
    print(f"\n--- Post {i+1}/{len(to_post)} ---")
    print(f"Article: {article['headline'][:80]}")
    print(f"Post ({len(post_text)} chars):\n{post_text}\n")

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
        )
        resp_json = resp.json()
        print(f"Container response: {resp.status_code} {resp_json}")

        if "id" not in resp_json:
            # Image might have failed, fall back to TEXT
            print("Image container failed, falling back to TEXT...")
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
                print(f"ERROR: Could not create container: {resp_json}")
                errors += 1
                continue

        container_id = resp_json["id"]

        # Step 2: Wait for processing then publish
        print("Waiting 10s for image processing...")
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
            print(f"ERROR: Publish failed: {pub_json}")
            errors += 1
            continue

        post_id = pub_json["id"]
        print(f"✅ Posted! Threads post ID: {post_id}")

        # Update log
        threads_log[str(article["id"])] = {
            "slug": article["slug"],
            "threads_post_id": str(post_id),
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, "w") as f:
            json.dump(threads_log, f, indent=2)

        posted += 1

    except Exception as e:
        print(f"ERROR posting article {article['id']}: {e}")
        errors += 1

    # Wait between posts
    if i < len(to_post) - 1:
        print("Waiting 10s between posts...")
        time.sleep(10)

print(f"\n=== SUMMARY ===")
print(f"Posted: {posted}/{len(to_post)}")
print(f"Errors: {errors}")
