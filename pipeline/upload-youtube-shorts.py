#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts."""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
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
MAX_UPLOADS = 2

# Skip test/dev files
SKIP_PATTERNS = {"reel-v2-final.mp4", "reel-v2-fixed.mp4", "reel-test.mp4"}

# --- Load log ---
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
    if fname in SKIP_PATTERNS:
        continue
    # Skip files that don't follow naming convention (reel-<slug>-<date>.mp4)
    if not re.match(r'^reel-.+\d{8}\.mp4$', fname):
        print(f"  ⏭️  Skipping non-standard filename: {fname}")
        continue
    if fname in yt_log:
        continue
    full_path = os.path.join(REELS_DIR, fname)
    mtime = os.path.getmtime(full_path)
    reel_files.append((fname, full_path, mtime))

# Sort newest first
reel_files.sort(key=lambda x: x[2], reverse=True)

print(f"Found {len(reel_files)} unuploaded reel(s)")
if not reel_files:
    print("Nothing to upload. Done.")
    sys.exit(0)

# --- Fetch recent articles from Supabase ---
print("Fetching recent articles from Supabase...")
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    r.raise_for_status()
    articles = r.json()
    print(f"  Loaded {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️  Failed to fetch articles: {e}")
    articles = []

# --- Category hashtags ---
CATEGORY_HASHTAGS = {
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

BASE_HASHTAGS = ["#TheVideshi", "#Shorts", "#IndianDiaspora", "#NRI"]

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace(".mp4", "")
    # Remove reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Remove trailing date (8 digits)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find matching article by slug fragments."""
    slug_words = extract_slug_words(filename)
    slug_fragment = '-'.join(slug_words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Check how many words from reel filename appear in article slug
        score = sum(1 for w in slug_words if w in slug)
        # Require at least 3 matching words or 60% match
        threshold = max(3, int(len(slug_words) * 0.6))
        if score >= threshold and score > best_score:
            best_score = score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Fallback: construct title from filename words."""
    words = extract_slug_words(filename)
    # Capitalize each word, join
    skip = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are'}
    titled = []
    for i, w in enumerate(words):
        if i == 0 or w not in skip:
            titled.append(w.capitalize())
        else:
            titled.append(w)
    return ' '.join(titled)

def extract_topic_hashtags(headline):
    """Extract person/place/topic hashtags from headline."""
    tags = []
    # Common patterns - capitalize words that look like proper nouns
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', headline or "")
    seen = set()
    for w in words:
        tag = '#' + w.replace(' ', '')
        if tag not in seen and len(tag) > 3:
            seen.add(tag)
            tags.append(tag)
            if len(tags) >= 5:
                break
    return tags

def build_description(article, category):
    """Build YouTube description."""
    subheadline = (article or {}).get("subheadline", "")
    slug = (article or {}).get("slug", "")
    headline = (article or {}).get("headline", "")
    
    cat_hashtags = CATEGORY_HASHTAGS.get(category, ["#IndiaNews"])
    topic_hashtags = extract_topic_hashtags(headline)
    all_hashtags = BASE_HASHTAGS + cat_hashtags + topic_hashtags
    # Deduplicate while preserving order
    seen = set()
    unique_hashtags = []
    for h in all_hashtags:
        hl = h.lower()
        if hl not in seen:
            seen.add(hl)
            unique_hashtags.append(h)
    
    hashtag_str = ' '.join(unique_hashtags[:20])
    
    article_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}" if slug else ""
    
    desc = f"""{subheadline}
{article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtag_str}"""
    
    return desc.strip()

def build_tags(article, category):
    """Build YouTube tags list."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News"]
    if category:
        tags.append(category.replace('-', ' ').title())
    tags.append("Shorts")
    
    headline = (article or {}).get("headline", "")
    # Extract proper nouns for tags
    proper = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', headline)
    for p in proper[:4]:
        if p not in tags and len(p) > 2:
            tags.append(p)
    
    return tags[:12]

# --- Build YouTube client ---
print("Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ Authenticated")

# --- Upload loop ---
uploaded = []
errors = []

for i, (fname, fpath, mtime) in enumerate(reel_files[:MAX_UPLOADS]):
    print(f"\n--- Uploading {i+1}/{min(len(reel_files), MAX_UPLOADS)}: {fname} ---")
    
    # Match article
    article = match_article(fname, articles)
    if article:
        headline = article["headline"]
        slug = article["slug"]
        category = article.get("category", "news")
        print(f"  📰 Matched article: {headline[:80]}")
    else:
        headline = make_title_from_filename(fname)
        slug = None
        category = "news"
        print(f"  ⚠️  No article match, using filename title: {headline}")
    
    # Compose metadata
    title = headline[:93] + " #Shorts" if len(headline) <= 93 else headline[:90] + "... #Shorts"
    description = build_description(article, category)
    tags = build_tags(article, category)
    
    print(f"  📌 Title: {title}")
    print(f"  🏷️  Tags: {', '.join(tags[:5])}...")
    
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
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((fname, url))
        
        # Wait between uploads
        if i < min(len(reel_files), MAX_UPLOADS) - 1:
            print("  ⏳ Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((fname, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {len(uploaded)}")
for fname, url in uploaded:
    print(f"  ✅ {fname} → {url}")
if errors:
    print(f"Errors: {len(errors)}")
    for fname, err in errors:
        print(f"  ❌ {fname}: {err}")
print(f"Remaining unuploaded: {max(0, len(reel_files) - MAX_UPLOADS)}")
