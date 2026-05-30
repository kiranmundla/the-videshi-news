#!/usr/bin/env python3
"""Post recent Videshi articles to Threads (@the.videshi)."""

import json, os, sys, time, requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
MAX_POST = 3

# Load secrets
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

# Category emoji map
EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏",
    "travel": "✈️", "lifestyle-health": "🧘", "markets-finance": "📈",
    "technology": "💻", "sports": "🏏", "entertainment": "🎬", "food": "🍛"
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

# Load log
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Filter: not yet posted, has image
candidates = [a for a in articles if str(a['id']) not in threads_log and a.get('image_url')]
print(f"Candidates (not posted, has image): {len(candidates)}")

to_post = candidates[:MAX_POST]
if not to_post:
    print("Nothing new to post. Done.")
    sys.exit(0)

# --- Compose & post ---
def compose_post(article):
    cat = (article.get('category') or 'news').lower()
    emoji = EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace('-', ' ')
    
    # Punchy headline - just uppercase the existing headline for now
    headline = article['headline'].upper()
    
    # Summary from subheadline or first chunk of body
    summary = article.get('subheadline') or ''
    if not summary and article.get('body'):
        # Grab first meaningful sentence from body
        body = article['body']
        # Strip markdown headers
        lines = [l.strip() for l in body.split('\n') if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('---')]
        if lines:
            summary = lines[0][:200]
    
    slug = article.get('slug', '')
    url = f"📰 thevideshi.com/articles/{slug}"
    
    separator = "━━━━━━━━━━━━━━━━━━━━"
    
    post = f"{emoji} {cat_label} | The Videshi\n\n{separator}\n\n{headline}\n\n{summary}\n\n{url}"
    
    # Trim to 500 chars
    if len(post) > 500:
        # Trim summary to fit
        over = len(post) - 500
        if len(summary) > over + 20:
            summary = summary[:len(summary) - over - 3].rstrip() + "..."
            post = f"{emoji} {cat_label} | The Videshi\n\n{separator}\n\n{headline}\n\n{summary}\n\n{url}"
        else:
            # Drop summary entirely
            post = f"{emoji} {cat_label} | The Videshi\n\n{separator}\n\n{headline}\n\n{url}"
    
    if len(post) > 500:
        post = post[:497] + "..."
    
    return post

posted = 0
errors = []

for i, article in enumerate(to_post):
    aid = str(article['id'])
    slug = article.get('slug', 'unknown')
    print(f"\n--- Posting [{i+1}/{len(to_post)}]: {slug} ---")
    
    post_text = compose_post(article)
    print(f"Post text ({len(post_text)} chars):\n{post_text}\n")
    
    # Step 1: Create media container with image
    image_url = article['image_url']
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
        print(f"Container response: {resp.status_code} {resp_json}")
        
        if "id" not in resp_json:
            # Image might have failed, try text-only
            print("Image container failed, falling back to TEXT...")
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
            print(f"Text container response: {resp.status_code} {resp_json}")
            
            if "id" not in resp_json:
                errors.append(f"{slug}: container creation failed: {resp_json}")
                continue
        
        container_id = resp_json["id"]
        
        # Step 2: Wait for processing then publish
        print(f"Waiting 12s for media processing...")
        time.sleep(12)
        
        # Check container status before publishing
        status_resp = requests.get(
            f"https://graph.threads.net/v1.0/{container_id}",
            params={"fields": "status", "access_token": THREADS_ACCESS_TOKEN},
            timeout=15
        )
        status_json = status_resp.json()
        print(f"Container status: {status_json}")
        
        # If not finished, wait more
        container_status = status_json.get("status", "")
        wait_count = 0
        while container_status not in ("FINISHED", "PUBLISHED", "") and wait_count < 3:
            print(f"Status is '{container_status}', waiting 10 more seconds...")
            time.sleep(10)
            status_resp = requests.get(
                f"https://graph.threads.net/v1.0/{container_id}",
                params={"fields": "status", "access_token": THREADS_ACCESS_TOKEN},
                timeout=15
            )
            status_json = status_resp.json()
            container_status = status_json.get("status", "")
            print(f"Container status: {status_json}")
            wait_count += 1
        
        if container_status == "ERROR":
            # Fall back to text-only
            print("Container errored (likely image issue), falling back to TEXT...")
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
            if "id" not in resp_json:
                errors.append(f"{slug}: text fallback also failed: {resp_json}")
                continue
            container_id = resp_json["id"]
            time.sleep(5)
        
        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN
            },
            timeout=30
        )
        pub_json = pub_resp.json()
        print(f"Publish response: {pub_resp.status_code} {pub_json}")
        
        if "id" in pub_json:
            post_id = pub_json["id"]
            threads_log[aid] = {
                "slug": slug,
                "threads_post_id": str(post_id),
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            with open(LOG_PATH, 'w') as f:
                json.dump(threads_log, f, indent=2)
            posted += 1
            print(f"✅ Posted successfully: {post_id}")
        else:
            errors.append(f"{slug}: publish failed: {pub_json}")
            print(f"❌ Publish failed")
        
    except Exception as e:
        errors.append(f"{slug}: {str(e)}")
        print(f"❌ Error: {e}")
    
    # Wait between posts
    if i < len(to_post) - 1:
        print("Waiting 10s before next post...")
        time.sleep(10)

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: {posted}/{len(to_post)} posted successfully")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"Total in log: {len(threads_log)}")
