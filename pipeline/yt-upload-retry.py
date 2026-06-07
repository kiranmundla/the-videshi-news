#!/usr/bin/env python3
"""Upload reel to YouTube Shorts with extended timeout."""

import json, os, re, requests, time
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httplib2

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

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_KEY', sb_env.get('SUPABASE_ANON_KEY', ''))

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')
REEL_FILE = 'reel-jemimah-rodrigues-flexibility-yastika-bhatia-comeback-india-women-t20-world-cup-.mp4'
reel_path = os.path.join(REELS_DIR, REEL_FILE)

# --- Fetch article ---
print("📰 Fetching articles...")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()

# Match
base = REEL_FILE.replace('reel-', '', 1).replace('.mp4', '')
base = re.sub(r'-?\d{8,}$', '', base)
words = [w for w in base.split('-') if len(w) > 2]

best_match = None
best_score = 0
for art in articles:
    slug = art.get('slug', '') or ''
    score = sum(1 for w in words if w in slug)
    ratio = score / max(len(words), 1)
    if ratio > best_score and ratio >= 0.4:
        best_score = ratio
        best_match = art

if best_match:
    headline = best_match['headline']
    subheadline = best_match.get('subheadline', '') or ''
    slug = best_match['slug']
    category = best_match.get('category', 'news')
    print(f"  Matched: {headline[:80]}")
else:
    headline = ' '.join(w.capitalize() for w in base.split('-'))
    subheadline = ''
    slug = base
    category = 'sports'
    print(f"  No match, using: {headline}")

# --- Build metadata ---
title = headline
if len(title) + 8 > 100:
    title = title[:91] + '…'
title = f"{title} #Shorts"

CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'lifestyle-health': '#DesiLifestyle #Wellness #Health',
    'markets-finance': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'food': '#IndianFood #IndianCuisine #DesiFood',
}

# Topic hashtags from headline
def extract_topic_hashtags(hl):
    tags = []
    name_parts = []
    for w in hl.split():
        clean = re.sub(r'[^A-Za-z0-9]', '', w)
        if clean and clean[0].isupper() and len(clean) > 2:
            name_parts.append(clean)
        else:
            if name_parts:
                tags.append('#' + ''.join(name_parts))
                name_parts = []
    if name_parts:
        tags.append('#' + ''.join(name_parts))
    seen = set()
    unique = []
    for t in tags:
        tl = t.lower()
        if tl not in seen and len(t) > 3:
            seen.add(tl)
            unique.append(t)
    return unique[:5]

base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
topic_tags = ' '.join(extract_topic_hashtags(headline))
all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()

article_url = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
desc = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News",
           category.replace('-', ' ').title(), "Shorts",
           "Jemimah Rodrigues", "Women Cricket", "T20 World Cup", "India Women"]
yt_tags = yt_tags[:12]

print(f"\n📝 Title: {title}")
print(f"🏷️  Tags: {yt_tags}")

# --- Upload with extended timeout ---
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

# Build with extended timeout
http = httplib2.Http(timeout=120)
youtube = build("youtube", "v3", credentials=creds, http=None)

body = {
    "snippet": {
        "title": title,
        "description": desc,
        "tags": yt_tags,
        "categoryId": "25"
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False
    }
}

media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024)

print("\n⬆️  Starting upload...")
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
        status, response = request.next_chunk(num_retries=3)
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")
    except Exception as e:
        retries += 1
        if retries > max_retries:
            print(f"❌ Upload failed after {max_retries} retries: {e}")
            raise
        print(f"  ⚠️ Retry {retries}/{max_retries}: {e}")
        time.sleep(5 * retries)

video_id = response["id"]
url = f"https://youtube.com/shorts/{video_id}"
print(f"\n✅ Uploaded: {url}")

# --- Log ---
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}
yt_log[REEL_FILE] = {
    "video_id": video_id,
    "article_slug": slug or "unknown",
    "uploaded_at": datetime.utcnow().isoformat() + "Z",
    "url": url
}
with open(LOG_PATH, 'w') as f:
    json.dump(yt_log, f, indent=2)

print(f"📝 Logged to youtube-log.json")
print(f"\n📊 SUMMARY: 1 reel uploaded successfully → {url}")
