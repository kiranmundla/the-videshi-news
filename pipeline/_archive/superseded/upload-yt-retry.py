#!/usr/bin/env python3
"""Upload a single reel to YouTube with extended timeout."""

import json
import os
import re
import socket
from datetime import datetime

import requests as req
import httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Increase default socket timeout
socket.setdefaulttimeout(300)

# --- Load env files ---
def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        return env
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN", "")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY", "") or sb_env.get("SUPABASE_KEY", "") or sb_env.get("SUPABASE_ANON_KEY", "")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

REEL_FILENAME = "reel-celina-jaitly-peter-haag-defamation-notice-custody-battle-austria-india-nri-2026.mp4"
REEL_PATH = os.path.join(REELS_DIR, REEL_FILENAME)

# Load log
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

if REEL_FILENAME in yt_log:
    print(f"✅ Already uploaded: {yt_log[REEL_FILENAME]['url']}")
    exit(0)

# Fetch article
print("📰 Fetching article match...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
except:
    articles = []

# Match article
def extract_slug_fragments(filename):
    name = filename.replace('reel-', '', 1).replace('.mp4', '')
    name = re.sub(r'-?\d{8,}$', '', name)
    name = re.sub(r'-?2026\d*$', '', name)
    return name

fragments = extract_slug_fragments(REEL_FILENAME)
frag_words = set(fragments.split('-'))

best_match = None
best_score = 0
for art in articles:
    slug = art.get('slug', '') or ''
    slug_words = set(slug.split('-'))
    overlap = len(frag_words.intersection(slug_words) - {'the', 'a', 'an', 'in', 'of', 'for', 'and', 'to', 'is', 'on', 'at', 'by'})
    if overlap > best_score and overlap >= 3:
        best_score = overlap
        best_match = art

article = best_match

if article:
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '') or ''
    slug = article.get('slug', '')
    category = article.get('category', 'news')
    art_tags = article.get('tags', []) or []
    print(f"  Matched: {headline[:70]}...")
else:
    headline = ' '.join(w.capitalize() for w in fragments.split('-'))[:90]
    subheadline = ''
    slug = fragments
    category = 'news'
    art_tags = []
    print(f"  No match, using filename title: {headline}")

# Build metadata
CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'food': '#IndianFood #IndianCuisine #DesiFood',
    'culture': '#DesiLifestyle #Wellness #DesiCulture',
    'economy': '#StockMarket #Nifty #Sensex #IndianMarkets',
}

title = headline[:90].strip()
if len(title) + 9 <= 100:
    title = f"{title} #Shorts"

cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #BreakingNews')
topic_tags = []
for w in re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or ''):
    tag = '#' + w.replace(' ', '')
    if len(tag) > 3 and tag not in topic_tags:
        topic_tags.append(tag)
topic_tags = topic_tags[:5]

article_url = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"

description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {' '.join(topic_tags)}""".strip()

tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category or "News", "Shorts"]
if art_tags:
    for t in art_tags[:4]:
        if t and t not in tags:
            tags.append(t)
for t in topic_tags[:3]:
    clean = t.replace('#', '')
    if clean not in tags:
        tags.append(clean)
tags = tags[:12]

print(f"\n📝 Title: {title}")
print(f"🏷️  Tags: {tags}")

# YouTube upload with extended timeout
print("\n🔑 Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

# Build with a high-timeout http object
http = httplib2.Http(timeout=300)
youtube = build("youtube", "v3", credentials=creds, static_discovery=False)

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

file_size_mb = os.path.getsize(REEL_PATH) / (1024 * 1024)
print(f"📤 Uploading {REEL_FILENAME} ({file_size_mb:.1f} MB)...")

media = MediaFileUpload(REEL_PATH, mimetype="video/mp4", resumable=True, chunksize=1024*1024)

request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)

response = None
retries = 0
max_retries = 3

while response is None:
    try:
        status, response = request.next_chunk(num_retries=5)
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")
    except Exception as e:
        retries += 1
        if retries > max_retries:
            print(f"❌ Upload failed after {max_retries} retries: {e}")
            raise
        print(f"  ⚠️  Retry {retries}/{max_retries}: {e}")
        import time
        time.sleep(5 * retries)

video_id = response["id"]
video_url = f"https://youtube.com/shorts/{video_id}"
print(f"✅ Uploaded: {video_url}")

# Log
yt_log[REEL_FILENAME] = {
    "video_id": video_id,
    "article_slug": slug or "unknown",
    "uploaded_at": datetime.utcnow().isoformat() + "Z",
    "url": video_url
}
with open(LOG_PATH, 'w') as f:
    json.dump(yt_log, f, indent=2)

print(f"\n📊 SUMMARY: 1 reel uploaded successfully")
print(f"🔗 {video_url}")
