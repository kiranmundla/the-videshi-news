#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime

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
    "lifestyle": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

# --- Fetch articles ---
print("Fetching untweeted articles from Supabase...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    headers=SUPA_HEADERS
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
eligible = [a for a in articles if a.get("image_url")]
to_post = eligible[:4]
print(f"Will post {len(to_post)} articles (with images)")

if not to_post:
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

# --- Compose posts ---
def extract_summary_and_takeaways(article):
    """Extract key content from article body for the X post."""
    body = article.get("body", "") or ""
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    category = article.get("category", "news")
    slug = article.get("slug", "")
    
    emoji = CATEGORY_EMOJI.get(category, "📰")
    label = CATEGORY_LABELS.get(category, category.upper())
    
    # Strip markdown formatting helpers
    clean_body = body.replace("**", "").replace("*", "").replace("##", "").replace("#", "").strip()
    
    # Get first ~600 words of body for context
    words = clean_body.split()
    context = " ".join(words[:600])
    
    return {
        "emoji": emoji,
        "label": label,
        "headline": headline,
        "subheadline": subheadline,
        "body_context": context,
        "slug": slug,
        "category": category
    }

def compose_post(article):
    """Compose a long-form X post from article data."""
    info = extract_summary_and_takeaways(article)
    
    # Build the post - we'll construct it line by line
    lines = []
    lines.append(f"{info['emoji']} {info['label']} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(info['headline'].upper() if len(info['headline']) < 100 else info['headline'])
    lines.append("")
    
    # Use subheadline as first paragraph if available
    if info['subheadline']:
        lines.append(info['subheadline'])
        lines.append("")
    
    # Extract 2-3 key paragraphs from body
    body = article.get("body", "") or ""
    # Split into paragraphs
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    # Filter out markdown headers and very short lines
    content_paragraphs = []
    for p in paragraphs:
        clean = p.strip().lstrip("#").strip()
        if len(clean) > 50 and not clean.startswith("![") and not clean.startswith("---"):
            # Remove markdown bold/italic
            clean = clean.replace("**", "").replace("*", "").replace("##", "").replace("#", "")
            content_paragraphs.append(clean)
    
    # Pick 2-3 best paragraphs (skip first if it's too similar to subheadline)
    selected = []
    for p in content_paragraphs:
        if len(selected) >= 3:
            break
        # Skip if too similar to subheadline
        if info['subheadline'] and p[:50] == info['subheadline'][:50]:
            continue
        selected.append(p)
    
    for p in selected[:2]:
        # Truncate long paragraphs
        words = p.split()
        if len(words) > 80:
            p = " ".join(words[:80]) + "..."
        lines.append(p)
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Key Takeaways:")
    lines.append("")
    
    # Extract key facts from body
    takeaways = []
    for p in content_paragraphs:
        if len(takeaways) >= 4:
            break
        # Look for sentences with numbers, names, or strong facts
        sentences = p.replace(". ", ".\n").split("\n")
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and len(s) < 200 and len(takeaways) < 4:
                # Prefer sentences with numbers or key words
                if any(c.isdigit() for c in s) or any(w in s.lower() for w in ['billion', 'million', 'percent', '%', 'first', 'largest', 'record', 'announced', 'launched']):
                    takeaways.append(s)
    
    # If we didn't find enough fact-heavy sentences, just use first sentences from paragraphs
    if len(takeaways) < 3:
        for p in content_paragraphs:
            if len(takeaways) >= 4:
                break
            first_sentence = p.split(". ")[0].strip()
            if len(first_sentence) > 30 and first_sentence not in takeaways:
                takeaways.append(first_sentence + ("." if not first_sentence.endswith(".") else ""))
    
    for t in takeaways[:4]:
        lines.append(f"▸ {t}")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{info['slug']}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")
    
    post_text = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten by reducing paragraphs
        while len(post_text) > 3900 and selected:
            selected.pop()
            # Rebuild
            lines_rebuild = []
            lines_rebuild.append(f"{info['emoji']} {info['label']} | The Videshi")
            lines_rebuild.append("")
            lines_rebuild.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_rebuild.append("")
            lines_rebuild.append(info['headline'])
            lines_rebuild.append("")
            if info['subheadline']:
                lines_rebuild.append(info['subheadline'])
                lines_rebuild.append("")
            for p in selected[:2]:
                words = p.split()
                if len(words) > 60:
                    p = " ".join(words[:60]) + "..."
                lines_rebuild.append(p)
                lines_rebuild.append("")
            lines_rebuild.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_rebuild.append("")
            lines_rebuild.append(f"📰 Full story: thevideshi.com/articles/{info['slug']}")
            lines_rebuild.append("")
            lines_rebuild.append("The Videshi — Your daily source for Indian diaspora news")
            lines_rebuild.append("🌐 thevideshi.com")
            post_text = "\n".join(lines_rebuild)
    
    return post_text

# --- Post loop ---
TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
if os.path.exists(TWEET_LOG_PATH):
    with open(TWEET_LOG_PATH) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}

posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(to_post):
    slug = article.get("slug", "unknown")
    article_id = article["id"]
    print(f"\n--- Posting {i+1}/{len(to_post)}: {slug} ---")
    
    # Compose post
    post_text = compose_post(article)
    print(f"Post length: {len(post_text)} chars")
    
    # Download and upload image
    media_id = None
    image_url = article.get("image_url", "")
    if image_url:
        try:
            print(f"Downloading image: {image_url[:80]}...")
            img_resp = requests.get(image_url, timeout=15)
            img_resp.raise_for_status()
            
            # Determine extension
            ct = img_resp.headers.get("content-type", "image/jpeg")
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
            
            print("Uploading image to X...")
            media = api_v1.media_upload(filename=tmp_path)
            media_id = media.media_id
            print(f"Image uploaded, media_id={media_id}")
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
        tweet_urls.append(tweet_url)
        
        # Update Supabase
        now_utc = datetime.utcnow().isoformat() + "Z"
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
            json={"tweeted_at": now_utc},
            headers=SUPA_HEADERS
        )
        if patch_resp.status_code < 300:
            print(f"Supabase updated: tweeted_at={now_utc}")
        else:
            print(f"Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article_id,
            "slug": slug,
            "posted_at": now_utc
        }
        with open(TWEET_LOG_PATH, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
    except Exception as e:
        err_msg = f"Failed to post {slug}: {e}"
        print(f"❌ {err_msg}")
        errors.append(err_msg)
    
    # Wait between posts
    if i < len(to_post) - 1:
        print("Waiting 30s...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print("Errors:")
    for e in errors:
        print(f"  {e}")
print(f"{'='*50}")
