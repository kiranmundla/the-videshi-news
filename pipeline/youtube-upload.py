#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env files ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY", sb_env.get("SUPABASE_KEY", ""))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
reel_files = sorted(
    [f for f in os.listdir(REELS_DIR) if f.endswith(".mp4")],
    key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)),
    reverse=True
)

unuploaded = [f for f in reel_files if f not in yt_log]
print(f"Total reels: {len(reel_files)}, Already uploaded: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("Nothing to upload.")
    exit(0)

# Skip test reels
unuploaded = [f for f in unuploaded if "test" not in f.lower()]
if not unuploaded:
    print("Only test reels remain unuploaded. Skipping.")
    exit(0)

# Limit to 2 per run
batch = unuploaded[:2]
print(f"Will upload {len(batch)} reel(s): {batch}")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"Fetched {len(articles)} articles")

# --- Category hashtag map ---
CATEGORY_HASHTAGS = {
    "news": "#IndiaNews #BreakingNews #DesiNews #SouthAsian",
    "entertainment": "#Bollywood #BollywoodNews #IndianCinema #Tollywood",
    "sports": "#Cricket #IPL #IPL2026 #TeamIndia #BCCI",
    "technology": "#TechNews #IndianTech #SiliconValley #AI",
    "culture": "#DesiLifestyle #Wellness #Health",
    "economy": "#StockMarket #Nifty #Sensex #IndianMarkets",
    "immigration": "#H1B #H1BVisa #GreenCard #USImmigration #USCIS",
    "nri-world": "#NRILife #DesiAbroad #IndianAmerican",
    "travel": "#TravelIndia #IncredibleIndia #IndiaTravel",
    "food": "#IndianFood #IndianCuisine #DesiFood",
}

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date pattern (YYYYMMDD or similar)
    name = re.sub(r'-?\d{8,}$', '', name)
    return name.split("-")

def match_article(filename, articles):
    """Find matching article by slug fragment matching."""
    slug_words = extract_slug_words(filename)
    slug_text = "-".join(slug_words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Count how many slug words appear in the article slug
        score = sum(1 for w in slug_words if w in slug and len(w) > 2)
        # Bonus for consecutive matches
        if slug_text in slug:
            score += 10
        if score > best_score:
            best_score = score
            best_match = art
    
    if best_score >= 3:
        return best_match
    return None

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags based on category and headline."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common patterns for person names and entities
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', headline or "")
    for w in words[:5]:
        tag = "#" + w.replace(" ", "")
        if len(tag) > 3 and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    all_tags = f"{base} {cat_tags}"
    if topic_tags:
        all_tags += " " + " ".join(topic_tags[:5])
    
    return all_tags

def make_title(headline):
    """Create YouTube title under 100 chars with #Shorts."""
    suffix = " #Shorts"
    max_len = 100 - len(suffix)
    if len(headline) <= max_len:
        return headline + suffix
    # Truncate at word boundary
    truncated = headline[:max_len].rsplit(" ", 1)[0]
    return truncated + suffix

def make_tags(category, headline):
    """Generate 8-12 tags."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    if category:
        cat_name = category.replace("-", " ").title()
        tags.append(cat_name)
    # Extract names/topics from headline
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', headline or "")
    for w in words[:4]:
        if w not in tags and len(w) > 2:
            tags.append(w)
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
print("YouTube client ready")

# --- Upload loop ---
uploaded_count = 0
errors = []
results = []

for i, reel_filename in enumerate(batch):
    print(f"\n{'='*60}")
    print(f"Processing {i+1}/{len(batch)}: {reel_filename}")
    reel_path = os.path.join(REELS_DIR, reel_filename)
    
    # Match article
    article = match_article(reel_filename, articles)
    
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "news")
        print(f"  Matched article: {headline[:80]}...")
        print(f"  Category: {category}, Slug: {slug[:60]}")
    else:
        # Construct from filename
        slug_words = extract_slug_words(reel_filename)
        headline = " ".join(w.capitalize() for w in slug_words)
        subheadline = headline
        slug = "-".join(slug_words)
        category = "news"
        print(f"  No article match. Constructed title: {headline[:80]}")
    
    # Compose metadata
    title = make_title(headline)
    hashtags = generate_hashtags(category, headline)
    tags = make_tags(category, headline)
    
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
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
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append({"filename": reel_filename, "url": url, "title": title})
        
        # Wait between uploads
        if i < len(batch) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        err_msg = f"Error uploading {reel_filename}: {str(e)}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: Uploaded {uploaded_count}/{len(batch)} reels")
for r in results:
    print(f"  ✅ {r['title'][:70]}... → {r['url']}")
if errors:
    print(f"  ❌ Errors: {len(errors)}")
    for e in errors:
        print(f"    {e}")
