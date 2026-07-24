#!/usr/bin/env python3
"""YouTube Shorts upload for The Videshi — scheduled run."""

import json, os, sys, time, re, requests
from datetime import datetime

# ── Load env ──
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

YOUTUBE_CLIENT_ID     = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']

SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY       = sb_env.get('SUPABASE_SERVICE_ROLE_KEY') or sb_env.get('SUPABASE_ANON_KEY')

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH  = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

# ── Load log ──
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# ── Identify unuploaded reels ──
all_mp4s = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
unuploaded = [f for f in all_mp4s if f not in yt_log]
unuploaded.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

print(f"Total MP4s: {len(all_mp4s)}, Logged: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

# ── Filter: skip voice auditions and intermediate builds ──
SKIP_PATTERNS = ['voice-audition', 'end-card', 'test-', 'indian-beat-']

def should_skip(fname):
    for pat in SKIP_PATTERNS:
        if pat in fname:
            return True
    return False

# Group duplicate versions (same base, different timestamps)
# e.g. ss-reel-eb2-india-...-2328.mp4, ss-reel-eb2-india-...-2331.mp4
def base_name(fname):
    """Strip trailing timestamp from ss-reel filenames for grouping."""
    m = re.match(r'^(ss-reel-.+?)-\d{4}\.mp4$', fname)
    if m:
        return m.group(1)
    return fname

# Group by base name
groups = {}
for f in unuploaded:
    bn = base_name(f)
    if bn not in groups:
        groups[bn] = []
    groups[bn].append(f)

# For each group, pick the newest; skip the rest
to_upload = []
to_skip = []

for bn, files in groups.items():
    files.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)
    if should_skip(files[0]):
        for f in files:
            to_skip.append((f, "skipped-test-file"))
    elif len(files) > 1:
        to_upload.append(files[0])  # newest
        for f in files[1:]:
            to_skip.append((f, "skip-older-version"))
    else:
        to_upload.append(files[0])

# Sort to_upload by mtime newest first
to_upload.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

print(f"\nTo upload: {len(to_upload)}")
for f in to_upload:
    print(f"  📤 {f}")
print(f"To skip: {len(to_skip)}")
for f, reason in to_skip:
    print(f"  ⏭️  {f} ({reason})")

# ── Log skipped files ──
for fname, reason in to_skip:
    yt_log[fname] = {
        "video_id": reason,
        "article_slug": "skipped",
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "url": "skipped"
    }

with open(LOG_PATH, 'w') as f:
    json.dump(yt_log, f, indent=2)

if not to_upload:
    print("\n✅ Nothing to upload.")
    sys.exit(0)

# ── Fetch recent articles from Supabase ──
print("\nFetching articles from Supabase...")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"  Fetched {len(articles)} published articles")

def match_article(fname):
    """Try to match reel filename to an article."""
    # Strip prefix and date suffix
    name = fname.replace('.mp4', '')
    # Remove ss-reel- or reel- prefix
    name = re.sub(r'^(ss-)?reel-', '', name)
    # Remove trailing timestamp like -2348 or -20260609
    name = re.sub(r'-\d{4}$', '', name)  # -2348
    name = re.sub(r'-\d{8}$', '', name)  # -20260609
    
    slug_words = set(name.split('-'))
    
    best_match = None
    best_score = 0
    
    for art in articles:
        if not art.get('slug'):
            continue
        art_words = set(art['slug'].split('-'))
        overlap = len(slug_words & art_words)
        score = overlap / max(len(slug_words), 1)
        if score > best_score and score > 0.4:
            best_score = score
            best_match = art
    
    return best_match

# ── Category hashtag map ──
CATEGORY_TAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
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
    # Common person/entity patterns
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '')
        if len(tag) > 3 and tag not in tags:
            tags.append(tag)
    return ' '.join(tags[:5])

def compose_metadata(fname, article):
    """Build YouTube title, description, tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        # Construct from filename
        name = fname.replace('.mp4', '')
        name = re.sub(r'^(ss-)?reel-', '', name)
        name = re.sub(r'-\d{4}$', '', name)
        name = re.sub(r'-\d{8}$', '', name)
        words = name.split('-')
        headline = ' '.join(w.capitalize() for w in words)
        subheadline = ''
        slug = ''
        category = 'news'
        art_tags = []
    
    # Title: under 100 chars with #Shorts
    title = headline[:93] + ' #Shorts' if len(headline) > 93 else headline + ' #Shorts'
    
    # Category hashtags
    cat_tags = CATEGORY_TAGS.get(category, CATEGORY_TAGS['news'])
    topic_tags = make_topic_hashtags(headline)
    
    all_hashtags = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_tags}".strip()
    
    # Description
    article_link = f"\n\n📰 Full story: https://thevideshi.com/articles/{slug}" if slug else ""
    
    description = f"""{subheadline}{article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags list
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic words from headline
    for t in (art_tags or [])[:3]:
        if t not in yt_tags:
            yt_tags.append(t)
    for w in re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline or '')[:3]:
        if w not in yt_tags:
            yt_tags.append(w)
    
    return title, description, yt_tags[:12], slug

# ── YouTube auth ──
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

# ── Upload up to 2 reels ──
MAX_UPLOADS = 2
uploaded = []
errors = []

for fname in to_upload[:MAX_UPLOADS]:
    reel_path = os.path.join(REELS_DIR, fname)
    size_mb = os.path.getsize(reel_path) / (1024*1024)
    print(f"\n{'='*60}")
    print(f"Uploading: {fname} ({size_mb:.1f} MB)")
    
    article = match_article(fname)
    if article:
        print(f"  Matched article: {article.get('slug', 'unknown')}")
    else:
        print(f"  No article match, using filename-derived title")
    
    title, description, tags, slug = compose_metadata(fname, article)
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
        
        media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)
        
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
        
        # Log it
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((fname, video_id, url))
        
        # Wait between uploads
        if len(uploaded) < MAX_UPLOADS and fname != to_upload[min(MAX_UPLOADS-1, len(to_upload)-1)]:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append((fname, str(e)))

# ── Summary ──
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"  Uploaded: {len(uploaded)}")
for fname, vid, url in uploaded:
    print(f"    ✅ {fname} → {url}")
print(f"  Skipped: {len(to_skip)}")
print(f"  Errors: {len(errors)}")
for fname, err in errors:
    print(f"    ❌ {fname}: {err}")
