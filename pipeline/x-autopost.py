#!/usr/bin/env python3
"""Auto-post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
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
    "Prefer": "return=minimal"
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

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
eligible = [a for a in articles if a.get("image_url")]
to_post = eligible[:4]
print(f"Selected {len(to_post)} articles to post (with images)")

if not to_post:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose posts ---
def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("##", "").replace("**", "").replace("*", "").replace("#", "")
    # Get first ~1500 chars of body for source material
    body_excerpt = body_clean[:1500]
    
    # Build summary from body - extract first few meaningful paragraphs
    paragraphs = [p.strip() for p in body_clean.split('\n') if p.strip() and len(p.strip()) > 40]
    
    # Build 2-3 paragraph summary (~150-250 words)
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:
        words = p.split()
        if word_count + len(words) > 250:
            if word_count < 100:  # Need at least some content
                summary_parts.append(p)
            break
        summary_parts.append(p)
        word_count += len(words)
    
    summary = "\n\n".join(summary_parts[:3]) if summary_parts else subheadline
    
    # Extract key facts for takeaways from subheadline + body
    # Pull sentences with numbers, names, or key facts
    all_sentences = []
    for p in paragraphs:
        sents = [s.strip() for s in p.replace('. ', '.\n').split('\n') if s.strip() and len(s.strip()) > 20]
        all_sentences.extend(sents)
    
    # Pick sentences with numbers or key indicators as takeaways
    takeaways = []
    for s in all_sentences:
        if any(c.isdigit() for c in s) or any(kw in s.lower() for kw in ['billion', 'million', 'percent', '%', 'announce', 'launch', 'first', 'record', 'new', 'ban', 'approve']):
            clean = s.strip().rstrip('.')
            if len(clean) > 20 and len(clean) < 200:
                takeaways.append(clean)
            if len(takeaways) >= 4:
                break
    
    # If not enough takeaways from numbers, grab first few meaningful sentences
    if len(takeaways) < 3:
        for s in all_sentences:
            clean = s.strip().rstrip('.')
            if clean not in takeaways and len(clean) > 30 and len(clean) < 200:
                takeaways.append(clean)
            if len(takeaways) >= 4:
                break
    
    takeaway_text = "\n".join(f"▸ {t}" for t in takeaways[:4])
    
    post = f"""{emoji} {cat_label} | The Videshi

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
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary_short = "\n\n".join(summary_parts[:2]) if len(summary_parts) > 1 else summary[:500]
        post = f"""{emoji} {cat_label} | The Videshi

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

# --- Post loop ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)

posted = 0
errors = []

for i, article in enumerate(to_post):
    slug = article.get("slug", "unknown")
    aid = article["id"]
    print(f"\n--- [{i+1}/{len(to_post)}] Posting: {slug} ---")
    
    try:
        # Compose post
        post_text = compose_post(article)
        print(f"Post length: {len(post_text)} chars")
        
        # Try to attach image
        media_id = None
        image_url = article.get("image_url", "")
        if image_url:
            try:
                print(f"Downloading image: {image_url[:80]}...")
                img_resp = requests.get(image_url, timeout=15)
                img_resp.raise_for_status()
                
                # Determine extension
                ct = img_resp.headers.get("content-type", "")
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
                
                print(f"Uploading image to X ({len(img_resp.content)} bytes)...")
                media = api_v1.media_upload(filename=tmp_path)
                media_id = media.media_id
                print(f"Media uploaded: {media_id}")
                os.unlink(tmp_path)
            except Exception as e:
                print(f"Image upload failed (will post without): {e}")
                media_id = None
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Post tweet
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"✅ Posted: {tweet_url}")
        
        # Update Supabase
        now_utc = datetime.utcnow().isoformat() + "Z"
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{aid}",
            headers=SB_HEADERS,
            json={"tweeted_at": now_utc}
        )
        if patch_resp.status_code < 300:
            print(f"Supabase updated: tweeted_at = {now_utc}")
        else:
            print(f"Supabase update warning: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": aid,
            "slug": slug,
            "posted_at": now_utc
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("Waiting 30s before next post...")
            time.sleep(30)
    
    except Exception as e:
        err_msg = f"{slug}: {e}"
        errors.append(err_msg)
        print(f"❌ Error: {err_msg}")

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
