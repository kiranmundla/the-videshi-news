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

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
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
    "lifestyle": "LIFESTYLE & HEALTH",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

def fetch_untweeted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_body_text(body_md):
    """Extract plain text from markdown body, strip formatting."""
    if not body_md:
        return ""
    import re
    text = body_md
    # Remove markdown images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = extract_body_text(article.get("body", ""))
    
    # Build a summary from the body - take first ~300 words for context
    body_excerpt = " ".join(body.split()[:300]) if body else subheadline
    
    # Use AI-style extraction: build summary from body content
    # Take meaningful paragraphs from the body
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build 2-3 paragraph summary from body content
    summary_parts = []
    word_count = 0
    for para in paragraphs[:6]:
        words = para.split()
        if word_count + len(words) > 250:
            break
        summary_parts.append(para)
        word_count += len(words)
    
    if not summary_parts and subheadline:
        summary_parts = [subheadline]
    
    summary = "\n\n".join(summary_parts[:3])
    
    # If summary is too short, just use what we have
    if len(summary) < 80 and subheadline:
        summary = subheadline
    
    # Extract key takeaways - look for numbered points, key facts
    takeaways = []
    # Try to find key facts from the body
    sentences = [s.strip() for s in body.replace('\n', ' ').split('.') if len(s.strip()) > 20]
    
    # Pick sentences with numbers, names, or strong facts
    import re
    fact_sentences = []
    for s in sentences:
        if re.search(r'\d+', s) or re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', s):
            fact_sentences.append(s.strip() + '.')
    
    # Take up to 4 key facts
    seen = set()
    for fs in fact_sentences:
        short = fs[:60]
        if short not in seen and len(fs) < 200:
            seen.add(short)
            takeaways.append(fs)
            if len(takeaways) >= 4:
                break
    
    # If we don't have enough, pull from subheadline
    if len(takeaways) < 3 and subheadline:
        for part in subheadline.split(';'):
            part = part.strip()
            if part and part not in takeaways:
                takeaways.append(part)
                if len(takeaways) >= 4:
                    break
    
    takeaways = takeaways[:4]
    
    # Build the post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    if takeaways:
        lines.append("Key Takeaways:")
        lines.append("")
        for t in takeaways:
            lines.append(f"▸ {t}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
    
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")
    
    post = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary = " ".join(summary.split()[:100])
        return compose_post_short(article, emoji, label, headline, summary, takeaways, slug)
    
    return post

def compose_post_short(article, emoji, label, headline, summary, takeaways, slug):
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    if takeaways:
        lines.append("Key Takeaways:")
        lines.append("")
        for t in takeaways[:3]:
            lines.append(f"▸ {t}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")
    return "\n".join(lines)

def download_image(image_url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(image_url, timeout=15)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  ⚠️ Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        print(f"  📷 Downloaded image ({size} bytes)")
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def post_tweet(client, api_v1, text, image_path=None):
    """Post tweet with optional image. Returns tweet response."""
    media_ids = None
    if image_path:
        try:
            media = api_v1.media_upload(filename=image_path)
            media_ids = [media.media_id]
            print(f"  📤 Image uploaded to X (media_id: {media.media_id})")
        except Exception as e:
            print(f"  ⚠️ Image upload failed: {e}")
            media_ids = None
    
    kwargs = {"text": text}
    if media_ids:
        kwargs["media_ids"] = media_ids
    
    response = client.create_tweet(**kwargs)
    return response

def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.utcnow().isoformat() + "Z"
    r = requests.patch(url, json={"tweeted_at": now}, headers=SUPABASE_HEADERS, timeout=15)
    r.raise_for_status()
    print(f"  ✅ Supabase updated (tweeted_at: {now})")

def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }
    
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  📝 Logged to tweet-log.json")

def main():
    print("=" * 50)
    print("🐦 The Videshi X Auto-Post")
    print(f"🕐 {datetime.utcnow().isoformat()}Z")
    print("=" * 50)
    
    # Fetch untweeted articles
    print("\n📥 Fetching untweeted articles...")
    articles = fetch_untweeted_articles()
    print(f"   Found {len(articles)} untweeted articles")
    
    if not articles:
        print("\n✅ No articles to post. Done.")
        return
    
    # Filter: must have image_url and slug
    eligible = [a for a in articles if a.get("image_url") and a.get("slug")]
    print(f"   {len(eligible)} have images and slugs")
    
    # Pick up to 4
    to_post = eligible[:4]
    print(f"   Will post {len(to_post)} articles")
    
    if not to_post:
        print("\n✅ No eligible articles to post. Done.")
        return
    
    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    posted = 0
    errors = []
    tweet_urls = []
    
    for i, article in enumerate(to_post):
        print(f"\n{'─' * 40}")
        print(f"📄 [{i+1}/{len(to_post)}] {article['headline'][:80]}")
        print(f"   Category: {article.get('category', 'unknown')} | Slug: {article['slug'][:50]}")
        
        try:
            # Compose post
            post_text = compose_post(article)
            print(f"   Post length: {len(post_text)} chars")
            
            # Download image
            image_path = download_image(article["image_url"]) if article.get("image_url") else None
            
            # Post to X
            print("   🐦 Posting to X...")
            response = post_tweet(client, api_v1, post_text, image_path)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"   ✅ Posted! {tweet_url}")
            tweet_urls.append(tweet_url)
            
            # Clean up image
            if image_path and os.path.exists(image_path):
                os.unlink(image_path)
            
            # Update Supabase
            update_supabase(article["id"])
            
            # Log tweet
            log_tweet(tweet_id, article)
            
            posted += 1
            
            # Wait between posts
            if i < len(to_post) - 1:
                print("   ⏳ Waiting 30s before next post...")
                time.sleep(30)
                
        except Exception as e:
            error_msg = f"{article['headline'][:50]}: {str(e)}"
            errors.append(error_msg)
            print(f"   ❌ Error: {e}")
            # Clean up image on error
            if 'image_path' in dir() and image_path and os.path.exists(image_path):
                os.unlink(image_path)
    
    # Summary
    print(f"\n{'=' * 50}")
    print(f"📊 SUMMARY")
    print(f"   Posted: {posted}/{len(to_post)}")
    if tweet_urls:
        print(f"   Tweet URLs:")
        for url in tweet_urls:
            print(f"     → {url}")
    if errors:
        print(f"   Errors ({len(errors)}):")
        for e in errors:
            print(f"     ⚠️ {e}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()
