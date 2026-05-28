#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SERVICE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
}

# Category emoji mapping
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


def strip_markdown(text):
    """Strip markdown formatting to extract plain text."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_content(body, subheadline):
    """Extract the most interesting content from an article body."""
    plain = strip_markdown(body or "")
    paragraphs = [p.strip() for p in plain.split("\n\n") if p.strip() and len(p.strip()) > 40]
    return paragraphs, plain


def compose_post(article):
    """Compose a long-form X post for the article."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    slug = article["slug"]
    headline = article["headline"]
    subheadline = article.get("subheadline", "")
    body = article.get("body", "")
    
    paragraphs, plain_text = extract_key_content(body, subheadline)
    
    # Build summary from article body (2-3 paragraphs, 150-250 words target)
    summary_parts = []
    word_count = 0
    for p in paragraphs[:8]:  # scan first 8 paragraphs
        words = len(p.split())
        if word_count + words > 280:
            break
        if word_count + words > 150 and len(summary_parts) >= 2:
            break
        summary_parts.append(p)
        word_count += words
        if len(summary_parts) >= 3:
            break
    
    # If body was too short, use subheadline
    if word_count < 30 and subheadline:
        summary_parts = [subheadline]
    
    summary = "\n\n".join(summary_parts)
    
    # Extract key takeaways (look for numbers, names, specific facts)
    takeaways = []
    # Try to find bullet-like content or sentences with numbers
    for p in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', p)
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and len(s) < 200:
                # Prefer sentences with numbers, dollar amounts, percentages
                if re.search(r'(\$[\d,.]+|\d+%|\d{4}|billion|million|trillion|\d+ )', s):
                    if s not in takeaways and len(takeaways) < 5:
                        takeaways.append(s)
    
    # If not enough takeaways, grab key sentences
    if len(takeaways) < 3:
        for p in paragraphs[1:6]:
            sentences = re.split(r'(?<=[.!?])\s+', p)
            for s in sentences:
                s = s.strip()
                if 30 < len(s) < 180 and s not in takeaways:
                    takeaways.append(s)
                    if len(takeaways) >= 4:
                        break
            if len(takeaways) >= 4:
                break
    
    takeaways = takeaways[:4]
    
    # Build the post
    lines = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
        summary,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    
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
    
    post_text = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        summary_words = summary.split()
        summary = " ".join(summary_words[:120]) + "..."
        lines[6] = summary
        post_text = "\n".join(lines)
    
    return post_text


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
        
        # Verify file has content
        if os.path.getsize(tmp.name) < 1000:
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def main():
    # Fetch untweeted articles
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
        headers=SB_HEADERS,
    )
    resp.raise_for_status()
    articles = resp.json()
    print(f"📋 Found {len(articles)} untweeted articles")
    
    # Filter to those with images, take top MAX_POSTS
    candidates = [a for a in articles if a.get("image_url")]
    if not candidates:
        print("❌ No articles with images to post")
        return
    
    to_post = candidates[:MAX_POSTS]
    print(f"📝 Will post {len(to_post)} articles\n")
    
    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Tweet log
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    posted = 0
    errors = []
    tweet_urls = []
    
    for i, article in enumerate(to_post):
        slug = article["slug"]
        headline = article["headline"]
        cat = article.get("category", "?")
        print(f"{'─'*50}")
        print(f"[{i+1}/{len(to_post)}] [{cat}] {headline[:70]}...")
        
        # Compose the post
        post_text = compose_post(article)
        print(f"  📝 Post length: {len(post_text)} chars")
        
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
                    print(f"  🖼️ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠️ Image upload failed: {e}")
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
            tweet_urls.append(tweet_url)
            
            # Update Supabase
            patch_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                json={"tweeted_at": datetime.utcnow().isoformat() + "Z"},
                headers=SB_HEADERS,
            )
            if patch_resp.status_code < 300:
                print(f"  📦 Supabase updated (tweeted_at set)")
            else:
                print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": slug,
                "posted_at": datetime.utcnow().isoformat() + "Z",
            }
            with open(log_path, "w") as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"[{slug}] {e}"
            print(f"  ❌ Post failed: {e}")
            errors.append(err_msg)
        
        finally:
            # Clean up temp image
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 SUMMARY: {posted}/{len(to_post)} posted successfully")
    if tweet_urls:
        print("🔗 Tweet URLs:")
        for url in tweet_urls:
            print(f"   {url}")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   {e}")


if __name__ == "__main__":
    main()
