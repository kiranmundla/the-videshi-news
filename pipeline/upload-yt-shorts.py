#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, re, time, sys
from datetime import datetime
from pathlib import Path

# Load env files
def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY")

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials in .env.youtube")
    sys.exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key in .env.supabase")
    sys.exit(1)

print(f"✅ Credentials loaded")

# Load tracking log
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

if os.path.exists(LOG_PATH):
    yt_log = json.load(open(LOG_PATH))
else:
    yt_log = {}
    with open(LOG_PATH, 'w') as f:
        json.dump(yt_log, f, indent=2)

# Find unuploaded reels (skip test files like reel-v2-final, reel-v2-fixed)
SKIP_PATTERNS = ['reel-v2-final', 'reel-v2-fixed', 'reel-test', 'reel-v2-']
reel_files = []
for f in Path(REELS_DIR).glob("reel-*.mp4"):
    fname = f.name
    if fname in yt_log:
        continue
    if any(pat in fname for pat in SKIP_PATTERNS):
        print(f"⏭️  Skipping test file: {fname}")
        continue
    reel_files.append(f)

# Sort newest first
reel_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

if not reel_files:
    print("✅ No new reels to upload. All caught up!")
    sys.exit(0)

print(f"📹 Found {len(reel_files)} unuploaded reel(s)")
to_upload = reel_files[:2]

# Fetch recent articles from Supabase
import requests as req

r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"📰 Loaded {len(articles)} recent articles for matching")

# Category hashtag map
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
    """Extract meaningful words from reel filename for article matching."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date pattern
    name = re.sub(r'-\d{8}$', '', name)
    name = re.sub(r'-\d{4}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find the best matching article for a reel filename."""
    slug_words = extract_slug_words(filename)
    # Try to match on slug
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get('slug', '')
        if not slug:
            continue
        score = sum(1 for w in slug_words if w in slug)
        # Normalize by total words
        norm_score = score / max(len(slug_words), 1)
        if norm_score > best_score and norm_score > 0.4:
            best_score = norm_score
            best_match = art
    return best_match

def make_title_from_filename(filename):
    """Create a readable title from filename."""
    words = extract_slug_words(filename)
    return ' '.join(w.capitalize() for w in words[:12])

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common name patterns
    headline_words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', headline or '')
    for w in headline_words[:5]:
        tag = '#' + w.replace(' ', '')
        if len(tag) > 3 and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    topic_str = ' '.join(topic_tags[:5])
    return f"{base} {cat_tags} {topic_str}".strip()

def generate_tags(category, headline):
    """Generate 8-12 YouTube tags."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News"]
    if category:
        tags.append(category.replace('-', ' ').title())
    tags.append("Shorts")
    
    # Extract meaningful words from headline
    if headline:
        words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', headline)
        for w in words[:4]:
            if w not in tags and len(w) > 2:
                tags.append(w)
    
    return tags[:12]

# YouTube upload setup
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

for i, reel_path in enumerate(to_upload):
    fname = reel_path.name
    print(f"\n{'='*60}")
    print(f"📹 Processing {i+1}/{len(to_upload)}: {fname}")
    
    # Match article
    article = match_article(fname, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        print(f"  📰 Matched: {headline[:80]}")
    else:
        headline = make_title_from_filename(fname)
        subheadline = "News for the global Indian diaspora"
        slug = re.sub(r'^reel-', '', fname.replace('.mp4', ''))
        category = 'news'
        print(f"  ⚠️  No article match, using filename title: {headline}")
    
    # Compose title (under 100 chars with " #Shorts" = 8 chars)
    title = headline
    max_headline = 100 - len(" #Shorts")  # 92
    if len(title) > max_headline:
        title = title[:max_headline - 3].rstrip() + "..."
    title = f"{title} #Shorts"
    assert len(title) <= 100, f"Title too long: {len(title)} chars"
    
    # Compose description
    hashtags = generate_hashtags(category, headline)
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""

    tags = generate_tags(category, headline)
    
    print(f"  📝 Title: {title}")
    print(f"  🏷️  Tags: {', '.join(tags[:6])}...")
    
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
        
        media = MediaFileUpload(str(reel_path), mimetype="video/mp4", resumable=True)
        
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
        
        uploaded.append({"file": fname, "url": yt_url, "title": title})
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  ⏳ Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error uploading {fname}: {e}")
        errors.append({"file": fname, "error": str(e)})

# Summary
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {len(uploaded)}")
print(f"  Errors: {len(errors)}")
for u in uploaded:
    print(f"  ✅ {u['title'][:60]}... → {u['url']}")
for e in errors:
    print(f"  ❌ {e['file']}: {e['error']}")
