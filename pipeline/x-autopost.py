#!/usr/bin/env python3
"""Auto-post Videshi articles to X with long-form Premium posts."""

import json, os, sys, time, tempfile, requests
from datetime import datetime

import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# --- Load keys ---
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

sb_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
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

CATEGORY_LABELS = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle": "LIFESTYLE",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS",
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}


def fetch_articles():
    """Fetch up to 20 recent published articles not yet tweeted."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=sb_headers,
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
    )
    r.raise_for_status()
    return r.json()


def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = article.get("category", "news") or "news"
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABELS.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "") or ""
    slug = article.get("slug", "")

    # Extract key content from body - strip markdown formatting
    body_clean = body.replace("##", "").replace("**", "").replace("*", "")
    # Get first ~600 words for summary material
    body_words = body_clean.split()
    summary_source = " ".join(body_words[:600])

    # Build the post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")

    # Use subheadline as first paragraph if available
    if subheadline:
        lines.append(subheadline)
        lines.append("")

    # Extract a meaningful summary from body
    # Take first few paragraphs that aren't headers
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    summary_paras = []
    for p in paragraphs:
        p_clean = p.strip().lstrip("#").strip()
        if not p_clean:
            continue
        # Skip markdown headers, image refs, very short lines
        if p_clean.startswith("!["): continue
        if p_clean.startswith("---"): continue
        if len(p_clean) < 30: continue
        # Clean markdown
        p_clean = p_clean.replace("**", "").replace("*", "").replace("##", "").replace("#", "").strip()
        summary_paras.append(p_clean)
        if len(summary_paras) >= 3:
            break

    # Add 2-3 summary paragraphs
    for p in summary_paras[:3]:
        # Truncate very long paragraphs
        if len(p) > 400:
            # Find sentence boundary
            sentences = p.split(". ")
            truncated = ""
            for s in sentences:
                if len(truncated) + len(s) + 2 > 350:
                    break
                truncated += s + ". "
            p = truncated.strip()
        lines.append(p)
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Key Takeaways:")
    lines.append("")

    # Extract key facts from body and subheadline
    # Pull sentences with numbers, names, dates
    all_sentences = []
    for p in paragraphs:
        p_clean = p.strip().lstrip("#").strip().replace("**", "").replace("*", "")
        if len(p_clean) < 20: continue
        if p_clean.startswith("!["): continue
        for sent in p_clean.replace(". ", ".\n").split("\n"):
            sent = sent.strip()
            if len(sent) > 30 and len(sent) < 200:
                all_sentences.append(sent)

    # Pick sentences with numbers/facts as takeaways
    fact_sentences = []
    for s in all_sentences:
        has_number = any(c.isdigit() for c in s)
        has_currency = any(sym in s for sym in ["$", "₹", "%", "billion", "million", "crore", "lakh"])
        if has_number or has_currency:
            fact_sentences.append(s)

    # Fill remaining from top sentences
    takeaways = fact_sentences[:4]
    if len(takeaways) < 3:
        for s in all_sentences:
            if s not in takeaways:
                takeaways.append(s)
            if len(takeaways) >= 4:
                break

    for t in takeaways[:4]:
        # Ensure it ends with period
        if not t.endswith(".") and not t.endswith("!") and not t.endswith("?"):
            t += "."
        lines.append(f"▸ {t}")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    post_text = "\n".join(lines)

    # Ensure under 4000 chars
    if len(post_text) > 3900:
        # Trim summary paragraphs
        lines_trimmed = []
        summary_count = 0
        for line in lines:
            if summary_count >= 2 and line and not line.startswith("━") and not line.startswith("▸") and not line.startswith("📰") and not line.startswith("🌐") and not line.startswith("Key") and not line.startswith("The Videshi"):
                continue
            lines_trimmed.append(line)
            if line and not line.startswith("━") and not line.startswith(emoji):
                summary_count += 1
        post_text = "\n".join(lines)[:3900]

    return post_text


def upload_image(image_url):
    """Download and upload image to X. Returns media_id or None."""
    try:
        r = requests.get(image_url, timeout=15)
        r.raise_for_status()

        # Determine extension from content-type
        ct = r.headers.get("content-type", "image/jpeg")
        ext = ".jpg"
        if "png" in ct: ext = ".png"
        elif "webp" in ct: ext = ".webp"
        elif "gif" in ct: ext = ".gif"

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(r.content)
            tmp_path = tmp.name

        # Upload via v1.1 API
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=tmp_path)

        os.unlink(tmp_path)
        return media.media_id
    except Exception as e:
        print(f"  ⚠️ Image upload failed: {e}")
        try:
            os.unlink(tmp_path)
        except:
            pass
        return None


def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.utcnow().isoformat() + "Z"
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=sb_headers,
        json={"tweeted_at": now},
    )
    if r.status_code < 300:
        print(f"  ✅ Supabase updated (tweeted_at: {now})")
    else:
        print(f"  ⚠️ Supabase update failed: {r.status_code} {r.text}")


def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)

    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  ✅ Logged to tweet-log.json")


def main():
    print(f"=== Videshi X Auto-Post — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    # Fetch articles
    articles = fetch_articles()
    print(f"Found {len(articles)} untweeted articles\n")

    if not articles:
        print("No articles to post. Done.")
        return

    # Filter to ones with images, take up to MAX_POSTS
    eligible = [a for a in articles if a.get("image_url")]
    print(f"{len(eligible)} have images\n")

    to_post = eligible[:MAX_POSTS]
    print(f"Will post {len(to_post)} articles:\n")
    for i, a in enumerate(to_post):
        print(f"  {i+1}. [{a['category']}] {a['headline'][:80]}")
    print()

    # Set up tweepy v2 client
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    posted = 0
    errors = []

    for i, article in enumerate(to_post):
        print(f"\n--- Posting {i+1}/{len(to_post)}: {article['headline'][:60]}... ---\n")

        try:
            # Compose post
            post_text = compose_post(article)
            print(f"  Post length: {len(post_text)} chars")

            # Upload image
            media_id = None
            if article.get("image_url"):
                print(f"  Uploading image: {article['image_url'][:80]}...")
                media_id = upload_image(article["image_url"])

            # Post tweet
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")

            # Update Supabase
            update_supabase(article["id"])

            # Log tweet
            log_tweet(tweet_id, article)

            posted += 1

            # Delay between posts
            if i < len(to_post) - 1:
                print(f"\n  ⏳ Waiting {POST_DELAY}s before next post...")
                time.sleep(POST_DELAY)

        except Exception as e:
            err_msg = f"Failed to post '{article['headline'][:50]}': {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted successfully")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
