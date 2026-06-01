#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, time, re, sys
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env ---
def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env(os.path.expanduser("~/workspace/.env.youtube"))
sb_env = load_env(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN", "")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_KEY", "")

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials"); sys.exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key"); sys.exit(1)

# --- Paths ---
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels sorted by mtime desc
all_reels = []
for fn in os.listdir(REELS_DIR):
    if fn.endswith('.mp4') and fn not in yt_log:
        fp = os.path.join(REELS_DIR, fn)
        all_reels.append((fn, fp, os.path.getmtime(fp)))

all_reels.sort(key=lambda x: x[2], reverse=True)
print(f"Found {len(all_reels)} unuploaded reel(s)")

if not all_reels:
    print("Nothing to upload.")
    sys.exit(0)

# Fetch recent articles from Supabase
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
except Exception as e:
    print(f"⚠️  Supabase fetch failed: {e}")
    articles = []

def match_article(filename):
    """Try to match a reel filename to an article."""
    # Strip reel- prefix and .mp4
    base = filename.replace('.mp4', '')
    if base.startswith('reel-'):
        base = base[5:]
    # Remove trailing date pattern like -20260531
    base_no_date = re.sub(r'-\d{8}$', '', base)
    words = set(base_no_date.split('-'))
    
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get('slug', '')
        slug_words = set(slug.split('-'))
        overlap = len(words & slug_words)
        if overlap > best_score and overlap >= min(3, len(words)):
            best_score = overlap
            best_match = art
    return best_match

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

def make_hashtags(category, headline):
    base = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    # Extract topic hashtags from headline
    topic_tags = []
    # Remove common stop words and make hashtags from significant words
    stop = {'the','a','an','in','on','at','to','for','of','is','are','was','and','or','but','with','from','by','as','its','it','has','have','had','been','be','will','can','may','this','that','their','new','first','after','over','how','why','what','not','no','all','more','most','into','out','up','about'}
    words = re.findall(r'\b[A-Za-z][a-z]{2,}\b', headline)
    for w in words:
        if w.lower() not in stop and len(topic_tags) < 5:
            tag = f'#{w}'
            if tag not in topic_tags:
                topic_tags.append(tag)
    return f"{base} {cat_tags} {' '.join(topic_tags)}"

def title_from_filename(filename):
    base = filename.replace('.mp4', '')
    if base.startswith('reel-'):
        base = base[5:]
    base = re.sub(r'-\d{8}$', '', base)
    base = re.sub(r'-nri$', '', base)
    words = base.split('-')
    return ' '.join(w.capitalize() for w in words)

# Build YouTube client
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)

uploaded = 0
errors = []
MAX_UPLOADS = 2

for fn, fp, mtime in all_reels[:MAX_UPLOADS]:
    print(f"\n📹 Processing: {fn}")
    
    art = match_article(fn)
    if art:
        headline = art.get('headline', '')
        subheadline = art.get('subheadline', '') or ''
        slug = art.get('slug', 'unknown')
        category = art.get('category', 'news')
        print(f"  Matched article: {slug}")
    else:
        headline = title_from_filename(fn)
        subheadline = "News for the global Indian diaspora"
        slug = 'unknown'
        category = 'news'
        print(f"  No article match, using filename title: {headline}")
    
    # Title: keep under 100 chars, add #Shorts
    title = headline[:90].strip()
    if not title.endswith('#Shorts'):
        title = f"{title} #Shorts"
    if len(title) > 100:
        title = title[:96] + " #Shorts" if len(title[:96].strip() + " #Shorts") <= 100 else title[:100]
    
    hashtags = make_hashtags(category, headline)
    
    article_url = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"
    
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""

    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic words from headline
    hw = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', headline)
    for w in hw[:4]:
        if w not in tags and len(tags) < 12:
            tags.append(w)
    if len(tags) < 8:
        tags.extend(["South Asian", "Desi", "Global Indian"])
    tags = tags[:12]

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
        media = MediaFileUpload(fp, mimetype="video/mp4", resumable=True)
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
        
        # Log
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded += 1
        
        if uploaded < MAX_UPLOADS and len(all_reels) > 1:
            print("  ⏳ Waiting 10s before next upload...")
            time.sleep(10)
            
    except Exception as e:
        err_msg = f"Failed to upload {fn}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

print(f"\n{'='*50}")
print(f"📊 Summary: {uploaded} uploaded, {len(errors)} error(s)")
if errors:
    for e in errors:
        print(f"  ⚠️  {e}")
