#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

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
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY", sb_env.get("SUPABASE_ANON_KEY", ""))

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Skip test/intermediate files
SKIP_FILES = {"reel-v2-final.mp4", "reel-v2-fixed.mp4"}

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels (newest first) ---
reel_files = []
for fn in os.listdir(REELS_DIR):
    if fn.endswith('.mp4') and fn not in SKIP_FILES and fn not in yt_log:
        full = os.path.join(REELS_DIR, fn)
        reel_files.append((fn, full, os.path.getmtime(full)))

reel_files.sort(key=lambda x: x[2], reverse=True)  # newest first

if not reel_files:
    print("✅ No unuploaded reels found. All caught up!")
    exit(0)

print(f"Found {len(reel_files)} unuploaded reel(s). Will upload up to 2.\n")

# --- Fetch recent articles from Supabase ---
print("Fetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Fetched {len(articles)} recent articles.\n")
except Exception as e:
    print(f"  ⚠️ Failed to fetch articles: {e}")
    articles = []

# --- Category hashtags ---
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

def extract_slug_words(filename):
    """Extract searchable words from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    name = re.sub(r'-\d{8}$', '', name)  # strip trailing date
    return name.split('-')

def match_article(filename, articles):
    """Try to find matching article by slug fragments."""
    words = extract_slug_words(filename)
    slug_fragment = '-'.join(words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        # Count how many words from the reel filename appear in the article slug
        score = sum(1 for w in words if w in slug and len(w) > 2)
        if score > best_score and score >= min(3, len(words) * 0.4):
            best_score = score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Construct a readable title from filename words."""
    words = extract_slug_words(filename)
    title = ' '.join(w.capitalize() for w in words if len(w) > 1)
    return title[:90]

def generate_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common figures/entities
    patterns = {
        r'\bmodi\b': '#NarendraModi', r'\btrump\b': '#Trump',
        r'\bkohli\b': '#ViratKohli', r'\brohit\b': '#RohitSharma',
        r'\bipl\b': '#IPL2026', r'\bh1b\b': '#H1B', r'\bh-1b\b': '#H1B',
        r'\buscis\b': '#USCIS', r'\bgreen\s*card\b': '#GreenCard',
        r'\bmumbai\b': '#Mumbai', r'\bdelhi\b': '#Delhi',
        r'\bbengaluru\b|bangalore\b': '#Bengaluru',
        r'\bhyberabad\b|\bhyperabad\b|\bhyderabad\b': '#Hyderabad',
        r'\brbi\b': '#RBI', r'\brupee\b': '#IndianRupee',
        r'\bcricket\b': '#Cricket', r'\bbollywood\b': '#Bollywood',
        r'\binfosys\b': '#Infosys', r'\btata\b': '#Tata',
        r'\badani\b': '#Adani', r'\bambani\b': '#Ambani',
        r'\bjaishankar\b': '#Jaishankar', r'\brajnath\b': '#RajnathSingh',
        r'\bopt\b': '#OPT', r'\bvisa\b': '#Visa',
        r'\beu\b': '#EU', r'\bcanada\b': '#Canada',
        r'\bgermany\b': '#Germany', r'\buk\b': '#UK',
        r'\bpunjab\b': '#Punjab', r'\baap\b': '#AAP',
        r'\bbengal\b': '#WestBengal', r'\bmamata\b': '#MamataBanerjee',
        r'\bcoal\b': '#CoalIndia', r'\bsupreme\s*court\b': '#SupremeCourt',
        r'\bfdns\b': '#FDNS', r'\bdeportation\b': '#Deportation',
    }
    hl = headline.lower()
    for pat, tag in patterns.items():
        if re.search(pat, hl) and tag not in tags:
            tags.append(tag)
    return tags[:5]

# --- Build YouTube client ---
print("Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

youtube = build("youtube", "v3", credentials=creds)
print("  ✅ Authenticated.\n")

# --- Upload up to 2 ---
uploaded = []
errors = []

for i, (fn, reel_path, mtime) in enumerate(reel_files[:2]):
    print(f"--- Reel {i+1}/{min(len(reel_files), 2)}: {fn} ---")
    
    # Match article
    match = match_article(fn, articles)
    
    if match:
        headline = match.get('headline', '')
        subheadline = match.get('subheadline', '') or ''
        slug = match.get('slug', '')
        category = match.get('category', 'news')
        print(f"  Matched article: {headline[:80]}...")
    else:
        headline = make_title_from_filename(fn)
        subheadline = "News for the global Indian diaspora"
        slug = "unknown"
        category = "news"
        print(f"  No article match. Using filename title: {headline}")
    
    # Title — must be under 100 chars total
    suffix = " #Shorts"
    max_hl = 100 - len(suffix)  # 92
    if len(headline) <= max_hl:
        title = headline + suffix
    else:
        title = headline[:max_hl - 3].rstrip() + "..." + suffix
    
    # Hashtags
    base_tags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = ' '.join(generate_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()
    
    # Description
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
    
    # Tags array
    tag_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    topic_kw = generate_topic_hashtags(headline)
    for t in topic_kw:
        tag_list.append(t.replace('#', ''))
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
        yt_log[fn] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((fn, yt_url))
        
        # Wait between uploads
        if i < min(len(reel_files), 2) - 1:
            print("  Waiting 10 seconds before next upload...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((fn, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {len(uploaded)}")
for fn, url in uploaded:
    print(f"  ✅ {fn}")
    print(f"     → {url}")
if errors:
    print(f"Errors: {len(errors)}")
    for fn, err in errors:
        print(f"  ❌ {fn}: {err}")
print(f"Total reels in log: {len(yt_log)}")
