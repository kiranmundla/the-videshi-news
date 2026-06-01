#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts."""

import json, os, re, time, glob, requests
from datetime import datetime
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SB_KEY", "")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels
mp4s = sorted(
    glob.glob(os.path.join(REELS_DIR, "reel-*.mp4")),
    key=lambda p: os.path.getmtime(p),
    reverse=True  # newest first
)
# Filter out cover images & already uploaded
unuploaded = [p for p in mp4s if os.path.basename(p) not in yt_log and not p.endswith("-cover.jpg")]

print(f"Found {len(mp4s)} total reels, {len(unuploaded)} unuploaded")
if not unuploaded:
    print("Nothing to upload.")
    exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reels:")
for p in to_upload:
    print(f"  - {os.path.basename(p)}")

# Fetch recent articles from Supabase
articles = []
if SB_KEY:
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        articles = r.json()
        print(f"Fetched {len(articles)} recent articles from Supabase")
    except Exception as e:
        print(f"Warning: Could not fetch articles: {e}")

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace(".mp4", "")
    name = re.sub(r"^reel-", "", name)
    # Remove trailing date pattern (YYYYMMDD)
    name = re.sub(r"-\d{8}$", "", name)
    return name.split("-")

def match_article(filename, articles):
    """Try to match a reel filename to an article."""
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
        ratio = score / max(len(fragments), 1)
        if ratio > best_score and ratio >= 0.5:
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

def generate_hashtags(category, headline):
    """Generate hashtags for a YouTube Short."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common name patterns
    names_map = {
        "kohli": "#ViratKohli", "rohit": "#RohitSharma", "modi": "#NarendraModi",
        "trump": "#Trump", "rcb": "#RCB", "ipl": "#IPL2026", "csk": "#CSK",
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bengaluru": "#Bengaluru",
        "h1b": "#H1BVisa", "uscis": "#USCIS", "green card": "#GreenCard",
        "sensex": "#Sensex", "nifty": "#Nifty", "rbi": "#RBI",
        "infosys": "#Infosys", "tcs": "#TCS", "wipro": "#Wipro",
        "bollywood": "#Bollywood", "netflix": "#Netflix",
        "cricket": "#Cricket", "bcci": "#BCCI",
        "sooryavanshi": "#Sooryavanshi", "dhoni": "#MSDhoni",
        "bumrah": "#JaspritBumrah", "hardik": "#HardikPandya",
        "eb1a": "#EB1A", "eb1": "#EB1",
        "dynasty": "#Dynasty", "champions": "#Champions",
        "taekwondo": "#Taekwondo", "rupa bayor": "#RupaBayor",
    }
    
    hl_lower = headline.lower() if headline else ""
    for key, tag in names_map.items():
        if key in hl_lower and tag not in topic_tags:
            topic_tags.append(tag)
    
    all_tags = f"{base} {cat_tags} {' '.join(topic_tags[:5])}"
    return all_tags

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "unknown")
        category = article.get("category", "news")
    else:
        # Construct from filename
        fragments = extract_slug_fragments(filename)
        headline = " ".join(w.capitalize() for w in fragments)
        subheadline = ""
        slug = "unknown"
        category = "news"
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + "…"
    title = f"{title} #Shorts"
    
    # Description
    hashtags = generate_hashtags(category, headline)
    
    article_link = f"📰 Full story: https://thevideshi.com/articles/{slug}" if slug != "unknown" else ""
    
    description = f"""{subheadline}

{article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}""".strip()
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    # Add topic words from headline
    if headline:
        words = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', headline)
        for w in words[:4]:
            if w not in tags and len(w) > 2:
                tags.append(w)
    if len(tags) < 8:
        tags.extend(["South Asian", "Desi"])
    tags = tags[:12]
    
    return title, description, tags, slug, category

# Set up YouTube API
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

uploaded_count = 0
errors = []
results = []

for i, reel_path in enumerate(to_upload):
    filename = os.path.basename(reel_path)
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(to_upload)}] Uploading: {filename}")
    
    # Match article
    article = match_article(filename, articles)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"  No article match found, using filename")
    
    title, description, tags, slug, category = compose_metadata(article, filename)
    print(f"  Title: {title}")
    print(f"  Category: {category}")
    
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
        media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
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
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append({"filename": filename, "url": url, "title": title})
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append({"filename": filename, "error": str(e)})

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY: {uploaded_count}/{len(to_upload)} uploaded successfully")
if results:
    for r in results:
        print(f"  ✅ {r['title'][:60]} → {r['url']}")
if errors:
    print(f"  ❌ {len(errors)} errors:")
    for e in errors:
        print(f"     {e['filename']}: {e['error']}")
