#!/usr/bin/env python3
"""Post recently published Videshi articles to X with long-form formatting + images."""

import json, os, sys, time, tempfile, re
from datetime import datetime

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# Category emoji mapping
EMOJI_MAP = {
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

CATEGORY_LABELS = {
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


def load_env(filepath):
    """Load KEY=VALUE pairs from a file."""
    env = {}
    if os.path.exists(filepath):
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def extract_summary_and_takeaways(body, headline, subheadline):
    """Extract key content from the article body markdown to compose the post."""
    if not body:
        # Fallback to subheadline
        return subheadline or headline, []

    # Clean markdown: remove images, links formatting
    text = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'---+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 40]

    # Take first 2-3 substantive paragraphs for summary
    summary_paras = []
    total_len = 0
    for p in paragraphs[:6]:  # Look at first 6 paragraphs
        if total_len > 600:
            break
        if len(p) < 40:
            continue
        summary_paras.append(p)
        total_len += len(p)
        if len(summary_paras) >= 3:
            break

    summary = '\n\n'.join(summary_paras) if summary_paras else (subheadline or headline)

    # Truncate summary if too long (aim for ~250 words max in summary)
    words = summary.split()
    if len(words) > 250:
        summary = ' '.join(words[:250]) + '...'

    # Extract key facts for takeaways - look for sentences with numbers, names, dates
    all_sentences = []
    for p in paragraphs:
        sents = re.split(r'(?<=[.!?])\s+', p)
        all_sentences.extend(sents)

    # Prefer sentences with numbers, dollar amounts, percentages, names
    fact_sentences = []
    for s in all_sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Score sentences by factual content
        score = 0
        if re.search(r'\d', s):
            score += 2
        if re.search(r'[\$₹€£%]', s):
            score += 2
        if re.search(r'\b(billion|million|crore|lakh|percent)\b', s, re.I):
            score += 2
        if re.search(r'\b(announced|launched|reported|filed|signed|approved|ordered)\b', s, re.I):
            score += 1
        if score >= 2:
            fact_sentences.append((score, s))

    fact_sentences.sort(key=lambda x: -x[0])
    takeaways = [s for _, s in fact_sentences[:4]]

    # If not enough fact sentences, pull from subheadline and early paragraphs
    if len(takeaways) < 3 and subheadline:
        sub_facts = re.split(r'(?<=[.!?])\s+', subheadline)
        for sf in sub_facts:
            if sf.strip() and sf.strip() not in takeaways and len(sf.strip()) > 15:
                takeaways.append(sf.strip())
                if len(takeaways) >= 4:
                    break

    return summary, takeaways[:4]


def compose_post(article):
    """Compose a long-form X post for the given article."""
    cat = article.get("category", "news")
    emoji = EMOJI_MAP.get(cat, "📰")
    label = CATEGORY_LABELS.get(cat, cat.upper())
    headline = article["headline"]
    slug = article["slug"]
    body = article.get("body", "")
    subheadline = article.get("subheadline", "")

    summary, takeaways = extract_summary_and_takeaways(body, headline, subheadline)

    # Build the post
    parts = []
    parts.append(f"{emoji} {label} | The Videshi")
    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(headline.upper() if len(headline) < 100 else headline)
    parts.append("")
    parts.append(summary)
    parts.append("")

    if takeaways:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        for t in takeaways:
            # Clean up the takeaway
            t = t.strip().rstrip('.')
            parts.append(f"▸ {t}")
        parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")

    post_text = '\n'.join(parts)

    # Ensure within 4000 char limit
    if len(post_text) > 3900:
        # Truncate summary
        over = len(post_text) - 3800
        summary_words = summary.split()
        cut_words = max(1, over // 6)
        summary = ' '.join(summary_words[:-cut_words]) + '...'
        # Recompose
        return compose_post_with_parts(emoji, label, headline, summary, takeaways, slug)

    return post_text


def compose_post_with_parts(emoji, label, headline, summary, takeaways, slug):
    """Helper to recompose with truncated summary."""
    parts = []
    parts.append(f"{emoji} {label} | The Videshi")
    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(headline.upper() if len(headline) < 100 else headline)
    parts.append("")
    parts.append(summary)
    parts.append("")

    if takeaways:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        for t in takeaways:
            t = t.strip().rstrip('.')
            parts.append(f"▸ {t}")
        parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")

    return '\n'.join(parts)


def main():
    # Load credentials
    tw_env = load_env(os.path.expanduser("~/workspace/.env.twitter"))
    sb_env = load_env(os.path.expanduser("~/workspace/.env.supabase"))

    consumer_key = tw_env["TWITTER_CONSUMER_KEY"]
    consumer_secret = tw_env["TWITTER_CONSUMER_SECRET"]
    access_token = tw_env["TWITTER_ACCESS_TOKEN"]
    access_token_secret = tw_env["TWITTER_ACCESS_TOKEN_SECRET"]
    sb_key = sb_env["SUPABASE_SERVICE_ROLE_KEY"]

    sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}

    # Initialize tweepy clients
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api_v1 = tweepy.API(auth)

    # Fetch untweeted articles
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
        headers=sb_headers,
        timeout=30,
    )
    r.raise_for_status()
    articles = r.json()
    print(f"Found {len(articles)} untweeted articles")

    # Filter to those with images, take up to MAX_POSTS
    eligible = [a for a in articles if a.get("image_url")]
    to_post = eligible[:MAX_POSTS]
    print(f"Will post {len(to_post)} articles (with images)")

    # Tweet log
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)

    posted = 0
    errors = []

    for i, article in enumerate(to_post):
        try:
            post_text = compose_post(article)
            print(f"\n--- Article {i+1}/{len(to_post)} ---")
            print(f"  Headline: {article['headline'][:80]}")
            print(f"  Category: {article['category']}")
            print(f"  Post length: {len(post_text)} chars")

            # Try to upload image
            media_id = None
            image_url = article.get("image_url", "")
            if image_url:
                try:
                    img_r = requests.get(image_url, timeout=15)
                    if img_r.status_code == 200:
                        # Determine extension
                        ct = img_r.headers.get("content-type", "")
                        ext = ".jpg"
                        if "png" in ct:
                            ext = ".png"
                        elif "webp" in ct:
                            ext = ".webp"
                        elif "gif" in ct:
                            ext = ".gif"

                        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                            tmp.write(img_r.content)
                            tmp_path = tmp.name

                        media = api_v1.media_upload(filename=tmp_path)
                        media_id = media.media_id
                        os.unlink(tmp_path)
                        print(f"  Image uploaded: media_id={media_id}")
                    else:
                        print(f"  Image download failed: HTTP {img_r.status_code}")
                except Exception as e:
                    print(f"  Image upload failed: {e}")
                    # Clean up temp file if it exists
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            # Post tweet
            tweet_kwargs = {"text": post_text}
            if media_id:
                tweet_kwargs["media_ids"] = [media_id]

            response = client.create_tweet(**tweet_kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")

            # Update Supabase
            now_utc = datetime.utcnow().isoformat() + "Z"
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                json={"tweeted_at": now_utc},
                headers={**sb_headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                timeout=15,
            )
            if patch_r.status_code < 300:
                print(f"  Supabase updated: tweeted_at = {now_utc}")
            else:
                print(f"  Supabase update failed: {patch_r.status_code} {patch_r.text}")

            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": article["slug"],
                "posted_at": now_utc,
            }
            with open(log_path, "w") as f:
                json.dump(tweet_log, f, indent=2)

            posted += 1

            # Wait between posts
            if i < len(to_post) - 1:
                print(f"  Waiting {POST_DELAY}s...")
                time.sleep(POST_DELAY)

        except Exception as e:
            error_msg = f"{article['headline'][:60]}: {e}"
            errors.append(error_msg)
            print(f"  ❌ Error: {e}")

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
