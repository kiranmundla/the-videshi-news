#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, textwrap
from datetime import datetime, timezone

import requests
import tweepy

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
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


def extract_key_content(body, max_chars=3000):
    """Extract the most useful content from article markdown body."""
    if not body:
        return ""
    # Strip markdown images and links formatting, keep text
    import re
    text = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Strip markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Strip bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text[:max_chars].strip()


def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    slug = article.get("slug", "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body_text = extract_key_content(article.get("body", ""))

    # Build the content we'll use for AI-like summarization
    # Since we don't have an LLM call here, we'll extract smartly from the body
    
    # Get first few meaningful paragraphs for summary
    paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build summary (2-3 paragraphs, ~150-250 words)
    summary_parts = []
    word_count = 0
    for p in paragraphs[:5]:
        words = p.split()
        if word_count + len(words) > 250:
            # Take partial if we haven't got enough yet
            if word_count < 100:
                remaining = 250 - word_count
                summary_parts.append(' '.join(words[:remaining]) + '...')
            break
        summary_parts.append(p)
        word_count += len(words)
    
    summary = '\n\n'.join(summary_parts) if summary_parts else subheadline or headline
    
    # Extract key facts for takeaways
    # Look for sentences with numbers, names, percentages
    import re
    all_sentences = re.split(r'(?<=[.!?])\s+', body_text)
    fact_sentences = []
    for s in all_sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, dollar amounts, percentages, or proper nouns
        if re.search(r'\d+|%|\$|billion|million|crore|lakh', s, re.IGNORECASE):
            fact_sentences.append(s)
    
    # If not enough fact sentences, use subheadline parts
    if len(fact_sentences) < 3 and subheadline:
        for part in subheadline.split('. '):
            if part.strip() and part.strip() not in fact_sentences:
                fact_sentences.append(part.strip())
    
    # Take top 3-4 takeaways
    takeaways = fact_sentences[:4] if fact_sentences else [subheadline or headline]
    
    # Compose the post
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━"
    
    takeaway_lines = '\n'.join(f"▸ {t}" for t in takeaways)
    
    post = f"""{emoji} {label} | The Videshi

{separator}

{headline.upper()}

{summary}

{separator}

Key Takeaways:

{takeaway_lines}

{separator}

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary_words = summary.split()
        summary = ' '.join(summary_words[:120]) + '...'
        post = f"""{emoji} {label} | The Videshi

{separator}

{headline.upper()}

{summary}

{separator}

Key Takeaways:

{takeaway_lines}

{separator}

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post


def download_image(url):
    """Download image to temp file. Returns path or None."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get('content-type', '')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def main():
    print(f"🐦 X Autopost — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    
    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"📋 Found {len(articles)} untweeted articles")
    
    # Filter: must have image_url, take up to 4
    candidates = [a for a in articles if a.get("image_url")]
    if not candidates:
        print("✅ No articles with images to post. Done.")
        return
    
    to_post = candidates[:4]
    print(f"📝 Will post {len(to_post)} articles\n")
    
    # Setup tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth_v1 = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth_v1)
    
    # Tweet log
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        slug = article.get('slug', 'unknown')
        headline = article.get('headline', 'No headline')
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  📰 {headline}")
        print(f"  🔗 thevideshi.com/articles/{slug}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  📏 Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        img_path = None
        if article.get('image_url'):
            img_path = download_image(article['image_url'])
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
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Update Supabase
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}"
            patch_resp = requests.patch(
                patch_url,
                headers=SUPABASE_HEADERS,
                json={"tweeted_at": now_utc},
                timeout=15
            )
            if patch_resp.status_code < 300:
                print(f"  📝 Supabase updated (tweeted_at set)")
            else:
                print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article['id'],
                "slug": slug,
                "posted_at": now_utc
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
        except Exception as e:
            error_msg = f"{headline}: {e}"
            errors.append(error_msg)
            print(f"  ❌ Failed: {e}")
        
        # Clean up temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting 30s...")
            time.sleep(30)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
    print("Done!")


if __name__ == "__main__":
    main()
