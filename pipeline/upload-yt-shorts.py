#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, re, time, sys
from datetime import datetime, timezone

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
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

# Load tracking log
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# Find unuploaded reels sorted newest first
all_reels = []
for fname in os.listdir(REELS_DIR):
    if fname.endswith('.mp4') and fname.startswith('reel-'):
        if fname not in yt_log:
            fpath = os.path.join(REELS_DIR, fname)
            mtime = os.path.getmtime(fpath)
            all_reels.append((mtime, fname, fpath))

all_reels.sort(reverse=True)  # newest first
to_upload = all_reels[:2]

if not to_upload:
    print("✅ No unuploaded reels found. Nothing to do.")
    sys.exit(0)

print(f"Found {len(all_reels)} unuploaded reels. Will upload {len(to_upload)}:")
for _, fn, _ in to_upload:
    print(f"  - {fn}")

# Fetch recent articles from Supabase
import requests as req_lib

print("\nFetching recent articles from Supabase...")
r = req_lib.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"  Got {len(articles)} recent articles")

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date like -20260527
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find matching article by fuzzy slug match."""
    fragments = extract_slug_fragments(filename)
    frag_str = '-'.join(fragments)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        # Count how many fragments appear in the slug
        score = sum(1 for f in fragments if f in slug)
        # Require at least 3 matching fragments or 60% match
        threshold = max(3, len(fragments) * 0.5)
        if score >= threshold and score > best_score:
            best_score = score
            best_match = art
    
    return best_match

def get_category_hashtags(category):
    """Get category-specific hashtags."""
    cat_map = {
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
    return cat_map.get(category, '#IndiaNews #DesiNews')

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common person/entity patterns
    known = {
        'modi': '#NarendraModi', 'trump': '#Trump', 'kohli': '#ViratKohli',
        'dhoni': '#MSDhoni', 'bumrah': '#JaspritBumrah', 'rohit': '#RohitSharma',
        'jaishankar': '#Jaishankar', 'mamata': '#MamataBanerjee', 'bjp': '#BJP',
        'congress': '#Congress', 'h1b': '#H1B', 'ipl': '#IPL2026',
        'sensex': '#Sensex', 'nifty': '#Nifty', 'cci': '#CCI',
        'amazon': '#Amazon', 'netflix': '#Netflix', 'bollywood': '#Bollywood',
        'ebola': '#Ebola', 'who': '#WHO', 'oil': '#OilCrisis',
        'hormuz': '#StraitOfHormuz', 'bengal': '#WestBengal', 'carney': '#MarkCarney',
        'canada': '#Canada', 'gcc': '#GCC', 'dharma': '#DharmaProductions',
        'ananya': '#AnanyaPanday', 'supreme court': '#SupremeCourt',
        'petrol': '#PetrolPrice', 'monsoon': '#Monsoon', 'cricket': '#Cricket',
        'venezuela': '#Venezuela', 'africa': '#Africa', 'uae': '#UAE',
        'visa': '#Visa', 'uscis': '#USCIS',
    }
    hl = headline.lower() if headline else ''
    for word, tag in known.items():
        if word in hl:
            tags.append(tag)
    return tags[:5]

def make_title_from_filename(filename):
    """Construct title from filename words."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    name = re.sub(r'-\d{8}$', '', name)
    words = name.split('-')
    return ' '.join(w.capitalize() for w in words)

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

for idx, (mtime, reel_filename, reel_path) in enumerate(to_upload):
    print(f"\n{'='*60}")
    print(f"[{idx+1}/{len(to_upload)}] Processing: {reel_filename}")
    
    # Match article
    article = match_article(reel_filename, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        print(f"  Matched article: {headline[:80]}...")
        print(f"  Category: {category}")
    else:
        headline = make_title_from_filename(reel_filename)
        subheadline = ''
        slug = re.sub(r'^reel-', '', reel_filename.replace('.mp4', ''))
        category = 'news'
        print(f"  No article match. Using filename title: {headline}")
    
    # Compose title (under 100 chars with #Shorts)
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"
    
    # Compose hashtags
    base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = get_category_hashtags(category)
    topic_tags = extract_topic_hashtags(headline)
    topic_tags_str = ' '.join(topic_tags)
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags_str}".strip()
    
    # Compose description
    desc_parts = []
    if subheadline:
        desc_parts.append(subheadline)
    desc_parts.append('')
    desc_parts.append(f'📰 Full story: https://thevideshi.com/articles/{slug}')
    desc_parts.append('')
    desc_parts.append('The Videshi — News for the global Indian diaspora')
    desc_parts.append('🌐 thevideshi.com')
    desc_parts.append('')
    desc_parts.append('Follow us:')
    desc_parts.append('📸 Instagram: https://instagram.com/the.videshi')
    desc_parts.append('🐦 X/Twitter: https://x.com/thevideshi')
    desc_parts.append('🧵 Threads: https://threads.net/@the.videshi')
    desc_parts.append('')
    desc_parts.append(all_hashtags)
    description = '\n'.join(desc_parts)
    
    # Tags
    tags_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category, "Shorts"]
    # Add topic-specific tags
    for t in topic_tags:
        tag_clean = t.replace('#', '')
        if tag_clean not in tags_list:
            tags_list.append(tag_clean)
    tags_list = tags_list[:12]
    
    print(f"  Title: {title}")
    print(f"  Tags: {tags_list}")
    
    # Upload
    try:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags_list,
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
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": yt_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if idx < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        err_msg = f"Error uploading {reel_filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  Uploaded: {uploaded_count}/{len(to_upload)}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    - {e}")
print(f"  Remaining unuploaded: {len(all_reels) - uploaded_count}")
