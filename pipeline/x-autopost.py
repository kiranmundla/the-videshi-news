#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime, timezone

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
DELAY_BETWEEN = 30  # seconds
TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            env[key.strip()] = val.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supa_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Category emoji map
EMOJI_MAP = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "culture": "🧘",
    "markets": "📈",
    "economy": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

# --- Tweepy clients ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)


def fetch_articles():
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        },
        headers=SUPA_HEADERS
    )
    resp.raise_for_status()
    return resp.json()


def strip_markdown(text):
    """Strip markdown formatting for plain text output."""
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
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = article.get("category", "news") or "news"
    emoji = EMOJI_MAP.get(cat, "📰")
    label = cat.upper().replace("-", " ")
    
    headline = article["headline"]
    slug = article["slug"]
    body = strip_markdown(article.get("body", "") or "")
    subheadline = article.get("subheadline", "") or ""
    
    # Extract key paragraphs from body for summary
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 50]
    
    # Build summary: take the most informative paragraphs, aiming for 150-250 words
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:
        p_words = len(p.split())
        if word_count + p_words > 280:
            break
        summary_parts.append(p)
        word_count += p_words
        if word_count >= 150:
            break
    
    summary = "\n\n".join(summary_parts) if summary_parts else subheadline
    
    # Truncate if summary is too long (aim for ~250 words max)
    words = summary.split()
    if len(words) > 250:
        summary = " ".join(words[:250]) + "..."
    
    # Extract key takeaways from subheadline and body
    takeaways = extract_takeaways(article)
    takeaway_lines = "\n".join(f"▸ {t}" for t in takeaways)
    
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        while len(post) > 3900 and len(summary.split()) > 80:
            words = summary.split()
            summary = " ".join(words[:-20]).rstrip(",.:;") + "..."
            post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post


def extract_takeaways(article):
    """Extract 3-4 key takeaway bullet points from article."""
    body = strip_markdown(article.get("body", "") or "")
    subheadline = article.get("subheadline", "") or ""
    
    # Gather candidate sentences with numbers, names, or key facts
    all_text = subheadline + "\n" + body
    sentences = re.split(r'(?<=[.!?])\s+', all_text)
    
    # Prioritize sentences with numbers, percentages, dollar amounts
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Score sentences by fact density
        score = 0
        if re.search(r'\d+', s):
            score += 2
        if re.search(r'[$₹%]', s):
            score += 2
        if re.search(r'\b(billion|million|trillion|crore|lakh)\b', s, re.I):
            score += 2
        if re.search(r'\b(first|largest|highest|record|new|launch|announce|sign)\b', s, re.I):
            score += 1
        if score > 0:
            fact_sentences.append((score, s))
    
    fact_sentences.sort(key=lambda x: -x[0])
    
    takeaways = []
    seen = set()
    for _, s in fact_sentences:
        # Avoid very similar takeaways
        key = s[:40].lower()
        if key not in seen:
            seen.add(key)
            takeaways.append(s)
        if len(takeaways) >= 4:
            break
    
    # Fallback: if not enough fact sentences, use first few substantive sentences
    if len(takeaways) < 3:
        for s in sentences:
            s = s.strip()
            if 30 < len(s) < 200 and s not in takeaways:
                takeaways.append(s)
            if len(takeaways) >= 3:
                break
    
    return takeaways[:4]


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        resp.raise_for_status()
        
        # Determine extension
        ct = resp.headers.get("Content-Type", "")
        if "png" in ct:
            ext = ".png"
        elif "gif" in ct:
            ext = ".gif"
        elif "webp" in ct:
            ext = ".webp"
        else:
            ext = ".jpg"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def upload_image_to_x(image_path):
    """Upload image to X, return media_id or None."""
    try:
        media = api_v1.media_upload(filename=image_path)
        return media.media_id
    except Exception as e:
        print(f"  ⚠️ Image upload to X failed: {e}")
        return None


def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=SUPA_HEADERS,
        json={"tweeted_at": now}
    )
    if resp.status_code < 300:
        print(f"  ✅ Supabase tweeted_at updated")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")


def log_tweet(tweet_id, article):
    """Append to local tweet log."""
    log = {}
    if os.path.exists(TWEET_LOG_PATH):
        with open(TWEET_LOG_PATH) as f:
            log = json.load(f)
    
    log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }
    
    with open(TWEET_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)


def main():
    print("=" * 50)
    print("The Videshi — X Auto-Post")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    
    # Fetch articles
    articles = fetch_articles()
    print(f"\n📋 Found {len(articles)} untweeted published articles")
    
    if not articles:
        print("Nothing to post. Done.")
        return
    
    # Filter: must have image_url, pick top 4
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📸 {len(eligible)} have images")
    
    to_post = eligible[:MAX_POSTS]
    print(f"📝 Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    tweet_urls = []
    
    for i, article in enumerate(to_post):
        print(f"\n--- [{i+1}/{len(to_post)}] {article['headline'][:70]}...")
        print(f"    Category: {article.get('category', 'unknown')}")
        print(f"    Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"    Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            img_path = download_image(article["image_url"])
            if img_path:
                media_id = upload_image_to_x(img_path)
                if media_id:
                    media_ids = [media_id]
                    print(f"  📸 Image uploaded (media_id: {media_id})")
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            tweet_urls.append(tweet_url)
            
            # Update Supabase
            mark_tweeted(article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Tweet failed for '{article['headline'][:50]}': {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)
        
        # Clean up temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {DELAY_BETWEEN}s...")
            time.sleep(DELAY_BETWEEN)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {posted}/{len(to_post)} posted successfully")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
    if tweet_urls:
        print(f"\n🔗 Tweet URLs:")
        for url in tweet_urls:
            print(f"   {url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
