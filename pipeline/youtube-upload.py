#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
from datetime import datetime

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Config ---
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
ENV_YT = os.path.expanduser("~/workspace/.env.youtube")
ENV_SB = os.path.expanduser("~/workspace/.env.supabase")
MAX_UPLOADS = 2
SKIP_PATTERNS = ["reel-v2-", "test-", "demo-"]

# --- Load env files ---
def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env(ENV_YT)
sb_env = load_env(ENV_SB)

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SB_KEY")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
all_reels = [f for f in os.listdir(REELS_DIR) if f.endswith(".mp4")]
# Skip test files
all_reels = [f for f in all_reels if not any(p in f for p in SKIP_PATTERNS)]
# Filter unuploaded
unuploaded = [f for f in all_reels if f not in yt_log]
# Sort by modification time, newest first
unuploaded.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

print(f"Found {len(all_reels)} reels total, {len(unuploaded)} unuploaded")
if not unuploaded:
    print("Nothing to upload. All reels are already on YouTube.")
    exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reel(s):\n  " + "\n  ".join(to_upload))

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Fetched {len(articles)} articles")
except Exception as e:
    print(f"  Warning: Could not fetch articles: {e}")
    articles = []

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
    """Find matching article for reel filename."""
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
        # Bonus for consecutive match
        if frag_str in slug:
            score += len(fragments)
        if score > best_score and score >= max(2, len(fragments) * 0.4):
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

def build_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common name patterns
    names_map = {
        "modi": "#NarendraModi", "trump": "#Trump", "kohli": "#ViratKohli",
        "dhoni": "#MSDhoni", "bumrah": "#JaspritBumrah", "rohit": "#RohitSharma",
        "shah": "#AmitShah", "rahul": "#RahulGandhi", "jaishankar": "#Jaishankar",
        "mamata": "#MamataBanerjee", "kejriwal": "#Kejriwal", "yogi": "#YogiAdityanath",
        "adani": "#Adani", "ambani": "#Ambani", "elon": "#ElonMusk", "musk": "#ElonMusk",
        "zuckerberg": "#Zuckerberg", "sundar": "#SundarPichai", "satya": "#SatyaNadella",
        "biden": "#Biden",
    }
    hl_lower = headline.lower() if headline else ""
    for key, tag in names_map.items():
        if key in hl_lower:
            tags.append(tag)
    
    # Place/event patterns
    places = {
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bangalore": "#Bangalore",
        "hyderabad": "#Hyderabad", "chennai": "#Chennai", "kolkata": "#Kolkata",
        "kerala": "#Kerala", "bengal": "#WestBengal", "punjab": "#Punjab",
        "kashmir": "#Kashmir", "silicon valley": "#SiliconValley",
    }
    for key, tag in places.items():
        if key in hl_lower:
            tags.append(tag)
    
    return tags[:5]

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "unknown")
        category = article.get("category", "news")
        art_tags = article.get("tags") or []
    else:
        # Construct from filename
        fragments = extract_slug_fragments(filename)
        headline = " ".join(f.capitalize() for f in fragments)
        subheadline = ""
        slug = "unknown"
        category = "news"
        art_tags = []
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = build_topic_hashtags(headline)
    topic_str = " ".join(topic_tags)
    
    all_hashtags = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags}"
    if topic_str:
        all_hashtags += f" {topic_str}"
    # Ensure we have 15+ hashtags
    extra = "#India #Desi #SouthAsian #GlobalIndian #NRINews #IndiaAbroad #BreakingIndia"
    all_hashtags += f" {extra}"
    
    # Description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != "unknown" else "https://thevideshi.com"
    
    desc_parts = []
    if subheadline:
        desc_parts.append(subheadline)
    desc_parts.append(f"\n📰 Full story: {article_link}")
    desc_parts.append("\nThe Videshi — News for the global Indian diaspora")
    desc_parts.append("🌐 thevideshi.com")
    desc_parts.append("\nFollow us:")
    desc_parts.append("📸 Instagram: https://instagram.com/the.videshi")
    desc_parts.append("🐦 X/Twitter: https://x.com/thevideshi")
    desc_parts.append("🧵 Threads: https://threads.net/@the.videshi")
    desc_parts.append(f"\n{all_hashtags}")
    
    description = "\n".join(desc_parts)
    
    # Tags list
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    for t in topic_tags[:3]:
        yt_tags.append(t.replace("#", ""))
    if art_tags:
        for t in art_tags[:3]:
            if t not in yt_tags:
                yt_tags.append(t)
    # Pad to 8-12
    for extra_t in ["Indian American", "South Asian", "Desi", "India", "Global Indian"]:
        if len(yt_tags) >= 12:
            break
        if extra_t not in yt_tags:
            yt_tags.append(extra_t)
    
    return title, description, yt_tags, slug

# --- YouTube auth ---
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET,
)
youtube = build("youtube", "v3", credentials=creds)
print("  Authenticated ✓")

# --- Upload loop ---
uploaded_count = 0
errors = []
results = []

for i, reel_filename in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(to_upload)}] {reel_filename}")
    print(f"  File size: {os.path.getsize(reel_path) / 1024 / 1024:.1f} MB")
    
    # Match article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"  No article match found, using filename-derived title")
    
    # Compose metadata
    title, description, tags, slug = compose_metadata(article, reel_filename)
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
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((reel_filename, url))
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Failed to upload {reel_filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"  Uploaded: {uploaded_count}/{len(to_upload)}")
for fn, url in results:
    print(f"    {fn} → {url}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    {e}")
print(f"  Total in log: {len(yt_log)}")
