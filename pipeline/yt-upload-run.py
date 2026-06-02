#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, sys, time, re, glob
from datetime import datetime

# Load env files
def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        print(f"WARNING: {p} not found")
        return env
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                env[k.strip()] = v
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env.get('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = yt_env.get('YOUTUBE_CLIENT_SECRET', '')
YOUTUBE_REFRESH_TOKEN = yt_env.get('YOUTUBE_REFRESH_TOKEN', '')
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_KEY', sb_env.get('SUPABASE_KEY', sb_env.get('SUPABASE_ANON_KEY', '')))

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("ERROR: Missing YouTube credentials")
    sys.exit(1)
if not SB_KEY:
    print("ERROR: Missing Supabase key")
    sys.exit(1)

print(f"YouTube client ID: {YOUTUBE_CLIENT_ID[:20]}...")
print(f"Supabase URL: {SUPABASE_URL}")

# Load tracking log
log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')
yt_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

# Find unuploaded reels
reels_dir = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels/')
all_reels = glob.glob(os.path.join(reels_dir, '*.mp4'))
all_reels.sort(key=lambda x: os.path.getmtime(x), reverse=True)

unuploaded = [r for r in all_reels if os.path.basename(r) not in yt_log]
print(f"\nTotal reels: {len(all_reels)}, Already uploaded: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("Nothing to upload. Done.")
    sys.exit(0)

# Limit to 2 per run
to_upload = unuploaded[:2]
print(f"Will upload {len(to_upload)} reel(s) this run.\n")

# Fetch recent articles from Supabase
import requests as req

print("Fetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"Fetched {len(articles)} recent articles.")

# Category hashtag map
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

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date pattern (YYYYMMDD or partial)
    name = re.sub(r'-?\d{6,8}$', '', name)
    # Split into words
    return name.split('-')

def match_article(filename, articles):
    """Find matching article by slug fragment matching."""
    fragments = extract_slug_fragments(filename)
    if not fragments:
        return None
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        slug_words = set(slug.lower().split('-'))
        frag_set = set(f.lower() for f in fragments)
        
        # Count overlapping words (skip very short ones)
        overlap = len([w for w in frag_set if len(w) > 2 and w in slug_words])
        if overlap > best_score:
            best_score = overlap
            best_match = art
    
    if best_score >= 3:
        return best_match
    return None

def make_title_from_filename(filename):
    """Fallback: construct title from filename."""
    fragments = extract_slug_fragments(filename)
    # Capitalize and join
    title = ' '.join(w.capitalize() for w in fragments if len(w) > 1)
    return title[:90]

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common person/entity patterns
    name_patterns = {
        'modi': '#NarendraModi', 'trump': '#Trump', 'kohli': '#ViratKohli',
        'rohit': '#RohitSharma', 'dhoni': '#MSDhoni', 'jaishankar': '#Jaishankar',
        'adani': '#Adani', 'ambani': '#Ambani', 'sundar': '#SundarPichai',
        'satya': '#SatyaNadella', 'elon': '#ElonMusk', 'zuckerberg': '#Zuckerberg',
        'shah rukh': '#ShahRukhKhan', 'aamir': '#AamirKhan', 'salman': '#SalmanKhan',
        'priyanka': '#PriyankaChopra', 'deepika': '#DeepikaPadukone',
        'mumbai': '#Mumbai', 'delhi': '#Delhi', 'bengaluru': '#Bengaluru',
        'chennai': '#Chennai', 'hyderabad': '#Hyderabad', 'kolkata': '#Kolkata',
        'infosys': '#Infosys', 'tcs': '#TCS', 'wipro': '#Wipro',
        'isro': '#ISRO', 'iit': '#IIT', 'iim': '#IIM',
        'h-1b': '#H1B', 'h1b': '#H1B', 'green card': '#GreenCard',
        'uscis': '#USCIS', 'quad': '#Quad',
        'sensex': '#Sensex', 'nifty': '#Nifty',
        'ar rahman': '#ARRahman', 'rahman': '#ARRahman',
        'naseeruddin': '#NaseeruddinShah', 'tata': '#Tata', 'jrd': '#JRDTata',
        'titan': '#Titan', 'amazon': '#Amazon', 'praggnanandhaa': '#Praggnanandhaa',
        'gukesh': '#Gukesh', 'chess': '#Chess',
    }
    
    hl = headline.lower() if headline else ''
    for pattern, tag in name_patterns.items():
        if pattern in hl and tag not in tags:
            tags.append(tag)
    
    return tags[:5]

def compose_metadata(article, filename):
    """Compose YouTube title, description, and tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news') or 'news'
        art_tags = article.get('tags', []) or []
    else:
        headline = make_title_from_filename(filename)
        subheadline = ''
        slug = ''
        category = 'news'
        art_tags = []
    
    # Title — under 100 chars with #Shorts
    title = headline[:90].strip()
    if len(title) + 8 <= 100:
        title = f"{title} #Shorts"
    
    # Description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
    
    # Build hashtags
    base_hashtags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_hashtags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_hashtags = ' '.join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_hashtags} {cat_hashtags}"
    if topic_hashtags:
        all_hashtags += f" {topic_hashtags}"
    
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags array
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    topic_tags = extract_topic_hashtags(headline)
    for t in topic_tags:
        clean = t.replace('#', '')
        if clean not in tags:
            tags.append(clean)
    # Pad to 8-12
    if len(tags) < 8:
        for extra in ["South Asian", "Desi", "Indian American", "Breaking News", "Global India"]:
            if extra not in tags:
                tags.append(extra)
            if len(tags) >= 10:
                break
    
    return title, description, tags[:12], slug

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

uploaded_count = 0
errors = []

for reel_path in to_upload:
    filename = os.path.basename(reel_path)
    print(f"Processing: {filename}")
    
    # Match article
    article = match_article(filename, articles)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"  No article match — using filename-derived title")
    
    # Compose metadata
    title, description, tags, slug = compose_metadata(article, filename)
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
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")
        
        # Log
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(log_path, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if reel_path != to_upload[-1]:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Failed to upload {filename}: {str(e)}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY: Uploaded {uploaded_count}/{len(to_upload)} reels")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"Total in YouTube log: {len(yt_log)}")
