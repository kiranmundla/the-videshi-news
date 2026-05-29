#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime, timezone

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_FETCH = 20
MAX_POST = 4
DELAY_BETWEEN = 30  # seconds

# Load env
def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env

twitter_env = load_env(os.path.expanduser("~/workspace/.env.twitter"))
supabase_env = load_env(os.path.expanduser("~/workspace/.env.supabase"))

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
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

def get_category_label(cat):
    """Return a display label for the category."""
    labels = {
        "news": "NEWS",
        "immigration": "IMMIGRATION",
        "nri-world": "NRI WORLD",
        "travel": "TRAVEL",
        "lifestyle": "LIFESTYLE",
        "lifestyle-health": "LIFESTYLE & HEALTH",
        "markets": "MARKETS & FINANCE",
        "markets-finance": "MARKETS & FINANCE",
        "technology": "TECHNOLOGY",
        "sports": "SPORTS",
        "entertainment": "ENTERTAINMENT",
        "food": "FOOD",
    }
    return labels.get(cat, cat.upper() if cat else "NEWS")

def fetch_untweeted_articles():
    """Fetch up to MAX_FETCH recent published articles without tweeted_at."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit={MAX_FETCH}"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SB_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def compose_post(article):
    """Compose a long-form X post from the article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = get_category_label(cat)
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "")
    
    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("**", "").replace("##", "").replace("###", "").replace("*", "").replace("`", "")
    # Take first ~2000 chars of body for context
    body_excerpt = body_clean[:2000]
    
    # Build the post - we'll return a template that needs AI synthesis
    # For now, build a structured post from available data
    post = compose_smart_post(emoji, label, headline, subheadline, body_excerpt, slug)
    
    # Ensure within limits
    if len(post) > 3900:
        # Trim the summary section
        lines = post.split('\n')
        while len('\n'.join(lines)) > 3900 and len(lines) > 10:
            # Remove lines from middle (summary area)
            mid = len(lines) // 2
            lines.pop(mid)
        post = '\n'.join(lines)
    
    return post

def compose_smart_post(emoji, label, headline, subheadline, body_excerpt, slug):
    """Compose a journalist-style long-form post."""
    # Extract sentences from body for summary
    sentences = []
    for s in body_excerpt.replace('\n', ' ').split('. '):
        s = s.strip()
        if len(s) > 20:
            sentences.append(s.rstrip('.') + '.')
    
    # Build 2-3 paragraph summary from first ~8 meaningful sentences
    summary_sentences = sentences[:8]
    
    # Split into paragraphs
    if len(summary_sentences) >= 6:
        para1 = ' '.join(summary_sentences[:3])
        para2 = ' '.join(summary_sentences[3:6])
        para3 = ' '.join(summary_sentences[6:8]) if len(summary_sentences) > 6 else ""
    elif len(summary_sentences) >= 3:
        para1 = ' '.join(summary_sentences[:2])
        para2 = ' '.join(summary_sentences[2:])
        para3 = ""
    else:
        para1 = ' '.join(summary_sentences)
        para2 = ""
        para3 = ""
    
    # Extract key takeaways from subheadline and body
    takeaways = extract_takeaways(subheadline, body_excerpt)
    
    # Build post
    parts = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
    ]
    
    if para1:
        parts.append(para1)
        parts.append("")
    if para2:
        parts.append(para2)
        parts.append("")
    if para3:
        parts.append(para3)
        parts.append("")
    
    if takeaways:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        for t in takeaways[:4]:
            parts.append(f"▸ {t}")
        parts.append("")
    
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")
    
    return '\n'.join(parts)

def extract_takeaways(subheadline, body):
    """Extract 3-4 key fact bullets from article content."""
    takeaways = []
    
    # Use subheadline as first takeaway if meaningful
    if subheadline and len(subheadline) > 15:
        takeaways.append(subheadline.rstrip('.'))
    
    # Look for sentences with numbers, names, or key facts
    sentences = body.replace('\n', ' ').split('. ')
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts, names
        has_data = any(c.isdigit() for c in s) or '$' in s or '%' in s
        if has_data and len(takeaways) < 4:
            clean = s.rstrip('.').strip()
            if clean and clean not in takeaways:
                takeaways.append(clean)
    
    # If still need more, take strong opening sentences
    if len(takeaways) < 3:
        for s in sentences[1:6]:
            s = s.strip().rstrip('.')
            if len(s) > 25 and len(s) < 180 and s not in takeaways:
                takeaways.append(s)
                if len(takeaways) >= 4:
                    break
    
    return takeaways[:4]

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

def post_tweet(client, api_v1, text, image_path=None):
    """Post a tweet with optional image. Returns tweet response."""
    media_ids = None
    if image_path:
        try:
            media = api_v1.media_upload(filename=image_path)
            media_ids = [media.media_id]
            print(f"  📷 Image uploaded (media_id: {media.media_id})")
        except Exception as e:
            print(f"  ⚠️ Image upload failed, posting without: {e}")
            media_ids = None
    
    kwargs = {"text": text}
    if media_ids:
        kwargs["media_ids"] = media_ids
    
    response = client.create_tweet(**kwargs)
    return response

def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    resp = requests.patch(url, headers=SB_HEADERS, json={"tweeted_at": now}, timeout=15)
    if resp.status_code < 300:
        print(f"  ✅ Supabase updated (tweeted_at set)")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")

def log_tweet(tweet_id, article):
    """Log tweet to local JSON file."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        try:
            with open(log_path) as f:
                tweet_log = json.load(f)
        except:
            pass
    
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article.get("slug", ""),
        "posted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }
    
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("🐦 The Videshi X Auto-Poster")
    print("=" * 40)
    
    # Init tweepy clients
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Fetch articles
    print("\n📥 Fetching untweeted articles...")
    articles = fetch_untweeted_articles()
    print(f"   Found {len(articles)} untweeted articles")
    
    if not articles:
        print("\n✅ No articles to post. Done.")
        return
    
    # Filter: must have image_url and slug
    eligible = [a for a in articles if a.get("image_url") and a.get("slug")]
    print(f"   {len(eligible)} eligible (with image_url + slug)")
    
    if not eligible:
        print("\n✅ No eligible articles to post. Done.")
        return
    
    to_post = eligible[:MAX_POST]
    print(f"\n📝 Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  📰 {article['headline'][:80]}...")
        print(f"  🏷️ Category: {article.get('category', 'unknown')}")
        print(f"  🔗 Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  📏 Post length: {len(post_text)} chars")
        
        # Download image
        img_path = None
        if article.get("image_url"):
            print(f"  🖼️ Downloading image...")
            img_path = download_image(article["image_url"])
        
        # Post tweet
        try:
            response = post_tweet(client, api_v1, post_text, img_path)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Update Supabase
            mark_tweeted(article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Failed to post: {error_msg}")
            errors.append({"headline": article["headline"][:60], "error": error_msg})
        finally:
            # Clean up temp image
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)
        
        # Delay between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {DELAY_BETWEEN}s before next post...")
            time.sleep(DELAY_BETWEEN)
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📊 SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"   • {e['headline']}: {e['error']}")
    print("=" * 40)

if __name__ == "__main__":
    main()
