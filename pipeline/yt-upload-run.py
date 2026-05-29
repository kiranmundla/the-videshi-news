#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""
import json, os, re, time, sys
from datetime import datetime, timezone

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_SERVICE_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
SKIP_FILES = {"reel-v2-final.mp4", "reel-v2-fixed.mp4"}
MAX_UPLOADS = 2

# --- Load log ---
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# --- Find unuploaded reels ---
reel_files = []
for fn in os.listdir(REELS_DIR):
    if not fn.endswith(".mp4") or fn in SKIP_FILES:
        continue
    if fn not in yt_log:
        full = os.path.join(REELS_DIR, fn)
        reel_files.append((fn, full, os.path.getmtime(full)))

reel_files.sort(key=lambda x: x[2], reverse=True)  # newest first
reel_files = reel_files[:MAX_UPLOADS]

if not reel_files:
    print("No unuploaded reels found. Nothing to do.")
    sys.exit(0)

print(f"Found {len(reel_files)} unuploaded reel(s):")
for fn, _, _ in reel_files:
    print(f"  - {fn}")

# --- Fetch recent articles from Supabase ---
import requests as req

print("\nFetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"  Got {len(articles)} articles")

def match_article(filename):
    """Try to match a reel filename to an article."""
    # Strip reel- prefix and trailing date + .mp4
    base = filename.replace(".mp4", "")
    if base.startswith("reel-"):
        base = base[5:]
    # Remove trailing date like -20260529
    base = re.sub(r'-\d{8}$', '', base)
    slug_words = set(base.split('-'))
    
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get("slug", "")
        art_words = set(slug.split('-'))
        overlap = len(slug_words & art_words)
        if overlap > best_score and overlap >= 3:
            best_score = overlap
            best_match = art
    return best_match

CATEGORY_HASHTAGS = {
    "news": "#IndiaNews #BreakingNews #DesiNews #SouthAsian",
    "immigration": "#H1B #H1BVisa #GreenCard #USImmigration #USCIS",
    "nri-world": "#NRILife #DesiAbroad #IndianAmerican",
    "travel": "#TravelIndia #IncredibleIndia #IndiaTravel",
    "lifestyle-health": "#DesiLifestyle #Wellness #Health",
    "markets-finance": "#StockMarket #Nifty #Sensex #IndianMarkets",
    "technology": "#TechNews #IndianTech #SiliconValley #AI",
    "sports": "#Cricket #IPL #IPL2026 #TeamIndia #BCCI",
    "entertainment": "#Bollywood #BollywoodNews #IndianCinema #Tollywood",
    "food": "#IndianFood #IndianCuisine #DesiFood",
}

def make_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common person/entity patterns
    entities = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or "")
    for ent in entities[:5]:
        tag = "#" + ent.replace(" ", "")
        if len(tag) > 3 and tag not in tags:
            tags.append(tag)
    return tags[:5]

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "unknown")
        category = article.get("category", "news")
    else:
        # Construct from filename
        base = filename.replace(".mp4", "")
        if base.startswith("reel-"):
            base = base[5:]
        base = re.sub(r'-\d{8}$', '', base)
        words = base.split('-')
        headline = ' '.join(w.capitalize() for w in words)
        subheadline = headline
        slug = "unknown"
        category = "news"

    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + "…"
    title = f"{title} #Shorts"

    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = make_topic_hashtags(headline)
    all_hashtags = "#TheVideshi #Shorts #IndianDiaspora #NRI " + cat_tags
    if topic_tags:
        all_hashtags += " " + " ".join(topic_tags)

    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    tags_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category, "Shorts"]
    # Add topic tags as plain words
    for t in topic_tags[:4]:
        tags_list.append(t.replace("#", ""))
    # Ensure 8-12 tags
    for extra in ["South Asian", "Desi", "Global Indian"]:
        if len(tags_list) < 8:
            tags_list.append(extra)

    return title, description, tags_list, slug

# --- YouTube upload ---
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ YouTube API client ready")

uploaded = []
errors = []

for i, (fn, reel_path, _) in enumerate(reel_files):
    print(f"\n--- Uploading {i+1}/{len(reel_files)}: {fn} ---")
    
    article = match_article(fn)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:60]}...")
    else:
        print("  No article match, using filename-derived title")
    
    title, description, tags, slug = compose_metadata(article, fn)
    print(f"  Title: {title}")
    
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
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")
        
        # Log it
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((fn, url))
        
        # Wait between uploads
        if i < len(reel_files) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append((fn, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: {len(uploaded)} uploaded, {len(errors)} errors")
for fn, url in uploaded:
    print(f"  ✅ {fn} → {url}")
for fn, err in errors:
    print(f"  ❌ {fn} → {err}")
