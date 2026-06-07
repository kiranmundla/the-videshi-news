#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form posts with images."""

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
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            env[key.strip()] = val.strip()
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
    "lifestyle": "🧘",
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=SB_HEADERS,
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get("image_url")]
selected = candidates[:4]
print(f"Selected {len(selected)} articles to post")

if not selected:
    print("Nothing to post.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth_v1 = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth_v1)

# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}


def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("**", "").replace("*", "").replace("##", "").replace("#", "")
    # Get first ~1500 chars of body for context
    body_excerpt = body_clean[:2000]

    # Build the post using AI-style summarization from the body
    # Extract paragraphs from body
    paragraphs = [p.strip() for p in body_clean.split("\n\n") if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first few substantial paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs:
        if char_count > 600:
            break
        # Skip markdown artifacts, image refs, headers
        if p.startswith("![") or p.startswith("---") or p.startswith("━") or len(p) < 50:
            continue
        summary_parts.append(p)
        char_count += len(p)
    
    summary = "\n\n".join(summary_parts[:3])
    # Trim to ~500 chars max for the summary section  
    if len(summary) > 600:
        summary = summary[:597] + "..."

    # Extract key facts for takeaways
    takeaways = []
    for p in paragraphs:
        if len(takeaways) >= 4:
            break
        # Look for sentences with numbers, names, or key facts
        sentences = [s.strip() for s in p.replace(". ", ".\n").split("\n") if len(s.strip()) > 30]
        for s in sentences:
            if len(takeaways) >= 4:
                break
            # Prefer sentences with numbers, percentages, or strong facts
            if any(c.isdigit() for c in s) or any(word in s.lower() for word in ["million", "billion", "percent", "%", "first", "largest", "record"]):
                # Clean and trim
                fact = s.strip()
                if len(fact) > 120:
                    fact = fact[:117] + "..."
                if fact not in takeaways:
                    takeaways.append(fact)

    # If we didn't find enough number-based facts, add first few strong sentences
    if len(takeaways) < 3:
        for p in paragraphs[1:5]:
            if len(takeaways) >= 3:
                break
            sentences = [s.strip() for s in p.replace(". ", ".\n").split("\n") if len(s.strip()) > 30 and len(s.strip()) < 130]
            for s in sentences:
                if len(takeaways) >= 3:
                    break
                if s not in takeaways:
                    takeaways.append(s)

    takeaway_lines = "\n".join(f"▸ {t}" for t in takeaways[:4])

    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Ensure we're within 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary = summary[:300] + "..."
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        r.raise_for_status()
        
        # Determine extension from content type
        ct = r.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        print(f"  Downloaded image: {size} bytes")
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


def post_article(article, idx):
    """Post a single article to X. Returns (tweet_id, tweet_url) or (None, error_msg)."""
    print(f"\n--- Article {idx+1}/{len(selected)} ---")
    print(f"  Headline: {article['headline']}")
    print(f"  Category: {article.get('category', 'unknown')}")
    print(f"  Slug: {article['slug']}")

    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")

    # Try to attach image
    media_ids = None
    img_path = None
    if article.get("image_url"):
        img_path = download_image(article["image_url"])
        if img_path:
            try:
                media = api_v1.media_upload(filename=img_path)
                media_ids = [media.media_id]
                print(f"  Media uploaded: {media.media_id}")
            except Exception as e:
                print(f"  Media upload failed: {e}")
                media_ids = None

    # Post tweet
    try:
        tweet_kwargs = {"text": post_text}
        if media_ids:
            tweet_kwargs["media_ids"] = media_ids
        
        response = client.create_tweet(**tweet_kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")

        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SB_HEADERS,
            json={"tweeted_at": datetime.utcnow().isoformat() + "Z"},
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated (tweeted_at set)")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, "w") as f:
            json.dump(tweet_log, f, indent=2)

        return tweet_id, tweet_url

    except Exception as e:
        print(f"  ❌ Tweet failed: {e}")
        return None, str(e)

    finally:
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)


# --- Main loop ---
results = []
for i, article in enumerate(selected):
    tweet_id, result = post_article(article, i)
    results.append((article, tweet_id, result))
    
    # Wait between posts (skip wait after last)
    if i < len(selected) - 1:
        print(f"  Waiting 30s before next post...")
        time.sleep(30)

# --- Summary ---
print("\n" + "=" * 50)
print("POSTING SUMMARY")
print("=" * 50)
posted = [(a, tid, url) for a, tid, url in results if tid]
failed = [(a, tid, err) for a, tid, err in results if not tid]

print(f"Posted: {len(posted)}/{len(selected)}")
for a, tid, url in posted:
    print(f"  ✅ {a['headline'][:60]}...")
    print(f"     {url}")

if failed:
    print(f"\nFailed: {len(failed)}")
    for a, _, err in failed:
        print(f"  ❌ {a['headline'][:60]}...")
        print(f"     Error: {err}")

print(f"\nDone at {datetime.utcnow().isoformat()}Z")
