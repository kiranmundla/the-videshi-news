#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts - retry with better timeout handling."""

import json, os, sys, time, re, glob, socket
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httplib2

# Increase default socket timeout
socket.setdefaulttimeout(120)

# Load env files
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
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# The one reel to upload
fn = "reel-h1b-overhaul-bill-green-card-opt-tech-industry-20260608.mp4"
fp = os.path.join(REELS_DIR, fn)

if fn in yt_log:
    print("Already uploaded.")
    sys.exit(0)

if not os.path.exists(fp):
    print(f"File not found: {fp}")
    sys.exit(1)

fsize = os.path.getsize(fp)
print(f"📤 Uploading: {fn} ({fsize / 1024 / 1024:.1f} MB)")

# Article info (from previous run's match)
headline = "A New Bill Wants to Kill the H-1B-to-Green-Card Pipeline. Big Tech Should Be Nervous."
subheadline = ""

# Fetch subheadline from Supabase
print("📰 Fetching article details...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&slug=like.*h1b-overhaul*&select=id,slug,headline,subheadline,category,tags&limit=5",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    arts = r.json()
    if not arts:
        # Broader search
        r = req.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=20&select=id,slug,headline,subheadline,category,tags",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        arts = r.json()
        # Find match
        for a in arts:
            s = (a.get('slug') or '').lower()
            if 'h1b' in s and ('overhaul' in s or 'green-card' in s or 'bill' in s):
                arts = [a]
                break
        else:
            arts = []
    
    if arts:
        art = arts[0]
        headline = art.get('headline', headline)
        subheadline = art.get('subheadline', '')
        slug = art.get('slug', 'unknown')
        category = art.get('category', 'immigration')
        print(f"   Found: {headline[:80]}")
        print(f"   Slug: {slug}")
    else:
        slug = "unknown"
        category = "immigration"
        subheadline = "A proposed bill could reshape H-1B visa pathways and OPT programs, with major implications for Indian tech workers in America."
        print("   No exact match, using constructed metadata")
except Exception as e:
    slug = "unknown"
    category = "immigration"
    subheadline = "A proposed bill could reshape H-1B visa pathways and OPT programs, with major implications for Indian tech workers in America."
    print(f"   Supabase fetch error: {e}, using fallback metadata")

# Compose title
title = headline
if len(title) > 90:
    title = title[:87] + "..."
title = f"{title} #Shorts"

# Hashtags
hashtags = " ".join([
    "#TheVideshi", "#Shorts", "#IndianDiaspora", "#NRI",
    "#H1B", "#H1BVisa", "#GreenCard", "#USImmigration", "#USCIS",
    "#OPT", "#Immigration", "#TechWorkers", "#IndianAmerican",
    "#BigTech", "#SiliconValley", "#IndiaNews", "#DesiAbroad",
    "#NRILife", "#DesiNews"
])

# Description
article_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}\n" if slug != "unknown" else ""

description = f"""{subheadline}
{article_link}
The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""

tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts",
        "H1B", "Green Card", "OPT", "Immigration", "Tech Industry", "USCIS"]

print(f"   Title: {title}")

# YouTube upload with retry
print("🔑 Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

# Build with increased timeout
http = httplib2.Http(timeout=120)
youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
print("   ✅ YouTube API ready.")

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

# Use non-resumable for small files (< 5MB)
media = MediaFileUpload(fp, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)

MAX_RETRIES = 3
for attempt in range(1, MAX_RETRIES + 1):
    try:
        print(f"\n   Attempt {attempt}/{MAX_RETRIES}...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk(num_retries=3)
            if status:
                print(f"   Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"\n   ✅ Uploaded: {url}")
        
        # Log
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        print(f"\n📊 Summary: 1 reel uploaded successfully")
        print(f"   {fn} → {url}")
        sys.exit(0)
        
    except Exception as e:
        print(f"   ❌ Attempt {attempt} failed: {e}")
        if attempt < MAX_RETRIES:
            wait = 10 * attempt
            print(f"   Retrying in {wait}s...")
            time.sleep(wait)
        else:
            print(f"\n📊 Summary: Upload FAILED after {MAX_RETRIES} attempts")
            print(f"   Error: {e}")
            sys.exit(1)
