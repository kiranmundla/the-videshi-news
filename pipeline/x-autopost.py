#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime, timezone

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

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    headers=SUPA_HEADERS,
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get("image_url")][:4]
print(f"Selected {len(candidates)} articles to post")

if not candidates:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}


def strip_markdown(text):
    """Remove markdown formatting from article body for clean text extraction."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = strip_markdown(article.get("body", ""))
    
    # Extract key content from body - get first ~500 words for context
    body_words = body.split()
    body_excerpt = " ".join(body_words[:500]) if body_words else ""
    
    # Build the summary and takeaways using the article content
    # We'll construct a smart summary from body paragraphs
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build 2-3 paragraph summary from the article content
    summary_parts = []
    chars_used = 0
    for p in paragraphs[:6]:  # Look at first 6 paragraphs
        # Skip very short or list-like paragraphs
        if len(p) < 50 or p.startswith('▸') or p.startswith('•'):
            continue
        # Use first sentence or two from good paragraphs
        sentences = re.split(r'(?<=[.!?])\s+', p)
        chunk = " ".join(sentences[:2])
        if chars_used + len(chunk) > 600:
            break
        summary_parts.append(chunk)
        chars_used += len(chunk)
        if len(summary_parts) >= 3:
            break
    
    summary = "\n\n".join(summary_parts) if summary_parts else subheadline
    
    # Extract key takeaways - look for numbers, names, concrete facts
    takeaways = []
    # Use subheadline as a takeaway source
    if subheadline and len(subheadline) > 20:
        takeaways.append(subheadline)
    
    # Find fact-dense sentences in the body
    all_sentences = re.split(r'(?<=[.!?])\s+', body_excerpt)
    for sent in all_sentences:
        if len(takeaways) >= 4:
            break
        sent = sent.strip()
        if len(sent) < 30 or len(sent) > 200:
            continue
        # Prefer sentences with numbers, dollar signs, percentages, or proper nouns
        has_facts = bool(re.search(r'(\d+[%,.]|\$|billion|million|crore|lakh)', sent, re.I))
        has_names = bool(re.search(r'[A-Z][a-z]+\s[A-Z][a-z]+', sent))
        if (has_facts or has_names) and sent not in summary:
            # Avoid duplicating summary content
            if not any(sent[:40] in s for s in summary_parts):
                takeaways.append(sent)
    
    # Ensure we have at least 3 takeaways
    if len(takeaways) < 3:
        for sent in all_sentences:
            if len(takeaways) >= 3:
                break
            sent = sent.strip()
            if 40 < len(sent) < 180 and sent not in takeaways:
                if not any(sent[:40] in s for s in summary_parts):
                    takeaways.append(sent)
    
    takeaways = takeaways[:4]
    
    # Format takeaways
    takeaway_lines = "\n".join(f"▸ {t}" for t in takeaways) if takeaways else ""
    
    # Compose the post
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}"""

    if takeaway_lines:
        post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}"""

    post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Ensure we stay under 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary_trimmed = summary[:300] + "..."
        post = post.replace(summary, summary_trimmed)
    
    return post


def download_image(url):
    """Download image to a temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15, stream=True)
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get("content-type", "")
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
        if size < 1000:  # Too small, probably an error page
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


def post_tweet(article):
    """Post a single article to X. Returns (tweet_id, tweet_url) or (None, error)."""
    text = compose_post(article)
    print(f"\n--- Posting: {article['headline'][:60]}... ---")
    print(f"  Post length: {len(text)} chars")
    
    media_ids = []
    tmp_path = None
    
    # Try to attach image
    if article.get("image_url"):
        tmp_path = download_image(article["image_url"])
        if tmp_path:
            try:
                media = api_v1.media_upload(filename=tmp_path)
                media_ids = [media.media_id]
                print(f"  Image uploaded: media_id={media.media_id}")
            except Exception as e:
                print(f"  Image upload to X failed: {e}")
                media_ids = []
        
    # Post tweet
    try:
        kwargs = {"text": text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        response = client.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        return tweet_id, tweet_url
    except Exception as e:
        print(f"  ❌ Tweet failed: {e}")
        return None, str(e)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        json={"tweeted_at": now},
        headers=SUPA_HEADERS,
        timeout=15,
    )
    if r.status_code < 300:
        print(f"  Supabase updated: tweeted_at={now}")
    else:
        print(f"  ⚠️ Supabase update failed: {r.status_code} {r.text}")


# --- Main loop ---
posted = 0
errors = []

for i, article in enumerate(candidates):
    if i > 0:
        print(f"\nWaiting 30s before next post...")
        time.sleep(30)
    
    tweet_id, result = post_tweet(article)
    
    if tweet_id:
        posted += 1
        mark_tweeted(article["id"])
        
        # Log locally
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with open(LOG_PATH, "w") as f:
            json.dump(tweet_log, f, indent=2)
    else:
        errors.append({"slug": article["slug"], "error": result})

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: {posted}/{len(candidates)} articles posted to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e['slug']}: {e['error']}")
print(f"{'='*50}")
