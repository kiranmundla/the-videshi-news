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
MAX_ARTICLES = 4
DELAY_BETWEEN_POSTS = 30

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            if '=' in line:
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

# Category emoji mapping
CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "culture": "🧘",
    "lifestyle-health": "🧘",
    "markets": "📈",
    "markets-finance": "📈",
    "economy": "📈",
    "technology": "💻",
    "tech": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

CATEGORY_LABELS = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle": "LIFESTYLE",
    "culture": "LIFESTYLE & CULTURE",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "markets-finance": "MARKETS & FINANCE",
    "economy": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "tech": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def fetch_untweeted_articles():
    """Fetch up to 20 recent published articles not yet tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=get_supabase_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()

def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABELS.get(cat, cat.upper())
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body - strip markdown formatting
    body_clean = body.replace("##", "").replace("**", "").replace("*", "")
    # Get first ~1500 chars of body for context
    body_excerpt = body_clean[:2000]
    
    # Build the summary paragraphs from body content
    # Split into paragraphs and pick the meatiest ones
    paragraphs = [p.strip() for p in body_clean.split('\n\n') if p.strip() and len(p.strip()) > 50]
    
    # Skip the first paragraph if it's very similar to headline/subheadline
    summary_paras = []
    for p in paragraphs:
        if len(summary_paras) >= 3:
            break
        # Skip very short paras or those that are just headers
        if len(p) < 40:
            continue
        # Skip if it's just a repeat of headline
        if p.strip().lower()[:30] == headline.lower()[:30]:
            continue
        summary_paras.append(p)
    
    # Build summary text (aim for 150-250 words)
    summary = "\n\n".join(summary_paras[:3])
    # Trim if too long
    if len(summary) > 1200:
        summary = summary[:1200]
        # Cut at last sentence
        last_period = summary.rfind('.')
        if last_period > 600:
            summary = summary[:last_period + 1]
    
    # Extract key takeaways from body
    takeaways = extract_takeaways(body_clean, subheadline)
    takeaway_text = "\n".join(f"▸ {t}" for t in takeaways)
    
    # Compose full post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure within 4000 char limit
    if len(post) > 3900:
        # Trim summary further
        summary_short = summary[:800]
        last_period = summary_short.rfind('.')
        if last_period > 300:
            summary_short = summary_short[:last_period + 1]
        
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_short}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def extract_takeaways(body, subheadline):
    """Extract 3-4 key facts from the article body."""
    takeaways = []
    
    # Look for sentences with numbers, names, dates
    sentences = []
    for para in body.split('\n'):
        para = para.strip()
        if not para or len(para) < 20:
            continue
        # Split into sentences
        for sent in para.replace('. ', '.\n').split('\n'):
            sent = sent.strip()
            if len(sent) > 30 and len(sent) < 200:
                sentences.append(sent)
    
    # Prioritize sentences with numbers or key indicators
    priority = []
    normal = []
    for s in sentences:
        has_number = any(c.isdigit() for c in s)
        has_dollar = '$' in s or '₹' in s or '%' in s
        has_quote = '"' in s or '\u201c' in s
        if has_number or has_dollar or has_quote:
            priority.append(s)
        else:
            normal.append(s)
    
    # Pick from priority first, then normal
    candidates = priority + normal
    seen_starts = set()
    for s in candidates:
        if len(takeaways) >= 4:
            break
        # Deduplicate by first 20 chars
        start = s[:20].lower()
        if start in seen_starts:
            continue
        seen_starts.add(start)
        # Clean up
        s = s.strip().rstrip('.')
        if s:
            takeaways.append(s)
    
    # If we have subheadline and less than 3 takeaways, add it
    if subheadline and len(takeaways) < 3:
        takeaways.insert(0, subheadline.rstrip('.'))
    
    return takeaways[:4]

def download_image(image_url):
    """Download image to temp file, return path or None."""
    if not image_url or not image_url.strip():
        return None
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True
        )
        resp.raise_for_status()
        
        # Determine extension
        content_type = resp.headers.get('content-type', '')
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
        
        # Verify file size > 0
        if os.path.getsize(tmp.name) < 100:
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def update_tweeted_at(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    resp = requests.patch(
        url,
        headers=get_supabase_headers(),
        json={"tweeted_at": now},
        timeout=15
    )
    resp.raise_for_status()
    return now

def log_tweet(tweet_id, article):
    """Log tweet ID locally for future management."""
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
        "slug": article.get("slug", ""),
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
    }
    
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=" * 60)
    print("🐦 The Videshi — X Autopost (Long-Form)")
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Fetch articles
    print("\n📥 Fetching untweeted articles...")
    articles = fetch_untweeted_articles()
    print(f"   Found {len(articles)} untweeted articles")
    
    if not articles:
        print("\n✅ No articles to post. All caught up!")
        return
    
    # Filter: must have image_url and slug
    eligible = [a for a in articles if a.get("image_url") and a.get("slug")]
    print(f"   {len(eligible)} have images (eligible for posting)")
    
    if not eligible:
        print("\n⚠️ No eligible articles (all missing images). Skipping.")
        return
    
    # Pick up to MAX_ARTICLES
    to_post = eligible[:MAX_ARTICLES]
    print(f"\n📝 Will post {len(to_post)} articles:")
    for i, a in enumerate(to_post, 1):
        print(f"   {i}. [{a.get('category','')}] {a.get('headline','')[:80]}")
    
    # Set up Twitter clients
    print("\n🔑 Authenticating with X...")
    
    # v2 client for tweeting
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    # v1.1 API for media upload
    auth = tweepy.OAuth1UserHandler(
        CONSUMER_KEY, CONSUMER_SECRET,
        ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    api_v1 = tweepy.API(auth)
    
    posted = 0
    errors = []
    tweet_urls = []
    
    for i, article in enumerate(to_post):
        print(f"\n{'─' * 50}")
        print(f"📤 Posting {i+1}/{len(to_post)}: {article['headline'][:70]}...")
        
        try:
            # Compose post
            post_text = compose_post(article)
            print(f"   📝 Post length: {len(post_text)} chars")
            
            # Download and upload image
            media_ids = None
            img_path = download_image(article.get("image_url"))
            if img_path:
                try:
                    print(f"   🖼️ Uploading image...")
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"   ✅ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"   ⚠️ Image upload failed: {e}")
                finally:
                    try:
                        os.unlink(img_path)
                    except:
                        pass
            else:
                print(f"   ℹ️ No image available, posting text only")
            
            # Post tweet
            tweet_kwargs = {"text": post_text}
            if media_ids:
                tweet_kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**tweet_kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"   ✅ Posted! {tweet_url}")
            
            # Update Supabase
            update_tweeted_at(article["id"])
            print(f"   ✅ Supabase tweeted_at updated")
            
            # Log tweet
            log_tweet(tweet_id, article)
            print(f"   ✅ Tweet logged locally")
            
            posted += 1
            tweet_urls.append(tweet_url)
            
            # Wait between posts
            if i < len(to_post) - 1:
                print(f"\n   ⏳ Waiting {DELAY_BETWEEN_POSTS}s before next post...")
                time.sleep(DELAY_BETWEEN_POSTS)
        
        except Exception as e:
            err_msg = f"Article '{article.get('headline', '')[:50]}': {e}"
            print(f"   ❌ Error: {e}")
            errors.append(err_msg)
            # If it's a rate limit, stop
            if "429" in str(e) or "Too Many" in str(e):
                print("   🛑 Rate limited — stopping.")
                break
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"   Posted: {posted}/{len(to_post)}")
    if tweet_urls:
        print(f"   Tweet URLs:")
        for url in tweet_urls:
            print(f"     • {url}")
    if errors:
        print(f"   Errors ({len(errors)}):")
        for err in errors:
            print(f"     • {err}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
