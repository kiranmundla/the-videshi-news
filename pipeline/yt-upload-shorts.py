#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, re, sys, time
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Load env ──────────────────────────────────────────────────────────────────
def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env(os.path.expanduser('~/workspace/.env.youtube'))
sb_env = load_env(os.path.expanduser('~/workspace/.env.supabase'))

YOUTUBE_CLIENT_ID = yt_env.get('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = yt_env.get('YOUTUBE_CLIENT_SECRET', '')
YOUTUBE_REFRESH_TOKEN = yt_env.get('YOUTUBE_REFRESH_TOKEN', '')
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_ROLE_KEY', sb_env.get('SUPABASE_ANON_KEY', ''))

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials in ~/.env.youtube")
    sys.exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key in ~/.env.supabase")
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────────────────────────────
REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

# ── Load tracking log ─────────────────────────────────────────────────────────
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# ── Find unuploaded reels (skip test files) ───────────────────────────────────
all_reels = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
unuploaded = [f for f in all_reels if f not in yt_log and 'test' not in f.lower()]
unuploaded.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

# Limit to 2 per run
batch = unuploaded[:2]
print(f"📹 Found {len(unuploaded)} unuploaded reel(s). Uploading {len(batch)} this run.\n")

# ── Fetch recent articles from Supabase ───────────────────────────────────────
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
except Exception as e:
    print(f"⚠️ Could not fetch articles: {e}")
    articles = []

# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_slug_words(filename):
    """Strip reel- prefix and trailing date + .mp4 to get slug fragments."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date patterns like -20260607 or -202606040953
    name = re.sub(r'-?\d{8,}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find best matching article by slug word overlap."""
    words = extract_slug_words(filename)
    if not words:
        return None
    best, best_score = None, 0
    for art in articles:
        slug = art.get('slug', '')
        slug_words = set(slug.split('-'))
        # Count overlapping words (excluding very short/common ones)
        overlap = sum(1 for w in words if len(w) > 2 and w in slug_words)
        if overlap > best_score:
            best_score = overlap
            best = art
    return best if best_score >= 3 else None

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
    """Extract 3-5 topic hashtags from headline words."""
    # Remove common stopwords and short words
    stops = {'the','a','an','in','on','at','to','for','of','and','is','are','was','by','with','from','has','have','its','over','after','new','how','why','what'}
    words = re.findall(r'[A-Z][a-z]+(?:[A-Z][a-z]+)*|[A-Z]{2,}', headline)
    tags = []
    for w in words:
        if w.lower() not in stops and len(w) > 2:
            tags.append(f'#{w.replace(" ", "")}')
            if len(tags) >= 5:
                break
    return ' '.join(tags)

def compose_metadata(article, filename):
    """Compose title, description, tags for YouTube upload."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', 'unknown')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        # Fallback: construct from filename
        words = extract_slug_words(filename)
        headline = ' '.join(w.capitalize() for w in words)
        subheadline = ''
        slug = 'unknown'
        category = 'news'
        art_tags = []

    # Title: under 100 chars + #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"

    # Hashtags
    base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = make_topic_hashtags(headline)
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}"

    # Description
    article_url = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else 'https://thevideshi.com'
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    # Tags list
    tag_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic words from headline
    headline_words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline)
    for w in headline_words[:4]:
        if w not in tag_list and len(w) > 2:
            tag_list.append(w)
    # Cap at 12
    tag_list = tag_list[:12]

    return title, description, tag_list, slug

# ── YouTube client ────────────────────────────────────────────────────────────
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)

# ── Upload loop ───────────────────────────────────────────────────────────────
uploaded_count = 0
errors = []
results = []

for i, reel_filename in enumerate(batch):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"[{i+1}/{len(batch)}] {reel_filename}")

    # Match article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  📝 Matched: {article['headline'][:80]}")
    else:
        print(f"  ⚠️ No article match — using filename-derived title")

    title, description, tags, slug = compose_metadata(article, reel_filename)
    print(f"  🏷️ Title: {title}")

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

    try:
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
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)

        uploaded_count += 1
        results.append((reel_filename, url))

    except Exception as e:
        err_msg = str(e)
        print(f"  ❌ Error: {err_msg}")
        errors.append((reel_filename, err_msg))

    # Wait between uploads
    if i < len(batch) - 1:
        print("  ⏳ Waiting 10s...")
        time.sleep(10)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"📊 Upload Summary")
print(f"  Uploaded: {uploaded_count}/{len(batch)}")
for fn, url in results:
    print(f"    ✅ {fn}")
    print(f"       → {url}")
if errors:
    print(f"  Errors: {len(errors)}")
    for fn, err in errors:
        print(f"    ❌ {fn}: {err}")
print(f"{'='*60}")
