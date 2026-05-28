#!/usr/bin/env python3
"""Sports writer for The Videshi - May 28, 2026
Sinner's historic French Open collapse article.
"""

import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone

import requests
import urllib.parse

# Load environment
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key available")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate that image URL returns a valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        elif "image" in content_type and content_length == 0:
            # Some servers don't return Content-Length for HEAD
            r2 = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image invalid: type={content_type}, size={content_length}")
        return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False


def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    return any(b in url for b in banned)


def publish_article(article):
    """Publish article to Supabase."""
    payload = {
        "id": str(uuid.uuid4()),
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "status": "published",
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        print(f"  ✓ Published: {article['headline'][:60]}... (slug: {article['slug']})")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:200]}")
        return False


def write_sinner_collapse():
    """Sinner's historic French Open collapse."""
    headline = "He Was One Game Away. Then Jannik Sinner Lost Eighteen Straight Points and the French Open."
    subheadline = "The world number one was up 6-3, 6-2, 5-1, serving for the match. What happened next was one of the most extraordinary collapses in Grand Slam history."
    slug = "sinner-collapse-french-open-2026-cerundolo-heat-djokovic-25th-grand-slam-20260528"

    body = """The scoreboard told a simple story. Jannik Sinner led Juan Manuel Cerúndolo 6-3, 6-2, 5-1. He was serving for the match. He had lost seven games in two and a half sets. The world number one, riding a thirty-match winning streak that included three consecutive clay-court Masters titles, was about to cruise into the third round of the 2026 French Open.

Then he lost eighteen straight points.

## The Collapse

It began at 0-40 in the third set. Sinner looked visibly uncomfortable, pausing between points, bouncing less on his toes. He held a lengthy discussion with the chair umpire, then walked off Court Philippe Chatrier for medical treatment. The temperature in Paris had climbed past 32 degrees Celsius — around 90 degrees Fahrenheit — and the scorching conditions that had already claimed multiple players this week finally found their biggest victim.

When Sinner returned, he was a different player. Cerúndolo won the final six games of the third set. He won the fourth set 6-1. He won the fifth set 6-1. The final score read 3-6, 2-6, 7-5, 6-1, 6-1 — a result so improbable that one bettor who had wagered $5,000 on Sinner's moneyline at -10000 odds (for a potential $50 return) lost everything.

Sinner committed 54 unforced errors and hit 7 double faults across the match. In the final three sets, his body language deteriorated from discomfort to resignation. He lost 18 of the last 20 games.

"Of course, it's tough for him. He was leading the match. I couldn't win more than three games per set," Cerúndolo said afterward. "I think I was a little bit lucky. I feel sorry for him because he deserved to win. But then I don't know what happened — I think he was cramping maybe, or maybe the pressure, I don't know."

## The Numbers

According to ESPN Insights, Sinner is now the first man in the Open Era to lose more than one Grand Slam match as the top seed after holding a two-sets-to-love lead. It is a record no one wants.

The 24-year-old Italian had entered Roland Garros as the overwhelming favourite. With Carlos Alcaraz — the defending champion and world number two — sidelined by a wrist injury that will also keep him out of Wimbledon, Sinner's path to a maiden French Open title and a career Grand Slam had looked historically clear. He had won five consecutive Masters 1000 titles. His 30-match winning streak was the longest on tour. The French Open was the only major he had never won, having lost to Alcaraz in a fifth-set tiebreak in last year's epic final.

Now he is out in the second round — the earliest exit for a men's top seed at Roland Garros since 2008.

## A Tournament Without Its Two Best Players

For the first time since the 2023 US Open, a men's Grand Slam final will not feature either Alcaraz or Sinner. The two players who have shared the last seven major titles between them are both absent from the second week.

The new betting favourite is Alexander Zverev, the second seed, who has cruised through his opening matches. But the name on everyone's mind is Novak Djokovic.

The 39-year-old Serbian, seeded third, is chasing a record-breaking 25th Grand Slam singles title. He beat Frenchman Valentin Royer 6-3, 6-2, 6-7(7), 6-3 to reach the third round, where he faces the talented young Brazilian Joao Fonseca on Friday. After his second-round win, Djokovic celebrated with a Michael Jackson-style moonwalk on Chatrier — the kind of showmanship that suggests he senses an opportunity.

Sania Mirza, the Indian tennis icon, had flagged Djokovic as the "dark horse" in the men's draw before the tournament began. With Sinner gone, that assessment looks prophetic.

## The Diaspora Angle

For the Indian tennis community watching from afar, Sinner's exit reshapes the tournament in which India still has a stake. Yuki Bhambri and Sriram Balaji — India's last two men standing at Roland Garros — are into the second round of doubles. Their run continues even as the singles draw has been torn apart by heat and chaos.

This has been a French Open unlike any other. Seventeen players withdrew before the tournament began. Fifteen seeds lost in the first round. Czech player Jakub Menšík collapsed on court during his second-round match. Elena Rybakina, the world number two, was stunned in the second round. And now the world number one is gone too.

The 2026 French Open began with one clear favourite. It now has none. And in the brutal Paris heat, anything can happen.

## What Comes Next

Sinner's early exit will cost him significant ranking points — he had reached the final last year. The question now is whether the physical issues were a one-off heat reaction or something more concerning ahead of Wimbledon and the US Open.

For Djokovic, the draw has opened up in a way he could not have imagined. At thirty-nine, with knees that have been surgically repaired and a body that defies every athletic timeline, this may be his best and last chance at twenty-five."""

    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com/sports/tennis/ailing-sinner-knocked-out-french-open-second-round-by-cerundolo-2026-05-28/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/28/sport/jannik-sinner-crashes-out-roland-garros"},
        {"name": "New York Post", "url": "https://nypost.com/2026/05/28/sports/jannik-sinner-stunned-at-2026-french-open-in-all-time-collapse/"},
        {"name": "ESPN Insights", "url": "https://x.com/ESPNInsights"}
    ]

    # Image sourcing — Wikipedia for Sinner
    print("  Sourcing image for Sinner article...")
    image_url = None
    image_caption = "Jannik Sinner during his second-round match at the 2026 French Open"
    image_attribution = None

    # Try Wikipedia for Sinner
    wiki_img = fetch_wikipedia_person_image("Jannik Sinner")
    if wiki_img and not is_banned_url(wiki_img) and validate_image(wiki_img):
        image_url = wiki_img
        image_attribution = "Wikimedia Commons"
    else:
        # Try Pexels - specific clay court tennis
        pexels_img = fetch_pexels_image("tennis clay court Roland Garros match", "tennis player clay court heat")
        if pexels_img and not is_banned_url(pexels_img) and validate_image(pexels_img):
            image_url = pexels_img
            image_attribution = "Pexels"

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "sources": sources,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
    }


def main():
    print("=" * 60)
    print("The Videshi — Sports Writer (May 28, 2026)")
    print("=" * 60)

    # Check for duplicates
    print("\nChecking for duplicate articles...")
    try:
        three_days_ago = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            params={
                "select": "headline,slug",
                "status": "eq.published",
                "category": "eq.sports",
                "order": "published_at.desc",
                "limit": "30",
            },
            timeout=15,
        )
        existing = r.json() if r.status_code == 200 else []
        existing_slugs = [a["slug"] for a in existing]
        existing_headlines_lower = [a["headline"].lower() for a in existing]
        print(f"  Found {len(existing)} recent sports articles")
    except Exception as e:
        print(f"  ⚠ Could not check duplicates: {e}")
        existing_slugs = []
        existing_headlines_lower = []

    articles_to_write = []

    # Article 1: Sinner collapse
    sinner_slug = "sinner-collapse-french-open-2026-cerundolo-heat-djokovic-25th-grand-slam-20260528"
    sinner_dupe = any("sinner" in s and "collapse" in s for s in existing_slugs) or \
                  any("sinner" in h and "cerundolo" in h for h in existing_headlines_lower) or \
                  any("sinner" in h and "eighteen" in h for h in existing_headlines_lower)
    
    if not sinner_dupe:
        print("\n📝 Writing Article 1: Sinner's French Open Collapse")
        article = write_sinner_collapse()
        articles_to_write.append(article)
    else:
        print("\n⏭  Skipping Sinner article (duplicate detected)")

    # Publish
    print(f"\n{'=' * 60}")
    print(f"Publishing {len(articles_to_write)} article(s)...")
    
    success = 0
    for article in articles_to_write:
        if publish_article(article):
            success += 1

    print(f"\n✅ Done. Published {success}/{len(articles_to_write)} articles.")


if __name__ == "__main__":
    main()
