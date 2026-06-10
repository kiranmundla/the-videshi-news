#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime, timezone

import requests
import tweepy
# Use requests for OpenAI to avoid httpx/no_proxy IPv6 parsing bug

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_ARTICLES = 4
DELAY_BETWEEN_POSTS = 30

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            line = line.removeprefix('export ')
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")
openai_env = load_env("~/workspace/.env.openai")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]
OPENAI_KEY = openai_env["OPENAI_API_KEY"]

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# No httpx OpenAI client — use requests directly to avoid IPv6 no_proxy bug

# Category emoji mapping
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

def fetch_unposted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null"
        "&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=SB_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def compose_post_with_ai(article):
    """Use GPT-4o-mini to compose a sharp long-form X post."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article.get("slug", "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "")[:3000]  # Limit body for token efficiency

    prompt = f"""You are a sharp news editor for The Videshi, an Indian diaspora news platform. Write a long-form X (Twitter) post for this article. The post should feel like a proper news brief — someone reading just the X post should feel informed.

ARTICLE DATA:
- Headline: {headline}
- Subheadline: {subheadline}
- Category: {cat}
- Body (source material):
{body}

FORMAT (follow exactly — include the separator lines):

{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

[REWRITTEN HEADLINE — punchier, more conversational than original. Title Case or ALL CAPS for impact.]

[2-3 SHORT PARAGRAPHS summarizing the story. Write in present tense where possible. Be conversational but authoritative — think Reuters meets a smart friend who reads everything. Extract the most interesting facts, quotes, and angles from the body. 150-250 words total.]

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ [Hard fact 1 — numbers, names, dates]
▸ [Hard fact 2]
▸ [Hard fact 3]
▸ [Hard fact 4 — if available]

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com

RULES:
- NO hashtags
- NO emojis in the body (only the category emoji at top and 📰/🌐 at bottom)
- Total post MUST be under 3900 characters
- Key takeaways should be the hardest facts with specific numbers/names/dates
- Don't start paragraphs with "In a" or "The" repeatedly — vary sentence openings
- Write the output directly, no preamble or explanation"""

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1500,
            },
            timeout=60,
        )
        resp.raise_for_status()
        post = resp.json()["choices"][0]["message"]["content"].strip()
        
        # Safety: trim if over limit
        if len(post) > 3950:
            # Truncate to last complete line before limit
            post = post[:3900]
            last_nl = post.rfind('\n')
            if last_nl > 3000:
                post = post[:last_nl]
        
        return post
    except Exception as e:
        print(f"  ⚠ AI composition failed: {e}, falling back to template")
        return compose_post_fallback(article)

def compose_post_fallback(article):
    """Simple fallback if AI fails."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article.get("slug", "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    
    return f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{subheadline or ''}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

def download_image(image_url):
    if not image_url or not image_url.strip():
        return None
    try:
        r = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True
        )
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct: ext = ".png"
        elif "webp" in ct: ext = ".webp"
        elif "gif" in ct: ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        if os.path.getsize(tmp.name) < 1000:
            os.unlink(tmp.name)
            print(f"  ⚠ Image too small, skipping")
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

def upload_media(image_path):
    try:
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=image_path)
        return media
    except Exception as e:
        print(f"  ⚠ Media upload failed: {e}")
        return None

def update_supabase(article_id):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(url, json={"tweeted_at": now}, headers=SB_HEADERS, timeout=15)
    r.raise_for_status()
    print(f"  ✓ Supabase updated (tweeted_at = {now})")

def log_tweet(tweet_id, article):
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
    }
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  ✓ Logged to tweet-log.json")

def main():
    print("=" * 60)
    print("The Videshi — X Auto-Post (Long-form with AI)")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}Z")
    print("=" * 60)
    
    articles = fetch_unposted_articles()
    print(f"\nFound {len(articles)} unposted articles")
    
    if not articles:
        print("Nothing to post. Done.")
        return
    
    with_images = [a for a in articles if a.get("image_url")]
    print(f"Articles with images: {len(with_images)}")
    
    to_post = with_images[:MAX_ARTICLES]
    print(f"Will post: {len(to_post)} articles\n")
    
    if not to_post:
        print("No eligible articles. Done.")
        return
    
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    posted = 0
    errors = []
    tweet_urls = []
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  Headline: {article['headline']}")
        print(f"  Slug: {article['slug']}")
        print(f"  Category: {article.get('category', 'unknown')}")
        
        # Compose post with AI
        post_text = compose_post_with_ai(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        img_path = download_image(article.get("image_url"))
        if img_path:
            media = upload_media(img_path)
            if media:
                media_ids = [media.media_id]
                print(f"  ✓ Image uploaded (media_id: {media.media_id})")
            try:
                os.unlink(img_path)
            except:
                pass
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            tweet_urls.append(tweet_url)
            print(f"  ✓ Posted! {tweet_url}")
            
            update_supabase(article["id"])
            log_tweet(tweet_id, article)
            posted += 1
            
        except Exception as e:
            err_msg = f"Failed to post '{article['slug']}': {e}"
            print(f"  ✗ {err_msg}")
            errors.append(err_msg)
        
        if i < len(to_post) - 1:
            print(f"  Waiting {DELAY_BETWEEN_POSTS}s...")
            time.sleep(DELAY_BETWEEN_POSTS)
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: Posted {posted}/{len(to_post)} articles")
    if tweet_urls:
        print("\nTweet URLs:")
        for url in tweet_urls:
            print(f"  {url}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()
