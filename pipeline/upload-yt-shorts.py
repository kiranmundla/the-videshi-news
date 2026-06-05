#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json, os, re, time, sys, requests
from datetime import datetime

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']

SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_KEY', sb_env.get('SUPABASE_ANON_KEY', sb_env.get('SUPABASE_KEY', '')))

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels/')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

# --- Load tracking log ---
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# --- Find unuploaded reels ---
import glob
files = sorted(glob.glob(os.path.join(REELS_DIR, '*.mp4')),
               key=lambda f: os.path.getmtime(f), reverse=True)

unuploaded = []
for f in files:
    fname = os.path.basename(f)
    if fname in yt_log:
        continue
    # Skip test reels
    if 'test' in fname.lower():
        print(f"⏭️  Skipping test reel: {fname}")
        continue
    unuploaded.append(f)

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

print(f"📹 Found {len(unuploaded)} unuploaded reel(s). Will upload up to 2.\n")

# --- Fetch recent articles from Supabase ---
print("📰 Fetching recent articles from Supabase...")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"   Got {len(articles)} recent articles.\n")

def extract_slug_fragments(filename):
    """Extract searchable slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date (YYYYMMDD or similar)
    name = re.sub(r'-?\d{8,14}$', '', name)
    # Strip trailing -nri
    name = re.sub(r'-nri$', '', name)
    return name

def match_article(filename, articles):
    """Find matching article by slug fragments."""
    fragments = extract_slug_fragments(filename)
    frag_words = set(fragments.split('-'))
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        slug_words = set(slug.split('-'))
        overlap = len(frag_words & slug_words)
        score = overlap / max(len(frag_words), 1)
        if score > best_score and score >= 0.4:
            best_score = score
            best_match = art
    
    return best_match

# Category hashtag map
CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'lifestyle-health': '#DesiLifestyle #Wellness #Health',
    'culture': '#DesiLifestyle #Wellness #Health',
    'markets-finance': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'economy': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'food': '#IndianFood #IndianCuisine #DesiFood',
}

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common person/entity patterns
    entities = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or '')
    for e in entities[:5]:
        tag = '#' + e.replace(' ', '')
        if len(tag) > 3 and len(tag) < 30:
            tags.append(tag)
    return tags[:5]

def compose_metadata(article, filename):
    """Compose YouTube metadata for a reel."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        tags_list = article.get('tags', []) or []
    else:
        # Construct from filename
        frags = extract_slug_fragments(filename)
        headline = ' '.join(w.capitalize() for w in frags.split('-'))
        subheadline = headline
        slug = 'unknown'
        category = 'news'
        tags_list = []
    
    # Title (under 100 chars + #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + '...'
    title = f"{title} #Shorts"
    
    # Hashtags
    base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = ' '.join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()
    
    # Description
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
    
    # Tags array
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category, "Shorts"]
    for t in tags_list[:3]:
        if isinstance(t, str) and t not in yt_tags:
            yt_tags.append(t)
    topic_entities = extract_topic_hashtags(headline)
    for te in topic_entities[:3]:
        clean = te.replace('#', '')
        if clean not in yt_tags:
            yt_tags.append(clean)
    yt_tags = yt_tags[:12]
    
    return title, description, yt_tags, slug, category

# --- Setup YouTube client ---
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

# --- Upload loop ---
uploaded_count = 0
errors = []
results = []

for reel_path in unuploaded[:2]:
    filename = os.path.basename(reel_path)
    print(f"🎬 Processing: {filename}")
    
    # Match article
    article = match_article(filename, articles)
    if article:
        print(f"   📰 Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"   ⚠️  No article match, using filename-derived metadata")
    
    # Compose metadata
    title, description, tags, slug, category = compose_metadata(article, filename)
    print(f"   📝 Title: {title}")
    
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
                print(f"   Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"   ✅ Uploaded: {url}")
        
        # Log
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((filename, url))
        
        # Wait between uploads
        if uploaded_count < 2 and len(unuploaded) > 1:
            print("   ⏳ Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Error uploading {filename}: {str(e)}"
        print(f"   ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"📊 YouTube Shorts Upload Summary")
print(f"{'='*60}")
print(f"Uploaded: {uploaded_count}")
if results:
    for fname, url in results:
        print(f"  ✅ {fname}")
        print(f"     → {url}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  ❌ {e}")
print(f"{'='*60}")
