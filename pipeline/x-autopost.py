#!/usr/bin/env python3
"""Post recently published Videshi articles to X with long-form premium posts."""

import json
import os
import re
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

CATEGORY_LABELS = {
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

def strip_markdown(text):
    """Strip markdown formatting to get plain text for summarization context."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABELS.get(cat, cat.upper())
    headline = article["headline"]
    subheadline = article.get("subheadline") or ""
    slug = article["slug"]
    body_raw = article.get("body") or ""
    body_text = strip_markdown(body_raw)

    # Extract key content from the body for summary
    # Take the first ~1500 chars of body for context
    body_excerpt = body_text[:2000] if body_text else subheadline

    # Build the post content using AI-style extraction
    # We'll create a structured summary from the article content
    
    # Extract sentences for key takeaways
    sentences = [s.strip() for s in re.split(r'[.\n]', body_text) if len(s.strip()) > 30]
    
    # Build summary paragraphs from the body
    paragraphs = [p.strip() for p in body_text.split('\n\n') if len(p.strip()) > 40]
    
    # Create a 2-3 paragraph summary (take first meaningful paragraphs)
    summary_parts = []
    char_count = 0
    for p in paragraphs[:6]:
        if char_count > 600:
            break
        # Skip very short or heading-like paragraphs
        if len(p) < 40:
            continue
        summary_parts.append(p)
        char_count += len(p)
    
    summary = "\n\n".join(summary_parts[:3]) if summary_parts else subheadline

    # Trim summary if too long
    if len(summary) > 800:
        summary = summary[:797] + "..."

    # Extract key takeaways - look for sentences with numbers, names, or key facts
    takeaways = []
    for s in sentences:
        s = s.strip()
        if len(s) > 30 and len(s) < 200:
            # Prefer sentences with numbers, percentages, or proper nouns
            if any(c.isdigit() for c in s) or any(word[0].isupper() for word in s.split() if word):
                if s not in summary:
                    takeaways.append(s)
        if len(takeaways) >= 6:
            break
    
    # Take 3-4 best takeaways
    takeaways = takeaways[:4] if takeaways else [subheadline] if subheadline else []
    
    takeaway_text = "\n".join(f"▸ {t}" for t in takeaways) if takeaways else ""

    # Build the post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    if takeaway_text:
        post += f"""

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━"""

    post += f"""

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        excess = len(post) - 3800
        summary = summary[:len(summary) - excess] + "..."
        # Reconstruct
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━"""
        if takeaway_text:
            post += f"""

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━"""
        post += f"""

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


def main():
    # Fetch untweeted articles
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    params = {
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    }
    
    resp = requests.get(url, headers=SUPABASE_HEADERS, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"ERROR: Failed to fetch articles: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    articles = resp.json()
    print(f"Found {len(articles)} untweeted articles")
    
    if not articles:
        print("No articles to post. Done.")
        return
    
    # Filter to articles with images, take up to 4
    eligible = [a for a in articles if a.get("image_url")]
    print(f"{len(eligible)} articles have images")
    
    to_post = eligible[:4]
    print(f"Will post {len(to_post)} articles")
    
    # Setup tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    # v1.1 API for media upload
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
    
    for i, article in enumerate(to_post):
        print(f"\n--- Article {i+1}/{len(to_post)} ---")
        print(f"  Headline: {article['headline']}")
        print(f"  Slug: {article['slug']}")
        print(f"  Category: {article.get('category', 'unknown')}")
        
        try:
            post_text = compose_post(article)
            print(f"  Post length: {len(post_text)} chars")
            
            # Try to upload image
            media_ids = None
            if article.get("image_url"):
                try:
                    img_resp = requests.get(article["image_url"], timeout=15)
                    if img_resp.status_code == 200:
                        # Determine extension from content-type
                        ct = img_resp.headers.get("content-type", "image/jpeg")
                        ext = ".jpg"
                        if "png" in ct:
                            ext = ".png"
                        elif "webp" in ct:
                            ext = ".webp"
                        elif "gif" in ct:
                            ext = ".gif"
                        
                        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                            tmp.write(img_resp.content)
                            tmp_path = tmp.name
                        
                        media = api_v1.media_upload(filename=tmp_path)
                        media_ids = [media.media_id]
                        os.unlink(tmp_path)
                        print(f"  Image uploaded: media_id={media.media_id}")
                    else:
                        print(f"  Image download failed: {img_resp.status_code}")
                except Exception as e:
                    print(f"  Image upload error (posting without image): {e}")
                    # Clean up temp file if it exists
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            
            # Post tweet
            tweet_kwargs = {"text": post_text}
            if media_ids:
                tweet_kwargs["media_ids"] = media_ids
            
            tweet_resp = client.create_tweet(**tweet_kwargs)
            tweet_id = tweet_resp.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Update Supabase
            patch_url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}"
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_resp = requests.patch(
                patch_url,
                headers=SUPABASE_HEADERS,
                json={"tweeted_at": now_utc},
                timeout=15
            )
            if patch_resp.status_code in (200, 204):
                print(f"  Supabase updated: tweeted_at={now_utc}")
            else:
                print(f"  WARNING: Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": article["slug"],
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
            # Wait between posts
            if i < len(to_post) - 1:
                print("  Waiting 30s before next post...")
                time.sleep(30)
                
        except Exception as e:
            error_msg = f"{article['slug']}: {str(e)}"
            errors.append(error_msg)
            print(f"  ❌ Error: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print("Done.")


if __name__ == "__main__":
    main()
