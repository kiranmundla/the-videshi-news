#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, requests
from datetime import datetime, timezone

import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_ARTICLES = 4
DELAY_BETWEEN = 30  # seconds

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

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supa_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

supa_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --- Fetch articles ---
print("Fetching unposted articles from Supabase...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    headers=supa_headers,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} unposted articles")

# Filter: must have image_url
articles = [a for a in articles if a.get("image_url")]
print(f"After filtering for images: {len(articles)}")

# Take up to MAX_ARTICLES
articles = articles[:MAX_ARTICLES]
if not articles:
    print("No articles to post. Done.")
    sys.exit(0)

print(f"Will post {len(articles)} articles\n")

# --- Compose long-form post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    # Normalize category for emoji lookup
    cat_key = cat
    for key in CATEGORY_EMOJI:
        if key in cat:
            cat_key = key
            break
    emoji = CATEGORY_EMOJI.get(cat_key, "📰")
    cat_label = cat.upper().replace("-", " ")

    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Extract key content from body (strip markdown formatting for readability)
    body_clean = body.replace("**", "").replace("*", "").replace("##", "").replace("#", "")
    # Get first ~1500 chars of body for context
    body_excerpt = body_clean[:1500]

    # Build summary from body - extract first few meaningful paragraphs
    paragraphs = [p.strip() for p in body_clean.split("\n\n") if p.strip() and len(p.strip()) > 40]
    # Skip any that look like metadata
    paragraphs = [p for p in paragraphs if not p.startswith("Source") and not p.startswith("Image")]

    # Build 2-3 paragraph summary (150-250 words)
    summary_parts = []
    word_count = 0
    for p in paragraphs[:5]:
        words = p.split()
        if word_count + len(words) > 250:
            # Trim to fit
            remaining = 250 - word_count
            if remaining > 20:
                summary_parts.append(" ".join(words[:remaining]) + "...")
            break
        summary_parts.append(p)
        word_count += len(words)
        if word_count >= 150 and len(summary_parts) >= 2:
            break

    summary = "\n\n".join(summary_parts) if summary_parts else subheadline

    # Extract key takeaways from body - look for numbers, names, concrete facts
    # Use subheadline + first few sentences for key facts
    takeaways = []
    if subheadline:
        takeaways.append(subheadline)
    # Pull short factual sentences from body
    sentences = []
    for p in paragraphs:
        for s in p.replace(". ", ".\n").split("\n"):
            s = s.strip()
            if 20 < len(s) < 150 and any(c.isdigit() for c in s):
                sentences.append(s)
            elif 20 < len(s) < 150 and any(kw in s.lower() for kw in ["billion", "million", "percent", "%", "announced", "launched", "signed", "approved"]):
                sentences.append(s)
    for s in sentences:
        if s not in takeaways and len(takeaways) < 4:
            takeaways.append(s)
    # Pad if needed
    if len(takeaways) < 3:
        for p in paragraphs[1:4]:
            short = p[:120].strip()
            if short and short not in takeaways:
                takeaways.append(short + ("..." if len(p) > 120 else ""))
            if len(takeaways) >= 3:
                break

    takeaways = takeaways[:4]
    takeaway_lines = "\n".join(f"▸ {t}" for t in takeaways)

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

    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary_short = summary[:600] + "..."
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_short}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


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
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = {}
if os.path.exists(log_path):
    with open(log_path) as f:
        tweet_log = json.load(f)

# --- Post articles ---
results = []
for i, article in enumerate(articles):
    print(f"\n--- Article {i+1}/{len(articles)} ---")
    print(f"Headline: {article['headline']}")
    print(f"Category: {article.get('category', 'unknown')}")
    print(f"Slug: {article['slug']}")

    post_text = compose_post(article)
    print(f"Post length: {len(post_text)} chars")

    # Download and upload image
    media_id = None
    image_url = article.get("image_url", "")
    if image_url:
        try:
            print(f"Downloading image: {image_url[:80]}...")
            img_resp = requests.get(
                image_url,
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=15,
            )
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

            print(f"Uploading image to X...")
            media = api_v1.media_upload(filename=tmp_path)
            media_id = media.media_id
            print(f"Media uploaded: {media_id}")
            os.unlink(tmp_path)
        except Exception as e:
            print(f"Image upload failed: {e} — posting without image")
            media_id = None

    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]

        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"✅ Posted: {tweet_url}")

        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=supa_headers,
            json={"tweeted_at": now_utc},
        )
        if patch_resp.status_code < 300:
            print(f"Supabase updated: tweeted_at = {now_utc}")
        else:
            print(f"Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(log_path, "w") as f:
            json.dump(tweet_log, f, indent=2)

        results.append({"headline": article["headline"], "tweet_url": tweet_url, "status": "ok"})

    except Exception as e:
        print(f"❌ Failed to post: {e}")
        results.append({"headline": article["headline"], "status": f"error: {e}"})

    # Wait between posts
    if i < len(articles) - 1:
        print(f"Waiting {DELAY_BETWEEN}s before next post...")
        time.sleep(DELAY_BETWEEN)

# --- Summary ---
print("\n" + "=" * 50)
print("POSTING SUMMARY")
print("=" * 50)
ok = [r for r in results if r["status"] == "ok"]
fail = [r for r in results if r["status"] != "ok"]
print(f"Posted: {len(ok)} | Failed: {len(fail)}")
for r in ok:
    print(f"  ✅ {r['headline'][:60]} → {r['tweet_url']}")
for r in fail:
    print(f"  ❌ {r['headline'][:60]} → {r['status']}")
