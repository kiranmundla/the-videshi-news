#!/usr/bin/env python3
"""Auto-post recent Videshi articles to X with long-form premium posts + images."""

import json, os, sys, time, tempfile, requests
from datetime import datetime, timezone

import tweepy

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
supa_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_SERVICE_ROLE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPA_HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}

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

# --- Tweepy clients ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth_v1 = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth_v1)

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=SUPA_HEADERS,
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
to_post = candidates[:4]
print(f"Will post {len(to_post)} articles (with images)")

if not to_post:
    print("Nothing to post. Done.")
    sys.exit(0)


def strip_markdown(text):
    """Rough markdown stripping for body text."""
    import re
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
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_facts(body_text, subheadline):
    """Extract key factual sentences from the article body."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    # Prefer sentences with numbers, names, dates, percentages
    scored = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        score = 0
        if re.search(r'\d', s):
            score += 2
        if re.search(r'\$|%|billion|million|crore|lakh', s, re.I):
            score += 3
        if re.search(r'(said|announced|reported|according|confirmed|launched|signed)', s, re.I):
            score += 1
        scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    facts = [s for _, s in scored[:4]]
    # If we don't have enough, pull from subheadline
    if len(facts) < 3 and subheadline:
        sub_parts = re.split(r'[;.—]', subheadline)
        for p in sub_parts:
            p = p.strip()
            if p and p not in facts and len(p) > 15:
                facts.append(p)
                if len(facts) >= 4:
                    break
    return facts[:4]


def compose_post(article):
    """Compose a long-form X post."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = strip_markdown(article.get("body", ""))

    # Build summary paragraphs from body (first ~250 words)
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 30]
    summary_text = ""
    word_count = 0
    for p in paragraphs:
        words = p.split()
        if word_count + len(words) > 250:
            # Take partial if we haven't started yet
            if word_count == 0:
                summary_text = ' '.join(words[:200])
                word_count = 200
            break
        summary_text += p + "\n\n"
        word_count += len(words)
    summary_text = summary_text.strip()

    # If summary is too short, use subheadline
    if len(summary_text) < 100 and subheadline:
        summary_text = subheadline + "\n\n" + summary_text
        summary_text = summary_text.strip()

    # Key takeaways
    facts = extract_key_facts(body, subheadline)
    takeaways = "\n".join(f"▸ {f}" for f in facts) if facts else ""

    # Punchy headline rewrite — use original but make it title case
    punchy_headline = headline.strip().upper() if len(headline) < 60 else headline.strip().title()

    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━"""

    if takeaways:
        post += f"""

Key Takeaways:

{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━"""

    post += f"""

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if over 4000 chars
    if len(post) > 3900:
        # Truncate summary
        over = len(post) - 3800
        summary_text = summary_text[:len(summary_text) - over].rsplit(' ', 1)[0] + "..."
        # Recompose
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━"""
        if takeaways:
            post += f"""

Key Takeaways:

{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━"""
        post += f"""

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # Determine extension from content-type
        ct = r.headers.get("content-type", "image/jpeg")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        fd, path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, 'wb') as f:
            f.write(r.content)
        return path
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


def upload_media(img_path):
    """Upload image to X via v1.1 API, return media_id or None."""
    try:
        media = api_v1.media_upload(filename=img_path)
        return media.media_id
    except Exception as e:
        print(f"  Media upload failed: {e}")
        return None


# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}

posted = 0
errors = 0
results = []

for i, article in enumerate(to_post):
    print(f"\n--- Article {i+1}/{len(to_post)}: {article['headline'][:60]}... ---")

    # Compose post
    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")

    # Download and upload image
    media_id = None
    img_path = None
    if article.get("image_url"):
        img_path = download_image(article["image_url"])
        if img_path:
            media_id = upload_media(img_path)

    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")

        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SUPA_HEADERS,
            json={"tweeted_at": now_utc},
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"  ✅ Supabase updated (tweeted_at)")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(tweet_log, f, indent=2)

        posted += 1
        results.append({"slug": article["slug"], "tweet_url": tweet_url})

    except Exception as e:
        print(f"  ❌ Tweet failed: {e}")
        errors += 1
        results.append({"slug": article["slug"], "error": str(e)})

    finally:
        # Cleanup temp image
        if img_path and os.path.exists(img_path):
            os.remove(img_path)

    # Wait between posts
    if i < len(to_post) - 1:
        print("  Waiting 30s...")
        time.sleep(30)

print(f"\n{'='*50}")
print(f"SUMMARY: {posted} posted, {errors} errors out of {len(to_post)} attempted")
for r in results:
    if "tweet_url" in r:
        print(f"  ✅ {r['slug']} → {r['tweet_url']}")
    else:
        print(f"  ❌ {r['slug']} → {r['error']}")
