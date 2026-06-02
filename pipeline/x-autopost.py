#!/usr/bin/env python3
"""Auto-post Videshi articles to X as long-form Premium posts with images."""

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
supa_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPA_HEADERS = {
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
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

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
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_facts(body_text, subheadline):
    """Extract key facts/numbers from the article body."""
    # Look for sentences with numbers, percentages, proper nouns
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    facts = []
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, currency, percentages
        if re.search(r'\d', s) and len(facts) < 6:
            facts.append(s)
        elif re.search(r'(first|largest|record|billion|million|trillion|percent|announced|signed|launched|approved)', s, re.I) and len(facts) < 6:
            facts.append(s)
    return facts[:4] if len(facts) >= 3 else facts


def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, '🇮🇳')
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article['headline']
    subheadline = article.get('subheadline', '') or ''
    slug = article['slug']
    body = strip_markdown(article.get('body', '') or '')

    # Build summary - take first few substantial paragraphs from body
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]

    # Build a 2-3 paragraph summary (150-250 words target)
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:
        words = len(p.split())
        if word_count + words > 280:
            break
        summary_parts.append(p)
        word_count += words
        if word_count >= 150 and len(summary_parts) >= 2:
            break

    summary = '\n\n'.join(summary_parts)

    # If summary is too short, add more
    if word_count < 80 and len(paragraphs) > len(summary_parts):
        for p in paragraphs[len(summary_parts):len(summary_parts)+2]:
            summary_parts.append(p)
        summary = '\n\n'.join(summary_parts)

    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    # If we didn't get enough from number-matching, use subheadline parts
    if len(facts) < 3 and subheadline:
        sub_sentences = [s.strip() for s in re.split(r'[.;]', subheadline) if s.strip() and len(s.strip()) > 15]
        facts = (facts + sub_sentences)[:4]
    # Still need more? Use first short paragraphs we haven't used
    if len(facts) < 3:
        for p in paragraphs:
            if p not in summary_parts and 20 < len(p) < 180:
                facts.append(p)
                if len(facts) >= 3:
                    break

    # Truncate long facts
    facts = [f[:180] + '...' if len(f) > 180 else f for f in facts[:4]]

    # Build the post
    divider = "━━━━━━━━━━━━━━━━━━━━━━━━"

    takeaways = '\n'.join(f"▸ {f}" for f in facts) if facts else ""

    post = f"""{emoji} {label} | The Videshi

{divider}

{headline}

{summary}

{divider}

Key Takeaways:

{takeaways}

{divider}

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary_words = summary.split()
        while len(post) > 3900 and len(summary_words) > 50:
            summary_words = summary_words[:len(summary_words)-20]
            short_summary = ' '.join(summary_words) + '...'
            post = f"""{emoji} {label} | The Videshi

{divider}

{headline}

{short_summary}

{divider}

Key Takeaways:

{takeaways}

{divider}

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


def main():
    # Fetch untweeted articles
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=SUPA_HEADERS,
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        }
    )
    articles = r.json()
    print(f"Fetched {len(articles)} untweeted articles")

    # Filter to those with images, take top 4
    candidates = [a for a in articles if a.get('image_url')][:4]
    print(f"Posting {len(candidates)} articles\n")

    if not candidates:
        print("No articles to post.")
        return

    # Set up Twitter clients
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

    posted = 0
    errors = []

    for i, article in enumerate(candidates):
        print(f"\n--- Article {i+1}/{len(candidates)} ---")
        print(f"Headline: {article['headline'][:100]}")
        print(f"Category: {article['category']}")
        print(f"Slug: {article['slug']}")

        # Compose post
        post_text = compose_post(article)
        print(f"Post length: {len(post_text)} chars")

        # Try to download and upload image
        media_id = None
        image_url = article.get('image_url', '')
        if image_url:
            try:
                img_resp = requests.get(image_url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; TheVideshi/1.0)'
                })
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    # Determine extension
                    ct = img_resp.headers.get('content-type', '')
                    ext = '.jpg'
                    if 'png' in ct:
                        ext = '.png'
                    elif 'webp' in ct:
                        ext = '.webp'

                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp.write(img_resp.content)
                        tmp_path = tmp.name

                    media = api_v1.media_upload(filename=tmp_path)
                    media_id = media.media_id
                    os.unlink(tmp_path)
                    print(f"Image uploaded, media_id: {media_id}")
                else:
                    print(f"Image download failed: status={img_resp.status_code}, size={len(img_resp.content)}")
            except Exception as e:
                print(f"Image error (will post without): {e}")
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]

            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"✅ Posted: {tweet_url}")

            # Update Supabase
            now_utc = datetime.utcnow().isoformat() + "Z"
            patch_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                headers=SUPA_HEADERS,
                json={"tweeted_at": now_utc}
            )
            print(f"Supabase update: {patch_resp.status_code}")

            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article['id'],
                "slug": article['slug'],
                "posted_at": now_utc
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)

            posted += 1

        except Exception as e:
            err_msg = f"Error posting '{article['slug']}': {e}"
            print(f"❌ {err_msg}")
            errors.append(err_msg)

        # Wait between posts
        if i < len(candidates) - 1:
            print("Waiting 30s...")
            time.sleep(30)

    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(candidates)} articles posted successfully")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
