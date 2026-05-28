#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, requests
from datetime import datetime

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
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle-health": "🧘",
    "lifestyle": "🧘",
    "markets-finance": "📈",
    "markets": "📈",
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
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "lifestyle": "LIFESTYLE",
    "markets-finance": "MARKETS & FINANCE",
    "markets": "MARKETS",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

def fetch_untweeted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null"
        "&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SB_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Extract key content from body for summary
    # Clean markdown: remove headers, images, links formatting
    clean_body = body
    for prefix in ["#", "##", "###", "####"]:
        clean_body = clean_body.replace(prefix + " ", "")
    
    # Get first ~600 words of clean body for context
    words = clean_body.split()
    context = " ".join(words[:600])

    # Build the post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")
    
    # Use subheadline as the lead paragraph if available
    if subheadline:
        lines.append(subheadline)
        lines.append("")
    
    # We'll let the caller (the main script via Claude) compose the summary
    # For now, return a marker that needs to be replaced
    return "\n".join(lines), context

def mark_tweeted(article_id):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    ts = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(url, headers=SB_HEADERS, json={"tweeted_at": ts}, timeout=15)
    resp.raise_for_status()
    return ts

def log_tweet(tweet_id, article):
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)

def download_image(image_url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def main():
    print("=" * 60)
    print("🐦 The Videshi → X Autopost")
    print(f"⏰ {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"\n📋 Found {len(articles)} untweeted articles")
    
    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📸 {len(eligible)} with images (eligible)")
    
    if not eligible:
        print("\n✅ No articles to post. Done.")
        return
    
    # Pick up to 4
    to_post = eligible[:4]
    print(f"📝 Will post {len(to_post)} articles\n")
    
    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        slug = article.get("slug", "unknown")
        headline = article.get("headline", "No headline")
        print(f"--- Article {i+1}/{len(to_post)}: {headline[:60]}...")
        
        # Read composed post from the pre-generated file
        post_file = f"/tmp/videshi_post_{i}.txt"
        if not os.path.exists(post_file):
            print(f"  ❌ Post file {post_file} not found, skipping")
            errors.append(f"{slug}: post file missing")
            continue
        
        with open(post_file) as f:
            tweet_text = f.read().strip()
        
        if len(tweet_text) > 4000:
            tweet_text = tweet_text[:3990] + "..."
        
        print(f"  📏 Post length: {len(tweet_text)} chars")
        
        # Try to attach image
        media_ids = None
        tmp_path = None
        image_url = article.get("image_url", "")
        if image_url:
            tmp_path = download_image(image_url)
            if tmp_path:
                try:
                    media = api_v1.media_upload(filename=tmp_path)
                    media_ids = [media.media_id]
                    print(f"  📸 Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠️ Image upload failed: {e}")
                    media_ids = None
        
        # Post tweet
        try:
            kwargs = {"text": tweet_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Mark as tweeted in Supabase
            mark_tweeted(article["id"])
            print(f"  📊 Supabase updated (tweeted_at set)")
            
            # Log tweet
            log_tweet(tweet_id, article)
            print(f"  📝 Tweet logged")
            
            posted += 1
            
        except Exception as e:
            print(f"  ❌ Tweet failed: {e}")
            errors.append(f"{slug}: {e}")
        
        # Clean up temp image
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting 30s before next post...")
            time.sleep(30)
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {posted}/{len(to_post)} posted successfully")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()
