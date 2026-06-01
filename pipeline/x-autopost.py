#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form premium posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    headers=HEADERS,
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter to ones with image_url, pick up to 4
candidates = [a for a in articles if a.get("image_url")]
to_post = candidates[:4]
print(f"Selected {len(to_post)} articles to post (with images)")

if not to_post:
    print("Nothing to post. Exiting.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

def load_tweet_log():
    if os.path.exists(TWEET_LOG_PATH):
        with open(TWEET_LOG_PATH) as f:
            return json.load(f)
    return {}

def save_tweet_log(log):
    with open(TWEET_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body - strip markdown formatting
    body_clean = body.replace("##", "").replace("**", "").replace("*", "").strip()
    # Get first ~600 chars of body for summary material
    body_preview = body_clean[:2000]
    
    # Build the post - we'll use Claude-style summarization inline
    # Since we can't call an LLM here, we'll extract smartly from the body
    
    # Get paragraphs from body
    paragraphs = [p.strip() for p in body_clean.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first few substantive paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:6]:
        # Skip very short or header-like lines
        if len(p) < 50:
            continue
        # Clean up markdown artifacts
        p = p.replace('[', '').replace(']', '').replace('(http', ' (http')
        if char_count + len(p) > 800:
            break
        summary_parts.append(p)
        char_count += len(p)
    
    summary_text = '\n\n'.join(summary_parts[:3]) if summary_parts else subheadline
    
    # Extract key facts for takeaways from subheadline and body
    takeaways = []
    if subheadline:
        takeaways.append(subheadline)
    # Look for sentences with numbers, names, or key facts
    sentences = body_clean.replace('\n', ' ').split('. ')
    for s in sentences:
        s = s.strip()
        if len(s) > 40 and len(s) < 200:
            # Prefer sentences with numbers or specific details
            has_number = any(c.isdigit() for c in s)
            has_dollar = '$' in s or '%' in s
            if (has_number or has_dollar) and len(takeaways) < 4:
                takeaways.append(s.rstrip('.') if not s.endswith('.') else s[:-1])
    
    # Pad takeaways if needed
    while len(takeaways) < 3 and sentences:
        for s in sentences[2:8]:
            s = s.strip()
            if len(s) > 50 and s not in takeaways and len(takeaways) < 4:
                takeaways.append(s.rstrip('.'))
                break
        else:
            break
    
    takeaways = takeaways[:4]
    takeaway_lines = '\n'.join(f"▸ {t}" for t in takeaways)
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Truncate summary
        over = len(post) - 3800
        summary_text = summary_text[:len(summary_text) - over] + "..."
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def upload_image(image_url):
    """Download image and upload to X, return media_id or None."""
    try:
        img_resp = requests.get(image_url, timeout=15)
        img_resp.raise_for_status()
        
        # Determine extension from content type
        ct = img_resp.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(img_resp.content)
            tmp_path = tmp.name
        
        media = api_v1.media_upload(filename=tmp_path)
        os.unlink(tmp_path)
        return media.media_id
    except Exception as e:
        print(f"  ⚠️ Image upload failed: {e}")
        return None

def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={"id": f"eq.{article_id}"},
        headers=HEADERS,
        json={"tweeted_at": now},
        timeout=15,
    )
    if resp.status_code < 300:
        print(f"  ✅ Marked tweeted_at in Supabase")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")

# --- Post loop ---
posted = 0
errors = []
tweet_log = load_tweet_log()

for i, article in enumerate(to_post):
    print(f"\n--- Article {i+1}/{len(to_post)} ---")
    print(f"  Headline: {article['headline']}")
    print(f"  Category: {article.get('category', 'unknown')}")
    print(f"  Slug: {article['slug']}")
    
    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")
    
    # Upload image
    media_id = None
    if article.get("image_url"):
        print(f"  Uploading image...")
        media_id = upload_image(article["image_url"])
    
    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        response = client.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        
        # Update Supabase
        mark_tweeted(article["id"])
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        save_tweet_log(tweet_log)
        
        posted += 1
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  Waiting 30s before next post...")
            time.sleep(30)
    
    except Exception as e:
        err_msg = f"Failed to post '{article['headline']}': {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
