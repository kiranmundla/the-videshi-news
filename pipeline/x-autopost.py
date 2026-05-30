#!/usr/bin/env python3
"""Post recently published Videshi articles to X with long-form formatting and images."""

import json
import os
import re
import requests
import tempfile
import time
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

sb_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def fetch_articles():
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=sb_headers,
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
    )
    r.raise_for_status()
    return r.json()


def strip_markdown(text):
    """Strip markdown formatting for plain text extraction."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_points(body_text, subheadline):
    """Extract key factual points from the article body."""
    points = []
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    
    # Look for sentences with numbers, percentages, names, dates
    priority_patterns = [
        r'\d+[\.,]?\d*\s*(?:per\s*cent|percent|%)',
        r'\$\d+',
        r'₹\d+',
        r'\d+\s*(?:billion|million|crore|lakh)',
        r'\d{4}',  # years
    ]
    
    scored = []
    for s in sentences:
        s = s.strip()
        if len(s) < 30 or len(s) > 200:
            continue
        score = 0
        for pat in priority_patterns:
            if re.search(pat, s, re.IGNORECASE):
                score += 1
        if score > 0:
            scored.append((score, s))
    
    scored.sort(key=lambda x: -x[0])
    
    for _, s in scored[:4]:
        points.append(s)
    
    # If we don't have enough, pull from subheadline
    if len(points) < 3 and subheadline:
        sub_parts = re.split(r'[.;]', subheadline)
        for part in sub_parts:
            part = part.strip()
            if part and len(part) > 20 and part not in points:
                points.append(part)
                if len(points) >= 4:
                    break
    
    # Still not enough? Take first substantive sentences
    if len(points) < 3:
        for s in sentences:
            s = s.strip()
            if len(s) > 40 and s not in points:
                points.append(s)
                if len(points) >= 4:
                    break
    
    return points[:4]


def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article["headline"]
    subheadline = article.get("subheadline", "")
    slug = article["slug"]
    body = strip_markdown(article.get("body", ""))
    
    # Build the summary — extract the most interesting parts from body
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 50]
    
    # Take the first 2-3 substantive paragraphs as the summary
    summary_parts = []
    total_words = 0
    for p in paragraphs[:6]:
        # Skip very short paragraphs or ones that look like section headers
        if len(p) < 60:
            continue
        words = len(p.split())
        if total_words + words > 250:
            if total_words < 100:
                # Need at least some content
                summary_parts.append(p)
                total_words += words
            break
        summary_parts.append(p)
        total_words += words
        if len(summary_parts) >= 3:
            break
    
    summary = "\n\n".join(summary_parts)
    
    # If summary is too long, trim it
    if len(summary) > 1200:
        summary = summary[:1200].rsplit('.', 1)[0] + '.'
    
    # Extract key takeaways
    key_points = extract_key_points(body, subheadline)
    
    takeaways = ""
    if key_points:
        takeaways_lines = [f"▸ {p}" for p in key_points]
        takeaways = "\n".join(takeaways_lines)
    
    # Rewrite headline - make it punchier
    display_headline = headline.upper() if len(headline) < 80 else headline
    
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{display_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure we're under 4000 chars
    if len(post) > 3900:
        # Trim summary
        while len(post) > 3900 and len(summary_parts) > 1:
            summary_parts.pop()
            summary = "\n\n".join(summary_parts)
            post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{display_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}

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
        ct = r.headers.get("Content-Type", "")
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
        print(f"  ⚠ Image download failed: {e}")
        return None


def main():
    print("=" * 60)
    print("The Videshi → X Auto-Poster")
    print(f"Run time: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # Fetch articles
    articles = fetch_articles()
    print(f"\nFound {len(articles)} untweeted articles")
    
    if not articles:
        print("No articles to post. Done.")
        return
    
    # Filter to those with images, take up to 4
    candidates = [a for a in articles if a.get("image_url")]
    if not candidates:
        print("No articles with images found. Done.")
        return
    
    to_post = candidates[:4]
    print(f"Selected {len(to_post)} articles to post:\n")
    for a in to_post:
        print(f"  • [{a['category']}] {a['headline'][:70]}...")
    
    # Init tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Post loop
    posted = 0
    errors = []
    tweet_urls = []
    
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    for i, article in enumerate(to_post):
        print(f"\n--- Posting {i+1}/{len(to_post)}: {article['headline'][:60]}... ---")
        
        try:
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
                        print(f"  ✓ Image uploaded (media_id: {media.media_id})")
                    except Exception as e:
                        print(f"  ⚠ Image upload failed: {e}")
                        media_ids = None
            
            # Post tweet
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            tweet_urls.append(tweet_url)
            print(f"  ✓ Posted! {tweet_url}")
            
            # Clean up temp image
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)
            
            # Update Supabase
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                headers=sb_headers,
                json={"tweeted_at": datetime.utcnow().isoformat() + "Z"},
            )
            if patch_r.status_code < 300:
                print(f"  ✓ Supabase updated (tweeted_at set)")
            else:
                print(f"  ⚠ Supabase update failed: {patch_r.status_code} {patch_r.text}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": article["slug"],
                "posted_at": datetime.utcnow().isoformat() + "Z",
            }
            with open(log_path, "w") as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
            # Wait between posts
            if i < len(to_post) - 1:
                print("  ⏳ Waiting 30s before next post...")
                time.sleep(30)
                
        except Exception as e:
            errors.append({"article": article["headline"][:60], "error": str(e)})
            print(f"  ✗ ERROR: {e}")
            # Clean up temp image on error
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if tweet_urls:
        print("\nTweet URLs:")
        for url in tweet_urls:
            print(f"  {url}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  • {e['article']}: {e['error']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
