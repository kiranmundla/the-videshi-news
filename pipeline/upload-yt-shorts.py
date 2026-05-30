#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, re, time, glob
from datetime import datetime

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
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY")

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials"); exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key"); exit(1)

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load log
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# Find unuploaded reels (mp4 only, not covers)
all_reels = sorted(
    [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4') and not f.endswith('-cover.jpg')],
    key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)),
    reverse=True
)

unuploaded = [f for f in all_reels if f not in yt_log]
print(f"📊 Total reels: {len(all_reels)}, Already uploaded: {len(all_reels) - len(unuploaded)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("✅ All reels already uploaded. Nothing to do.")
    exit(0)

# Limit to 2 per run
batch = unuploaded[:2]
print(f"📤 Will upload {len(batch)} reel(s) this run")

# Fetch recent articles from Supabase
import requests as req
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"📰 Fetched {len(articles)} recent articles for matching")
except Exception as e:
    print(f"⚠️ Failed to fetch articles: {e}")
    articles = []

# Category hashtag map
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

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date pattern like -20260530
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Match a reel filename to an article."""
    words = extract_slug_words(filename)
    slug_fragment = '-'.join(words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        if not slug:
            continue
        # Count matching words
        score = sum(1 for w in words if w in slug and len(w) > 2)
        # Bonus for consecutive word match
        if slug_fragment[:25] in slug:
            score += 10
        if score > best_score and score >= 3:
            best_score = score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Create title from filename words."""
    words = extract_slug_words(filename)
    # Capitalize each word, join
    title = ' '.join(w.capitalize() for w in words if len(w) > 1)
    return title[:90]

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common patterns
    names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', headline or '')
    for name in names[:3]:
        tag = '#' + name.replace(' ', '')
        if len(tag) < 30:
            tags.append(tag)
    return tags[:5]

# YouTube setup
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

for reel_filename in batch:
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"\n{'='*60}")
    print(f"📹 Processing: {reel_filename}")
    
    # Match article
    article = match_article(reel_filename, articles)
    
    if article:
        headline = article['headline']
        subheadline = article.get('subheadline', '')
        slug = article['slug']
        category = article.get('category', 'news')
        print(f"  📰 Matched article: {headline[:60]}...")
    else:
        headline = make_title_from_filename(reel_filename)
        subheadline = "The Videshi — News for the global Indian diaspora"
        slug = 'unknown'
        category = 'news'
        print(f"  ⚠️ No article match, using filename title: {headline}")
    
    # Build title
    title = headline[:93] + " #Shorts" if len(headline) <= 93 else headline[:89] + "... #Shorts"
    
    # Build hashtags
    base_tags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_TAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = ' '.join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()
    
    # Build description
    article_url = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Build tags list
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    topic_words = extract_topic_hashtags(headline)
    for tw in topic_words:
        tags.append(tw.replace('#', ''))
    tags = tags[:12]
    
    print(f"  📝 Title: {title}")
    print(f"  🏷️ Tags: {', '.join(tags[:6])}...")
    
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
        print(f"  ✅ Uploaded: https://youtube.com/shorts/{video_id}")
        
        # Log
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": f"https://youtube.com/shorts/{video_id}"
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if reel_filename != batch[-1]:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        error_msg = f"Failed to upload {reel_filename}: {e}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)

# Summary
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}/{len(batch)}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    - {e}")
print(f"  Total in log: {len(yt_log)}")
