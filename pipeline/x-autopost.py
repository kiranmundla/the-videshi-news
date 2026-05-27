#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
from datetime import datetime, timezone

import tweepy

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
    "lifestyle-health": "🧘",
    "markets": "📈",
    "markets-finance": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

CATEGORY_LABEL = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle": "LIFESTYLE",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS",
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
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

# Filter: must have image_url and slug
eligible = [a for a in articles if a.get("image_url") and a.get("slug")]
print(f"{len(eligible)} eligible (have image + slug)")

# Pick up to 4
to_post = eligible[:4]
if not to_post:
    print("No articles to post. Done.")
    sys.exit(0)

print(f"Will post {len(to_post)} articles\n")

# --- Set up tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth_v1 = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth_v1)

# --- Compose post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article["slug"]
    body = article.get("body") or ""

    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("**", "").replace("##", "").replace("###", "").replace("*", "").strip()
    # Get first ~600 words for summary material
    body_words = body_clean.split()[:600]
    body_excerpt = " ".join(body_words)

    # Build the summary - we'll use the body to write a better version
    # Extract sentences for summary (first ~300 words worth)
    sentences = []
    current = ""
    for word in body_words[:300]:
        current += word + " "
        if any(current.rstrip().endswith(p) for p in ['.', '!', '?']):
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    # Build 2-3 paragraph summary from article content
    # Use first few meaningful sentences, skip very short ones
    good_sentences = [s for s in sentences if len(s) > 30]
    
    para1_sents = good_sentences[:3]
    para2_sents = good_sentences[3:6]
    
    para1 = " ".join(para1_sents) if para1_sents else subheadline or headline
    para2 = " ".join(para2_sents) if para2_sents else ""

    # Extract key takeaways from subheadline and body
    takeaways = []
    if subheadline:
        takeaways.append(subheadline[:120])
    # Pull notable sentences with numbers or key facts
    for s in good_sentences[2:10]:
        if len(takeaways) >= 4:
            break
        if any(c.isdigit() for c in s) or any(kw in s.lower() for kw in ['percent', 'billion', 'million', 'according', 'announced', 'launched', 'first', 'record']):
            clean = s.strip()[:150]
            if clean not in takeaways:
                takeaways.append(clean)
    # Fill remaining with other good sentences
    for s in good_sentences[4:12]:
        if len(takeaways) >= 4:
            break
        clean = s.strip()[:150]
        if clean not in takeaways:
            takeaways.append(clean)

    # Ensure at least 2 takeaways
    if len(takeaways) < 2:
        takeaways.append(headline[:120])

    takeaway_lines = "\n".join(f"▸ {t}" for t in takeaways[:4])

    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{para1}

{para2}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim to 4000 chars max
    if len(post) > 4000:
        post = post[:3990] + "…"
    
    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15, stream=True)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


def update_supabase(article_id):
    """Mark article as tweeted."""
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={"id": f"eq.{article_id}"},
        headers=SUPA_HEADERS,
        json={"tweeted_at": now},
        timeout=15
    )
    r.raise_for_status()
    return now


def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    try:
        tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}
    except:
        tweet_log = {}
    
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)


# --- Post articles ---
posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(to_post):
    print(f"[{i+1}/{len(to_post)}] Posting: {article['headline'][:80]}...")
    
    try:
        # Compose post
        text = compose_post(article)
        print(f"  Post length: {len(text)} chars")
        
        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  Image upload to X failed: {e}")
                    media_ids = None
        
        # Post tweet
        kwargs = {"text": text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        
        response = client.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        tweet_urls.append(tweet_url)
        print(f"  ✅ Posted: {tweet_url}")
        
        # Update Supabase
        ts = update_supabase(article["id"])
        print(f"  Supabase updated: tweeted_at={ts}")
        
        # Log tweet
        log_tweet(tweet_id, article)
        
        posted += 1
        
        # Cleanup
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  Waiting 30s...")
            time.sleep(30)
    
    except Exception as e:
        errors.append(f"{article['slug']}: {e}")
        print(f"  ❌ Error: {e}")
        if img_path and os.path.exists(img_path):
            try:
                os.unlink(img_path)
            except:
                pass

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: {posted}/{len(to_post)} articles posted to @thevideshi")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
print(f"{'='*50}")
