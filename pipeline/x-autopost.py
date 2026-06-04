#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import re
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
    "culture": "🧘",
    "markets": "📈",
    "economy": "📈",
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
    "culture": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "economy": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

def strip_markdown(text):
    """Remove markdown formatting for clean plaintext."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body_text, headline, subheadline):
    """Extract concrete facts (numbers, names, dates) from article body."""
    # Get sentences with numbers, percentages, dollar amounts
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prioritize sentences with concrete data
        has_number = bool(re.search(r'\d+', s))
        has_money = bool(re.search(r'\$[\d,.]+', s))
        has_percent = bool(re.search(r'\d+%', s))
        has_name = bool(re.search(r'[A-Z][a-z]+\s[A-Z][a-z]+', s))
        score = has_number + has_money * 2 + has_percent * 2 + has_name
        if score >= 1:
            fact_sentences.append((score, s))
    
    fact_sentences.sort(key=lambda x: -x[0])
    facts = []
    seen_starts = set()
    for _, s in fact_sentences:
        start = s[:30].lower()
        if start not in seen_starts and len(facts) < 4:
            # Truncate long facts
            if len(s) > 150:
                s = s[:147] + "..."
            facts.append(s)
            seen_starts.add(start)
    
    return facts

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    
    headline = article["headline"]
    subheadline = article.get("subheadline", "")
    slug = article["slug"]
    body = strip_markdown(article.get("body", "") or "")
    
    # Build summary from body - first few meaningful paragraphs
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Skip any paragraph that looks like a header or metadata
    content_paragraphs = []
    for p in paragraphs:
        if p.startswith('Published') or p.startswith('By ') or p.startswith('Source'):
            continue
        if len(p) < 50:
            continue
        content_paragraphs.append(p)
    
    # Take 2-3 paragraphs for summary, targeting 150-250 words
    summary_parts = []
    word_count = 0
    for p in content_paragraphs:
        words = len(p.split())
        if word_count + words > 280:
            break
        summary_parts.append(p)
        word_count += words
        if word_count >= 150 and len(summary_parts) >= 2:
            break
    
    summary = "\n\n".join(summary_parts)
    
    # If summary is too short, add subheadline context
    if word_count < 80 and subheadline:
        summary = subheadline + "\n\n" + summary
    
    # Extract key takeaways
    facts = extract_key_facts(body, headline, subheadline)
    
    # If we couldn't extract enough facts, use subheadline pieces
    if len(facts) < 3 and subheadline:
        # Split subheadline on common separators
        sub_parts = re.split(r'[;.—–]', subheadline)
        for sp in sub_parts:
            sp = sp.strip()
            if sp and len(sp) > 15 and len(facts) < 4:
                if sp not in facts:
                    facts.append(sp)
    
    # Build the post
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Punchy headline - make it impactful
    display_headline = headline.strip()
    if not display_headline.isupper() and len(display_headline) < 80:
        display_headline = display_headline.upper()
    
    parts = [
        f"{emoji} {label} | The Videshi",
        "",
        separator,
        "",
        display_headline,
        "",
        summary,
    ]
    
    if facts:
        parts.extend([
            "",
            separator,
            "",
            "Key Takeaways:",
            "",
        ])
        for f in facts[:4]:
            parts.append(f"▸ {f}")
    
    parts.extend([
        "",
        separator,
        "",
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com",
    ])
    
    post_text = "\n".join(parts)
    
    # Ensure we're within 4000 chars
    if len(post_text) > 3900:
        # Trim summary
        while len(post_text) > 3900 and len(summary_parts) > 1:
            summary_parts.pop()
            summary = "\n\n".join(summary_parts)
            parts[6] = summary
            post_text = "\n".join(parts)
    
    return post_text

def download_image(image_url):
    """Download article image to temp file. Returns path or None."""
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True
        )
        resp.raise_for_status()
        
        # Determine extension
        content_type = resp.headers.get('Content-Type', '')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:  # Too small, likely an error page
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

def main():
    # Set up tweepy clients
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Fetch untweeted articles
    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        },
        headers=sb_headers,
    )
    resp.raise_for_status()
    articles = resp.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter: must have image_url, pick up to 4
    candidates = [a for a in articles if a.get("image_url")]
    to_post = candidates[:4]
    print(f"Selected {len(to_post)} articles to post")
    
    posted = 0
    errors = []
    tweet_urls = []
    
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    for i, article in enumerate(to_post):
        print(f"\n--- [{i+1}/{len(to_post)}] {article['headline'][:70]}...")
        
        try:
            # Compose the long-form post
            post_text = compose_post(article)
            print(f"  Post length: {len(post_text)} chars")
            
            # Download and upload image
            media_ids = None
            img_path = None
            if article.get("image_url"):
                img_path = download_image(article["image_url"])
                if img_path:
                    try:
                        media = api_v1.media_upload(filename=img_path)
                        media_ids = [media.media_id]
                        print(f"  ✓ Image uploaded (media_id: {media.media_id})")
                    except Exception as e:
                        print(f"  ⚠ Image upload to X failed: {e}")
                        media_ids = None
                    finally:
                        if img_path and os.path.exists(img_path):
                            os.unlink(img_path)
            
            # Post tweet
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            tweet_resp = client.create_tweet(**kwargs)
            tweet_id = tweet_resp.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✓ Posted: {tweet_url}")
            tweet_urls.append(tweet_url)
            
            # Update Supabase
            now_utc = datetime.utcnow().isoformat() + "Z"
            patch_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                json={"tweeted_at": now_utc},
                headers={
                    **sb_headers,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
            )
            if patch_resp.status_code < 300:
                print(f"  ✓ Supabase updated (tweeted_at)")
            else:
                print(f"  ⚠ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
            
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
                print("  ⏳ Waiting 30s before next post...")
                time.sleep(30)
                
        except Exception as e:
            err_msg = f"{article['headline'][:50]}: {e}"
            errors.append(err_msg)
            print(f"  ✗ ERROR: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if tweet_urls:
        print("Tweet URLs:")
        for url in tweet_urls:
            print(f"  {url}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

if __name__ == "__main__":
    main()
