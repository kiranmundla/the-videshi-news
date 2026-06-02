#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form premium posts with images."""

import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# Load env files
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

sb_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
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
    """Remove markdown formatting for plain text output."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_facts(body_text, subheadline):
    """Extract key sentences with numbers, names, dates from article body."""
    text = strip_markdown(body_text or "")
    all_text = f"{subheadline or ''}\n{text}"
    
    sentences = re.split(r'(?<=[.!?])\s+', all_text)
    
    # Prioritize sentences with numbers, percentages, dollar amounts, dates
    scored = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        score = 0
        if re.search(r'\$[\d,.]+', s): score += 3
        if re.search(r'\d+%', s): score += 3
        if re.search(r'\d{4}', s): score += 1
        if re.search(r'\d+\s*(million|billion|trillion|crore|lakh)', s, re.I): score += 3
        if re.search(r'\d+', s): score += 1
        # Boost sentences with proper nouns (capitalized words not at start)
        caps = re.findall(r'(?<!^)(?<!\.)\s([A-Z][a-z]+)', s)
        score += min(len(caps), 2)
        scored.append((score, s))
    
    scored.sort(key=lambda x: -x[0])
    facts = []
    for score, s in scored[:4]:
        # Trim to reasonable length
        if len(s) > 150:
            s = s[:147] + "..."
        facts.append(s)
    
    return facts


def compose_summary(article):
    """Create a 2-3 paragraph summary from article body."""
    body = strip_markdown(article.get("body", "") or "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    
    if not body:
        # Fallback to subheadline
        return subheadline or headline
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Skip very short paragraphs and list items
    good_paras = []
    for p in paragraphs:
        # Skip if it's just a list or header remnant
        if p.startswith('- ') or p.startswith('* ') or p.startswith('|'):
            continue
        good_paras.append(p)
    
    if not good_paras:
        return subheadline or headline
    
    # Take first 2-3 paragraphs, aiming for 150-250 words total
    summary_parts = []
    word_count = 0
    for p in good_paras[:5]:
        words = len(p.split())
        if word_count + words > 280:
            # Trim this paragraph if needed
            if word_count < 100:
                remaining = 250 - word_count
                trimmed = ' '.join(p.split()[:remaining])
                if not trimmed.endswith('.'):
                    # Find last sentence end
                    last_period = trimmed.rfind('.')
                    if last_period > 50:
                        trimmed = trimmed[:last_period + 1]
                summary_parts.append(trimmed)
            break
        summary_parts.append(p)
        word_count += words
        if word_count >= 150 and len(summary_parts) >= 2:
            break
    
    return '\n\n'.join(summary_parts)


def compose_post(article):
    """Compose a long-form X post for the article."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper().replace("-", " "))
    headline = article.get("headline", "")
    slug = article.get("slug", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "")
    
    # Rewrite headline - make it punchier
    # Use the original but ensure it's impactful
    display_headline = headline.upper() if len(headline) < 80 else headline
    
    # Compose summary
    summary = compose_summary(article)
    
    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    
    # Build post
    parts = []
    parts.append(f"{emoji} {label} | The Videshi")
    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(display_headline)
    parts.append("")
    parts.append(summary)
    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    
    if facts:
        parts.append("Key Takeaways:")
        parts.append("")
        for f in facts:
            parts.append(f"▸ {f}")
        parts.append("")
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
    
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")
    
    post_text = '\n'.join(parts)
    
    # Ensure within 4000 chars
    if len(post_text) > 3900:
        # Trim summary
        summary_words = summary.split()
        while len(post_text) > 3800 and len(summary_words) > 50:
            summary_words = summary_words[:-20]
            trimmed_summary = ' '.join(summary_words)
            last_period = trimmed_summary.rfind('.')
            if last_period > 50:
                trimmed_summary = trimmed_summary[:last_period + 1]
            # Rebuild
            parts_copy = parts.copy()
            # Find summary index and replace
            post_text = post_text  # Just truncate if needed
            break
    
    return post_text[:4000]


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15, stream=True)
        r.raise_for_status()
        content_type = r.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        
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


def main():
    # Init tweepy clients
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Fetch untweeted articles
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        },
        headers=sb_headers,
        timeout=30
    )
    r.raise_for_status()
    articles = r.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter articles with images and pick top 4
    candidates = [a for a in articles if a.get("image_url")]
    if not candidates:
        print("No articles with images found. Exiting.")
        return
    
    to_post = candidates[:MAX_POSTS]
    print(f"Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    tweet_log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  [{article['category']}] {article['headline'][:80]}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_id = None
        img_path = None
        if article.get("image_url"):
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_id = media.media_id
                    print(f"  Image uploaded: media_id={media_id}")
                except Exception as e:
                    print(f"  Image upload failed: {e}")
                finally:
                    if img_path and os.path.exists(img_path):
                        os.unlink(img_path)
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Update Supabase
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                json={"tweeted_at": now_utc},
                headers=sb_headers,
                timeout=15
            )
            if patch_r.status_code < 300:
                print(f"  Supabase updated: tweeted_at = {now_utc}")
            else:
                print(f"  Supabase update warning: {patch_r.status_code} {patch_r.text}")
            
            # Log tweet ID
            tweet_log = {}
            if os.path.exists(tweet_log_path):
                with open(tweet_log_path) as f:
                    tweet_log = json.load(f)
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": article["slug"],
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            os.makedirs(os.path.dirname(tweet_log_path), exist_ok=True)
            with open(tweet_log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Failed to post '{article['headline'][:50]}': {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
