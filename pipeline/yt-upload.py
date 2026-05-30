#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, re, time, glob
from datetime import datetime

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/.env.youtube" if os.path.exists(os.path.expanduser("~/.env.youtube")) else "~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load tracking log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Get all reel MP4s sorted by mtime (newest first), skip test files
all_reels = sorted(
    glob.glob(os.path.join(REELS_DIR, "reel-*.mp4")),
    key=lambda x: os.path.getmtime(x),
    reverse=True
)

# Filter unuploaded (skip reel-v2-final and similar test files)
unuploaded = []
for reel_path in all_reels:
    fname = os.path.basename(reel_path)
    if fname in yt_log:
        continue
    if "v2-final" in fname or "v2-fixed" in fname or "test" in fname or not re.search(r'-\d{8}', fname):
        continue
    unuploaded.append(reel_path)

print(f"Found {len(unuploaded)} unuploaded reel(s)")
if not unuploaded:
    print("Nothing to upload.")
    exit(0)

# Limit to 2 per run
to_upload = unuploaded[:2]
print(f"Will upload {len(to_upload)} reel(s)")

# Fetch recent articles from Supabase
import requests as req_lib

r = req_lib.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"Fetched {len(articles)} recent articles for matching")

def extract_slug_fragments(fname):
    """Extract slug fragments from reel filename."""
    name = fname.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Remove trailing date pattern (YYYYMMDD or partial)
    name = re.sub(r'-\d{8}$', '', name)
    name = re.sub(r'-\d{3,}$', '', name)  # truncated dates
    return name.split("-")

def match_article(fname):
    """Find matching article for a reel filename."""
    frags = extract_slug_fragments(fname)
    frag_str = "-".join(frags)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Count how many fragments appear in the slug
        score = sum(1 for f in frags if f in slug)
        ratio = score / max(len(frags), 1)
        if ratio > best_score and ratio > 0.4:
            best_score = ratio
            best_match = art
    
    return best_match

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

def make_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common entities
    patterns = {
        r'\bModi\b': '#NarendraModi', r'\bTrump\b': '#Trump',
        r'\bKohli\b': '#ViratKohli', r'\bDhoni\b': '#MSDhoni',
        r'\bIPL\b': '#IPL2026', r'\bRBI\b': '#RBI',
        r'\bUSCIS\b': '#USCIS', r'\bH1B\b': '#H1BVisa',
        r'\bH-1B\b': '#H1BVisa', r'\bSensex\b': '#Sensex',
        r'\bNifty\b': '#Nifty', r'\bBollywood\b': '#Bollywood',
        r'\bMumbai\b': '#Mumbai', r'\bDelhi\b': '#Delhi',
        r'\bBengaluru\b': '#Bengaluru', r'\bHyderabad\b': '#Hyderabad',
        r'\bInfosys\b': '#Infosys', r'\bTCS\b': '#TCS',
        r'\bWipro\b': '#Wipro', r'\bAdani\b': '#Adani',
        r'\bAmbani\b': '#Ambani', r'\bRupee\b': '#IndianRupee',
        r'\bBJP\b': '#BJP', r'\bCongress\b': '#Congress',
        r'\bAAP\b': '#AAP', r'\bPunjab\b': '#Punjab',
        r'\bKerala\b': '#Kerala', r'\bBengal\b': '#WestBengal',
        r'\bAir India\b': '#AirIndia', r'\bMonsoon\b': '#Monsoon',
        r'\bOPT\b': '#OPT', r'\bGreen Card\b': '#GreenCard',
    }
    for pat, tag in patterns.items():
        if re.search(pat, headline, re.IGNORECASE):
            tags.append(tag)
    return tags[:5]

def compose_metadata(article, fname):
    """Compose YouTube metadata."""
    if article:
        headline = article["headline"]
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "news")
    else:
        # Construct from filename
        frags = extract_slug_fragments(fname)
        headline = " ".join(f.capitalize() for f in frags)
        subheadline = headline
        slug = ""
        category = "news"
    
    # Title (under 100 chars with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = make_topic_hashtags(headline)
    all_hashtags = "#TheVideshi #Shorts #IndianDiaspora #NRI " + cat_tags
    if topic_tags:
        all_hashtags += " " + " ".join(topic_tags)
    
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
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    # Add topic-specific tags from headline words
    for word in headline.split()[:3]:
        clean = re.sub(r'[^\w]', '', word)
        if len(clean) > 3 and clean not in tags:
            tags.append(clean)
    tags = tags[:12]
    
    return title, description, tags

# YouTube upload
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

for reel_path in to_upload:
    fname = os.path.basename(reel_path)
    print(f"\n--- Processing: {fname}")
    
    article = match_article(fname)
    if article:
        print(f"  Matched article: {article['headline'][:80]}")
    else:
        print(f"  No article match, using filename")
    
    title, description, tags = compose_metadata(article, fname)
    print(f"  Title: {title}")
    
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
        slug = article["slug"] if article else "unknown"
        print(f"  ✅ Uploaded: https://youtube.com/shorts/{video_id}")
        
        # Log
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": f"https://youtube.com/shorts/{video_id}"
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded += 1
        
        # Wait between uploads
        if reel_path != to_upload[-1]:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append({"file": fname, "error": str(e)})

print(f"\n=== Summary ===")
print(f"Uploaded: {uploaded}/{len(to_upload)}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  - {e['file']}: {e['error']}")
