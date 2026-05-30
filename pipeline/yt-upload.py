#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""
import json, os, re, time, glob, requests
from datetime import datetime
from pathlib import Path

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
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY", sb_env.get("SUPABASE_ANON_KEY", ""))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load log
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# Find unuploaded reels (newest first), skip test files
all_reels = sorted(glob.glob(os.path.join(REELS_DIR, "reel-*.mp4")), key=os.path.getmtime, reverse=True)
unuploaded = []
for rp in all_reels:
    fn = os.path.basename(rp)
    if fn in yt_log:
        continue
    # Skip test/prototype files
    if fn.startswith("reel-v2-") or not re.match(r'reel-.+-\d{8}\.mp4$', fn):
        print(f"  ⏭️  Skipping test file: {fn}")
        continue
    unuploaded.append(rp)

print(f"Found {len(unuploaded)} unuploaded reel(s)")
if not unuploaded:
    print("Nothing to upload. Done.")
    exit(0)

# Limit to 2 per run
unuploaded = unuploaded[:2]

# Fetch recent articles from Supabase
print("Fetching recent articles from Supabase...")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"  Fetched {len(articles)} recent articles")

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split("-")

def match_article(filename, articles):
    """Find matching article by slug fragments."""
    fragments = extract_slug_fragments(filename)
    frag_str = "-".join(fragments)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Count how many fragments appear in the slug
        score = sum(1 for f in fragments if f in slug)
        # Normalize by total fragments
        if len(fragments) > 0:
            ratio = score / len(fragments)
        else:
            ratio = 0
        if ratio > best_score and ratio >= 0.4:
            best_score = ratio
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
    # Common person/place/company patterns
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline)
    for w in words[:5]:
        tag = "#" + w.replace(" ", "")
        if len(tag) > 3 and tag not in tags:
            tags.append(tag)
    return " ".join(tags[:5])

def compose_metadata(article, filename):
    """Compose YouTube metadata from article info."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "unknown")
        category = article.get("category", "news")
    else:
        # Construct from filename
        frags = extract_slug_fragments(filename)
        headline = " ".join(f.capitalize() for f in frags)
        subheadline = headline
        slug = "unknown"
        category = "news"
    
    # Title: under 100 chars + #Shorts
    title = headline[:90] + " #Shorts" if len(headline) > 90 else headline + " #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = make_topic_hashtags(headline)
    all_hashtags = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_tags}"
    
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags array
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    # Add topic words from headline
    for word in re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline)[:4]:
        if word not in tags:
            tags.append(word)
    tags = tags[:12]
    
    return title, description, tags, slug

# Setup YouTube client
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

uploaded = []
errors = []

for i, reel_path in enumerate(unuploaded):
    reel_filename = os.path.basename(reel_path)
    print(f"\n--- Uploading {i+1}/{len(unuploaded)}: {reel_filename}")
    
    # Match article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:60]}...")
    else:
        print(f"  No article match found, using filename-based metadata")
    
    title, description, tags, slug = compose_metadata(article, reel_filename)
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
        
        # Log to youtube-log.json
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append({"filename": reel_filename, "url": url, "video_id": video_id})
        
        # Wait 10s between uploads
        if i < len(unuploaded) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append({"filename": reel_filename, "error": str(e)})

print(f"\n=== Summary ===")
print(f"Uploaded: {len(uploaded)}")
for u in uploaded:
    print(f"  ✅ {u['filename']} → {u['url']}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  ❌ {e['filename']}: {e['error']}")
print("Done.")
