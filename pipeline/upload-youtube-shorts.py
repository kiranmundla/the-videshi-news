#!/usr/bin/env python3
"""Upload recent Instagram Reels as YouTube Shorts for The Videshi channel."""

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


# ── Load AI review keys ───────────────────────────────────────────
def _load_env(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

_ai_env = _load_env("~/workspace/.env.openai")
_gemini_env = _load_env("~/workspace/.env.google-ai")
_OPENAI_KEY = _ai_env.get("OPENAI_API_KEY", "")
_GEMINI_KEY = _gemini_env.get("GOOGLE_AI_API_KEY", "")


def review_yt_quality(title, description, article):
    """AI quality gate for YouTube Shorts — checks title/description before upload.
    Returns (pass: bool, feedback: str)."""
    prompt = f"""You are a YouTube editor for The Videshi, an Indian diaspora news platform.
Review this YouTube Short title and description before upload.

TITLE: {title}
ARTICLE HEADLINE: {article.get('headline', 'N/A') if article else 'N/A'}
CATEGORY: {article.get('category', 'N/A') if article else 'N/A'}

DESCRIPTION (first 500 chars):
{description[:500]}

Score 1-10 and check:
1. Title is factually consistent with the article (no contradictions)
2. Title is under 100 chars and engaging but not clickbait
3. Description has relevant hashtags including #Shorts
4. No broken formatting
5. No hallucinated claims

Respond in JSON: {{"score": N, "pass": true/false, "issues": ["issue1"]}}
Score 7+ = pass."""

    for api_name, call_fn in [("GPT-4o-mini", lambda: _call_openai(prompt)), ("Gemini", lambda: _call_gemini(prompt))]:
        try:
            result = call_fn()
            if result:
                return result.get("pass", True), f"{api_name} score {result.get('score','?')}: {result.get('issues', [])}"
        except Exception as e:
            print(f"  ⚠️ {api_name} review failed: {e}")

    return True, "AI review unavailable — passing by default"


def _call_openai(prompt):
    if not _OPENAI_KEY:
        return None
    r = req.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {_OPENAI_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}],
              "temperature": 0.3, "response_format": {"type": "json_object"}},
        timeout=30
    )
    if r.status_code == 200:
        return json.loads(r.json()["choices"][0]["message"]["content"])
    return None


def _call_gemini(prompt):
    if not _GEMINI_KEY:
        return None
    r = req.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={_GEMINI_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}],
              "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}},
        timeout=30
    )
    if r.status_code == 200:
        return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
    return None

# --- Load env files ---
def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        print(f"⚠️  Env file not found: {p}")
        return env
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN", "")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY", "") or sb_env.get("SUPABASE_KEY", "") or sb_env.get("SUPABASE_ANON_KEY", "")

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
reel_files = sorted(
    [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4') and f.startswith('reel-')],
    key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)),
    reverse=True
)

# Filter out already uploaded and test reels
unuploaded = []
for f in reel_files:
    if f in yt_log:
        continue
    # Skip test reels
    if 'test' in f.lower():
        print(f"⏭️  Skipping test reel: {f}")
        continue
    unuploaded.append(f)

print(f"📊 Total reels: {len(reel_files)}, Already uploaded: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("✅ All reels already uploaded. Nothing to do.")
    exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"📤 Will upload {len(to_upload)} reel(s) this run\n")

# --- Fetch recent articles from Supabase ---
print("📰 Fetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"  Found {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️  Failed to fetch articles: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    # Strip reel- prefix
    name = filename.replace('reel-', '', 1)
    # Strip .mp4
    name = name.replace('.mp4', '')
    # Strip trailing date (YYYYMMDD or just numbers at end)
    name = re.sub(r'-?\d{8,}$', '', name)
    # Also strip dates like -2026MMDD or -202605XX patterns
    name = re.sub(r'-?2026\d*$', '', name)
    return name

def match_article(filename, articles):
    """Try to match a reel filename to an article."""
    fragments = extract_slug_fragments(filename)
    frag_words = set(fragments.split('-'))
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        slug_words = set(slug.split('-'))
        # Count overlapping words (excluding very short common words)
        overlap = len(frag_words.intersection(slug_words) - {'the', 'a', 'an', 'in', 'of', 'for', 'and', 'to', 'is', 'on', 'at', 'by'})
        if overlap > best_score and overlap >= 3:
            best_score = overlap
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Construct a title from filename words if no article match."""
    fragments = extract_slug_fragments(filename)
    words = fragments.split('-')
    title = ' '.join(w.capitalize() for w in words)
    return title[:90]

# Category to hashtags mapping
CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'lifestyle-health': '#DesiLifestyle #Wellness #Health',
    'culture': '#DesiLifestyle #Wellness #DesiCulture',
    'markets-finance': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'economy': '#StockMarket #Nifty #Sensex #IndianMarkets #Economy',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'food': '#IndianFood #IndianCuisine #DesiFood',
}

def extract_topic_hashtags(headline):
    """Extract person/topic-specific hashtags from headline."""
    tags = []
    # Common patterns: capitalize each word, remove spaces
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '')
        if len(tag) > 3 and tag not in tags:
            tags.append(tag)
    return tags[:5]

def build_metadata(article, filename):
    """Build YouTube title, description, and tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        headline = make_title_from_filename(filename)
        subheadline = ''
        slug = extract_slug_fragments(filename)
        category = 'news'
        art_tags = []

    # Title: keep under 100 chars, add #Shorts
    title = headline[:90].strip()
    if not title.endswith('#Shorts'):
        if len(title) + 9 <= 100:
            title = f"{title} #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS.get('news', ''))
    topic_tags = extract_topic_hashtags(headline)
    topic_tags_str = ' '.join(topic_tags)
    
    # Description
    article_url = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
    
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_tags_str}""".strip()

    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category or "News", "Shorts"]
    # Add topic-specific tags from article tags
    if art_tags:
        for t in art_tags[:4]:
            if t and t not in tags:
                tags.append(t)
    # Add from headline extraction
    for t in topic_tags[:3]:
        clean = t.replace('#', '')
        if clean not in tags:
            tags.append(clean)
    tags = tags[:12]

    return title, description, tags, slug

# --- Set up YouTube client ---
print("🔑 Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ YouTube client ready\n")

# --- Upload reels ---
uploaded_count = 0
errors = []

for i, reel_filename in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    file_size_mb = os.path.getsize(reel_path) / (1024 * 1024)
    print(f"{'='*60}")
    print(f"📹 [{i+1}/{len(to_upload)}] {reel_filename} ({file_size_mb:.1f} MB)")
    
    # Match to article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  📰 Matched article: {article.get('headline', '')[:60]}...")
    else:
        print(f"  ⚠️  No article match - using filename for title")
    
    title, description, tags, slug = build_metadata(article, reel_filename)
    print(f"  📝 Title: {title}")
    print(f"  🏷️  Tags: {', '.join(tags[:5])}...")

    # ── Quality gate ──
    print("  🔍 Running AI quality review...")
    yt_pass, yt_feedback = review_yt_quality(title, description, article)
    print(f"  Review: {'✅ PASS' if yt_pass else '❌ FAIL'} — {yt_feedback}")
    if not yt_pass:
        print(f"  ⛔ Short failed quality review — skipping upload: {reel_filename}")
        continue
    
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
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {video_url}")
        
        # Log the upload
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": video_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        # Update prebuilt_reels table if this reel has an entry
        try:
            if article and article.get('id'):
                pr_check = req.get(
                    f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
                    params={
                        "article_id": f"eq.{article['id']}",
                        "select": "id,status",
                        "limit": "1"
                    },
                    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
                    timeout=15
                )
                if pr_check.status_code == 200 and pr_check.json():
                    pr = pr_check.json()[0]
                    new_status = "posted" if pr["status"] == "ig_posted" else "yt_posted"
                    req.patch(
                        f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{pr['id']}",
                        headers={
                            "apikey": SB_KEY,
                            "Authorization": f"Bearer {SB_KEY}",
                            "Content-Type": "application/json",
                            "Prefer": "return=minimal"
                        },
                        json={
                            "status": new_status,
                            "yt_video_id": video_id,
                            "yt_posted_at": datetime.utcnow().isoformat() + "Z",
                            "updated_at": datetime.utcnow().isoformat() + "Z"
                        },
                        timeout=15
                    )
                    print(f"  📦 Prebuilt reel marked {new_status}")
        except Exception as pe:
            print(f"  ⚠️ prebuilt_reels update failed (non-fatal): {pe}")
        
        uploaded_count += 1
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        error_msg = f"Failed to upload {reel_filename}: {str(e)}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}/{len(to_upload)}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    ❌ {e}")
else:
    print(f"  Errors: None")

# Print URLs
for reel in to_upload:
    if reel in yt_log:
        print(f"  🔗 {yt_log[reel]['url']}")
