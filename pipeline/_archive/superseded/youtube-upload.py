#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, sys, time, re, glob
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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
MAX_UPLOADS = 2

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels
reel_files = glob.glob(os.path.join(REELS_DIR, "reel-*.mp4"))
# Filter out test files and already uploaded
unuploaded = []
for fp in reel_files:
    fn = os.path.basename(fp)
    if fn in yt_log:
        continue
    # Skip test reels
    if "test" in fn.lower():
        print(f"⏭️  Skipping test reel: {fn}")
        continue
    unuploaded.append((fp, fn, os.path.getmtime(fp)))

# Sort by modification time, newest first
unuploaded.sort(key=lambda x: x[2], reverse=True)

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

print(f"📹 Found {len(unuploaded)} unuploaded reel(s). Will upload up to {MAX_UPLOADS}.")

# Fetch recent articles from Supabase
print("📰 Fetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"   Fetched {len(articles)} recent articles.")

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    # Strip reel- prefix
    name = filename.replace("reel-", "").replace(".mp4", "")
    # Strip trailing date pattern (YYYYMMDD or just partial)
    name = re.sub(r'-?\d{8,}$', '', name)
    # Remove trailing partial patterns
    name = re.sub(r'-\d+$', '', name)
    return name.lower().split('-')

def match_article(filename, articles):
    """Find best matching article for a reel filename."""
    fragments = extract_slug_fragments(filename)
    if not fragments:
        return None
    
    best_match = None
    best_score = 0
    
    for article in articles:
        slug = (article.get('slug') or '').lower()
        if not slug:
            continue
        
        # Count how many fragments appear in the slug
        matches = sum(1 for f in fragments if f in slug and len(f) > 2)
        score = matches / max(len(fragments), 1)
        
        if score > best_score and score >= 0.4:
            best_score = score
            best_match = article
    
    return best_match

def generate_hashtags(category, headline):
    """Generate hashtags based on category and headline."""
    base = ["#TheVideshi", "#Shorts", "#IndianDiaspora", "#NRI"]
    
    cat_tags = {
        "news": ["#IndiaNews", "#BreakingNews", "#DesiNews", "#SouthAsian"],
        "immigration": ["#H1B", "#H1BVisa", "#GreenCard", "#USImmigration", "#USCIS"],
        "nri-world": ["#NRILife", "#DesiAbroad", "#IndianAmerican"],
        "travel": ["#TravelIndia", "#IncredibleIndia", "#IndiaTravel"],
        "lifestyle-health": ["#DesiLifestyle", "#Wellness", "#Health"],
        "markets-finance": ["#StockMarket", "#Nifty", "#Sensex", "#IndianMarkets"],
        "technology": ["#TechNews", "#IndianTech", "#SiliconValley", "#AI"],
        "sports": ["#Cricket", "#IPL", "#IPL2026", "#TeamIndia", "#BCCI"],
        "entertainment": ["#Bollywood", "#BollywoodNews", "#IndianCinema", "#Tollywood"],
        "food": ["#IndianFood", "#IndianCuisine", "#DesiFood"],
    }
    
    cat = (category or "news").lower()
    tags = base + cat_tags.get(cat, ["#IndiaNews", "#DesiNews"])
    
    # Extract topic-specific hashtags from headline
    headline_lower = (headline or "").lower()
    
    # Common name/topic mappings
    topic_hashtags = {
        "h1b": "#H1BVisa", "green card": "#GreenCard", "uscis": "#USCIS",
        "modi": "#NarendraModi", "kohli": "#ViratKohli", "ipl": "#IPL2026",
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bengaluru": "#Bengaluru",
        "infosys": "#Infosys", "tata": "#Tata", "trump": "#Trump",
        "cricket": "#Cricket", "bollywood": "#Bollywood", "nolan": "#ChristopherNolan",
        "deepseek": "#DeepSeek", "congress": "#Congress", "bjp": "#BJP",
        "rupee": "#IndianRupee", "sensex": "#Sensex", "nifty": "#Nifty50",
        "tesla": "#Tesla", "amazon": "#Amazon", "google": "#Google",
        "rbi": "#RBI", "supreme court": "#SupremeCourt",
        "opt": "#OPT", "immigration": "#Immigration",
    }
    
    for keyword, hashtag in topic_hashtags.items():
        if keyword in headline_lower and hashtag not in tags:
            tags.append(hashtag)
            if len(tags) >= 20:
                break
    
    return " ".join(tags)

def generate_tags_list(category, headline):
    """Generate YouTube tags list."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    cat = (category or "news").capitalize()
    if cat not in tags:
        tags.append(cat)
    
    # Extract key terms from headline
    words = (headline or "").split()
    # Get proper nouns / key terms (capitalized words that aren't common)
    skip = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "is", "are", "was", "were", "has", "have", "had", "with", "from", "by", "as", "its", "it", "that", "this", "will", "can", "may", "be", "been", "do", "does", "did", "not", "no", "but", "if", "how", "why", "what", "when", "where", "who"}
    for w in words:
        clean = re.sub(r'[^\w]', '', w)
        if clean and clean[0].isupper() and clean.lower() not in skip and len(clean) > 2:
            if clean not in tags and len(tags) < 12:
                tags.append(clean)
    
    return tags

# Set up YouTube client
print("🔑 Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("   ✅ YouTube API client ready.")

uploaded_count = 0
errors = []
results = []

for fp, fn, mtime in unuploaded[:MAX_UPLOADS]:
    print(f"\n{'='*60}")
    print(f"📤 Uploading: {fn}")
    print(f"   File size: {os.path.getsize(fp) / 1024 / 1024:.1f} MB")
    
    # Match article
    article = match_article(fn, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        slug = article.get('slug', 'unknown')
        category = article.get('category', 'news')
        print(f"   📰 Matched article: {headline[:80]}")
    else:
        # Construct from filename
        name_parts = fn.replace("reel-", "").replace(".mp4", "")
        name_parts = re.sub(r'-?\d{8,}$', '', name_parts)
        headline = " ".join(w.capitalize() for w in name_parts.split('-'))
        subheadline = f"Watch this short from The Videshi — news for the global Indian diaspora."
        slug = "unknown"
        category = "news"
        print(f"   ⚠️  No article match. Using filename: {headline}")
    
    # Compose title (under 100 chars, with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
    # Compose description
    hashtags = generate_hashtags(category, headline)
    
    article_link = ""
    if slug and slug != "unknown":
        article_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}\n"
    
    description = f"""{subheadline}
{article_link}
The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    tags = generate_tags_list(category, headline)
    
    print(f"   Title: {title}")
    print(f"   Tags: {tags}")
    
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
                print(f"   Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"   ✅ Uploaded: {url}")
        
        # Log success
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((fn, url))
        
        # Wait between uploads
        if uploaded_count < MAX_UPLOADS and len(unuploaded) > uploaded_count:
            print("   ⏳ Waiting 10 seconds before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Error uploading {fn}: {str(e)}"
        print(f"   ❌ {err_msg}")
        errors.append(err_msg)

# Summary
print(f"\n{'='*60}")
print(f"📊 Upload Summary:")
print(f"   Uploaded: {uploaded_count}/{min(len(unuploaded), MAX_UPLOADS)}")
for fn, url in results:
    print(f"   ✅ {fn} → {url}")
if errors:
    print(f"   Errors: {len(errors)}")
    for e in errors:
        print(f"   ❌ {e}")
print(f"{'='*60}")
