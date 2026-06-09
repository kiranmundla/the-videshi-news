#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, requests, tweepy
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
    "Prefer": "return=minimal"
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
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get("image_url")][:4]
print(f"Selected {len(candidates)} articles to post")

if not candidates:
    print("No articles to post. Done.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body for summary
    # Strip markdown formatting for cleaner reading
    import re
    clean_body = re.sub(r'#{1,6}\s+', '', body)
    clean_body = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_body)
    clean_body = re.sub(r'\*([^*]+)\*', r'\1', clean_body)
    clean_body = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_body)
    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', clean_body)
    clean_body = re.sub(r'<[^>]+>', '', clean_body)
    
    # Get paragraphs (non-empty lines that aren't just whitespace)
    paragraphs = [p.strip() for p in clean_body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first few meaningful paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:6]:
        if char_count + len(p) > 800:
            break
        summary_parts.append(p)
        char_count += len(p)
    
    summary = "\n\n".join(summary_parts[:3])
    
    # Extract key facts for takeaways
    # Look for sentences with numbers, names, specific facts
    all_sentences = []
    for p in paragraphs:
        sents = re.split(r'(?<=[.!?])\s+', p)
        all_sentences.extend([s.strip() for s in sents if len(s.strip()) > 20])
    
    # Pick sentences that have numbers or feel fact-dense
    fact_sentences = []
    for s in all_sentences:
        if re.search(r'\d+', s) or any(w in s.lower() for w in ['percent', 'billion', 'million', 'announced', 'launched', 'according']):
            if len(s) < 200:
                fact_sentences.append(s)
    
    # Use subheadline and fact sentences for takeaways
    takeaways = []
    if subheadline and len(subheadline) < 200:
        takeaways.append(subheadline)
    for s in fact_sentences:
        if s not in takeaways and len(takeaways) < 4:
            takeaways.append(s)
    # If we still need more, grab from early paragraphs
    if len(takeaways) < 3:
        for s in all_sentences[:10]:
            if s not in takeaways and len(s) < 180 and len(takeaways) < 4:
                takeaways.append(s)
    
    takeaways = takeaways[:4]
    takeaway_text = "\n".join(f"▸ {t}" for t in takeaways)
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary = "\n\n".join(summary_parts[:2])
        takeaways = takeaways[:3]
        takeaway_text = "\n".join(f"▸ {t}" for t in takeaways)
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post[:4000]

# --- Post loop ---
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(candidates):
    slug = article.get("slug", "unknown")
    article_id = article["id"]
    print(f"\n--- Article {i+1}/{len(candidates)}: {slug} ---")
    
    # Compose post
    post_text = compose_post(article)
    print(f"Post length: {len(post_text)} chars")
    
    # Try to download and upload image
    media_id = None
    image_url = article.get("image_url", "")
    if image_url:
        try:
            print(f"Downloading image: {image_url[:80]}...")
            img_resp = requests.get(
                image_url,
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=15
            )
            img_resp.raise_for_status()
            
            # Determine extension
            ct = img_resp.headers.get("content-type", "")
            ext = ".jpg"
            if "png" in ct: ext = ".png"
            elif "webp" in ct: ext = ".webp"
            elif "gif" in ct: ext = ".gif"
            
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(img_resp.content)
                tmp_path = tmp.name
            
            print(f"Uploading image to X ({len(img_resp.content)} bytes)...")
            media = api_v1.media_upload(filename=tmp_path)
            media_id = media.media_id
            print(f"Media uploaded: {media_id}")
            os.unlink(tmp_path)
        except Exception as e:
            print(f"Image failed ({e}), posting without image")
            media_id = None
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"✅ Posted: {tweet_url}")
        tweet_urls.append(tweet_url)
        
        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
            json={"tweeted_at": now_utc},
            headers=SUPA_HEADERS
        )
        if patch_resp.status_code < 300:
            print(f"✅ Supabase updated: tweeted_at = {now_utc}")
        else:
            print(f"⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article_id,
            "slug": slug,
            "posted_at": datetime.utcnow().isoformat() + "Z"
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
    except Exception as e:
        err_msg = f"Failed to post {slug}: {e}"
        print(f"❌ {err_msg}")
        errors.append(err_msg)
    
    # Wait between posts
    if i < len(candidates) - 1:
        print("Waiting 30s before next post...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(candidates)} articles")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
print("Done.")
