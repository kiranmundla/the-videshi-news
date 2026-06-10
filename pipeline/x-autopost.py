#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts."""

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
MAX_FETCH = 20
MAX_POST = 4
DELAY_BETWEEN_POSTS = 30

# Category emoji mapping
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

def load_env(filepath):
    """Load key=value pairs from a file."""
    env = {}
    with open(os.path.expanduser(filepath)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                # Strip optional 'export ' prefix
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env

def fetch_untweeted_articles(sb_key):
    """Fetch recent published articles without tweeted_at."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit={MAX_FETCH}"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {sb_key}",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()

def compose_post(article):
    """Compose a long-form X post from article data."""
    category = (article.get("category") or "news").lower().strip()
    emoji = CATEGORY_EMOJI.get(category, "📰")
    category_label = category.upper().replace("-", " ")
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Build the summary from the body - extract key content
    # Strip markdown formatting for cleaner text
    body_clean = body.replace("**", "").replace("*", "").replace("##", "").replace("#", "").strip()
    
    # Take first ~2000 chars of body as source material for the LLM-like summary
    # Since we can't call an LLM here, we'll extract the first few meaningful paragraphs
    paragraphs = [p.strip() for p in body_clean.split("\n\n") if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first 2-3 paragraphs (skip if it looks like a heading)
    summary_parts = []
    total_chars = 0
    for p in paragraphs:
        # Skip very short lines (likely headings) and lines that start with special chars
        if len(p) < 50 or p.startswith("▸") or p.startswith("-") or p.startswith("Key"):
            continue
        if total_chars + len(p) > 600:
            break
        summary_parts.append(p)
        total_chars += len(p)
    
    summary_text = "\n\n".join(summary_parts[:3]) if summary_parts else subheadline
    
    # Extract key takeaways - look for bullet-like content or key facts
    takeaways = []
    for p in paragraphs:
        if p.startswith("▸") or p.startswith("- ") or p.startswith("• "):
            cleaned = p.lstrip("▸-• ").strip()
            if len(cleaned) > 20:
                takeaways.append(cleaned)
    
    # If no bullet points found, extract short factual sentences from body
    if len(takeaways) < 3:
        takeaways = []
        for p in paragraphs:
            sentences = [s.strip() for s in p.replace(". ", ".\n").split("\n") if len(s.strip()) > 30 and len(s.strip()) < 150]
            for s in sentences:
                if len(takeaways) >= 4:
                    break
                # Prefer sentences with numbers, names, or concrete facts
                if any(c.isdigit() for c in s) or "$" in s or "%" in s:
                    takeaways.append(s.rstrip("."))
            if len(takeaways) >= 4:
                break
        # Fall back to subheadline if still nothing
        if not takeaways and subheadline:
            takeaways = [subheadline]
    
    takeaways = takeaways[:4]
    takeaway_lines = "\n".join(f"▸ {t}" for t in takeaways)
    
    post = f"""{emoji} {category_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{summary_text}

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

def download_image(image_url):
    """Download article image to temp file. Returns path or None."""
    if not image_url:
        return None
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        resp.raise_for_status()
        
        # Determine extension
        content_type = resp.headers.get("content-type", "image/jpeg")
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
            print(f"  ⚠ Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        print(f"  ✓ Downloaded image ({size:,} bytes)")
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

def update_supabase(sb_key, article_id):
    """Mark article as tweeted in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    headers = {
        "apikey": sb_key,
        "Authorization": f"Bearer {sb_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    now = datetime.now(timezone.utc).isoformat()
    resp = requests.patch(url, headers=headers, json={"tweeted_at": now}, timeout=15)
    resp.raise_for_status()
    print(f"  ✓ Supabase updated (tweeted_at = {now})")

def log_tweet(tweet_id, article):
    """Append tweet to local log."""
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
    print(f"  ✓ Logged to tweet-log.json")

def main():
    # Load credentials
    tw_env = load_env("~/workspace/.env.twitter")
    sb_env = load_env("~/workspace/.env.supabase")
    
    consumer_key = tw_env["TWITTER_CONSUMER_KEY"]
    consumer_secret = tw_env["TWITTER_CONSUMER_SECRET"]
    access_token = tw_env["TWITTER_ACCESS_TOKEN"]
    access_token_secret = tw_env["TWITTER_ACCESS_TOKEN_SECRET"]
    sb_key = sb_env["SUPABASE_SERVICE_ROLE_KEY"]
    
    # Init tweepy clients
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api_v1 = tweepy.API(auth)
    
    # Fetch articles
    print("Fetching untweeted articles...")
    articles = fetch_untweeted_articles(sb_key)
    print(f"Found {len(articles)} untweeted articles")
    
    if not articles:
        print("Nothing to post.")
        return
    
    # Filter: must have image_url, take up to MAX_POST
    eligible = [a for a in articles if a.get("image_url")]
    print(f"{len(eligible)} have images (eligible for posting)")
    
    to_post = eligible[:MAX_POST]
    if not to_post:
        print("No eligible articles to post.")
        return
    
    print(f"\nWill post {len(to_post)} articles:\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        slug = article.get("slug", "?")
        headline = article.get("headline", "?")
        print(f"--- [{i+1}/{len(to_post)}] {headline[:80]}...")
        print(f"    slug: {slug}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"    Post length: {len(post_text)} chars")
        
        # Download and upload image
        img_path = download_image(article.get("image_url"))
        media_ids = None
        
        if img_path:
            try:
                media = api_v1.media_upload(filename=img_path)
                media_ids = [media.media_id]
                print(f"  ✓ Image uploaded to X (media_id: {media.media_id})")
            except Exception as e:
                print(f"  ⚠ Image upload failed: {e}")
                media_ids = None
            finally:
                if img_path and os.path.exists(img_path):
                    os.unlink(img_path)
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✓ Posted! {tweet_url}")
            
            # Update Supabase
            update_supabase(sb_key, article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Failed to post '{slug}': {e}"
            print(f"  ✗ {err_msg}")
            errors.append(err_msg)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {DELAY_BETWEEN_POSTS}s...")
            time.sleep(DELAY_BETWEEN_POSTS)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: Posted {posted}/{len(to_post)} articles")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
