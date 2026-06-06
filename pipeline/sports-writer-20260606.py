#!/usr/bin/env python3
"""Sports writer for The Videshi — June 6, 2026 batch"""

import json
import os
import sys
import uuid
import time
import requests
import subprocess
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    try:
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3'
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_and_upload_image(image_url, filename):
    """Download image, compress, upload to Supabase storage. Returns public URL or None."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Download failed: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"  ✗ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return None
        
        compressed = compress_image(r.content)
        print(f"  ✓ Compressed: {len(r.content)} → {len(compressed)} bytes")
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        up = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ✗ Upload failed: {up.status_code} {up.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Image processing error: {e}")
        return None

def source_image(person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution, caption_hint) or (None, None, None)."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": "high"})
    
    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries:
            commons = fetch_wikimedia_commons_images(q)
            for r in commons[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "relevance": "medium"})
    
    # Source 3: Pexels
    if pexels_query:
        pexels_img = fetch_pexels_image(pexels_query)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": "low"})
    
    if not candidates:
        return None, None, None
    
    # Prefer wikipedia > wikimedia_commons > pexels
    priority = {"wikipedia": 0, "wikimedia_commons": 1, "pexels": 2}
    candidates.sort(key=lambda c: priority.get(c["source"], 99))
    best = candidates[0]
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
    return best["url"], attribution, best["source"]

def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    art_id = str(uuid.uuid4())
    
    # Source and upload image
    img_url = None
    img_attribution = None
    
    raw_url, attribution, src = source_image(
        person_name=article.get("image_person"),
        topic_queries=article.get("image_topics"),
        pexels_query=article.get("image_pexels")
    )
    
    if raw_url:
        filename = f"{art_id}.jpg"
        img_url = download_and_upload_image(raw_url, filename)
        img_attribution = attribution
    
    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": json.dumps(article["sources"]),
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": article.get("image_caption", ""),
        "image_attribution": img_attribution or "",
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        print(f"\n✅ Published: {article['headline'][:80]}")
        print(f"   ID: {art_id}")
        print(f"   Slug: {article['slug']}")
        if img_url:
            print(f"   Image: {img_url[:80]}...")
        return True
    else:
        print(f"\n❌ Failed to publish: {r.status_code}")
        print(f"   Response: {r.text[:500]}")
        return False


# ============================================================
# ARTICLE 1: Bumrah Returns for Asian Games
# ============================================================

article1_body = """India have named a full-strength squad for the 2026 Asian Games cricket tournament in Aichi-Nagoya, Japan, and the most significant name on the list is Jasprit Bumrah.

The pace spearhead, who was rested for the upcoming T20I tours of Ireland and England as part of the BCCI's workload management programme, returns for the continental event where India will defend the gold medal they won in Hangzhou three years ago. His inclusion signals the seriousness with which the board views the Asian Games — this is not a development exercise.

## Iyer Leads, Tilak Is His Deputy

Shreyas Iyer, freshly appointed as India's T20I captain after replacing Suryakumar Yadav, will lead the 15-member squad. Tilak Varma has been named vice-captain, a reward for his consistent performances across formats over the past year.

The rest of the squad reads like India's first-choice white-ball XI: Abhishek Sharma and Sanju Samson at the top, Ishan Kishan as the second keeper, Shivam Dube and Nitish Kumar Reddy providing middle-order depth, and Axar Patel, Washington Sundar, Varun Chakaravarthy, and Ravi Bishnoi forming a deep spin contingent. Arshdeep Singh and Harshit Rana complete the pace unit alongside Bumrah.

And then there is Vaibhav Sooryavanshi. The 15-year-old has been named in all three of India's white-ball squads — the Ireland T20Is, the England T20Is, and now the Asian Games. His IPL 2026 season, in which he scored 776 runs at a strike rate of 237 and broke Chris Gayle's record for most sixes in a single campaign, has left the selectors with no choice but to fast-track him.

## Who Is Missing

The absences tell their own story. Suryakumar Yadav, who captained India at the 2026 T20 World Cup, has been dropped entirely — not rested, dropped. Chief selector Ajit Agarkar made no attempt to soften it, pointing instead to Iyer's franchise leadership record as the reason for the change.

Kuldeep Yadav is the other notable omission. The left-arm wrist spinner is part of the Test squad currently playing Afghanistan in Mullanpur but finds no place in any of the three T20I assignments. With Chakaravarthy, Bishnoi, and Sundar all ahead of him in the white-ball pecking order, Kuldeep's path back into India's limited-overs plans has narrowed sharply.

Hardik Pandya is absent too, still recovering from the back injury he sustained during the IPL. He has reportedly cleared his fitness test and remains in the ODI squad for the Afghanistan series, but the BCCI is taking no chances with his T20I workload before a tournament that does not begin until September.

## What the Asian Games Mean

Cricket made its return to the Asian Games in 2023 after a 13-year absence, and India made the most of it. A second-string squad led by Ruturaj Gaikwad swept through the Hangzhou tournament to claim the country's first-ever Asian Games cricket gold.

This time, the event moves to the Aichi prefecture in Japan, with Nagoya as the hub city. The men's competition runs from September 24 to October 3, featuring ten teams in the T20 format. India will face Afghanistan, Bangladesh, Pakistan, Sri Lanka, hosts Japan, and four qualifiers — Nepal, Malaysia, Hong Kong, and Oman.

The tournament matters beyond the medal. For India's sizable diaspora in Japan — estimated at over 46,000 and growing, concentrated in Tokyo, Osaka, and Nagoya's tech corridors — it is a rare chance to watch international cricket in person. The BCCI's decision to send its best squad, rather than a development team, suggests they understand the significance.

## India's Full Squad for Asian Games 2026

Shreyas Iyer (C), Tilak Varma (VC), Abhishek Sharma, Sanju Samson (WK), Ishan Kishan (WK), Shivam Dube, Nitish Kumar Reddy, Axar Patel, Washington Sundar, Varun Chakaravarthy, Ravi Bishnoi, Harshit Rana, Arshdeep Singh, Vaibhav Sooryavanshi, Jasprit Bumrah.

The Asian Games are still three months away. But the squad tells you everything you need to know about what India think of this tournament: it is not a second priority. Not any more."""

article1 = {
    "headline": "Bumrah Is Back. India Have Named Their Strongest T20 Squad for the Asian Games. Kuldeep Yadav Is Nowhere in It.",
    "subheadline": "The BCCI's 15-member squad for the September tournament in Aichi-Nagoya includes Sooryavanshi across all three white-ball assignments. Suryakumar Yadav and Kuldeep Yadav have been left out. India defend their Hangzhou gold.",
    "body": article1_body.strip(),
    "slug": "bumrah-returns-india-asian-games-2026-squad-aichi-nagoya-kuldeep-out-sooryavanshi-nri",
    "sources": [
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"},
        {"name": "BCCI", "url": "https://www.bcci.tv"},
        {"name": "Reuters", "url": "https://www.reuters.com"}
    ],
    "image_person": "Jasprit Bumrah",
    "image_topics": ["Jasprit Bumrah cricket bowling", "Jasprit Bumrah India cricket"],
    "image_pexels": "cricket fast bowler India",
    "image_caption": "Jasprit Bumrah during an international match for India"
}


# ============================================================
# ARTICLE 2: Jaiswal Replaces Kohli for ODIs
# ============================================================

article2_body = """The BCCI has named Yashasvi Jaiswal as Virat Kohli's replacement in India's ODI squad for the three-match series against Afghanistan, starting June 14. Kohli tore his hamstring during the IPL final last week — a match he refused to leave despite the injury — and is expected to be fit only in time for the England ODI series in July.

Jaiswal, 24, has been one of India's most dependable batters in Test cricket over the past 18 months. He scored 386 runs in the home series against New Zealand, 391 in Australia, and has looked increasingly comfortable against pace and spin on varied surfaces. But his ODI career has barely begun. He has played just a handful of one-day internationals, and his selection over Ruturaj Gaikwad, the man widely expected to fill Kohli's spot, is a clear statement of hierarchy.

## Gaikwad Goes to Sri Lanka

Gaikwad, who led India to the Asian Games gold in Hangzhou in 2023 and has been prolific in domestic cricket, was not named in the ODI squad. He has instead been picked in the India A squad for a multi-day tour of Sri Lanka under the captaincy of Dhruv Jurel.

The India A squad is not a punishment — it includes several players with international experience, including Devdutt Padikkal, Sai Sudharsan, and Anshul Kamboj. But for Gaikwad, who was in the frame for Kohli's spot just days ago, the assignment stings. The selectors had a choice between the man who has been India's most reliable white-ball understudy for two years and the man who has been their most exciting red-ball prospect. They chose Jaiswal.

## Agarkar Leaves the Door Open for Kohli

Chief selector Ajit Agarkar, speaking to reporters in Mumbai after the selection meeting on Saturday, said the timeline on Kohli's recovery remained uncertain. "With Virat at this point, it's just been less than a week since he injured himself in the finals," Agarkar said. "We don't know the timelines yet. But it looks like he might be fit for that England one-day series. It's not a definitive answer, so don't hold me to it. I haven't had a clear timeline from the physio yet."

Kohli has already retired from Test cricket and T20 internationals, making the ODI format his only remaining international commitment. At 37, the hamstring injury is a reminder that every series he misses is one he may not get back.

## The ODI Series Schedule

India host Afghanistan in three ODIs at home:

- **First ODI**: June 14
- **Second ODI**: June 17
- **Third ODI**: June 20

The series serves as preparation for India's three-match ODI tour of England in July, where Kohli is expected to return.

## What Jaiswal Brings to the ODI Middle Order

Jaiswal is primarily an opener in Test cricket, but the selectors see him as adaptable enough to slot into India's ODI top order. His T20I career has been limited, and this ODI opportunity is his chance to prove that his technique — built on patience and accumulation in the longer formats — can translate to the 50-over game.

If he succeeds, India's batting bench gains depth for the 2027 ODI World Cup cycle. If he does not, Gaikwad will be waiting. But the BCCI has made its preference clear: for now, Jaiswal is the future, and Gaikwad is the fallback.

## India A Squad for Sri Lanka Tour

Dhruv Jurel (C, WK), Devdutt Padikkal (VC), Sai Sudharsan, Ruturaj Gaikwad, N Jagadeesan (WK), Aman Mokhade, Shaik Rasheed, Ayush Pandey, Harsh Dubey, Saransh Jain, Gurnoor Brar, Auqib Nabi, Yash Thakur, Anshul Kamboj, Zeeshan Ansari.

The India A multi-day matches in Sri Lanka are scheduled for June-July, overlapping partially with the Afghanistan ODI series. Gaikwad's presence there and not in the senior squad is not an accident. It is a signal."""

article2 = {
    "headline": "Jaiswal Gets Kohli's ODI Spot. Gaikwad, Who Won India Gold at the Last Asian Games, Goes to Sri Lanka With the A Team.",
    "subheadline": "The BCCI has named Yashasvi Jaiswal as Kohli's replacement for the three-match Afghanistan series starting June 14. Ruturaj Gaikwad has been picked for India A's Sri Lanka tour instead. The pecking order is clear.",
    "body": article2_body.strip(),
    "slug": "jaiswal-replaces-kohli-odi-squad-afghanistan-gaikwad-india-a-sri-lanka-nri",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "BCCI", "url": "https://www.bcci.tv"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "InsideSport", "url": "https://www.insidesport.in"}
    ],
    "image_person": "Yashasvi Jaiswal",
    "image_topics": ["Yashasvi Jaiswal cricket", "Yashasvi Jaiswal India batting"],
    "image_pexels": "cricket batsman India",
    "image_caption": "Yashasvi Jaiswal during an international cricket match for India"
}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi Sports Writer — June 6, 2026")
    print("=" * 60)
    
    articles = [article1, article2]
    success = 0
    
    for i, article in enumerate(articles, 1):
        print(f"\n{'─' * 50}")
        print(f"Article {i}: {article['headline'][:80]}...")
        print(f"{'─' * 50}")
        
        # Validate
        word_count = len(article['body'].split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ⚠ BELOW MINIMUM (400 words)")
        
        if publish_article(article):
            success += 1
        
        time.sleep(1)
    
    print(f"\n{'=' * 60}")
    print(f"Results: {success}/{len(articles)} articles published")
    print(f"{'=' * 60}")
