#!/usr/bin/env python3
"""Upload unuploaded reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load credentials ---
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
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY", sb_env.get("SUPABASE_ANON_KEY", ""))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
all_mp4s = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
# Only consider files that start with "reel-" and skip test files
unuploaded = []
for f in all_mp4s:
    if f not in yt_log and f.startswith("reel-") and "test-social-embed" not in f:
        full_path = os.path.join(REELS_DIR, f)
        mtime = os.path.getmtime(full_path)
        unuploaded.append((f, full_path, mtime))

# Sort by modification time, newest first
unuploaded.sort(key=lambda x: x[2], reverse=True)

if not unuploaded:
    print("✅ No new reels to upload.")
    exit(0)

print(f"Found {len(unuploaded)} unuploaded reel(s). Will upload up to 2.")
for f, _, mt in unuploaded[:5]:
    print(f"  - {f} ({datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M')})")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Fetched {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️ Failed to fetch articles: {e}")
    articles = []

def match_article(filename, articles):
    """Try to match a reel filename to an article."""
    # Strip reel- prefix and .mp4
    base = filename.replace("reel-", "", 1).replace(".mp4", "")
    # Remove trailing date pattern (YYYYMMDD)
    base = re.sub(r'-\d{8}$', '', base)
    # Extract meaningful words
    words = [w for w in base.split('-') if len(w) > 2 and w not in ('nri', 'the', 'and', 'for')]
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "") or ""
        score = sum(1 for w in words if w in slug)
        # Normalize by number of words to get percentage
        if words:
            pct = score / len(words)
        else:
            pct = 0
        if pct > best_score and pct >= 0.4 and score >= 3:
            best_score = pct
            best_match = art
    
    return best_match

def title_from_filename(filename):
    """Generate title from filename when no article match."""
    base = filename.replace("reel-", "", 1).replace(".mp4", "")
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

def generate_hashtags(category, headline):
    """Generate hashtags for YouTube Shorts."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common person/topic patterns
    headline_lower = (headline or "").lower()
    
    # Extract capitalized words that look like names/proper nouns from original headline
    if headline:
        # Find multi-word proper nouns
        proper_nouns = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline)
        for noun in proper_nouns[:5]:
            tag = '#' + noun.replace(' ', '')
            if len(tag) > 3 and tag not in topic_tags:
                topic_tags.append(tag)
    
    topic_str = ' '.join(topic_tags[:5])
    return f"{base} {cat_tags} {topic_str}".strip()

def generate_tags(category, headline):
    """Generate tags array for YouTube."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    if category:
        tags.append(category.replace('-', ' ').title())
    
    # Extract key terms from headline
    if headline:
        proper_nouns = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline)
        for noun in proper_nouns[:5]:
            if noun not in tags and len(noun) > 2:
                tags.append(noun)
    
    return tags[:12]

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
print("  ✅ YouTube API client ready")

# --- Upload loop (max 2) ---
uploaded = []
errors = []

for i, (filename, reel_path, mtime) in enumerate(unuploaded[:2]):
    print(f"\n{'='*60}")
    print(f"[{i+1}/2] Processing: {filename}")
    print(f"  File size: {os.path.getsize(reel_path) / 1024 / 1024:.1f} MB")
    
    # Match to article
    article = match_article(filename, articles)
    
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "") or ""
        slug = article.get("slug", "unknown")
        category = article.get("category", "news")
        print(f"  📰 Matched article: {headline[:80]}")
        print(f"     Slug: {slug}")
    else:
        headline = title_from_filename(filename)
        subheadline = "News for the global Indian diaspora"
        slug = "unknown"
        category = "news"
        print(f"  ⚠️ No article match, using filename: {headline}")
    
    # Compose title (under 100 chars, with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    if len(title) > 100:
        title = title[:97] + "..."
    
    # Compose description
    hashtags = generate_hashtags(category, headline)
    
    article_url = f"https://thevideshi.com/articles/{slug}" if slug != "unknown" else "https://thevideshi.com"
    
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    tags = generate_tags(category, headline)
    
    print(f"  Title: {title}")
    print(f"  Tags: {tags}")
    
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
        
        # Log
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((filename, url))
        
        # Wait between uploads
        if i < 1 and len(unuploaded) > 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((filename, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print("📊 SUMMARY")
print(f"  Uploaded: {len(uploaded)}")
for f, url in uploaded:
    print(f"    ✅ {f}")
    print(f"       → {url}")
if errors:
    print(f"  Errors: {len(errors)}")
    for f, err in errors:
        print(f"    ❌ {f}: {err}")
print(f"  Remaining unuploaded: {len(unuploaded) - len(uploaded) - len(errors)}")
