#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, re, time, sys
from datetime import datetime, timezone

# --- Load env files ---
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
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# Skip test/intermediate files
SKIP_PATTERNS = {"reel-v2-final.mp4", "reel-v2-fixed.mp4"}

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
reel_files = []
for fname in os.listdir(REELS_DIR):
    if not fname.endswith('.mp4'):
        continue
    if fname in SKIP_PATTERNS:
        continue
    if fname in yt_log:
        continue
    full = os.path.join(REELS_DIR, fname)
    mtime = os.path.getmtime(full)
    reel_files.append((fname, full, mtime))

# Sort newest first
reel_files.sort(key=lambda x: x[2], reverse=True)

if not reel_files:
    print("✅ No unuploaded reels found. All caught up!")
    sys.exit(0)

print(f"Found {len(reel_files)} unuploaded reel(s). Will upload up to {MAX_UPLOADS}.")
for f, _, _ in reel_files[:MAX_UPLOADS]:
    print(f"  → {f}")

# --- Fetch recent articles from Supabase ---
import requests as req

print("\nFetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"  Got {len(articles)} recent articles")

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
    """Find matching article for a reel filename."""
    frags = extract_slug_fragments(filename)
    frag_str = '-'.join(frags)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        # Direct containment check
        if frag_str in slug or slug.startswith(frag_str):
            return art
        # Word overlap
        slug_words = set(slug.split('-'))
        frag_words = set(frags)
        overlap = len(slug_words & frag_words)
        if overlap > best_score and overlap >= max(3, len(frag_words) * 0.5):
            best_score = overlap
            best_match = art
    
    return best_match

def get_category(article, filename):
    """Determine category from article or filename."""
    if article and article.get('category'):
        return article['category']
    lower = filename.lower()
    if any(w in lower for w in ['h1b', 'visa', 'green-card', 'immigration', 'uscis']):
        return 'immigration'
    if any(w in lower for w in ['cricket', 'ipl', 'bcci', 'kohli']):
        return 'sports'
    if any(w in lower for w in ['bollywood', 'netflix', 'movie', 'box-office']):
        return 'entertainment'
    if any(w in lower for w in ['market', 'sensex', 'nifty', 'stock', 'inflation', 'fed', 'pce', 'divestment']):
        return 'markets-finance'
    if any(w in lower for w in ['tech', 'ai', 'silicon']):
        return 'technology'
    return 'news'

def build_hashtags(category, headline):
    """Build 15-20 hashtags."""
    base = ['#TheVideshi', '#Shorts', '#IndianDiaspora', '#NRI']
    
    cat_tags = {
        'news': ['#IndiaNews', '#BreakingNews', '#DesiNews', '#SouthAsian'],
        'immigration': ['#H1B', '#H1BVisa', '#GreenCard', '#USImmigration', '#USCIS'],
        'nri-world': ['#NRILife', '#DesiAbroad', '#IndianAmerican'],
        'travel': ['#TravelIndia', '#IncredibleIndia', '#IndiaTravel'],
        'lifestyle-health': ['#DesiLifestyle', '#Wellness', '#Health'],
        'markets-finance': ['#StockMarket', '#Nifty', '#Sensex', '#IndianMarkets'],
        'technology': ['#TechNews', '#IndianTech', '#SiliconValley', '#AI'],
        'sports': ['#Cricket', '#IPL', '#IPL2026', '#TeamIndia', '#BCCI'],
        'entertainment': ['#Bollywood', '#BollywoodNews', '#IndianCinema', '#Tollywood'],
        'food': ['#IndianFood', '#IndianCuisine', '#DesiFood'],
    }
    
    tags = base + cat_tags.get(category, ['#IndiaNews', '#DesiNews'])
    
    # Extract topic hashtags from headline
    if headline:
        # Common name/entity patterns
        words = headline.split()
        for i, w in enumerate(words):
            clean = re.sub(r'[^a-zA-Z0-9]', '', w)
            if clean and clean[0].isupper() and len(clean) > 3:
                # Check if it's a proper noun (capitalized, not first word of sentence)
                if i > 0 or len(clean) > 5:
                    tag = f"#{clean}"
                    if tag not in tags and len(tags) < 20:
                        tags.append(tag)
        
        # Special keyword extraction
        hl = headline.lower()
        keyword_map = {
            'modi': '#NarendraModi', 'kohli': '#ViratKohli', 'trump': '#Trump',
            'bjp': '#BJP', 'congress': '#Congress', 'rbi': '#RBI',
            'ipl': '#IPL2026', 'mumbai': '#Mumbai', 'delhi': '#Delhi',
            'infosys': '#Infosys', 'tcs': '#TCS', 'wipro': '#Wipro',
            'iran': '#Iran', 'pakistan': '#Pakistan', 'china': '#China',
            'canada': '#Canada', 'uk': '#UK', 'usa': '#USA',
            'pce': '#PCEInflation', 'inflation': '#Inflation', 'fed': '#FederalReserve',
            'coal india': '#CoalIndia', 'oil': '#OilPrices',
        }
        for kw, tag in keyword_map.items():
            if kw in hl and tag not in tags and len(tags) < 20:
                tags.append(tag)
    
    return tags[:20]

def build_tags_list(category, headline):
    """Build 8-12 YouTube tags."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    
    if headline:
        # Extract key entities
        words = headline.split()
        for w in words:
            clean = re.sub(r'[^a-zA-Z0-9\s]', '', w).strip()
            if clean and len(clean) > 3 and clean[0].isupper() and clean not in tags:
                tags.append(clean)
                if len(tags) >= 12:
                    break
    
    return tags[:12]

# --- YouTube upload ---
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("\nAuthenticating with YouTube...")
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

for i, (fname, fpath, mtime) in enumerate(reel_files[:MAX_UPLOADS]):
    print(f"\n{'='*60}")
    print(f"Processing [{i+1}/{min(len(reel_files), MAX_UPLOADS)}]: {fname}")
    
    # Match article
    article = match_article(fname, articles)
    category = get_category(article, fname)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', 'unknown')
        print(f"  Matched article: {headline[:80]}")
    else:
        # Construct from filename
        frags = extract_slug_fragments(fname)
        headline = ' '.join(w.capitalize() for w in frags)
        subheadline = f"Latest {category.replace('-', ' ').title()} update for the Indian diaspora"
        slug = 'unknown'
        print(f"  No article match, using constructed title: {headline[:80]}")
    
    # Build metadata
    title = headline[:93] + " #Shorts" if len(headline) <= 93 else headline[:89] + "... #Shorts"
    
    hashtags = build_hashtags(category, headline)
    hashtag_str = ' '.join(hashtags)
    
    article_url = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"
    
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtag_str}"""
    
    tags = build_tags_list(category, headline)
    
    print(f"  Title: {title}")
    print(f"  Category: {category}")
    print(f"  Tags: {', '.join(tags[:5])}...")
    
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
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")
        
        # Log
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((fname, url))
        
        # Wait between uploads
        if i < min(len(reel_files), MAX_UPLOADS) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append((fname, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {len(uploaded)}")
for fname, url in uploaded:
    print(f"  ✅ {fname}")
    print(f"     → {url}")
if errors:
    print(f"Errors: {len(errors)}")
    for fname, err in errors:
        print(f"  ❌ {fname}: {err}")
if not uploaded and not errors:
    print("  Nothing to upload.")
