#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, time, re, sys
from datetime import datetime

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
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels (skip test files like reel-v2-*)
all_reels = []
for fn in os.listdir(REELS_DIR):
    if not fn.endswith('.mp4'):
        continue
    if not fn.startswith('reel-'):
        continue
    # Skip test/dev files
    if fn.startswith('reel-v2'):
        continue
    if fn in yt_log:
        continue
    fpath = os.path.join(REELS_DIR, fn)
    mtime = os.path.getmtime(fpath)
    all_reels.append((fn, fpath, mtime))

# Sort newest first
all_reels.sort(key=lambda x: x[2], reverse=True)

if not all_reels:
    print("✅ No unuploaded reels found. All caught up!")
    sys.exit(0)

# Limit to 2 per run
to_upload = all_reels[:2]
print(f"Found {len(all_reels)} unuploaded reel(s). Uploading {len(to_upload)}.")

# Fetch recent articles from Supabase
import requests as req

r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"Fetched {len(articles)} recent articles for matching.")

def extract_slug_fragments(filename):
    """Strip reel- prefix and trailing date + .mp4 to get slug fragments."""
    name = filename.replace('.mp4', '')
    if name.startswith('reel-'):
        name = name[5:]
    # Remove trailing date pattern like -20260528
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find best matching article by slug fragment overlap."""
    fragments = extract_slug_fragments(filename)
    frag_str = '-'.join(fragments)
    
    best_match = None
    best_score = 0
    
    for a in articles:
        slug = a.get('slug', '')
        if not slug:
            continue
        # Check how many fragments appear in the slug
        score = sum(1 for f in fragments if f in slug)
        # Bonus for substring match
        if frag_str in slug or slug in frag_str:
            score += len(fragments)
        if score > best_score and score >= max(2, len(fragments) * 0.4):
            best_score = score
            best_match = a
    
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
    """Extract 3-5 topic hashtags from headline."""
    tags = []
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline)
    # Look for proper nouns / entities
    for w in words:
        clean = w.replace(' ', '')
        if len(clean) > 3 and clean not in ('The', 'This', 'That', 'With', 'From', 'What', 'When', 'Where', 'Will', 'Could', 'Would', 'Should', 'Have', 'Does', 'After', 'Before', 'About', 'Into', 'Over', 'Under', 'More', 'Most', 'Than', 'Then', 'Just', 'Also', 'Still', 'Back', 'Even', 'Every', 'Here', 'Much', 'Many', 'Some', 'Only', 'Other', 'Through', 'Between', 'Within', 'Without', 'During', 'Behind', 'Beyond', 'Around'):
            tags.append(f'#{clean}')
    return ' '.join(tags[:5])

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        # Construct from filename
        frags = extract_slug_fragments(filename)
        headline = ' '.join(w.capitalize() for w in frags)
        subheadline = ''
        slug = '-'.join(frags)
        category = 'news'
        art_tags = []
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = make_topic_hashtags(headline)
    
    hashtag_block = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_tags}"
    
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtag_block}"""

    # Tags list
    tags_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category or "News", "Shorts"]
    # Add topic tags from article
    if art_tags and isinstance(art_tags, list):
        for t in art_tags[:4]:
            if t not in tags_list:
                tags_list.append(t)
    # Pad to 8-12
    for w in extract_slug_fragments(filename)[:3]:
        cap = w.capitalize()
        if cap not in tags_list and len(cap) > 3:
            tags_list.append(cap)
    tags_list = tags_list[:12]
    
    return title, description, tags_list, slug

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

for i, (fn, fpath, mtime) in enumerate(to_upload):
    print(f"\n--- Reel {i+1}/{len(to_upload)}: {fn}")
    
    # Match article
    article = match_article(fn, articles)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"  No article match found, constructing from filename")
    
    title, description, tags, slug = compose_metadata(article, fn)
    print(f"  Title: {title}")
    
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
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")
        
        # Log
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        if i < len(to_upload) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Error uploading {fn}: {e}")
        errors.append((fn, str(e)))

print(f"\n{'='*50}")
print(f"Summary: {uploaded_count}/{len(to_upload)} uploaded successfully")
if errors:
    print(f"Errors: {len(errors)}")
    for fn, err in errors:
        print(f"  - {fn}: {err}")
