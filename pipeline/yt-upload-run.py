#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""
import json, os, time, re, sys, requests
from datetime import datetime, timezone

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels (skip test files)
skip_files = {"reel-v2-final.mp4", "reel-v2-fixed.mp4"}
all_reels = []
for fn in os.listdir(REELS_DIR):
    if fn.endswith(".mp4") and fn not in skip_files and fn not in yt_log:
        fpath = os.path.join(REELS_DIR, fn)
        mtime = os.path.getmtime(fpath)
        all_reels.append((mtime, fn, fpath))

all_reels.sort(reverse=True)  # newest first
to_upload = all_reels[:2]

if not to_upload:
    print("No unuploaded reels found. All caught up!")
    sys.exit(0)

print(f"Found {len(to_upload)} reel(s) to upload:\n")
for _, fn, _ in to_upload:
    print(f"  - {fn}")

# Fetch recent articles from Supabase
print("\nFetching recent articles from Supabase...")
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Got {len(articles)} articles")
except Exception as e:
    print(f"  Warning: Could not fetch articles: {e}")
    articles = []

def match_article(filename):
    """Try to match reel filename to an article."""
    # Strip reel- prefix and trailing date + .mp4
    base = filename.replace(".mp4", "")
    if base.startswith("reel-"):
        base = base[5:]
    # Remove trailing date pattern like -20260529
    base = re.sub(r'-\d{8}$', '', base)
    words = set(base.split('-'))
    
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get("slug", "")
        slug_words = set(slug.split('-'))
        overlap = len(words & slug_words)
        if overlap > best_score and overlap >= 3:
            best_score = overlap
            best_match = art
    return best_match

def make_title_from_filename(filename):
    base = filename.replace(".mp4", "")
    if base.startswith("reel-"):
        base = base[5:]
    base = re.sub(r'-\d{8}$', '', base)
    words = base.split('-')
    return ' '.join(w.capitalize() for w in words)

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

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common patterns
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline)
    for w in words:
        clean = w.replace(' ', '')
        if len(clean) > 3 and clean not in ('The', 'This', 'That', 'What', 'When', 'Where', 'How', 'Why', 'For', 'From', 'With', 'About', 'Into', 'Over', 'After', 'Before', 'Under', 'Between', 'Through', 'During', 'Could', 'Would', 'Should', 'Their', 'Here', 'They', 'Will', 'Have', 'Been', 'More', 'Most', 'Than', 'Also', 'Just', 'Your', 'Some'):
            tags.append(f"#{clean}")
    return list(dict.fromkeys(tags))[:5]  # dedupe, max 5

def compose_metadata(article, filename):
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "news")
        tags_list = article.get("tags") or []
    else:
        headline = make_title_from_filename(filename)
        subheadline = ""
        slug = ""
        category = "news"
        tags_list = []
    
    # Title
    title = headline[:93] + " #Shorts" if len(headline) > 93 else headline + " #Shorts"
    
    # Hashtags
    base_hashtags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_hashtags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_hashtags = extract_topic_hashtags(headline)
    all_hashtags = f"{base_hashtags} {cat_hashtags} " + " ".join(topic_hashtags)
    
    # Description
    article_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}" if slug else ""
    desc = f"""{subheadline}{article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    for t in topic_hashtags[:4]:
        yt_tags.append(t.replace("#", ""))
    if isinstance(tags_list, list):
        for t in tags_list[:2]:
            if isinstance(t, str) and t not in yt_tags:
                yt_tags.append(t)
    yt_tags = yt_tags[:12]
    
    return title, desc, yt_tags, slug

# Set up YouTube client
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

uploaded = 0
errors = []

for i, (mtime, fn, fpath) in enumerate(to_upload):
    print(f"\n{'='*60}")
    print(f"Uploading {i+1}/{len(to_upload)}: {fn}")
    
    article = match_article(fn)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:60]}...")
    else:
        print(f"  No article match; using filename-derived title")
    
    title, desc, tags, slug = compose_metadata(article, fn)
    print(f"  Title: {title}")
    
    body = {
        "snippet": {
            "title": title,
            "description": desc,
            "tags": tags,
            "categoryId": "25"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(fpath, mimetype="video/mp4", resumable=True)
    
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
        
        # Log
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded += 1
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((fn, str(e)))

print(f"\n{'='*60}")
print(f"SUMMARY: {uploaded} uploaded, {len(errors)} error(s)")
if errors:
    for fn, err in errors:
        print(f"  ❌ {fn}: {err}")
