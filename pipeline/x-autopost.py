#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

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
            if '=' in line and not line.startswith('#'):
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
    "lifestyle": "LIFESTYLE",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS",
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
    resp = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def extract_summary_from_body(body, max_words=250):
    """Extract clean text from markdown body for summary writing."""
    if not body:
        return ""
    # Remove markdown formatting artifacts but keep the text
    lines = body.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        # Skip image lines, headers with just #, empty lines
        if line.startswith('![') or line.startswith('http') or line == '---':
            continue
        # Remove markdown headers
        if line.startswith('#'):
            line = line.lstrip('#').strip()
        clean_lines.append(line)
    text = ' '.join(clean_lines)
    # Truncate to roughly max_words
    words = text.split()
    if len(words) > max_words * 2:
        text = ' '.join(words[:max_words * 2])
    return text

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body
    body_text = extract_summary_from_body(body)
    
    # Build the summary - use body text to write 2-3 engaging paragraphs
    # We'll extract the first few meaningful paragraphs from the body
    paragraphs = []
    if body:
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('![') or line.startswith('---') or line.startswith('|'):
                continue
            # Clean markdown
            clean = line.replace('**', '').replace('*', '').replace('`', '')
            if len(clean) > 40:  # meaningful paragraph
                paragraphs.append(clean)
            if len(paragraphs) >= 3:
                break
    
    # Build summary text (2-3 paragraphs)
    summary = '\n\n'.join(paragraphs[:3]) if paragraphs else subheadline
    
    # Extract key takeaways from subheadline and body
    takeaways = []
    if subheadline:
        # Split subheadline on periods or semicolons for takeaways
        parts = [p.strip() for p in subheadline.replace(';', '.').split('.') if p.strip() and len(p.strip()) > 15]
        takeaways.extend(parts[:2])
    
    # Try to find more from body bullet points or key facts
    if body:
        for line in body.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                clean = line.lstrip('-•').strip().replace('**', '').replace('*', '')
                if len(clean) > 20 and len(takeaways) < 4:
                    takeaways.append(clean)
    
    # If still not enough takeaways, extract from paragraphs
    if len(takeaways) < 3 and paragraphs:
        for p in paragraphs:
            sentences = [s.strip() for s in p.split('.') if s.strip() and len(s.strip()) > 25]
            for s in sentences:
                if len(takeaways) < 4 and s not in takeaways:
                    takeaways.append(s)
                    if len(takeaways) >= 4:
                        break
    
    takeaways = takeaways[:4]
    
    # Compose the post
    post = f"{emoji} {label} | The Videshi\n\n"
    post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    post += f"{headline.upper()}\n\n"
    post += f"{summary}\n\n"
    post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if takeaways:
        post += "Key Takeaways:\n\n"
        for t in takeaways:
            # Truncate long takeaways
            if len(t) > 150:
                t = t[:147] + "..."
            post += f"▸ {t}\n"
        post += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    post += f"📰 Full story: thevideshi.com/articles/{slug}\n\n"
    post += "The Videshi — Your daily source for Indian diaspora news\n"
    post += "🌐 thevideshi.com"
    
    # Ensure within 4000 char limit
    if len(post) > 3900:
        # Trim summary
        summary_short = summary[:500] + "..."
        post = f"{emoji} {label} | The Videshi\n\n"
        post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        post += f"{headline.upper()}\n\n"
        post += f"{summary_short}\n\n"
        post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        if takeaways:
            post += "Key Takeaways:\n\n"
            for t in takeaways[:3]:
                if len(t) > 120:
                    t = t[:117] + "..."
                post += f"▸ {t}\n"
            post += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        post += f"📰 Full story: thevideshi.com/articles/{slug}\n\n"
        post += "The Videshi — Your daily source for Indian diaspora news\n"
        post += "🌐 thevideshi.com"
    
    return post

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        # Determine extension
        ct = resp.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in ct:
            ext = '.png'
        elif 'webp' in ct:
            ext = '.webp'
        elif 'gif' in ct:
            ext = '.gif'
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def upload_media(image_path):
    """Upload image to X via v1.1 API, return media object or None."""
    try:
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=image_path)
        return media
    except Exception as e:
        print(f"  ⚠️ Media upload failed: {e}")
        return None

def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    resp = requests.patch(url, json={"tweeted_at": ts}, headers=SUPABASE_HEADERS, timeout=15)
    if resp.status_code < 300:
        print(f"  ✅ Supabase updated (tweeted_at)")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")

def log_tweet(tweet_id, article):
    """Append to local tweet log."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        try:
            with open(log_path) as f:
                tweet_log = json.load(f)
        except:
            tweet_log = {}
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=" * 50)
    print("📰 The Videshi — X Auto-Post")
    print(f"🕐 {datetime.utcnow().isoformat()}Z")
    print("=" * 50)
    
    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"\n📥 Found {len(articles)} untweeted articles")
    
    if not articles:
        print("No articles to post. Done.")
        return
    
    # Filter: must have image_url, pick up to 4
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📸 {len(eligible)} have images (eligible)")
    
    to_post = eligible[:4]
    print(f"📝 Will post {len(to_post)} articles\n")
    
    # Init tweepy v2 client
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"\n--- Article {i+1}/{len(to_post)} ---")
        print(f"📰 {article['headline'][:80]}")
        print(f"📂 {article.get('category', 'unknown')}")
        print(f"🔗 thevideshi.com/articles/{article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"📏 Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        image_path = None
        if article.get("image_url"):
            image_path = download_image(article["image_url"])
            if image_path:
                media = upload_media(image_path)
                if media:
                    media_ids = [media.media_id]
                    print(f"  📸 Image uploaded (media_id: {media.media_id})")
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Update Supabase
            mark_tweeted(article["id"])
            
            # Log tweet
            log_tweet(tweet_id, article)
            
            posted += 1
        except Exception as e:
            err_msg = str(e)
            print(f"  ❌ Tweet failed: {err_msg}")
            errors.append({"article": article["headline"][:60], "error": err_msg})
        finally:
            # Clean up temp image
            if image_path and os.path.exists(image_path):
                os.unlink(image_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  ⏳ Waiting 30s...")
            time.sleep(30)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"  - {e['article']}: {e['error']}")
    print("=" * 50)

if __name__ == "__main__":
    main()
