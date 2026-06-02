#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import re
from datetime import datetime, timezone

import requests
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
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

def fetch_articles():
    """Fetch up to 20 recent published articles not yet tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null"
        "&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def strip_markdown(text):
    """Strip markdown formatting to plain text."""
    if not text:
        return ""
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # images
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links
    text = re.sub(r'#{1,6}\s*', '', text)  # headers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # inline code
    text = re.sub(r'>\s*', '', text)  # blockquotes
    text = re.sub(r'[-*+]\s+', '', text)  # list items
    text = re.sub(r'\n{3,}', '\n\n', text)  # multiple newlines
    return text.strip()

def extract_key_facts(body_text, subheadline):
    """Extract key facts from the article body for takeaways."""
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    # Filter for sentences with numbers, names, or strong factual content
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts, dates
        if re.search(r'\d', s) or re.search(r'%|\$|billion|million|crore|lakh', s, re.I):
            fact_sentences.append(s)
    
    # Also consider subheadline
    if subheadline:
        fact_sentences.insert(0, subheadline)
    
    return fact_sentences[:5]

def compose_post(article):
    """Compose a long-form X post for an article."""
    category = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(category, "📰")
    category_label = category.upper().replace("-", " ")
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = strip_markdown(article.get("body", ""))
    
    # Build the summary from the body
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 30]
    
    # Take first few substantial paragraphs for the summary
    summary_parts = []
    total_chars = 0
    for p in paragraphs[:8]:
        if total_chars > 600:
            break
        # Skip very short paragraphs or section headers
        if len(p) < 40:
            continue
        summary_parts.append(p)
        total_chars += len(p)
    
    summary_text = '\n\n'.join(summary_parts[:3])
    
    # Truncate summary if too long
    if len(summary_text) > 800:
        summary_text = summary_text[:797] + "..."
    
    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    takeaways = []
    for f in facts[:4]:
        f = f.strip().rstrip('.')
        if len(f) > 150:
            f = f[:147] + "..."
        takeaways.append(f"▸ {f}")
    
    # If we don't have enough takeaways from numbers, take first strong sentences
    if len(takeaways) < 3:
        sentences = re.split(r'(?<=[.!?])\s+', body)
        for s in sentences:
            if len(takeaways) >= 4:
                break
            s = s.strip()
            if 30 < len(s) < 160 and s not in [t[2:] for t in takeaways]:
                takeaways.append(f"▸ {s.rstrip('.')}")
    
    takeaway_block = '\n'.join(takeaways[:4])
    
    # Assemble the post
    post = f"""{emoji} {category_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_block}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure we're within limits
    if len(post) > 3900:
        # Trim summary
        summary_text = summary_text[:400] + "..."
        post = f"""{emoji} {category_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_block}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15, stream=True)
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
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None

def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    resp = requests.patch(url, json={"tweeted_at": now}, headers=SUPABASE_HEADERS, timeout=15)
    resp.raise_for_status()
    print(f"  Supabase updated: tweeted_at = {now}")

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
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z",
    }
    
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=== Videshi X Autopost ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}Z\n")
    
    # Fetch articles
    articles = fetch_articles()
    print(f"Found {len(articles)} untweeted articles")
    
    if not articles:
        print("Nothing to post.")
        return
    
    # Filter: must have image_url
    with_images = [a for a in articles if a.get("image_url")]
    print(f"Articles with images: {len(with_images)}")
    
    # Pick up to 4
    to_post = with_images[:4]
    print(f"Will post: {len(to_post)}\n")
    
    if not to_post:
        print("No articles with images to post.")
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
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  Headline: {article['headline']}")
        print(f"  Category: {article.get('category', 'unknown')}")
        print(f"  Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  Image uploaded: media_id={media.media_id}")
                except Exception as e:
                    print(f"  Image upload failed: {e}")
                    media_ids = None
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Update Supabase
            mark_tweeted(article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            error_msg = f"Tweet failed for '{article['headline']}': {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
        
        # Clean up temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  Waiting 30s...")
            time.sleep(30)
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("No errors.")
    print("Done.")

if __name__ == "__main__":
    main()
