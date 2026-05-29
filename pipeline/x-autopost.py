#!/usr/bin/env python3
"""Auto-post recent Videshi articles to X as long-form posts with images."""

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
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    timeout=30
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
selected = [a for a in articles if a.get("image_url")][:4]
print(f"Selected {len(selected)} articles to post (with images)")

if not selected:
    print("No articles to post. Done.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
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
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("**", "").replace("##", "").replace("###", "").replace("*", "")
    # Get first ~800 chars of body for summary material
    body_preview = body_clean[:2000]

    # Build summary paragraphs from body content
    paragraphs = [p.strip() for p in body_preview.split("\n\n") if p.strip() and len(p.strip()) > 40]
    # Take 2-3 best paragraphs, skip ones that look like headers
    summary_paras = []
    for p in paragraphs:
        if len(p) < 50:
            continue
        if p.startswith("#"):
            continue
        # Clean up markdown artifacts
        p = p.replace("[", "").replace("]", "").replace("(http", " (http")
        # Truncate overly long paragraphs
        if len(p) > 300:
            # Cut at sentence boundary
            sentences = p.split(". ")
            truncated = ""
            for s in sentences:
                if len(truncated) + len(s) + 2 < 280:
                    truncated += s + ". "
                else:
                    break
            p = truncated.strip()
        if p:
            summary_paras.append(p)
        if len(summary_paras) >= 3:
            break

    summary_text = "\n\n".join(summary_paras) if summary_paras else subheadline

    # Extract key takeaways from body
    takeaways = []
    # Look for bullet points, key facts, numbers
    lines = body_clean.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("- ") or line.startswith("• "):
            fact = line.lstrip("- •").strip()
            if len(fact) > 20 and len(fact) < 200:
                takeaways.append(fact)
        elif any(char.isdigit() for char in line) and 30 < len(line) < 200 and "http" not in line:
            # Lines with numbers often contain key facts
            if line and not line.startswith("#"):
                takeaways.append(line)
        if len(takeaways) >= 6:
            break

    # If not enough takeaways from bullets, use subheadline
    if len(takeaways) < 3 and subheadline:
        takeaways.insert(0, subheadline)

    # Deduplicate and pick best 3-4
    seen = set()
    unique_takeaways = []
    for t in takeaways:
        t_lower = t.lower()[:50]
        if t_lower not in seen:
            seen.add(t_lower)
            unique_takeaways.append(t)
    takeaways = unique_takeaways[:4]

    # Build the post
    parts = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
        summary_text,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    if takeaways:
        parts.append("Key Takeaways:")
        parts.append("")
        for t in takeaways:
            parts.append(f"▸ {t}")
        parts.append("")
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")

    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")

    post_text = "\n".join(parts)

    # Ensure within 4000 char limit
    if len(post_text) > 3900:
        # Trim summary
        summary_text = summary_text[:600] + "..."
        parts[6] = summary_text
        post_text = "\n".join(parts)

    return post_text


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


# --- Post loop ---
posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(selected):
    print(f"\n--- Article {i+1}/{len(selected)} ---")
    print(f"  Headline: {article['headline']}")
    print(f"  Category: {article.get('category')}")
    print(f"  Slug: {article['slug']}")

    # Compose post
    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")

    # Download and upload image
    media_id = None
    tmp_path = None
    if article.get("image_url"):
        tmp_path = download_image(article["image_url"])
        if tmp_path:
            try:
                media = api_v1.media_upload(filename=tmp_path)
                media_id = media.media_id
                print(f"  Image uploaded: media_id={media_id}")
            except Exception as e:
                print(f"  Image upload to X failed: {e}")
                media_id = None

    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        tweet_urls.append(tweet_url)

        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SB_HEADERS,
            json={"tweeted_at": datetime.now(timezone.utc).isoformat()},
            timeout=15
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated (tweeted_at set)")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
        }
        with open(LOG_PATH, "w") as f:
            json.dump(tweet_log, f, indent=2)

        posted += 1

    except Exception as e:
        err_msg = f"Tweet failed for '{article['headline']}': {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Wait between posts
    if i < len(selected) - 1:
        print("  Waiting 30s before next post...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(selected)} articles to X")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
