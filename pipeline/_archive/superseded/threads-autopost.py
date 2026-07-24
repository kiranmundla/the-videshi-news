#!/usr/bin/env python3
"""Post recent Videshi articles to Threads (@the.videshi)."""

import json, os, sys, time, requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")

# Load env
def load_env(path):
    d = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                d[k.strip()] = v.strip()
    return d

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

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
    with open(LOG_PATH, 'w') as f:
        json.dump(threads_log, f, indent=2)

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
print(f"Fetched {len(articles)} recent published articles")

# --- Filter to unposted with images ---
candidates = []
for a in articles:
    aid = str(a['id'])
    if aid in threads_log:
        continue
    if not a.get('image_url'):
        print(f"  Skipping {aid} ({a.get('headline','?')[:50]}) — no image")
        continue
    candidates.append(a)

candidates = candidates[:3]
print(f"Candidates to post: {len(candidates)}")

if not candidates:
    print("Nothing new to post. Done.")
    sys.exit(0)

# --- Compose post text ---
def compose_post(article):
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace('-', ' ')
    
    # Rewrite headline: punchy, ALL CAPS
    headline = article['headline'].upper()
    
    # Extract summary from body — first 1-2 meaningful sentences
    body = article.get('body', '') or ''
    # Strip markdown headers and formatting
    lines = []
    for line in body.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('![') or line.startswith('---'):
            continue
        if line.startswith('**') and line.endswith('**'):
            continue
        lines.append(line)
    
    # Get first meaningful paragraph
    summary_text = ""
    for line in lines:
        # Clean markdown
        clean = line.replace('**', '').replace('*', '').replace('[', '').replace(']', '')
        if len(clean) > 40:
            summary_text = clean
            break
    
    # Trim summary to fit ~2 sentences
    if summary_text:
        sentences = []
        current = ""
        for ch in summary_text:
            current += ch
            if ch in '.!?' and len(current.strip()) > 20:
                sentences.append(current.strip())
                current = ""
                if len(sentences) >= 2:
                    break
        if current.strip() and len(sentences) < 2:
            sentences.append(current.strip())
        summary_text = ' '.join(sentences)
    
    slug = article.get('slug', '')
    url = f"📰 thevideshi.com/articles/{slug}"
    
    separator = "━━━━━━━━━━━━━━━━━━━━"
    
    post = f"{emoji} {cat_label} | The Videshi\n\n{separator}\n\n{headline}\n\n{summary_text}\n\n{url}"
    
    # Ensure under 500 chars
    if len(post) > 500:
        # Trim summary
        over = len(post) - 495
        summary_text = summary_text[:len(summary_text) - over].rsplit(' ', 1)[0] + '.'
        post = f"{emoji} {cat_label} | The Videshi\n\n{separator}\n\n{headline}\n\n{summary_text}\n\n{url}"
    
    if len(post) > 500:
        # Drop summary entirely
        post = f"{emoji} {cat_label} | The Videshi\n\n{separator}\n\n{headline}\n\n{url}"
    
    return post[:500]

# --- Post to Threads ---
posted = 0
errors = []

for i, article in enumerate(candidates):
    aid = str(article['id'])
    post_text = compose_post(article)
    print(f"\n--- Posting article {i+1}/{len(candidates)}: {article['headline'][:60]} ---")
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
            data=container_data
        )
        resp_json = resp.json()
        print(f"Container response: {resp.status_code} — {resp_json}")
        
        if 'error' in resp_json or 'id' not in resp_json:
            print(f"Image container failed, falling back to TEXT-only")
            container_data = {
                "media_type": "TEXT",
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN
            }
            resp = requests.post(
                f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                data=container_data
            )
            resp_json = resp.json()
            print(f"Text container response: {resp.status_code} — {resp_json}")
            
            if 'id' not in resp_json:
                errors.append(f"{aid}: Container creation failed — {resp_json}")
                continue
        
        container_id = resp_json['id']
        
        # Step 2: Wait then publish
        print(f"Waiting 10s for media processing...")
        time.sleep(10)
        
        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN
            }
        )
        pub_json = pub_resp.json()
        print(f"Publish response: {pub_resp.status_code} — {pub_json}")
        
        if 'id' in pub_json:
            post_id = pub_json['id']
            threads_log[aid] = {
                "slug": article.get('slug', ''),
                "threads_post_id": str(post_id),
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            with open(LOG_PATH, 'w') as f:
                json.dump(threads_log, f, indent=2)
            posted += 1
            print(f"✅ Posted! ID: {post_id}")
        else:
            errors.append(f"{aid}: Publish failed — {pub_json}")
            print(f"❌ Publish failed: {pub_json}")
        
    except Exception as e:
        errors.append(f"{aid}: Exception — {str(e)}")
        print(f"❌ Exception: {e}")
    
    # Wait between posts
    if i < len(candidates) - 1:
        print("Waiting 10s before next post...")
        time.sleep(10)

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: {posted}/{len(candidates)} posted successfully")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"Total in threads-log.json: {len(threads_log)}")
