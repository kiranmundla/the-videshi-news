#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, re, time, sys
from datetime import datetime

# Load env files
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
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY", sb_env.get("SUPABASE_KEY", ""))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels (mp4 only, not covers)
all_reels = []
for fn in os.listdir(REELS_DIR):
    if fn.endswith('.mp4') and not fn.endswith('-cover.jpg'):
        if fn not in yt_log:
            full_path = os.path.join(REELS_DIR, fn)
            mtime = os.path.getmtime(full_path)
            all_reels.append((fn, full_path, mtime))

# Sort newest first
all_reels.sort(key=lambda x: x[2], reverse=True)

print(f"Found {len(all_reels)} unuploaded reel(s)")
if not all_reels:
    print("Nothing to upload.")
    sys.exit(0)

# Limit to 2 per run
batch = all_reels[:2]

# Fetch recent articles from Supabase
import requests as req
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"Fetched {len(articles)} recent articles for matching")
except Exception as e:
    print(f"Warning: Could not fetch articles: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find matching article by slug fragments."""
    fragments = extract_slug_fragments(filename)
    frag_str = '-'.join(fragments)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        # Count matching fragments
        score = sum(1 for f in fragments if f in slug)
        # Also check if slug contains the fragment string
        if frag_str in slug:
            score += len(fragments)
        if score > best_score and score >= max(3, len(fragments) * 0.4):
            best_score = score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Construct title from filename words."""
    name = filename.replace('.mp4', '')
    if name.startswith('reel-'):
        name = name[5:]
    name = re.sub(r'-\d{8}$', '', name)
    words = name.split('-')
    return ' '.join(w.capitalize() for w in words)

CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'lifestyle-health': '#DesiLifestyle #Wellness #Health',
    'markets-finance': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'food': '#IndianFood #IndianCuisine #DesiFood',
}

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags."""
    base = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews #SouthAsian')
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or '')
    for w in words:
        tag = '#' + w.replace(' ', '')
        if tag not in base and tag not in cat_tags and len(tag) > 3:
            topic_tags.append(tag)
    
    # Also extract capitalized compound words
    for word in (headline or '').split():
        clean = re.sub(r'[^a-zA-Z0-9]', '', word)
        if len(clean) > 3 and clean[0].isupper():
            tag = '#' + clean
            if tag not in base and tag not in cat_tags and tag not in topic_tags:
                topic_tags.append(tag)
    
    topic_tags = topic_tags[:5]
    return f"{base} {cat_tags} {' '.join(topic_tags)}"

def generate_tags(category, headline):
    """Generate 8-12 YouTube tags."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    if category:
        tags.append(category.replace('-', ' ').title())
    # Extract key terms from headline
    if headline:
        words = headline.split()
        for i, w in enumerate(words):
            clean = re.sub(r'[^a-zA-Z0-9\s]', '', w)
            if len(clean) > 3 and clean[0].isupper() and clean not in tags:
                tags.append(clean)
                if len(tags) >= 12:
                    break
    return tags[:12]

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

uploaded = []
errors = []

for i, (reel_filename, reel_path, mtime) in enumerate(batch):
    print(f"\n--- Reel {i+1}/{len(batch)}: {reel_filename} ---")
    
    # Match article
    article = match_article(reel_filename, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        print(f"  Matched article: {headline[:80]}")
    else:
        headline = make_title_from_filename(reel_filename)
        subheadline = ''
        slug = ''
        category = 'news'
        print(f"  No article match, using filename title: {headline[:80]}")
    
    # Compose title (under 100 chars, with #Shorts)
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"
    
    # Compose description
    hashtags = generate_hashtags(category, headline)
    article_link = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
    
    description = f"""{subheadline}

📰 Full story: {article_link}

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
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((reel_filename, url))
        
        # Wait between uploads
        if i < len(batch) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error uploading {reel_filename}: {e}")
        errors.append((reel_filename, str(e)))

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY: {len(uploaded)} uploaded, {len(errors)} errors")
for fn, url in uploaded:
    print(f"  ✅ {fn} → {url}")
for fn, err in errors:
    print(f"  ❌ {fn}: {err}")
