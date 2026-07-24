#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, sys, time, re
from datetime import datetime
from pathlib import Path

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            env[k.strip()] = v
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

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels (skip intermediate/assembled/test files)
SKIP_PATTERNS = ['-assembled', '-test-', 'test-social-embed']
all_reels = []
for fname in os.listdir(REELS_DIR):
    if not fname.endswith('.mp4'):
        continue
    if fname in yt_log:
        continue
    if any(p in fname for p in SKIP_PATTERNS):
        print(f"  ⏭️  Skipping intermediate file: {fname}")
        # Mark as skipped in log so we don't revisit
        yt_log[fname] = {
            "video_id": "skipped-intermediate",
            "article_slug": "skipped",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": "skipped"
        }
        continue
    fpath = os.path.join(REELS_DIR, fname)
    mtime = os.path.getmtime(fpath)
    all_reels.append((fname, fpath, mtime))

# Sort newest first
all_reels.sort(key=lambda x: x[2], reverse=True)

print(f"\n📊 Found {len(all_reels)} unuploaded reels")
for r in all_reels:
    print(f"  - {r[0]}")

if not all_reels:
    print("\n✅ No new reels to upload.")
    # Save any skip entries
    with open(LOG_PATH, 'w') as f:
        json.dump(yt_log, f, indent=2)
    sys.exit(0)

# Limit to 2 per run
to_upload = all_reels[:2]
print(f"\n🚀 Will upload {len(to_upload)} reels this run")

# Fetch recent articles from Supabase for matching
import requests as req

print("\n📰 Fetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Got {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️ Could not fetch articles: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date pattern (YYYYMMDD)
    name = re.sub(r'-?\d{8}$', '', name)
    # Remove -final, -v2, etc.
    name = re.sub(r'-(final|v\d+)$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find best matching article for a reel filename."""
    fragments = extract_slug_fragments(filename)
    if not fragments:
        return None
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        slug_words = set(slug.lower().split('-'))
        frag_set = set(f.lower() for f in fragments)
        
        # Count overlapping words (exclude very short/common words)
        overlap = slug_words & frag_set
        overlap = {w for w in overlap if len(w) > 2}
        
        score = len(overlap)
        if score > best_score and score >= 3:
            best_score = score
            best_match = art
    
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
    
    # Extract topic hashtags from headline
    if headline:
        # Common names/entities to hashtagify
        words = headline.split()
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-zA-Z0-9]', '', word)
            if len(clean) > 3 and clean[0].isupper():
                # Check multi-word names
                if i + 1 < len(words):
                    next_clean = re.sub(r'[^a-zA-Z0-9]', '', words[i+1])
                    if next_clean and next_clean[0].isupper() and len(next_clean) > 2:
                        combined = f"#{clean}{next_clean}"
                        if combined not in tags and len(tags) < 20:
                            tags.append(combined)
                            continue
                tag = f"#{clean}"
                if tag not in tags and len(tags) < 20:
                    tags.append(tag)
    
    return tags[:20]

# Setup YouTube API
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

for i, (fname, fpath, mtime) in enumerate(to_upload):
    print(f"\n{'='*60}")
    print(f"📹 [{i+1}/{len(to_upload)}] Processing: {fname}")
    
    # Match article
    article = match_article(fname, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        print(f"  📰 Matched article: {headline[:80]}")
    else:
        # Construct from filename
        fragments = extract_slug_fragments(fname)
        headline = ' '.join(f.capitalize() for f in fragments)
        subheadline = f"Latest update from The Videshi"
        slug = '-'.join(fragments)
        category = 'news'
        print(f"  ⚠️ No article match, using filename: {headline[:80]}")
    
    # Compose title (under 100 chars with #Shorts)
    title = headline
    if len(title) > 91:  # Leave room for " #Shorts"
        title = title[:88] + "..."
    title = f"{title} #Shorts"
    
    # Generate hashtags
    hashtags = generate_hashtags(category, headline)
    hashtag_str = ' '.join(hashtags)
    
    # Compose description
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtag_str}"""
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic words from headline
    for word in headline.split():
        clean = re.sub(r'[^a-zA-Z0-9]', '', word)
        if len(clean) > 3 and clean[0].isupper() and clean not in tags:
            tags.append(clean)
            if len(tags) >= 12:
                break
    
    print(f"  📝 Title: {title}")
    print(f"  🏷️ Tags: {tags}")
    
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
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")
        
        # Log
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        error_msg = f"Failed to upload {fname}: {e}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)

# Summary
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}/{len(to_upload)}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    - {e}")
print(f"  Remaining unuploaded: {len(all_reels) - len(to_upload)}")
