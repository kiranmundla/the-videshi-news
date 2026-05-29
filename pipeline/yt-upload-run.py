#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts (max 2 per run)."""

import json, os, re, time, glob
from datetime import datetime, timezone

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

# Skip test/dev files
SKIP_PATTERNS = ["reel-v2-final.mp4", "reel-v2-fixed.mp4", "reel-v2-"]

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
mp4s = glob.glob(os.path.join(REELS_DIR, "reel-*.mp4"))
mp4s.sort(key=lambda p: os.path.getmtime(p), reverse=True)  # newest first

unuploaded = []
for p in mp4s:
    fname = os.path.basename(p)
    if fname in yt_log:
        continue
    if any(skip in fname for skip in SKIP_PATTERNS):
        print(f"  ⏭️  Skipping test file: {fname}")
        continue
    unuploaded.append(p)

print(f"Found {len(unuploaded)} unuploaded reel(s)")
if not unuploaded:
    print("Nothing to upload. Done.")
    exit(0)

# Limit to 2
to_upload = unuploaded[:2]
print(f"Will upload {len(to_upload)} reel(s)\n")

# --- Fetch recent articles from Supabase ---
import requests as req

print("Fetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"  Got {len(articles)} recent articles\n")

def match_article(filename):
    """Try to match a reel filename to an article."""
    # Strip reel- prefix and trailing date + .mp4
    base = filename.replace("reel-", "", 1).replace(".mp4", "")
    # Remove trailing date like -20260529
    base = re.sub(r'-\d{8}$', '', base)
    words = set(base.split('-'))
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        slug_words = set(slug.split('-'))
        # Count overlapping words (exclude very short words)
        overlap = len(words.intersection(slug_words) - {''})
        significant_words = {w for w in words if len(w) > 2}
        significant_overlap = len(significant_words.intersection(slug_words))
        
        if significant_overlap > best_score and significant_overlap >= 3:
            best_score = significant_overlap
            best_match = art
    
    return best_match

# --- Category hashtag map ---
CATEGORY_TAGS = {
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
    # Common name patterns
    names_map = {
        "modi": "#NarendraModi", "trump": "#Trump", "kohli": "#ViratKohli",
        "jaishankar": "#Jaishankar", "sitharaman": "#NirmalaSitharaman",
        "adani": "#Adani", "ambani": "#Ambani", "kejriwal": "#Kejriwal",
        "rahul gandhi": "#RahulGandhi", "mamata": "#MamataBanerjee",
        "dhoni": "#Dhoni", "bumrah": "#JaspritBumrah", "sachin": "#SachinTendulkar",
        "rohit": "#RohitSharma",
    }
    hl = headline.lower()
    for key, tag in names_map.items():
        if key in hl:
            tags.append(tag)
    
    # Place/org patterns
    places = {
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bangalore": "#Bangalore",
        "hyderabad": "#Hyderabad", "chennai": "#Chennai", "kolkata": "#Kolkata",
        "silicon valley": "#SiliconValley", "wall street": "#WallStreet",
        "infosys": "#Infosys", "tcs": "#TCS", "wipro": "#Wipro",
        "ipl": "#IPL2026", "bcci": "#BCCI",
    }
    for key, tag in places.items():
        if key in hl:
            tags.append(tag)
    
    return tags[:5]

def build_title(headline):
    """Build YouTube title under 100 chars with #Shorts."""
    suffix = " #Shorts"
    max_len = 100 - len(suffix)
    if len(headline) > max_len:
        headline = headline[:max_len-3] + "..."
    return headline + suffix

def build_description(article, category):
    """Build YouTube description."""
    subheadline = article.get("subheadline", "") or ""
    slug = article.get("slug", "")
    headline = article.get("headline", "")
    
    cat_tags = CATEGORY_TAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = make_topic_hashtags(headline)
    
    all_hashtags = "#TheVideshi #Shorts #IndianDiaspora #NRI " + cat_tags
    if topic_tags:
        all_hashtags += " " + " ".join(topic_tags)
    
    desc = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    return desc

def build_tags(article, category):
    """Build YouTube video tags list."""
    headline = article.get("headline", "")
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category or "News", "Shorts"]
    
    # Add topic words from headline
    topic_tags = make_topic_hashtags(headline)
    for t in topic_tags:
        clean = t.replace("#", "")
        if clean not in tags:
            tags.append(clean)
    
    # Pad to at least 8
    filler = ["South Asian", "Desi", "Indian American", "NRI News", "Global Indian"]
    for f in filler:
        if len(tags) >= 12:
            break
        if f not in tags:
            tags.append(f)
    
    return tags[:12]

# --- YouTube upload ---
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

for reel_path in to_upload:
    fname = os.path.basename(reel_path)
    print(f"📹 Processing: {fname}")
    
    # Match article
    article = match_article(fname)
    if article:
        headline = article["headline"]
        slug = article["slug"]
        category = article.get("category", "news")
        print(f"  ✅ Matched article: {slug}")
    else:
        # Construct from filename
        base = fname.replace("reel-", "", 1).replace(".mp4", "")
        base = re.sub(r'-\d{8}$', '', base)
        headline = " ".join(w.capitalize() for w in base.split("-"))
        slug = base
        category = "news"
        print(f"  ⚠️  No article match, using filename: {headline}")
        article = {"headline": headline, "subheadline": "", "slug": slug, "category": category}
    
    title = build_title(headline)
    description = build_description(article, category)
    tags = build_tags(article, category)
    
    print(f"  Title: {title}")
    print(f"  Tags: {tags}")
    
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
        print(f"  ✅ Uploaded: {url}\n")
        
        # Log
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append({"file": fname, "url": url, "title": title})
        
        # Wait between uploads
        if reel_path != to_upload[-1]:
            print("  ⏳ Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error uploading {fname}: {e}")
        errors.append({"file": fname, "error": str(e)})

# --- Summary ---
print("\n" + "=" * 60)
print(f"📊 SUMMARY")
print(f"  Uploaded: {len(uploaded)}")
print(f"  Errors: {len(errors)}")
for u in uploaded:
    print(f"  ✅ {u['title']}")
    print(f"     {u['url']}")
for e in errors:
    print(f"  ❌ {e['file']}: {e['error']}")
print("=" * 60)
