#!/usr/bin/env python3
"""Post up to 4 recent Videshi articles to X as long-form posts with images."""

import tweepy
import requests
import json
import os
import sys
import time
import tempfile
import re
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# Load env
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

def strip_markdown(text):
    """Strip markdown formatting to plain text for X post."""
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
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*{3,}$', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body_text, subheadline, n=4):
    """Extract key facts from article body for takeaways."""
    facts = []
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    
    # Look for sentences with numbers, percentages, names, strong facts
    priority_patterns = [
        r'\$[\d,.]+',  # dollar amounts
        r'\d+%',       # percentages
        r'₹[\d,.]+',   # rupee amounts
        r'\d+\s*(billion|million|trillion|crore|lakh)',  # large numbers
    ]
    
    scored = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        score = 0
        for pat in priority_patterns:
            if re.search(pat, s, re.IGNORECASE):
                score += 2
        # Prefer sentences with proper nouns (capitalized words mid-sentence)
        caps = re.findall(r'(?<!\.\s)[A-Z][a-z]+', s[1:])
        score += min(len(caps), 2)
        scored.append((score, s))
    
    scored.sort(key=lambda x: -x[0])
    
    for score, s in scored[:n]:
        # Clean up the sentence
        s = re.sub(r'\s+', ' ', s).strip()
        if not s.endswith(('.', '!', '?')):
            s += '.'
        facts.append(s)
    
    # If we don't have enough, pull from subheadline
    if len(facts) < 3 and subheadline:
        sub_sentences = re.split(r'(?<=[.!?])\s+', subheadline)
        for s in sub_sentences:
            s = s.strip()
            if s and len(s) > 15 and s not in facts:
                facts.append(s)
                if len(facts) >= n:
                    break
    
    return facts[:n]

def compose_post(article):
    """Compose a long-form X post for the article."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article["headline"]
    subheadline = article.get("subheadline", "")
    slug = article["slug"]
    body = strip_markdown(article.get("body", ""))
    
    # Create a punchy headline for X
    # Remove trailing periods, make it impactful
    x_headline = headline.strip().rstrip('.')
    
    # Build summary from body - take the first few meaningful paragraphs
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:
        p_words = len(p.split())
        if word_count + p_words > 250:
            break
        summary_parts.append(p)
        word_count += p_words
        if word_count >= 120:
            break
    
    summary = '\n\n'.join(summary_parts)
    
    # If summary is too short, add subheadline context
    if len(summary) < 100 and subheadline:
        summary = subheadline + '\n\n' + summary
    
    # Trim summary to reasonable length
    if len(summary) > 1200:
        summary = summary[:1200].rsplit('.', 1)[0] + '.'
    
    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    
    takeaways = ""
    if facts:
        takeaways = "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\nKey Takeaways:\n\n"
        for f in facts:
            takeaways += f"▸ {f}\n"
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{x_headline}

{summary}
{takeaways}
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure within 4000 char limit
    if len(post) > 3900:
        # Trim summary
        excess = len(post) - 3800
        summary = summary[:len(summary) - excess].rsplit('.', 1)[0] + '.'
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{x_headline}

{summary}
{takeaways}
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def main():
    # Init Twitter clients
    # v2 client for posting tweets
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    # v1.1 API for media upload
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Supabase headers
    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    
    # Fetch untweeted articles
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=sb_headers,
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        }
    )
    
    if resp.status_code != 200:
        print(f"ERROR: Supabase fetch failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    articles = resp.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter to articles with images, take up to 4
    candidates = [a for a in articles if a.get("image_url")]
    if not candidates:
        print("No articles with images found. Nothing to post.")
        return
    
    to_post = candidates[:4]
    print(f"Will post {len(to_post)} articles\n")
    
    # Load tweet log
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  Headline: {article['headline'][:80]}...")
        print(f"  Category: {article['category']}")
        print(f"  Slug: {article['slug']}")
        
        # Compose the post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_id = None
        tmp_path = None
        try:
            img_url = article["image_url"]
            img_resp = requests.get(img_url, timeout=15)
            if img_resp.status_code == 200:
                # Determine extension
                content_type = img_resp.headers.get("Content-Type", "image/jpeg")
                ext = ".jpg"
                if "png" in content_type:
                    ext = ".png"
                elif "webp" in content_type:
                    ext = ".webp"
                
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
                with os.fdopen(tmp_fd, 'wb') as f:
                    f.write(img_resp.content)
                
                media = api_v1.media_upload(filename=tmp_path)
                media_id = media.media_id
                print(f"  Image uploaded: media_id={media_id}")
            else:
                print(f"  Image download failed: {img_resp.status_code}")
        except Exception as e:
            print(f"  Image error (posting without): {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]
            
            tweet_resp = client.create_tweet(**kwargs)
            tweet_id = tweet_resp.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Update Supabase
            now_utc = datetime.utcnow().isoformat() + "Z"
            patch_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                headers=sb_headers,
                json={"tweeted_at": now_utc}
            )
            if patch_resp.status_code in (200, 204):
                print(f"  Supabase updated: tweeted_at={now_utc}")
            else:
                print(f"  Supabase update warning: {patch_resp.status_code} {patch_resp.text}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": article["slug"],
                "posted_at": now_utc
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Tweet failed for {article['slug']}: {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  Waiting 30s...")
            time.sleep(30)
    
    print(f"\n=== SUMMARY ===")
    print(f"Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")

if __name__ == "__main__":
    main()