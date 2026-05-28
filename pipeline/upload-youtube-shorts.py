#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
from datetime import datetime, timezone

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Config ---
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# --- Load env files ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
reel_files = []
for fname in os.listdir(REELS_DIR):
    if not fname.endswith(".mp4"):
        continue
    # Skip test/dev files
    if fname in ("reel-v2-final.mp4", "reel-v2-fixed.mp4") or not fname.startswith("reel-"):
        continue
    if fname in yt_log:
        continue
    fpath = os.path.join(REELS_DIR, fname)
    mtime = os.path.getmtime(fpath)
    reel_files.append((fname, fpath, mtime))

# Sort newest first
reel_files.sort(key=lambda x: x[2], reverse=True)

if not reel_files:
    print("✅ No unuploaded reels found. All caught up!")
    exit(0)

print(f"Found {len(reel_files)} unuploaded reel(s). Will upload up to {MAX_UPLOADS}.")
for fname, _, _ in reel_files:
    print(f"  • {fname}")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Loaded {len(articles)} recent articles.")
except Exception as e:
    print(f"  ⚠️ Failed to fetch articles: {e}")
    articles = []

# --- Category hashtag map ---
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

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split("-")

def match_article(filename, articles):
    """Try to match a reel filename to an article."""
    slug_words = extract_slug_words(filename)
    slug_fragment = "-".join(slug_words)
    
    best_match = None
    best_score = 0
    
    for article in articles:
        slug = article.get("slug", "")
        if not slug:
            continue
        # Check how many words from the reel filename appear in the article slug
        score = sum(1 for w in slug_words if w in slug and len(w) > 2)
        # Bonus for exact substring match
        if slug_fragment in slug or slug in slug_fragment:
            score += 10
        if score > best_score and score >= 3:
            best_score = score
            best_match = article
    
    return best_match

def make_title_from_filename(filename):
    """Construct a title from filename words if no article match."""
    words = extract_slug_words(filename)
    return " ".join(w.capitalize() for w in words)

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags based on category + content."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common name patterns
    names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', headline or "")
    for name in names[:3]:
        tag = "#" + name.replace(" ", "")
        if tag not in topic_tags:
            topic_tags.append(tag)
    
    # Key terms
    headline_lower = (headline or "").lower()
    keyword_map = {
        "modi": "#NarendraModi", "kohli": "#ViratKohli", "ipl": "#IPL2026",
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bengaluru": "#Bengaluru",
        "infosys": "#Infosys", "tcs": "#TCS", "reliance": "#Reliance",
        "h1b": "#H1BVisa", "h-1b": "#H1BVisa", "green card": "#GreenCard",
        "bollywood": "#Bollywood", "cricket": "#Cricket", "tesla": "#Tesla",
        "ai ": "#AI", "trump": "#Trump", "mamata": "#MamataBanerjee",
        "bjp": "#BJP", "congress": "#Congress", "west bengal": "#WestBengal",
        "oil": "#OilPrices", "hormuz": "#StraitOfHormuz",
        "supreme court": "#SupremeCourt", "amazon": "#Amazon",
    }
    for kw, tag in keyword_map.items():
        if kw in headline_lower and tag not in topic_tags:
            topic_tags.append(tag)
    
    all_tags = f"{base} {cat_tags} {' '.join(topic_tags[:5])}"
    return all_tags

# --- YouTube auth ---
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ YouTube client ready.")

# --- Upload loop ---
uploaded = []
errors = []

for i, (fname, fpath, mtime) in enumerate(reel_files[:MAX_UPLOADS]):
    print(f"\n{'='*60}")
    print(f"[{i+1}/{min(len(reel_files), MAX_UPLOADS)}] Processing: {fname}")
    
    # Match article
    article = match_article(fname, articles)
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "unknown")
        category = article.get("category", "news")
        print(f"  📰 Matched article: {headline[:80]}")
    else:
        headline = make_title_from_filename(fname)
        subheadline = ""
        slug = "unknown"
        category = "news"
        print(f"  ⚠️ No article match. Using filename title: {headline}")
    
    # Compose title (under 100 chars + #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
    # Compose description
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
    # Add topic tags from headline
    name_matches = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', headline or "")
    for nm in name_matches[:3]:
        if nm not in tags:
            tags.append(nm)
    if len(tags) < 8:
        tags.extend(["South Asian", "Desi", "Global India"][:8-len(tags)])
    tags = tags[:12]
    
    print(f"  📝 Title: {title}")
    print(f"  🏷️ Category: {category}")
    print(f"  🔖 Tags: {', '.join(tags)}")
    
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
        
        media = MediaFileUpload(fpath, mimetype="video/mp4", resumable=True)
        
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
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((fname, url))
        
        # Wait between uploads
        if i < min(len(reel_files), MAX_UPLOADS) - 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((fname, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print("📊 UPLOAD SUMMARY")
print(f"  Uploaded: {len(uploaded)}/{min(len(reel_files), MAX_UPLOADS)}")
for fname, url in uploaded:
    print(f"    ✅ {fname}")
    print(f"       → {url}")
if errors:
    print(f"  Errors: {len(errors)}")
    for fname, err in errors:
        print(f"    ❌ {fname}: {err}")
if len(reel_files) > MAX_UPLOADS:
    print(f"  ⏭️ {len(reel_files) - MAX_UPLOADS} reel(s) remaining for next run.")
print("Done!")
