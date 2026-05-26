#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json, os, sys, time, re, glob
from datetime import datetime
from dotenv import load_dotenv

# Load env files
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# Load youtube log
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# Find reel MP4s sorted by mtime newest first
reel_files = sorted(glob.glob(os.path.join(REELS_DIR, "*.mp4")), key=os.path.getmtime, reverse=True)

# Filter unuploaded
unuploaded = [r for r in reel_files if os.path.basename(r) not in yt_log]
print(f"Found {len(reel_files)} total reels, {len(unuploaded)} unuploaded")

if not unuploaded:
    print("Nothing to upload. Done.")
    sys.exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reels this run\n")

# Fetch recent articles from Supabase for matching
import urllib.request
req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
)
try:
    resp = urllib.request.urlopen(req)
    articles = json.loads(resp.read().decode())
    print(f"Loaded {len(articles)} recent articles for matching")
except Exception as e:
    print(f"Warning: Could not fetch articles: {e}")
    articles = []

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split("-")

def find_matching_article(filename):
    """Find best matching article for a reel filename."""
    words = extract_slug_words(filename)
    if not words:
        return None
    
    best_match = None
    best_score = 0
    
    for article in articles:
        slug = article.get("slug", "")
        if not slug:
            continue
        # Count how many reel words appear in the article slug
        score = sum(1 for w in words if w in slug)
        ratio = score / len(words) if words else 0
        if ratio > best_score and ratio >= 0.4:
            best_score = ratio
            best_match = article
    
    return best_match

def title_from_filename(filename):
    """Construct a title from filename words."""
    words = extract_slug_words(filename)
    return " ".join(w.capitalize() for w in words)

# Setup YouTube API
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

youtube = build("youtube", "v3", credentials=creds)

uploaded_count = 0
errors = []

for reel_path in to_upload:
    filename = os.path.basename(reel_path)
    print(f"--- Processing: {filename}")
    
    article = find_matching_article(filename)
    
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "News")
        print(f"  Matched article: {slug}")
    else:
        headline = title_from_filename(filename)
        subheadline = "News for the global Indian diaspora"
        slug = "unknown"
        category = "News"
        print(f"  No article match, using filename title: {headline}")
    
    # Compose title (under 100 chars with #Shorts)
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + "…"
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
    
    media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
    
    try:
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
        print(f"  ✅ Uploaded: https://youtube.com/shorts/{video_id}")
        
        # Log to youtube-log.json
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": f"https://youtube.com/shorts/{video_id}"
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if reel_path != to_upload[-1]:
            print("  Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Failed to upload {filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

print(f"\n=== Summary ===")
print(f"Uploaded: {uploaded_count}/{len(to_upload)}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("No errors.")
