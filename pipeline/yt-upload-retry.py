#!/usr/bin/env python3
"""Upload one reel to YouTube Shorts with extended timeout."""

import json, os, re, time, socket, httplib2
from datetime import datetime, timezone

# Increase default socket timeout
socket.setdefaulttimeout(300)

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SB_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

reel_path = os.path.join(REELS_DIR, "reel-us-india-trade-deal-ambassador-gor-tariffs-nri-businesses-20260529.mp4")
fname = os.path.basename(reel_path)

# --- Fetch article match from Supabase ---
import requests as req

print("Fetching articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&slug=like.*us-india-trade-deal*&select=id,slug,headline,subheadline,category,tags&limit=5",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"  Found {len(articles)} matching articles")

if articles:
    article = articles[0]
    headline = article["headline"]
    slug = article["slug"]
    category = article.get("category", "news")
    subheadline = article.get("subheadline", "") or ""
    print(f"  Matched: {slug}")
else:
    headline = "US India Trade Deal Ambassador Gor Tariffs NRI Businesses"
    slug = "us-india-trade-deal-ambassador-gor-tariffs-nri-businesses-20260529"
    category = "news"
    subheadline = ""

# Build title
suffix = " #Shorts"
max_len = 100 - len(suffix)
title = headline[:max_len-3] + "..." + suffix if len(headline) > max_len else headline + suffix

# Build description
cat_tags_map = {
    "news": "#IndiaNews #BreakingNews #DesiNews #SouthAsian",
    "immigration": "#H1B #H1BVisa #GreenCard #USImmigration #USCIS",
    "nri-world": "#NRILife #DesiAbroad #IndianAmerican",
    "markets-finance": "#StockMarket #Nifty #Sensex #IndianMarkets",
    "technology": "#TechNews #IndianTech #SiliconValley #AI",
    "sports": "#Cricket #IPL #IPL2026 #TeamIndia #BCCI",
    "entertainment": "#Bollywood #BollywoodNews #IndianCinema #Tollywood",
}
cat_tags = cat_tags_map.get(category, "#IndiaNews #DesiNews")

# Topic hashtags from headline
topic_ht = []
hl_lower = headline.lower()
for kw, ht in [("modi", "#NarendraModi"), ("trump", "#Trump"), ("india", "#India"),
               ("trade", "#TradeDeal"), ("tariff", "#Tariffs"), ("nri", "#NRIBusiness"),
               ("ambassador", "#Diplomacy")]:
    if kw in hl_lower:
        topic_ht.append(ht)
all_ht = "#TheVideshi #Shorts #IndianDiaspora #NRI " + cat_tags + " " + " ".join(topic_ht[:5])

description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_ht}"""

tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(),
        "Shorts", "US India Trade", "Tariffs", "Ambassador", "NRI Business", "Diplomacy", "Trade Deal"]

print(f"\n  Title: {title}")
print(f"  Category: {category}")

# --- Upload ---
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

# Build with extended http timeout
http = httplib2.Http(timeout=300)
youtube = build("youtube", "v3", credentials=creds)

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
file_size = os.path.getsize(reel_path)
print(f"  File size: {file_size / 1024 / 1024:.1f} MB")

media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)

print("  Uploading to YouTube...")
request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)

MAX_RETRIES = 3
for attempt in range(1, MAX_RETRIES + 1):
    try:
        print(f"  Attempt {attempt}...")
        response = None
        while response is None:
            status, response = request.next_chunk(num_retries=3)
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"\n  ✅ Uploaded: {url}")
        
        # Log
        yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        print(f"  ✅ Logged to youtube-log.json")
        break
    except Exception as e:
        print(f"  ❌ Attempt {attempt} failed: {e}")
        if attempt == MAX_RETRIES:
            print(f"  ❌ All {MAX_RETRIES} attempts failed.")
            raise
        print(f"  Retrying in 15s...")
        time.sleep(15)
        # Recreate request for retry
        media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

print("\n✅ Done.")
