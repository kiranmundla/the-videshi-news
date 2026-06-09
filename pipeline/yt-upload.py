#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, sys, time, re
from datetime import datetime
from pathlib import Path

# --- Load env files ---
def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        print(f"⚠️  Missing env file: {p}")
        return env
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN", "")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY", sb_env.get("SUPABASE_ANON_KEY", ""))

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials"); sys.exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key"); sys.exit(1)

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
SKIP_PATTERNS = ["end-card", "-assembled", "-music.mp4", "-normalized", "landscape-test", "test-social-embed"]

all_mp4s = sorted(
    [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4') and f.startswith('reel-')],
    key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)),
    reverse=True  # newest first
)

unuploaded = []
for f in all_mp4s:
    if f in yt_log:
        continue
    # Skip intermediate/build files
    if any(pat in f for pat in SKIP_PATTERNS):
        continue
    # Skip very small files (< 100KB likely broken)
    fpath = os.path.join(REELS_DIR, f)
    if os.path.getsize(fpath) < 100_000:
        continue
    unuploaded.append(f)

print(f"📊 Total reel files: {len(all_mp4s)}")
print(f"📊 Already in log: {len([f for f in all_mp4s if f in yt_log])}")
print(f"📊 Unuploaded candidates: {len(unuploaded)}")

if not unuploaded:
    print("\n✅ All reels already uploaded. Nothing to do.")
    sys.exit(0)

for f in unuploaded[:5]:
    fpath = os.path.join(REELS_DIR, f)
    sz = os.path.getsize(fpath) / 1024 / 1024
    print(f"  📹 {f} ({sz:.1f} MB)")

# --- Fetch recent articles from Supabase ---
import requests as req

print("\n🔍 Fetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"  Got {len(articles)} articles")
except Exception as e:
    print(f"  ⚠️  Supabase error: {e}")
    articles = []

def extract_slug_words(filename):
    """Extract slug-like words from reel filename."""
    name = filename.replace('.mp4', '')
    # Remove reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Remove trailing date pattern like -20260609
    name = re.sub(r'-\d{8}$', '', name)
    # Remove -n suffix (voiceover indicator)
    name = re.sub(r'-n$', '', name)
    # Remove -final, -v2 etc
    name = re.sub(r'-(final|v\d+)$', '', name)
    return set(name.split('-'))

def match_article(filename, articles):
    """Find best matching article for a reel filename."""
    words = extract_slug_words(filename)
    if len(words) < 2:
        return None
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        slug_words = set(slug.split('-'))
        overlap = len(words & slug_words)
        score = overlap / max(len(words), 1)
        if score > best_score and overlap >= 3:
            best_score = score
            best_match = art
    
    return best_match

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

def make_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common people/entities
    patterns = {
        r'modi': '#NarendraModi', r'kohli': '#ViratKohli', r'trump': '#Trump',
        r'dhoni': '#Dhoni', r'bumrah': '#JaspritBumrah', r'rohit': '#RohitSharma',
        r'ipl': '#IPL2026', r'mumbai': '#Mumbai', r'delhi': '#Delhi',
        r'bengaluru|bangalore': '#Bengaluru', r'hyderabad': '#Hyderabad',
        r'chennai': '#Chennai', r'h1b|h-1b': '#H1B', r'green.?card': '#GreenCard',
        r'bollywood': '#Bollywood', r'cricket': '#Cricket', r'sensex': '#Sensex',
        r'nifty': '#Nifty', r'rbi': '#RBI', r'supreme.?court': '#SupremeCourt',
        r'suriya': '#Suriya', r'rajini': '#Rajinikanth', r'sachin': '#SachinTendulkar',
        r'tesla': '#Tesla', r'infosys': '#Infosys', r'tata': '#Tata',
        r'adani': '#Adani', r'ambani': '#Ambani', r'cannes': '#Cannes',
        r'oscar': '#Oscars', r'netflix': '#Netflix', r'amazon': '#AmazonPrime',
        r'ott': '#OTT', r'manoj.?bajpayee': '#ManojBajpayee', r'akshay': '#AkshayKumar',
        r'ranveer': '#RanveerSingh', r'anushka': '#AnushkaSharma',
        r'nolan': '#ChristopherNolan', r'malayalam': '#Malayalam #Mollywood',
        r'tamil': '#Tamil #Kollywood', r'telugu': '#Telugu',
        r'cbse': '#CBSE', r'uscis': '#USCIS', r'tariff': '#Tariffs #Trade',
    }
    hl = headline.lower() if headline else ''
    for pat, tag in patterns.items():
        if re.search(pat, hl):
            for t in tag.split():
                if t not in tags:
                    tags.append(t)
    return tags[:5]

def title_from_filename(filename):
    """Create a readable title from filename when no article match."""
    name = filename.replace('.mp4', '').replace('reel-', '')
    name = re.sub(r'-\d{8}$', '', name)
    name = re.sub(r'-(final|v\d+|n)$', '', name)
    words = name.split('-')
    return ' '.join(w.capitalize() for w in words[:12])

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

MAX_UPLOADS = 2
uploaded_count = 0
errors = []

for reel_filename in unuploaded[:MAX_UPLOADS]:
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"\n{'='*60}")
    print(f"📹 Processing: {reel_filename}")
    
    # Match article
    article = match_article(reel_filename, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', 'unknown')
        category = article.get('category', 'news')
        print(f"  📰 Matched article: {headline[:60]}...")
    else:
        headline = title_from_filename(reel_filename)
        subheadline = "The latest from The Videshi — news for the global Indian diaspora."
        slug = 'unknown'
        category = 'news'
        print(f"  ⚠️  No article match. Using filename title: {headline}")
    
    # Compose title (max 100 chars with #Shorts)
    title = headline
    if len(title) > 91:
        title = title[:88] + "..."
    title = f"{title} #Shorts"
    
    # Hashtags
    base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = make_topic_hashtags(headline)
    all_hashtags = f"{base_tags} {cat_tags}"
    if topic_tags:
        all_hashtags += ' ' + ' '.join(topic_tags)
    
    # Description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    topic_tag_words = [t.replace('#', '') for t in topic_tags[:4]]
    tags.extend(topic_tag_words)
    tags = tags[:12]
    
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
                print(f"  ⬆️  Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")
        
        # Log
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        if uploaded_count < MAX_UPLOADS and len(unuploaded) > uploaded_count:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"❌ Error uploading {reel_filename}: {e}"
        print(err_msg)
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"📊 UPLOAD SUMMARY")
print(f"  Uploaded: {uploaded_count}/{min(MAX_UPLOADS, len(unuploaded))}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    {e}")
else:
    print(f"  Errors: 0")
print(f"  Remaining unuploaded: {max(0, len(unuploaded) - uploaded_count)}")
