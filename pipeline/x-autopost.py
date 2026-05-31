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

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def fetch_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null"
        "&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def compose_post(article):
    cat = (article.get("category") or "news").lower().strip()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")

    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    body = article.get("body", "") or ""
    slug = article.get("slug", "")

    # Build a concise body excerpt for the AI-style summary
    # Strip markdown formatting for plain text extraction
    body_clean = body.replace("**", "").replace("*", "").replace("##", "").replace("#", "")
    # Take first ~2000 chars of body for context
    body_excerpt = body_clean[:2000]

    # Build summary paragraphs from the article body
    # Extract meaningful sentences from the body
    paragraphs = [p.strip() for p in body_excerpt.split("\n\n") if p.strip() and len(p.strip()) > 30]
    
    # Take the first 2-3 substantive paragraphs as summary
    summary_parts = []
    char_count = 0
    for p in paragraphs[:5]:
        # Skip lines that look like headers or metadata
        if p.startswith("---") or p.startswith("Source:") or p.startswith("Image:") or len(p) < 40:
            continue
        summary_parts.append(p)
        char_count += len(p)
        if char_count > 600 or len(summary_parts) >= 3:
            break

    summary = "\n\n".join(summary_parts) if summary_parts else subheadline

    # Truncate summary if too long
    if len(summary) > 800:
        summary = summary[:797] + "..."

    # Extract key facts from body and subheadline
    facts = []
    # Pull from subheadline first
    if subheadline:
        # Split subheadline on common delimiters
        sub_parts = [s.strip() for s in subheadline.replace(";", ".").split(".") if s.strip() and len(s.strip()) > 15]
        facts.extend(sub_parts[:2])
    
    # Pull additional facts from body paragraphs
    for p in paragraphs[1:8]:
        if len(facts) >= 4:
            break
        # Look for sentences with numbers, names, or key facts
        sentences = [s.strip() for s in p.split(". ") if s.strip() and len(s.strip()) > 20]
        for s in sentences:
            if len(facts) >= 4:
                break
            # Prefer sentences with numbers or specific details
            if any(c.isdigit() for c in s) or any(w in s.lower() for w in ["percent", "million", "billion", "announced", "reported", "according"]):
                fact = s.strip().rstrip(".")
                if len(fact) > 120:
                    fact = fact[:117] + "..."
                if fact not in facts:
                    facts.append(fact)

    # Fill remaining facts from any remaining paragraphs
    for p in paragraphs:
        if len(facts) >= 3:
            break
        sentences = [s.strip() for s in p.split(". ") if s.strip() and len(s.strip()) > 25]
        for s in sentences:
            if len(facts) >= 4:
                break
            fact = s.strip().rstrip(".")
            if len(fact) > 120:
                fact = fact[:117] + "..."
            if fact not in facts:
                facts.append(fact)

    facts = facts[:4]

    # Compose the post
    lines = []
    lines.append(f"{emoji} {cat_label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 80 else headline)
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Key Takeaways:")
    lines.append("")
    for f in facts:
        lines.append(f"▸ {f}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    post_text = "\n".join(lines)

    # Ensure within 4000 char limit
    if len(post_text) > 3900:
        # Truncate summary
        excess = len(post_text) - 3800
        summary = summary[:len(summary) - excess] + "..."
        # Recompose
        return compose_post_with(emoji, cat_label, headline, summary, facts, slug)

    return post_text

def compose_post_with(emoji, cat_label, headline, summary, facts, slug):
    lines = []
    lines.append(f"{emoji} {cat_label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 80 else headline)
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Key Takeaways:")
    lines.append("")
    for f in facts:
        lines.append(f"▸ {f}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")
    return "\n".join(lines)

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        # Check file size
        if os.path.getsize(tmp.name) < 1000:
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def mark_tweeted(article_id):
    now = datetime.now(timezone.utc).isoformat()
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    r = requests.patch(url, json={"tweeted_at": now}, headers=SUPABASE_HEADERS, timeout=15)
    if r.status_code < 300:
        print(f"  ✅ Marked tweeted_at in Supabase")
    else:
        print(f"  ⚠️ Failed to update tweeted_at: {r.status_code} {r.text}")

def log_tweet(tweet_id, article):
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        try:
            tweet_log = json.load(open(log_path))
        except:
            tweet_log = {}
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z",
    }
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=" * 50)
    print("🐦 The Videshi X Auto-Poster")
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    # Fetch articles
    articles = fetch_articles()
    print(f"\n📋 Found {len(articles)} un-tweeted articles")

    if not articles:
        print("Nothing to post. Exiting.")
        return

    # Filter: must have image_url, pick up to 4
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📸 {len(eligible)} have images (eligible)")

    to_post = eligible[:4]
    print(f"📝 Will post {len(to_post)} articles\n")

    # Setup tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    posted = 0
    errors = []

    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"📰 {article['headline'][:80]}")
        print(f"🏷️  {article.get('category', 'unknown')} | slug: {article['slug'][:50]}")

        # Compose post
        post_text = compose_post(article)
        print(f"📏 Post length: {len(post_text)} chars")

        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            print(f"🖼️  Downloading image...")
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  ✅ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠️ Image upload failed: {e}")
                    media_ids = None

        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")

            # Mark tweeted in Supabase
            mark_tweeted(article["id"])

            # Log tweet locally
            log_tweet(tweet_id, article)

            posted += 1
        except Exception as e:
            err_msg = str(e)
            print(f"  ❌ Failed to post: {err_msg}")
            errors.append({"slug": article["slug"], "error": err_msg})

        # Cleanup temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)

        # Wait between posts
        if i < len(to_post) - 1:
            print("  ⏳ Waiting 30s before next post...")
            time.sleep(30)

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {posted}/{len(to_post)} posted successfully")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   - {e['slug']}: {e['error'][:100]}")
    print("=" * 50)

if __name__ == "__main__":
    main()
