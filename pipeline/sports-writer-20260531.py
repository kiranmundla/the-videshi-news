#!/usr/bin/env python3
"""
The Videshi Sports Writer - 2026-05-31
Generates and publishes sports articles to Supabase.
"""

import os, json, sys, re, uuid, subprocess
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if 'PEXELS' in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

import requests
import urllib.parse

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
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels. Use curl to avoid 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that image URL returns 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        # Try GET for servers that don't support HEAD properly
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type:
            # Read first chunk to verify size
            chunk = next(r.iter_content(chunk_size=6000), b"")
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {content_type}")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
        return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False

def is_banned_image(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "scontent-"]
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False

def publish_article(article):
    """Publish article to Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": article.get("sources", "The Videshi Sports Desk"),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=payload,
        timeout=15
    )
    
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {article['headline'][:60]}... (id: {result[0].get('id', 'unknown')})")
            return True
        elif isinstance(result, dict):
            print(f"  ✓ Published: {article['headline'][:60]}... (id: {result.get('id', 'unknown')})")
            return True
    
    print(f"  ✗ Failed to publish: {r.status_code} - {r.text[:200]}")
    return False

# ==================== ARTICLES ====================

articles = []

# ==================== ARTICLE 1: Gulveer Singh Sub-4 Minute Mile ====================
print("\n--- Article 1: Gulveer Singh Sub-4 Minute Mile ---")

# Image: Try Wikipedia first, then Pexels for running track
img_url = fetch_wikipedia_person_image("Gulveer Singh (athlete)")
img_attr = "Wikimedia Commons"
if not img_url or is_banned_image(img_url) or not validate_image_url(img_url):
    img_url = fetch_wikipedia_person_image("Gulveer Singh")
    if not img_url or is_banned_image(img_url) or not validate_image_url(img_url):
        img_url = fetch_pexels_image("mile running track athletics finish line", "distance runner track race")
        img_attr = "Pexels"
        if not img_url or not validate_image_url(img_url):
            img_url = None
            img_attr = ""

article1 = {
    "headline": "Three Minutes and Fifty-Five Seconds. Gulveer Singh Is the First Indian to Run a Sub-Four-Minute Mile.",
    "subheadline": "The 27-year-old army runner, who trains in the United States, clocked 3:55.63 at a World Athletics Continental Tour event in Cleveland — adding another 'first Indian' milestone to a growing list.",
    "slug": "gulveer-singh-first-indian-sub-four-minute-mile-cleveland-355-athletics-nri-20260531",
    "body": """In a sport that has always measured its greatest barrier in four minutes, an Indian has finally broken through.

Gulveer Singh, 27, clocked **3:55.63** at the 24th Annual Music City Track Carnival at Lee University in Cleveland on Saturday, becoming the **first Indian runner to complete a mile in under four minutes**. He did not merely break the barrier — he won the race, finishing ahead of Americans Christopher Knight (3:59.72) and Tristan Trevino (4:00.27).

The sub-four-minute mile has been one of the most iconic benchmarks in athletics since Roger Bannister first cracked it in 1954. Seventy-two years later, an Indian army runner based in the United States added his name to the ledger at a World Athletics Continental Tour Challenger event.

## A Record-Breaker by Habit

For those who have followed Gulveer's trajectory, the milestone was less a surprise and more an inevitability. The distance runner from Punjab has made a habit of being the first Indian to reach marks that once seemed beyond the country's grasp.

He is the first Indian to break the **13-minute barrier** in the 5,000-metre track race, holding the national indoor record of **12:59.77**, set at the Boston University Terrier DMR Challenge last year. He also holds the Indian national track record for the 10,000 metres at **27:00.22**, and won a bronze medal in the event at the Asian Games.

The progression has been deliberate. Gulveer moved to the United States to train at altitude and alongside world-class fields — a path that has accelerated his development and placed him in competitive races that simply do not exist in India's domestic athletics circuit.

## What the Sub-Four Means for Indian Running

India has never been a middle-distance running nation. The country's strengths have historically leaned toward long-distance and marathon events, with the odd sprinter breaking through. A sub-four-minute mile from an Indian athlete signals that the ceiling is shifting.

The timing is significant. Gulveer is preparing for both the **Glasgow Commonwealth Games** and the **Asian Games in Japan**, where India will look to medal in multiple track events. His Cleveland performance — in a race where the only other sub-four finisher was an American — suggests he is in peak shape heading into a packed summer calendar.

## Part of a Bigger Week

Gulveer's achievement did not arrive in isolation. Indian athletics has had one of its most remarkable weeks in recent memory:

- **Pooja Singh** cleared 1.93 metres at the Asian U20 Athletics Championships in Hong Kong, breaking a 14-year-old national high jump record and winning gold.
- **Gurindervir Singh** ran 10.09 seconds in the 100 metres at the Federation Cup in Ranchi, becoming the first Indian under 10.10 seconds and qualifying for both the Commonwealth and Asian Games.
- **Vishal TK** ran 44.98 seconds in the 400 metres — the first Indian to go sub-45.
- **Tejaswin Shankar** crossed 8,000 decathlon points for the first time by an Indian athlete.

Five barriers. One week. For a country that has historically struggled to produce world-class track and field athletes beyond the occasional javelin thrower, the numbers represent a genuine shift in capability.

## The NRI Athlete Pipeline

Gulveer's story carries a particular resonance for the diaspora. Like a growing number of Indian athletes, he trains and competes primarily in the United States. The access to better facilities, structured coaching, competitive fields, and altitude training has transformed what is possible.

The Indian army runner's path — competing on American soil, breaking records at American university tracks, yet representing India on the world stage — mirrors the broader story of Indian talent finding its ceiling abroad before bringing it home.

When the Commonwealth Games begin in Glasgow, Gulveer will not be a curiosity. He will be a contender. And somewhere in his preparation, 3:55.63 in Cleveland will be the moment he knew the ceiling had finally cracked.

*Sources: Athletics Federation of India, World Athletics Continental Tour, IANS*""",
    "image_url": img_url,
    "image_attribution": img_attr,
    "sources": "The Videshi Sports Desk"
}
articles.append(article1)

# ==================== ARTICLE 2: Carlsen's Crisis at Norway Chess ====================
print("\n--- Article 2: Carlsen's Crisis at Norway Chess ---")

# Image: Carlsen from Wikipedia
img_url2 = fetch_wikipedia_person_image("Magnus Carlsen")
img_attr2 = "Wikimedia Commons"
if not img_url2 or is_banned_image(img_url2) or not validate_image_url(img_url2):
    img_url2 = fetch_pexels_image("chess grandmaster tournament", "chess board competition")
    img_attr2 = "Pexels"
    if not img_url2 or not validate_image_url(img_url2):
        img_url2 = None
        img_attr2 = ""

article2 = {
    "headline": "Carlsen Is in Last Place at Norway Chess. The World Number One Has Lost 16 Elo Points in Five Rounds.",
    "subheadline": "Wesley So inflicted a third loss on the Norwegian world number one, while India's Gukesh climbed to third with a classical victory over Praggnanandhaa. In the women's event, Divya Deshmukh leads at the halfway mark.",
    "slug": "carlsen-last-place-norway-chess-2026-gukesh-divya-deshmukh-so-firouzja-round-5-nri",
    "body": """Magnus Carlsen has played five rounds at Norway Chess 2026, and each one has peeled away another layer of the invincibility that has defined his career. The world number one, playing in his home country, sits last in a six-player field. He has **4.5 points**. He has lost **16.4 Elo points**. On Friday, he lost his third classical game of the tournament to Wesley So.

For the greatest chess player of his generation, this is unfamiliar territory. For the two Indians in the field, it has opened a window.

## So Takes Down the King

The American grandmaster Wesley So, playing with the black pieces, defeated Carlsen in round five to climb to sole second place on **8.5 points**. The loss was Carlsen's third in five rounds — a frequency of defeat he has rarely experienced in his career, let alone in a single tournament.

Carlsen's live rating has dropped to **2825**. He still leads the world rankings by a comfortable margin over Hikaru Nakamura (2792), but the gap is narrowing faster than at any point in recent years.

Tournament leader **Alireza Firouzja** of France maintained his grip on first place with **10 points**, winning his armageddon game against Germany's Vincent Keymer after a classical draw. The 23-year-old has been imperious throughout, losing only one match point across five rounds.

## Gukesh Turns Twenty and Finds His Spark

A day after turning 20, **D Gukesh** defeated compatriot **R Praggnanandhaa** in a gripping classical battle to pocket three full points and climb to sole third place on **6.5 points**.

The game, arising from a Ragozin Defence, swung repeatedly between the two young Indian grandmasters. Both enjoyed winning chances at various stages, but it was Gukesh — the reigning World Champion — who held his nerve when it mattered.

For Gukesh, the victory seemed to breathe life back into his campaign. Fans packed the arena for autographs and selfies with the world champion, who appeared visibly more relaxed after several difficult rounds in which he had slipped quietly from the playing hall following disappointing results.

Praggnanandhaa remains fourth on **6 points**, while Keymer holds fifth on **5 points**. The two Indians are separated by just half a point, with five rounds remaining.

## Divya Deshmukh Takes the Women's Lead

In the women's tournament, India's **Divya Deshmukh** moved into sole first place at the halfway mark with **8.5 points** after defeating China's Zhu Jiner 3-0 (a classical win) in round five.

The 20-year-old from Nagpur has been the most consistent performer in the six-player women's field, which also features former world champion Ju Wenjun, Kazakhstan's Bibisara Assaubayeva, and India's Koneru Humpy.

Assaubayeva is close behind on **8 points**, with Anna Muzychuk of Ukraine third on **7**. Humpy, who picked up her first match win of the tournament by defeating Ju Wenjun in armageddon, is sixth on **4.5 points** but remains in contention given the tournament's scoring system, where a single classical win is worth three points.

## What It Means

Norway Chess runs through June 5, with five rounds remaining in both the open and women's sections. The standings are fluid — Firouzja leads, but So, Gukesh, and even Praggnanandhaa are within striking distance if the Frenchman falters.

For Carlsen, the question is no longer whether he will win the tournament. It is whether he can avoid finishing last in his own country's marquee chess event. At 35, with his rating at its lowest point in years, the tournament has become less about the title and more about damage limitation.

For India, the picture is brighter. Gukesh and Divya Deshmukh are both in the top three of their respective sections. A classical victory from either in round six could shift the tournament's dynamics entirely.

**Round 6 pairings (Open):** Carlsen vs Firouzja, So vs Praggnanandhaa, Gukesh vs Keymer.
**Round 6 pairings (Women):** Divya vs Ju Wenjun, Assaubayeva vs Humpy, Zhu Jiner vs Muzychuk.

*Sources: Norway Chess, ChessBase, Chess.com*""",
    "image_url": img_url2,
    "image_attribution": img_attr2,
    "sources": "The Videshi Sports Desk"
}
articles.append(article2)

# ==================== PUBLISH ====================
print("\n=== Publishing articles ===")
success_count = 0
for i, article in enumerate(articles):
    print(f"\nPublishing article {i+1}/{len(articles)}: {article['headline'][:60]}...")
    if publish_article(article):
        success_count += 1

print(f"\n=== Done: {success_count}/{len(articles)} articles published ===")
