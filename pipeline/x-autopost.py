#!/usr/bin/env python3
"""Auto-post Videshi articles to X (@thevideshi) with long-form posts + images."""

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
    """Fetch up to 20 recent published articles not yet tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def extract_body_text(body_md):
    """Extract clean text from markdown body for summarization."""
    if not body_md:
        return ""
    # Strip markdown formatting for key content extraction
    lines = body_md.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            line = line.lstrip('#').strip()
        if line.startswith('!['):
            continue
        if line.startswith('---'):
            continue
        if line:
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = (article.get('category') or 'news').lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    
    headline = article.get('headline', '').strip()
    subheadline = article.get('subheadline', '').strip()
    slug = article.get('slug', '')
    body = extract_body_text(article.get('body', ''))
    
    # Build the summary from body content - extract key paragraphs
    body_paragraphs = [p.strip() for p in body.split('\n') if p.strip() and len(p.strip()) > 40]
    
    # Create a concise summary from the article body
    summary_parts = []
    char_count = 0
    for para in body_paragraphs[:8]:
        # Skip very short lines or headers
        if len(para) < 30:
            continue
        # Clean up markdown artifacts
        para = para.replace('**', '').replace('*', '').replace('`', '')
        if char_count + len(para) > 600:
            break
        summary_parts.append(para)
        char_count += len(para)
    
    summary = '\n\n'.join(summary_parts[:3]) if summary_parts else subheadline
    
    # Extract key takeaways from subheadline and body
    takeaways = []
    if subheadline:
        # Split subheadline on common delimiters
        parts = [s.strip() for s in subheadline.replace(';', '.').split('.') if s.strip() and len(s.strip()) > 15]
        takeaways.extend(parts[:2])
    
    # Try to find key facts from body
    for para in body_paragraphs:
        para_clean = para.replace('**', '').replace('*', '')
        # Look for paragraphs with numbers, percentages, or key facts
        if any(c.isdigit() for c in para_clean) and len(para_clean) < 200:
            fact = para_clean[:150].strip()
            if fact not in takeaways and len(takeaways) < 4:
                takeaways.append(fact)
        if len(takeaways) >= 4:
            break
    
    # Ensure at least 3 takeaways
    if len(takeaways) < 3:
        for para in body_paragraphs[1:6]:
            para_clean = para.replace('**', '').replace('*', '')
            if len(para_clean) < 200 and para_clean not in takeaways:
                takeaways.append(para_clean[:150].strip())
            if len(takeaways) >= 3:
                break
    
    takeaway_lines = '\n'.join(f"▸ {t}" for t in takeaways[:4])
    
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary = summary[:400] + "..."
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def download_image(url):
    """Download image to a temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size > 0
        if os.path.getsize(tmp.name) < 100:
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(url, json={"tweeted_at": now}, headers=SUPABASE_HEADERS, timeout=15)
    resp.raise_for_status()
    return now

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
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=" * 50)
    print("🐦 Videshi X Auto-Post")
    print(f"⏰ {datetime.utcnow().isoformat()}Z")
    print("=" * 50)
    
    # Fetch untweeted articles
    articles = fetch_untweeted_articles()
    print(f"\n📋 Found {len(articles)} untweeted articles")
    
    if not articles:
        print("✅ No articles to post. Done.")
        return
    
    # Filter: must have image_url, pick up to 4
    eligible = [a for a in articles if a.get('image_url')]
    print(f"📸 {len(eligible)} with images (of {len(articles)} total)")
    
    to_post = eligible[:4]
    if not to_post:
        print("⚠️ No articles with images to post. Done.")
        return
    
    print(f"🎯 Will post {len(to_post)} articles\n")
    
    # Init tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    posted = 0
    errors = 0
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"📰 {article['headline'][:80]}")
        print(f"🏷️ {article.get('category', 'unknown')} | slug: {article['slug'][:50]}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"📝 Post length: {len(post_text)} chars")
        
        # Download & upload image
        media_ids = None
        img_path = None
        if article.get('image_url'):
            print(f"📸 Downloading image...")
            img_path = download_image(article['image_url'])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  ✅ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠️ Image upload failed: {e}")
                    media_ids = None
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Mark as tweeted in Supabase
            mark_tweeted(article['id'])
            print(f"  ✅ Marked tweeted in Supabase")
            
            # Log tweet
            log_tweet(tweet_id, article)
            print(f"  ✅ Logged tweet ID")
            
            posted += 1
            
        except Exception as e:
            print(f"  ❌ Tweet failed: {e}")
            errors += 1
        
        # Cleanup temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting 30s before next post...")
            time.sleep(30)
    
    print(f"\n{'=' * 50}")
    print(f"📊 SUMMARY")
    print(f"  ✅ Posted: {posted}")
    print(f"  ❌ Errors: {errors}")
    print(f"  📋 Total eligible: {len(to_post)}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()
