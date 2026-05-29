#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json, os, re, time, glob
from datetime import datetime, timezone

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env ---
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
SB_KEY = sb_env.get("SUPABASE_ANON_KEY", sb_env.get("SUPABASE_KEY", ""))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
all_reels = glob.glob(os.path.join(REELS_DIR, "reel-*.mp4"))
# Skip test/dev files
skip_patterns = ["reel-v2-final", "reel-v2-fixed", "reel-test"]
unuploaded = []
for reel_path in all_reels:
    fname = os.path.basename(reel_path)
    if fname in yt_log:
        continue
    if any(pat in fname for pat in skip_patterns):
        continue
    unuploaded.append(reel_path)

# Sort by modification time, newest first
unuploaded.sort(key=lambda p: os.path.getmtime(p), reverse=True)

print(f"Found {len(unuploaded)} unuploaded reel(s)")
if not unuploaded:
    print("Nothing to upload. Done.")
    exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reel(s)")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Got {len(articles)} articles")
except Exception as e:
    print(f"  Warning: Could not fetch articles: {e}")
    articles = []

def match_article(filename):
    """Match a reel filename to an article by slug fragments."""
    # Strip reel- prefix and trailing date + .mp4
    base = filename.replace(".mp4", "")
    if base.startswith("reel-"):
        base = base[5:]
    # Remove trailing date pattern like -20260529
    base = re.sub(r'-\d{8}$', '', base)
    words = set(base.split('-'))
    
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get("slug", "")
        slug_words = set(slug.split('-'))
        overlap = len(words & slug_words)
        if overlap > best_score and overlap >= 3:
            best_score = overlap
            best_match = art
    return best_match

def title_from_filename(filename):
    """Construct a title from filename words."""
    base = filename.replace(".mp4", "")
    if base.startswith("reel-"):
        base = base[5:]
    base = re.sub(r'-\d{8}$', '', base)
    words = base.split('-')
    return ' '.join(w.capitalize() for w in words)

CATEGORY_HASHTAGS = {
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

def generate_hashtags(headline, category):
    """Generate 15-20 hashtags based on category + content."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common person/entity patterns
    headline_words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline or "")
    seen = set()
    for w in headline_words:
        tag = '#' + w.replace(' ', '')
        if tag not in seen and len(tag) > 3:
            seen.add(tag)
            topic_tags.append(tag)
            if len(topic_tags) >= 5:
                break
    
    all_tags = f"{base} {cat_tags}"
    if topic_tags:
        all_tags += " " + " ".join(topic_tags)
    
    # Add India-related if not already present
    if "#India" not in all_tags:
        all_tags += " #India"
    
    return all_tags

def make_tags_list(headline, category):
    """Generate 8-12 tags for YouTube."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    if category:
        tags.append(category.replace("-", " ").title())
    # Extract notable words from headline
    if headline:
        words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline)
        for w in words[:4]:
            if w not in tags:
                tags.append(w)
    while len(tags) < 8:
        tags.append("South Asian")
        break
    return tags[:12]

# --- Set up YouTube client ---
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  YouTube client ready")

# --- Upload loop ---
uploaded_count = 0
errors = []
results = []

for i, reel_path in enumerate(to_upload):
    fname = os.path.basename(reel_path)
    print(f"\n--- Reel {i+1}/{len(to_upload)}: {fname} ---")
    
    # Match article
    article = match_article(fname)
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "news")
        print(f"  Matched article: {slug}")
    else:
        headline = title_from_filename(fname)
        subheadline = ""
        slug = "unknown"
        category = "news"
        print(f"  No article match, using filename title: {headline}")
    
    # Compose title (under 100 chars total, with #Shorts suffix)
    shorts_suffix = " #Shorts"
    max_headline_len = 100 - len(shorts_suffix)  # 92 chars for headline
    title = headline
    if len(title) > max_headline_len:
        title = title[:max_headline_len - 3].rstrip() + "..."
    title = f"{title}{shorts_suffix}"
    # Safety check
    if len(title) > 100:
        title = title[:100]
    
    # Compose description
    hashtags = generate_hashtags(headline, category)
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != "unknown" else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    tags = make_tags_list(headline, category)
    
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
        
        uploaded_count += 1
        results.append({"file": fname, "url": url, "slug": slug})
        
    except Exception as e:
        err_msg = f"Failed to upload {fname}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)
    
    # Wait between uploads
    if i < len(to_upload) - 1:
        print("  Waiting 10 seconds...")
        time.sleep(10)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {uploaded_count}/{len(to_upload)}")
for r in results:
    print(f"  • {r['file']}")
    print(f"    → {r['url']}")
    print(f"    Article: {r['slug']}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  ⚠️ {e}")
print(f"{'='*60}")
