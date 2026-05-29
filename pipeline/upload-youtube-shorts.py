#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

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
                env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY", sb_env.get("SUPABASE_ANON_KEY", sb_env.get("SUPABASE_KEY", "")))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Skip test/dev files
SKIP_PREFIXES = ["reel-v2-"]

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels sorted by mtime (newest first)
all_reels = []
for fname in os.listdir(REELS_DIR):
    if not fname.endswith(".mp4"):
        continue
    if any(fname.startswith(p) for p in SKIP_PREFIXES):
        print(f"  Skipping test file: {fname}")
        continue
    if fname in yt_log:
        continue
    fpath = os.path.join(REELS_DIR, fname)
    all_reels.append((fname, fpath, os.path.getmtime(fpath)))

all_reels.sort(key=lambda x: x[2], reverse=True)
print(f"Found {len(all_reels)} unuploaded reel(s)")

if not all_reels:
    print("Nothing to upload.")
    sys.exit(0)

# Fetch recent articles from Supabase
import requests as req

try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"Loaded {len(articles)} recent articles for matching")
except Exception as e:
    print(f"Warning: Could not fetch articles: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Extract slug-like words from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date like -20260528
    name = re.sub(r'-\d{8}$', '', name)
    # Also strip truncated names (ending mid-word)
    return name.split("-")

def match_article(filename, articles):
    """Find best matching article for a reel filename."""
    frags = extract_slug_fragments(filename)
    frag_str = "-".join(frags)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Count how many fragments appear in the slug
        score = sum(1 for f in frags if f in slug)
        # Bonus for consecutive matches
        if frag_str in slug:
            score += len(frags)
        if score > best_score and score >= max(3, len(frags) * 0.4):
            best_score = score
            best_match = art
    
    return best_match

def get_category_hashtags(category):
    """Return category-specific hashtags."""
    cat_tags = {
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
    return cat_tags.get(category, "#IndiaNews #DesiNews #SouthAsian")

def extract_topic_hashtags(headline):
    """Extract person/topic hashtags from headline."""
    tags = []
    # Common patterns: proper nouns, multi-word names
    words = headline.split()
    i = 0
    while i < len(words):
        w = re.sub(r'[^\w]', '', words[i])
        if w and w[0].isupper() and len(w) > 2 and w.lower() not in {
            "the", "and", "for", "with", "from", "has", "are", "its",
            "new", "how", "why", "what", "who", "will", "can", "may",
            "after", "over", "into", "about", "could", "would", "should",
            "says", "said", "india", "indian", "nri", "news", "full", "story"
        }:
            tags.append(f"#{w}")
        i += 1
    return tags[:5]

def title_from_filename(filename):
    """Construct title from filename when no article match."""
    name = filename.replace(".mp4", "")
    if name.startswith("reel-"):
        name = name[5:]
    name = re.sub(r'-\d{8}$', '', name)
    words = name.split("-")
    return " ".join(w.capitalize() for w in words)

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

uploaded = 0
errors = []

for fname, fpath, mtime in all_reels[:2]:
    print(f"\n{'='*60}")
    print(f"Processing: {fname}")
    
    # Match article
    art = match_article(fname, articles)
    
    if art:
        headline = art["headline"]
        subheadline = art.get("subheadline", "")
        slug = art["slug"]
        category = art.get("category", "news")
        print(f"  Matched article: {slug}")
    else:
        headline = title_from_filename(fname)
        subheadline = "News for the global Indian diaspora"
        slug = "unknown"
        category = "news"
        print(f"  No article match, using filename title: {headline}")
    
    # Build title (under 100 chars, with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
    # Build hashtags
    base_tags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = get_category_hashtags(category)
    topic_tags = " ".join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()
    
    # Build description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != "unknown" else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    # Build tags list
    tag_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    for ht in extract_topic_hashtags(headline):
        tag_list.append(ht.replace("#", ""))
    tag_list = tag_list[:12]
    
    print(f"  Title: {title}")
    print(f"  Category: {category}")
    print(f"  Tags: {tag_list}")
    
    # Upload
    try:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tag_list,
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
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")
        
        # Log
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": yt_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded += 1
        
        # Wait between uploads
        if uploaded < 2:
            print("  Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        err_msg = f"Failed to upload {fname}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

print(f"\n{'='*60}")
print(f"SUMMARY: Uploaded {uploaded}/{min(len(all_reels), 2)} reels")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
