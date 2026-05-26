#!/usr/bin/env python3
"""Upload recent Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import time
import re
import urllib.request
from datetime import datetime
from dotenv import load_dotenv

# --- Load credentials ---
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ["SUPABASE_SERVICE_ROLE_KEY"]

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels (newest first) ---
reel_files = [f for f in os.listdir(REELS_DIR) if f.endswith(".mp4")]
reel_files.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

unuploaded = [f for f in reel_files if f not in yt_log]
print(f"Found {len(reel_files)} total reels, {len(unuploaded)} unuploaded")

if not unuploaded:
    print("Nothing to upload. Done.")
    exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reels this run\n")

# --- Fetch recent articles from Supabase (using curl to avoid urllib IncompleteRead) ---
import subprocess
curl_url = f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags"
result = subprocess.run(
    ["curl", "-s", "-H", f"apikey: {SUPABASE_KEY}", "-H", f"Authorization: Bearer {SUPABASE_KEY}", curl_url],
    capture_output=True, text=True
)
articles = json.loads(result.stdout)
print(f"Fetched {len(articles)} recent articles for matching\n")


def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    # Strip reel- prefix and .mp4 suffix
    name = filename.replace(".mp4", "")
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split("-")


def find_matching_article(filename):
    """Find the best matching article for a reel filename."""
    fragments = extract_slug_fragments(filename)
    if not fragments:
        return None

    best_match = None
    best_score = 0

    for article in articles:
        slug = article.get("slug", "") or ""
        slug_words = set(slug.split("-"))
        # Count how many reel fragments appear in the article slug
        score = sum(1 for frag in fragments if frag in slug_words)
        # Require at least 3 matching words or 50% of fragments
        threshold = max(3, len(fragments) * 0.4)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = article

    return best_match


def title_from_filename(filename):
    """Generate a title from filename if no article match."""
    fragments = extract_slug_fragments(filename)
    return " ".join(w.capitalize() for w in fragments)[:95] + " #Shorts"


# --- YouTube upload setup ---
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET,
)

youtube = build("youtube", "v3", credentials=creds)

uploaded = []
errors = []

for i, reel_filename in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"[{i+1}/{len(to_upload)}] Processing: {reel_filename}")

    # Find matching article
    article = find_matching_article(reel_filename)

    if article:
        headline = article["headline"]
        subheadline = article.get("subheadline") or ""
        slug = article["slug"]
        category = article.get("category") or "News"
        print(f"  Matched article: {slug}")
    else:
        headline = title_from_filename(reel_filename)
        subheadline = "News for the global Indian diaspora"
        slug = "unknown"
        category = "News"
        print("  No article match — using filename-derived title")

    # Compose metadata
    title = headline[:93] + " #Shorts" if len(headline) > 93 else headline + " #Shorts"
    if len(title) > 100:
        title = title[:97] + "..."

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
            "categoryId": "25",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    print(f"  Title: {title}")
    file_size_mb = os.path.getsize(reel_path) / (1024 * 1024)
    print(f"  File size: {file_size_mb:.1f} MB")

    try:
        media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")

        # Log success
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url,
        }
        with open(LOG_PATH, "w") as f:
            json.dump(yt_log, f, indent=2)

        uploaded.append({"filename": reel_filename, "url": yt_url, "title": title})

        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append({"filename": reel_filename, "error": str(e)})

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {len(uploaded)}")
for u in uploaded:
    print(f"  • {u['title'][:60]}...")
    print(f"    {u['url']}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  • {e['filename']}: {e['error']}")
print(f"Remaining unuploaded: {len(unuploaded) - len(uploaded) - len(errors)}")
