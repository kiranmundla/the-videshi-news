#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form premium posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TWITTER_CK = os.environ["TWITTER_CONSUMER_KEY"]
TWITTER_CS = os.environ["TWITTER_CONSUMER_SECRET"]
TWITTER_AT = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ATS = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
MAX_POSTS = 4
DELAY_SECS = 30

CATEGORY_EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏",
    "travel": "✈️", "lifestyle-health": "🧘", "markets-finance": "📈",
    "technology": "💻", "sports": "🏏", "entertainment": "🎬", "food": "🍛",
    "lifestyle": "🧘", "markets": "📈",
}

CATEGORY_LABEL = {
    "news": "NEWS", "immigration": "IMMIGRATION", "nri-world": "NRI WORLD",
    "travel": "TRAVEL", "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets-finance": "MARKETS & FINANCE", "technology": "TECHNOLOGY",
    "sports": "SPORTS", "entertainment": "ENTERTAINMENT", "food": "FOOD",
    "lifestyle": "LIFESTYLE", "markets": "MARKETS",
}

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

# --- Setup Twitter clients ---
client = tweepy.Client(
    consumer_key=TWITTER_CK,
    consumer_secret=TWITTER_CS,
    access_token=TWITTER_AT,
    access_token_secret=TWITTER_ATS,
)
auth = tweepy.OAuth1UserHandler(TWITTER_CK, TWITTER_CS, TWITTER_AT, TWITTER_ATS)
api_v1 = tweepy.API(auth)


def strip_markdown(text: str) -> str:
    """Strip markdown formatting to plain text."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_facts(body: str, subheadline: str) -> list[str]:
    """Extract key facts from article body for takeaways."""
    plain = strip_markdown(body or "")
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', plain)
    # Filter for fact-dense sentences (contain numbers, names, specific info)
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, currency, proper nouns
        has_facts = bool(re.search(r'(\d+[%,.]?\d*|\$|₹|€|£|million|billion|crore|lakh)', s))
        has_names = bool(re.search(r'[A-Z][a-z]+\s+[A-Z]', s))
        if has_facts or has_names:
            fact_sentences.append(s)
    
    # Also consider subheadline
    facts = []
    if subheadline:
        sub_clean = strip_markdown(subheadline)
        # Split subheadline if it has multiple parts
        sub_parts = re.split(r'[.;]', sub_clean)
        for p in sub_parts:
            p = p.strip()
            if len(p) > 15:
                facts.append(p)
    
    facts.extend(fact_sentences)
    # Deduplicate and take top 4
    seen = set()
    unique_facts = []
    for f in facts:
        f_lower = f.lower()[:40]
        if f_lower not in seen:
            seen.add(f_lower)
            # Trim to reasonable length
            if len(f) > 120:
                f = f[:117] + "..."
            unique_facts.append(f)
        if len(unique_facts) >= 4:
            break
    return unique_facts


def compose_post(article: dict) -> str:
    """Compose a long-form X Premium post from article data."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "")
    slug = article.get("slug", "")
    
    plain_body = strip_markdown(body)
    
    # Build summary: extract first few paragraphs worth of content
    paragraphs = [p.strip() for p in plain_body.split('\n\n') if p.strip() and len(p.strip()) > 30]
    
    # Build a 150-250 word summary from the first meaningful paragraphs
    summary_paras = []
    word_count = 0
    for p in paragraphs:
        # Skip very short paragraphs or ones that look like metadata
        if len(p) < 40:
            continue
        words = p.split()
        if word_count + len(words) > 250:
            # Take partial if we don't have enough yet
            if word_count < 100:
                remaining = 250 - word_count
                summary_paras.append(' '.join(words[:remaining]) + "...")
            break
        summary_paras.append(p)
        word_count += len(words)
        if word_count >= 150:
            break
    
    summary = '\n\n'.join(summary_paras) if summary_paras else subheadline or headline
    
    # Get key takeaways
    facts = extract_key_facts(body, subheadline)
    if len(facts) < 3:
        # Fallback: use first few sentences
        sentences = re.split(r'(?<=[.!?])\s+', plain_body)
        for s in sentences:
            s = s.strip()
            if 20 < len(s) < 150 and s not in facts:
                facts.append(s)
            if len(facts) >= 3:
                break
    
    # Build the post
    lines = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
        summary,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "Key Takeaways:",
        "",
    ]
    
    for f in facts[:4]:
        lines.append(f"▸ {f}")
    
    lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com",
    ])
    
    post = '\n'.join(lines)
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        while len(post) > 3900 and len(summary_paras) > 1:
            summary_paras.pop()
            summary = '\n\n'.join(summary_paras)
            lines[6] = summary
            post = '\n'.join(lines)
    
    return post


def download_image(image_url: str) -> str | None:
    """Download image to temp file, return path or None."""
    if not image_url:
        return None
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        resp.raise_for_status()
        
        # Determine extension
        ct = resp.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "gif" in ct:
            ext = ".gif"
        elif "webp" in ct:
            ext = ".webp"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Verify file isn't too small (likely error page)
        if os.path.getsize(tmp.name) < 1000:
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None


def update_supabase(article_id: str):
    """Mark article as tweeted in Supabase."""
    now = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=SB_HEADERS,
        json={"tweeted_at": now},
    )
    if resp.status_code < 300:
        print(f"  ✓ Supabase updated (tweeted_at = {now})")
    else:
        print(f"  ⚠ Supabase update failed: {resp.status_code} {resp.text}")


def log_tweet(tweet_id: str, article: dict):
    """Append to local tweet log."""
    log = {}
    if os.path.exists(TWEET_LOG_PATH):
        with open(TWEET_LOG_PATH) as f:
            log = json.load(f)
    log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }
    os.makedirs(os.path.dirname(TWEET_LOG_PATH), exist_ok=True)
    with open(TWEET_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def main():
    # 1. Fetch untweeted articles
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
    )
    articles = resp.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # 2. Filter and pick up to 4 with images
    candidates = [a for a in articles if a.get("image_url")]
    to_post = candidates[:MAX_POSTS]
    print(f"Selected {len(to_post)} articles to post")
    
    if not to_post:
        print("No articles to post. Done.")
        return
    
    # 3. Post each article
    posted = []
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(to_post)}] {article['headline'][:70]}...")
        print(f"  Category: {article['category']} | Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download & upload image
        media_id = None
        tmp_path = download_image(article.get("image_url"))
        if tmp_path:
            try:
                media = api_v1.media_upload(filename=tmp_path)
                media_id = media.media_id
                print(f"  ✓ Image uploaded (media_id: {media_id})")
            except Exception as e:
                print(f"  ⚠ Image upload to X failed: {e}")
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        else:
            print("  ⚠ No image available, posting text-only")
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]
            
            tweet_resp = client.create_tweet(**kwargs)
            tweet_id = tweet_resp.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✓ Posted! {tweet_url}")
            
            # Update Supabase
            update_supabase(article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted.append({
                "headline": article["headline"],
                "tweet_url": tweet_url,
                "slug": article["slug"],
            })
            
        except Exception as e:
            err_msg = str(e)
            print(f"  ✗ Tweet failed: {err_msg}")
            errors.append({"headline": article["headline"], "error": err_msg})
            # If rate limited, stop
            if "429" in err_msg or "Too Many" in err_msg:
                print("  Rate limited — stopping.")
                break
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {DELAY_SECS}s...")
            time.sleep(DELAY_SECS)
    
    # 4. Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(posted)} posted, {len(errors)} errors")
    for p in posted:
        print(f"  ✓ {p['headline'][:60]}... → {p['tweet_url']}")
    for e in errors:
        print(f"  ✗ {e['headline'][:60]}... → {e['error'][:80]}")


if __name__ == "__main__":
    main()
