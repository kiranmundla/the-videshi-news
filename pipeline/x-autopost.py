#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime, timezone

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
supa_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

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

# --- Fetch articles ---
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
    headers=SUPA_HEADERS,
    timeout=30
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter to those with images, pick up to 4
candidates = [a for a in articles if a.get("image_url")]
to_post = candidates[:4]
print(f"Will post {len(to_post)} articles (with images)")

if not to_post:
    print("No articles to post. Done.")
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

# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body for summary
    # Strip markdown formatting for cleaner reading
    body_clean = body.replace("**", "").replace("*", "").replace("##", "").replace("#", "")
    body_clean = body_clean.replace("---", "").strip()
    
    # Get first ~500 chars of meaningful body content for summary extraction
    paragraphs = [p.strip() for p in body_clean.split("\n\n") if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first 2-3 meaningful paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:5]:
        if char_count > 600:
            break
        # Skip very short lines or headers
        if len(p) < 30:
            continue
        summary_parts.append(p)
        char_count += len(p)
    
    summary = "\n\n".join(summary_parts[:3])
    # Truncate if too long
    if len(summary) > 800:
        summary = summary[:797].rsplit(" ", 1)[0] + "..."
    
    # Extract key facts for takeaways from subheadline and body
    takeaways = []
    if subheadline:
        # Split subheadline into potential takeaway points
        parts = [s.strip() for s in subheadline.replace(";", ".").split(".") if s.strip() and len(s.strip()) > 15]
        takeaways.extend(parts[:2])
    
    # Try to find more takeaways from body paragraphs
    for p in paragraphs[1:8]:
        if len(takeaways) >= 4:
            break
        # Look for sentences with numbers, names, or strong facts
        sentences = [s.strip() for s in p.split(".") if s.strip() and len(s.strip()) > 20]
        for s in sentences:
            if len(takeaways) >= 4:
                break
            # Prefer sentences with numbers or key indicators
            if any(c.isdigit() for c in s) or any(kw in s.lower() for kw in ["percent", "billion", "million", "announced", "launched", "according", "reported", "first", "largest"]):
                takeaway = s.strip()
                if not takeaway.endswith("."):
                    takeaway += "."
                if takeaway not in takeaways and len(takeaway) > 20:
                    takeaways.append(takeaway)
    
    # Ensure at least 3 takeaways
    if len(takeaways) < 3:
        for p in paragraphs[:6]:
            if len(takeaways) >= 3:
                break
            sentences = [s.strip() for s in p.split(".") if s.strip() and len(s.strip()) > 25]
            for s in sentences:
                if len(takeaways) >= 3:
                    break
                takeaway = s.strip()
                if not takeaway.endswith("."):
                    takeaway += "."
                if takeaway not in takeaways:
                    takeaways.append(takeaway)
    
    takeaways = takeaways[:4]
    
    # Build the post
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
    for t in takeaways:
        post += f"▸ {t}\n"
    
    post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary = summary[:400].rsplit(" ", 1)[0] + "..."
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
        for t in takeaways[:3]:
            post += f"▸ {t}\n"
        post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get("content-type", "image/jpeg")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


# --- Post loop ---
posted = 0
errors = []

for i, article in enumerate(to_post):
    slug = article.get("slug", "unknown")
    headline = article.get("headline", "No headline")
    print(f"\n--- [{i+1}/{len(to_post)}] {headline[:80]}...")
    
    # Compose post
    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")
    
    # Download and upload image
    media_ids = None
    img_path = None
    image_url = article.get("image_url", "")
    if image_url:
        img_path = download_image(image_url)
        if img_path:
            try:
                media = api_v1.media_upload(filename=img_path)
                media_ids = [media.media_id]
                print(f"  Image uploaded: media_id={media.media_id}")
            except Exception as e:
                print(f"  Image upload to X failed: {e}")
                media_ids = None
    
    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        
        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SUPA_HEADERS,
            json={"tweeted_at": datetime.now(timezone.utc).isoformat()},
            timeout=15
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated (tweeted_at set)")
        else:
            print(f"  Supabase update warning: {patch_resp.status_code} {patch_resp.text}")
        
        # Log locally
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": slug,
            "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
    except Exception as e:
        err_msg = f"Tweet failed for {slug}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)
    
    # Clean up temp image
    if img_path and os.path.exists(img_path):
        os.remove(img_path)
    
    # Wait between posts
    if i < len(to_post) - 1:
        print("  Waiting 30s...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print("Done.")
