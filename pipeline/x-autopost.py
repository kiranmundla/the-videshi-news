#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
from datetime import datetime, timezone

import tweepy

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                env[key.strip()] = val.strip().strip('"').strip("'")
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# --- Category emoji mapping ---
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

# --- Fetch untweeted articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter to those with image_url, take up to 4
articles_to_post = [a for a in articles if a.get("image_url")][:4]
print(f"Selected {len(articles_to_post)} articles to post (with images)")

if not articles_to_post:
    print("No articles to post. Exiting.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body (strip markdown)
    body_clean = body.replace("**", "").replace("##", "").replace("###", "").replace("*", "")
    # Get first ~1500 chars of body for context
    body_excerpt = body_clean[:2000]
    
    # Build summary from body - take meaningful paragraphs
    paragraphs = [p.strip() for p in body_clean.split("\n\n") if p.strip() and len(p.strip()) > 40]
    
    # Build a 2-3 paragraph summary
    summary_parts = []
    total_chars = 0
    for p in paragraphs[:5]:
        # Skip if it looks like a header or metadata
        if p.startswith("Lead:") or p.startswith("Context") or p.startswith("Source"):
            continue
        if total_chars + len(p) > 600:
            break
        summary_parts.append(p)
        total_chars += len(p)
    
    summary = "\n\n".join(summary_parts) if summary_parts else subheadline
    
    # Extract key takeaways from body
    takeaways = []
    for p in paragraphs:
        if any(c.isdigit() for c in p) or any(kw in p.lower() for kw in ["percent", "billion", "million", "according", "announced", "launched", "reported"]):
            # Trim to a reasonable takeaway length
            takeaway = p[:150].rsplit(".", 1)[0] + "." if len(p) > 150 else p
            if takeaway not in takeaways and len(takeaway) > 20:
                takeaways.append(takeaway)
            if len(takeaways) >= 4:
                break
    
    # Fallback takeaways from subheadline
    if len(takeaways) < 3 and subheadline:
        parts = [s.strip() for s in subheadline.replace(";", ".").split(".") if s.strip()]
        for part in parts:
            if part not in takeaways and len(part) > 15:
                takeaways.append(part)
            if len(takeaways) >= 4:
                break
    
    takeaways = takeaways[:4]
    
    takeaway_text = "\n".join(f"▸ {t}" for t in takeaways)
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary_short = summary[:300].rsplit(".", 1)[0] + "."
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_short}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

# --- Post articles ---
posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(articles_to_post):
    slug = article.get("slug", "unknown")
    print(f"\n--- Posting {i+1}/{len(articles_to_post)}: {slug} ---")
    
    try:
        post_text = compose_post(article)
        print(f"Post length: {len(post_text)} chars")
        
        # Try to attach image
        media_id = None
        image_url = article.get("image_url", "")
        if image_url:
            try:
                print(f"Downloading image: {image_url[:80]}...")
                img_resp = requests.get(image_url, timeout=15)
                img_resp.raise_for_status()
                
                # Determine extension
                content_type = img_resp.headers.get("Content-Type", "image/jpeg")
                ext = ".jpg"
                if "png" in content_type:
                    ext = ".png"
                elif "webp" in content_type:
                    ext = ".webp"
                
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(img_resp.content)
                    tmp_path = tmp.name
                
                print("Uploading image to X...")
                media = api_v1.media_upload(filename=tmp_path)
                media_id = media.media_id
                print(f"Image uploaded: media_id={media_id}")
                
                os.unlink(tmp_path)
            except Exception as e:
                print(f"Image upload failed ({e}), posting without image")
                media_id = None
        
        # Post tweet
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        tweet_urls.append(tweet_url)
        print(f"✅ Posted: {tweet_url}")
        
        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SUPABASE_HEADERS,
            json={"tweeted_at": now_utc}
        )
        if patch_resp.status_code < 300:
            print(f"✅ Supabase updated: tweeted_at={now_utc}")
        else:
            print(f"⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet ID
        log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
        tweet_log = {}
        if os.path.exists(log_path):
            with open(log_path) as f:
                tweet_log = json.load(f)
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": slug,
            "posted_at": datetime.utcnow().isoformat() + "Z"
        }
        with open(log_path, "w") as f:
            json.dump(tweet_log, f, indent=2)
        print(f"✅ Logged to tweet-log.json")
        
        posted += 1
        
        # Wait 30s between posts
        if i < len(articles_to_post) - 1:
            print("Waiting 30s before next post...")
            time.sleep(30)
    
    except Exception as e:
        err_msg = f"Error posting {slug}: {e}"
        print(f"❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(articles_to_post)} articles to X")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print("Errors:")
    for err in errors:
        print(f"  {err}")
print(f"{'='*50}")
