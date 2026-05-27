#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env files ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]

SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY", "")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels, sorted newest first ---
reel_files = sorted(
    Path(REELS_DIR).glob("reel-*.mp4"),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

unuploaded = [r for r in reel_files if r.name not in yt_log]
print(f"Found {len(reel_files)} total reels, {len(unuploaded)} unuploaded")

to_upload = unuploaded[:2]
if not to_upload:
    print("Nothing to upload. All reels already on YouTube.")
    exit(0)

print(f"Will upload {len(to_upload)} reel(s):\n")
for r in to_upload:
    print(f"  - {r.name}")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
try:
    resp = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = resp.json()
    print(f"  Got {len(articles)} recent articles")
except Exception as e:
    print(f"  Warning: Could not fetch articles: {e}")
    articles = []

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    name = re.sub(r'^reel-', '', name)
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find best matching article for a reel filename."""
    words = extract_slug_words(filename)
    slug_fragment = '-'.join(words)

    best_match = None
    best_score = 0

    for article in articles:
        slug = article.get("slug", "")
        if not slug:
            continue
        # Check how many words from filename appear in article slug
        score = sum(1 for w in words if w in slug and len(w) > 2)
        if score > best_score:
            best_score = score
            best_match = article

    # Require at least 3 matching words for a confident match
    if best_score >= 3:
        return best_match
    return None

def title_from_filename(filename):
    """Construct a title from filename words."""
    words = extract_slug_words(filename)
    return ' '.join(w.capitalize() for w in words)

# --- Build YouTube client ---
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

youtube = build("youtube", "v3", credentials=creds)
print("  YouTube client ready")

# --- Upload each reel ---
uploaded = []
errors = []

for i, reel_path in enumerate(to_upload):
    print(f"\n{'='*60}")
    print(f"Uploading {i+1}/{len(to_upload)}: {reel_path.name}")
    print(f"{'='*60}")

    # Match article
    article = match_article(reel_path.name, articles)

    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "") or ""
        slug = article.get("slug", "unknown")
        category = article.get("category", "News")
        print(f"  Matched article: {headline[:80]}")
        print(f"  Slug: {slug}")
    else:
        headline = title_from_filename(reel_path.name)
        subheadline = ""
        slug = "unknown"
        category = "News"
        print(f"  No article match. Using filename title: {headline[:80]}")

    # Compose title (under 100 chars with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"

    # Compose description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != "unknown" else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

#TheVideshi #IndianDiaspora #NRI #IndiaNews #Shorts"""

    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category, "Shorts"]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "25"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    try:
        media = MediaFileUpload(str(reel_path), mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")

        # Log success
        yt_log[reel_path.name] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)

        uploaded.append({"name": reel_path.name, "url": url, "title": title})

        # Wait 10s between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)

    except Exception as e:
        print(f"  ❌ Error uploading {reel_path.name}: {e}")
        errors.append({"name": reel_path.name, "error": str(e)})

# --- Summary ---
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {len(uploaded)}")
for u in uploaded:
    print(f"  ✅ {u['name']}")
    print(f"     {u['url']}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  ❌ {e['name']}: {e['error']}")
print(f"Total in YouTube log: {len(yt_log)}")
