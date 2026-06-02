#!/usr/bin/env python3
"""Auto-post Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime

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

SB_HEADERS = {
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

CATEGORY_LABEL = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

# --- Tweepy clients ---
client_v2 = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth_v1 = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth_v1)


def fetch_untweeted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SB_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def strip_markdown(text):
    """Rough markdown to plain text."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_facts(body_text, subheadline):
    """Extract sentences with numbers, names, or concrete facts."""
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    facts = []
    # Prioritize sentences with numbers, percentages, dollar amounts
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        if re.search(r'\d+[%$₹]|\$\d|₹\d|\d+\s*(million|billion|crore|lakh|percent)', s, re.I):
            facts.append(s)
        elif re.search(r'\d{4}', s) and len(facts) < 6:  # years
            facts.append(s)
    # If not enough, add subheadline-derived facts
    if subheadline and len(facts) < 3:
        for part in subheadline.split(';'):
            part = part.strip()
            if part and len(part) > 15:
                facts.append(part)
    # Deduplicate and limit
    seen = set()
    unique = []
    for f in facts:
        key = f[:40].lower()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique[:4]


def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    slug = article.get("slug", "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "") or ""
    
    body_text = strip_markdown(body)
    
    # Build summary: first ~250 words from the body, trimmed to complete sentences
    words = body_text.split()
    if len(words) > 250:
        summary_raw = " ".join(words[:250])
        # Trim to last complete sentence
        last_period = max(summary_raw.rfind('.'), summary_raw.rfind('!'), summary_raw.rfind('?'))
        if last_period > 100:
            summary_raw = summary_raw[:last_period + 1]
    else:
        summary_raw = " ".join(words)
    
    # Clean up: take first 2-3 paragraphs worth
    paras = [p.strip() for p in summary_raw.split('\n\n') if p.strip()]
    summary = "\n\n".join(paras[:3])
    
    # If summary is too short, use subheadline as supplement
    if len(summary) < 100 and subheadline:
        summary = subheadline + "\n\n" + summary
    
    # Key takeaways
    facts = extract_key_facts(body_text, subheadline)
    if len(facts) < 3 and subheadline:
        # Fallback: split subheadline into bullet points
        for part in subheadline.split('.'):
            part = part.strip()
            if part and len(part) > 15 and part not in facts:
                facts.append(part)
            if len(facts) >= 4:
                break
    
    takeaways = ""
    if facts:
        takeaways_lines = "\n".join(f"▸ {f}" for f in facts[:4])
        takeaways = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\nKey Takeaways:\n\n{takeaways_lines}"
    
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        words_summary = summary.split()
        while len(post) > 3900 and len(words_summary) > 50:
            words_summary = words_summary[:-20]
            truncated = " ".join(words_summary)
            last_p = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            if last_p > 50:
                truncated = truncated[:last_p + 1]
            summary = truncated
            post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post


def upload_image(image_url):
    """Download and upload image to X. Returns media_id or None."""
    if not image_url:
        return None
    try:
        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name
        
        media = api_v1.media_upload(filename=tmp_path)
        os.unlink(tmp_path)
        return media.media_id
    except Exception as e:
        print(f"  ⚠ Image upload failed: {e}")
        return None


def update_supabase(article_id):
    """Mark article as tweeted."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = {"tweeted_at": datetime.utcnow().isoformat() + "Z"}
    resp = requests.patch(url, headers=SB_HEADERS, json=payload, timeout=15)
    resp.raise_for_status()


def log_tweet(tweet_id, article):
    """Log tweet to local JSON."""
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
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)


def main():
    print("🐦 Videshi X Auto-Post — Long-form Premium Posts")
    print("=" * 50)
    
    # Fetch untweeted articles
    articles = fetch_untweeted_articles()
    print(f"\n📋 Found {len(articles)} untweeted articles")
    
    if not articles:
        print("✅ Nothing to post — all articles already tweeted.")
        return
    
    # Filter: must have image_url, pick up to 4
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📸 {len(eligible)} have images (eligible for posting)")
    
    to_post = eligible[:4]
    print(f"📤 Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        slug = article.get("slug", "?")
        headline = article.get("headline", "?")
        print(f"\n--- [{i+1}/{len(to_post)}] {headline[:80]} ---")
        print(f"    Slug: {slug}")
        print(f"    Category: {article.get('category', '?')}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"    Post length: {len(post_text)} chars")
        
        # Upload image
        media_id = upload_image(article.get("image_url"))
        if media_id:
            print(f"    📸 Image uploaded (media_id: {media_id})")
        else:
            print(f"    📸 No image attached")
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]
            
            response = client_v2.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"    ✅ Posted! {tweet_url}")
            
            # Update Supabase
            update_supabase(article["id"])
            print(f"    📝 Supabase updated (tweeted_at set)")
            
            # Log tweet
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            error_msg = f"Failed to post '{slug}': {e}"
            print(f"    ❌ {error_msg}")
            errors.append(error_msg)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"    ⏳ Waiting 30s before next post...")
            time.sleep(30)
    
    # Summary
    print(f"\n{'=' * 50}")
    print(f"📊 SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ No errors!")


if __name__ == "__main__":
    main()
