#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, sys, time, re, requests
from datetime import datetime

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_KEY', sb_env.get('SUPABASE_ANON_KEY', ''))

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

# --- Load tracking log ---
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# --- Find unuploaded reels ---
import glob
all_reels = glob.glob(os.path.join(REELS_DIR, '*.mp4'))
all_reels.sort(key=lambda x: os.path.getmtime(x), reverse=True)

# Filter: skip already uploaded, skip test reels, skip v1 if v2 exists
skip_patterns = ['test-social-embed', 'reel-v2-fixed', 'reel-v2-final']
unuploaded = []
for r in all_reels:
    fname = os.path.basename(r)
    if fname in yt_log:
        continue
    # Skip test reels
    if any(p in fname for p in skip_patterns):
        print(f"⏭️  Skipping test/misc reel: {fname}")
        # Log it so we don't keep checking
        yt_log[fname] = {"video_id": "skipped", "article_slug": "skipped", "uploaded_at": datetime.utcnow().isoformat() + "Z", "url": "skipped"}
        continue
    unuploaded.append(r)

# Skip v1 if v2 exists for same base name
v2_bases = set()
for r in unuploaded:
    fname = os.path.basename(r)
    if '-v2' in fname:
        base = fname.replace('-v2', '')
        v2_bases.add(base)

final_unuploaded = []
for r in unuploaded:
    fname = os.path.basename(r)
    if fname in v2_bases:
        print(f"⏭️  Skipping v1 (v2 exists): {fname}")
        yt_log[fname] = {"video_id": "skipped-v1-superseded", "article_slug": "skipped", "uploaded_at": datetime.utcnow().isoformat() + "Z", "url": "skipped"}
        continue
    final_unuploaded.append(r)

if not final_unuploaded:
    print("✅ No new reels to upload.")
    # Save any skip entries
    with open(LOG_PATH, 'w') as f:
        json.dump(yt_log, f, indent=2)
    sys.exit(0)

print(f"\n📹 Found {len(final_unuploaded)} unuploaded reel(s). Uploading up to 2.\n")

# --- Fetch recent articles from Supabase ---
print("📰 Fetching recent articles from Supabase...")
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Got {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️  Failed to fetch articles: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date pattern
    name = re.sub(r'-\d{8}$', '', name)
    # Remove -with-music, -v2, etc.
    name = re.sub(r'-with-music(-v\d+)?$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find matching article by slug fragment matching."""
    fragments = extract_slug_fragments(filename)
    if not fragments:
        return None

    best_match = None
    best_score = 0

    for article in articles:
        slug = article.get('slug', '') or ''
        slug_words = set(slug.lower().split('-'))
        frag_set = set(f.lower() for f in fragments)

        # Count how many fragments appear in the slug
        overlap = len(frag_set & slug_words)
        score = overlap / max(len(frag_set), 1)

        if score > best_score and score > 0.4:
            best_score = score
            best_match = article

    return best_match

def generate_hashtags(category, headline):
    """Generate hashtags based on category and headline."""
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

    cat = (category or '').lower()
    tags = base + cat_tags.get(cat, ['#IndiaNews', '#DesiNews'])

    # Extract topic-specific hashtags from headline
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '')
        if tag not in tags and len(tag) > 3:
            tags.append(tag)

    return ' '.join(tags[:20])

def generate_tags(category, headline):
    """Generate YouTube tags list."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News"]
    if category:
        tags.append(category.replace('-', ' ').title())
    tags.append("Shorts")

    # Extract key terms from headline
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or '')
    for w in words[:4]:
        if w not in tags:
            tags.append(w)

    return tags[:12]

# --- YouTube upload setup ---
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

for reel_path in final_unuploaded[:2]:
    reel_filename = os.path.basename(reel_path)
    print(f"\n{'='*60}")
    print(f"📹 Processing: {reel_filename}")

    # Match article
    article = match_article(reel_filename, articles)

    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', '')
        print(f"  📰 Matched article: {headline[:80]}")
    else:
        # Construct from filename
        fragments = extract_slug_fragments(reel_filename)
        headline = ' '.join(f.capitalize() for f in fragments)
        subheadline = ''
        slug = 'unknown'
        category = 'news'
        print(f"  ⚠️  No article match, using filename: {headline[:80]}")

    # Compose title (under 100 chars, with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + '...'
    title = f"{title} #Shorts"

    # Compose description
    hashtags = generate_hashtags(category, headline)
    article_url = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"

    description = f"""{subheadline}

📰 Full story: {article_url}

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
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)

        uploaded_count += 1

        # Wait between uploads
        if uploaded_count < 2 and len(final_unuploaded) > 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)

    except Exception as e:
        error_msg = f"❌ Failed to upload {reel_filename}: {e}"
        print(f"  {error_msg}")
        errors.append(error_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}")
print(f"  Errors: {len(errors)}")
for e in errors:
    print(f"  {e}")
