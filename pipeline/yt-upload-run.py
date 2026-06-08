#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, sys, time, re, glob
from datetime import datetime

# Load env files
def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env(os.path.expanduser("~/workspace/.env.youtube"))
sb_env = load_env(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY")

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials in ~/.env.youtube")
    sys.exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key in ~/.env.supabase")
    sys.exit(1)

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load tracking log
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# Find unuploaded reels (newest first), skip test files
all_reels = sorted(glob.glob(os.path.join(REELS_DIR, "*.mp4")), key=os.path.getmtime, reverse=True)
unuploaded = [r for r in all_reels if os.path.basename(r) not in yt_log and not os.path.basename(r).startswith("reel-test")]

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

print(f"Found {len(unuploaded)} unuploaded reel(s). Will upload up to 2.\n")

# Fetch recent articles from Supabase
print("Fetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"  Fetched {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️ Could not fetch articles: {e}")
    articles = []

def match_article(filename):
    """Match reel filename to an article by slug fragment matching."""
    # Strip reel- prefix and trailing date + .mp4
    base = filename.replace("reel-", "").replace(".mp4", "")
    # Remove trailing date pattern (YYYYMMDD or partial)
    base = re.sub(r'-?\d{6,8}$', '', base)
    words = set(base.split('-'))
    # Remove common filler words
    words -= {'nri', 'india', 'the', 'and', 'for', 'with', 'from', 'new', 'how', 'why'}
    
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get('slug', '')
        slug_words = set(slug.split('-'))
        overlap = len(words & slug_words)
        score = overlap / max(len(words), 1)
        if score > best_score and score >= 0.4:
            best_score = score
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
    # Person names / entities
    known = {
        "modi": "#NarendraModi", "trump": "#Trump", "kohli": "#ViratKohli",
        "dhoni": "#MSDhoni", "bumrah": "#JaspritBumrah", "rohit": "#RohitSharma",
        "gambhir": "#GautamGambhir", "gukesh": "#DGukesh", "nolan": "#ChristopherNolan",
        "deepseek": "#DeepSeek", "prasidh": "#PrasidhKrishna", "jemimah": "#JemimahRodrigues",
        "salim": "#SalimKumar", "anushka": "#AnushkaSharma", "naga": "#NagaChaitanya",
    }
    hl_lower = headline.lower()
    for key, tag in known.items():
        if key in hl_lower:
            tags.append(tag)
    return tags[:5]

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', 'unknown')
        category = article.get('category', 'news')
    else:
        # Fallback: construct from filename
        base = filename.replace("reel-", "").replace(".mp4", "")
        base = re.sub(r'-?\d{6,8}$', '', base)
        headline = ' '.join(w.capitalize() for w in base.split('-'))
        subheadline = headline
        slug = 'unknown'
        category = 'news'
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + "…"
    title = f"{title} #Shorts"
    
    # Hashtags
    base_tags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = ' '.join(make_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()
    
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    # Tags list
    tag_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    for ht in make_topic_hashtags(headline):
        tag_list.append(ht.replace("#", ""))
    tag_list = tag_list[:12]
    
    return title, description, tag_list, slug

# YouTube auth
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ YouTube API ready\n")

uploaded_count = 0
errors = []

for reel_path in unuploaded[:2]:
    filename = os.path.basename(reel_path)
    print(f"{'='*60}")
    print(f"Processing: {filename}")
    print(f"  Size: {os.path.getsize(reel_path)/1024/1024:.1f} MB")
    
    # Match article
    article = match_article(filename)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:80]}")
        print(f"  Slug: {article.get('slug', '')}")
    else:
        print(f"  ⚠️ No article match — using filename fallback")
    
    title, description, tags, slug = compose_metadata(article, filename)
    print(f"  Title: {title}")
    print(f"  Tags: {', '.join(tags[:6])}...")
    
    # Upload
    try:
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
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")
        
        # Log
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if uploaded_count < min(2, len(unuploaded)):
            print("  Waiting 10s before next upload...")
            time.sleep(10)
            
    except Exception as e:
        err_msg = f"Failed to upload {filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}")
print(f"  Errors: {len(errors)}")
if errors:
    for e in errors:
        print(f"    - {e}")
for fn, data in yt_log.items():
    if fn in [os.path.basename(r) for r in unuploaded[:2]]:
        print(f"  🔗 {data.get('url', '')}")
