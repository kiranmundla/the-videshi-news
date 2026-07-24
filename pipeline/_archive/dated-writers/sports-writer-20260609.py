#!/usr/bin/env python3
"""Sports writer for The Videshi — June 9, 2026 batch"""

import json
import os
import re
import requests
import subprocess
import time
from datetime import datetime, timezone

# Load Supabase credentials
env = {}
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            if line.startswith("export "):
                line = line[7:]
            key, val = line.split("=", 1)
            val = val.strip('"').strip("'")
            env[key] = val

SUPABASE_URL = env["SUPABASE_URL"]
SUPABASE_KEY = env["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_key = None
pexels_path = os.path.expanduser("~/.env.pexels")
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if "PEXELS_API_KEY" in line and "=" in line:
                pexels_key = line.split("=", 1)[1].strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    import urllib.parse
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/"):
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0),
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl (urllib gets 403)."""
    if not pexels_key:
        print("  ⚠ No Pexels API key available")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {pexels_key}",
             f"https://api.pexels.com/v1/search?query={query}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image_url(url):
    """Validate that URL returns a real image (HTTP 200, image/*, >5KB)."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            # Try GET for servers that don't support HEAD
            r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        elif "image" in content_type and content_length == 0:
            # Some servers don't report content-length; trust content-type
            print(f"  ✓ Image validated (no content-length): {content_type}")
            return True
        else:
            print(f"  ⚠ Image validation failed: type={content_type}, length={content_length}")
            return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Article inserted: {result[0].get('id', 'unknown')}")
            return result[0]
        print(f"  ✓ Article inserted (no ID in response)")
        return result
    else:
        print(f"  ✗ Insert failed: {r.status_code} — {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Rohit Sharma Cleared Fit for Afghanistan ODIs
# ============================================================
print("\n" + "=" * 60)
print("ARTICLE 1: Rohit Sharma Cleared for Afghanistan ODIs")
print("=" * 60)

# Image sourcing — Wikipedia for Rohit Sharma
print("\nSourcing image for Rohit Sharma...")
rohit_img = fetch_wikipedia_person_image("Rohit Sharma")
rohit_img_source = "Wikimedia Commons"

# Also check Wikimedia Commons
if not rohit_img:
    commons = fetch_wikimedia_commons_images("Rohit Sharma cricket captain", limit=3)
    if commons:
        rohit_img = commons[0]["url"]
        print(f"  ✓ Using Commons image: {rohit_img[:80]}...")

if rohit_img and not validate_image_url(rohit_img):
    rohit_img = None

# Fallback to Pexels only for generic cricket imagery (NOT for a named person)
if not rohit_img:
    print("  ⚠ No Wikipedia/Commons image found for Rohit Sharma, trying Pexels generic cricket...")
    rohit_img = fetch_pexels_image("cricket stadium india")
    rohit_img_source = "Pexels"
    if rohit_img and not validate_image_url(rohit_img):
        rohit_img = None

article1_body = """Rohit Sharma has been cleared to play. Four days before the first ODI against Afghanistan in Dharamsala, the BCCI's Centre of Excellence in Bengaluru has confirmed that both the former India captain and all-rounder Hardik Pandya have passed their fitness assessments and will join the squad.

The clearance ends weeks of uncertainty. Rohit had been nursing a hamstring injury sustained during IPL 2026, where he played only nine of Mumbai Indians' fourteen matches. Pandya, who dealt with a recurring back spasm, missed three games of his own before returning for MI's final league-stage fixtures.

## The Road Through the CoE

Rohit arrived at the Centre of Excellence on Sunday, June 8, for a three-day assessment that included batting sessions under lights and running between the wickets at full intensity. A fresh set of bowlers was called in specifically to test his readiness against pace and spin at match tempo.

"Hardik and Rohit are all set to play the ODI series against Afghanistan," a BCCI source confirmed on Tuesday. "Both have cleared their fitness test and will soon join the team."

Earlier, India's batting coach Sitanshu Kotak had remained cautiously optimistic after the team's record innings-and-300-run Test victory over Afghanistan in Mullanpur. "I have honestly not got the news whether they have been cleared or not," Kotak told reporters. "But I'm sure they will be there. Whatever I heard, they are fine."

## What Changes for India

Rohit's return reshapes the top of India's ODI batting order. With Virat Kohli ruled out of the entire Afghanistan series after tearing his hamstring in the IPL final, Yashasvi Jaiswal has been named as Kohli's replacement. But Rohit's presence at the top gives the lineup its most experienced opening option — a batter with over 10,000 ODI runs and 31 centuries in the format.

Pandya's availability is equally significant. India have lacked a genuine pace-bowling all-rounder in the ODI setup since his last 50-over appearance fifteen months ago. His ability to bowl ten overs and bat in the middle order restores the balance that coach Gautam Gambhir's side has been constructing ahead of the 2027 ODI World Cup.

The Afghanistan ODI series, starting Saturday in Dharamsala, is the first step in that World Cup preparation. India play three ODIs against Afghanistan (June 13, 15, and 17), followed by bilateral assignments against England, West Indies, and New Zealand through the rest of 2026.

## The Diaspora Angle

For NRI cricket fans across the US, UK, and Canada, the question had been simple: would India's two most recognisable limited-overs players be available for a summer packed with white-ball cricket? The answer is now yes.

Rohit, who turns 39 in April 2027, has stated publicly that the ODI World Cup is his target. Every match from here counts. His willingness to submit to the CoE process — rather than assume his place — signals the seriousness of that ambition.

India's ODI squad for the Afghanistan series: Shubman Gill (c), Rohit Sharma, Yashasvi Jaiswal, KL Rahul, Shreyas Iyer, Rishabh Pant (wk), Hardik Pandya, Washington Sundar, Kuldeep Yadav, Prasidh Krishna, Arshdeep Singh, Mohammed Siraj, Gurnoor Brar, Harsh Dubey, Sai Sudharsan.

*The first ODI begins Saturday, June 13, at the HPCA Stadium in Dharamsala. Broadcast details for NRI viewers: Zee Sports (India), Willow TV (US/Canada).*"""

article1 = {
    "headline": "Rohit Sharma Cleared Fit. He Will Play Against Afghanistan on Saturday.",
    "subheadline": "The former captain and Hardik Pandya both passed fitness assessments at the BCCI's Centre of Excellence in Bengaluru, ending weeks of uncertainty before the three-match ODI series starting June 13 in Dharamsala.",
    "body": article1_body,
    "slug": "rohit-sharma-fitness-cleared-afghanistan-odi-series-dharamsala-pandya-coe-nri",
    "category": "sports",
    "vertical": "sports",
    "image_url": rohit_img,
    "image_caption": "Rohit Sharma at the crease during an international ODI match",
    "image_attribution": rohit_img_source,
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "CricketAddictor", "url": "https://cricketaddictor.com"},
        {"name": "Sportskeeda", "url": "https://sportskeeda.com"},
        {"name": "InsideSport", "url": "https://insidesport.in"},
        {"name": "BCCI Official", "url": "https://bcci.tv"},
    ]),
    "published_at": datetime.now(timezone.utc).isoformat(),
}

if rohit_img:
    print(f"\nInserting Article 1...")
    result1 = insert_article(article1)
else:
    print("\n  ✗ No valid image found for Article 1 — skipping insert")
    result1 = None


# ============================================================
# ARTICLE 2: Prasidh Krishna Replaces Siraj for Ireland/England T20Is
# ============================================================
print("\n" + "=" * 60)
print("ARTICLE 2: Prasidh Krishna Replaces Siraj")
print("=" * 60)

# Image sourcing — Wikipedia for Prasidh Krishna
print("\nSourcing image for Prasidh Krishna...")
prasidh_img = fetch_wikipedia_person_image("Prasidh Krishna")
prasidh_img_source = "Wikimedia Commons"

if not prasidh_img:
    prasidh_img = fetch_wikipedia_person_image("Prasidh Krishna (cricketer)")
    
if not prasidh_img:
    commons = fetch_wikimedia_commons_images("Prasidh Krishna cricket India", limit=3)
    if commons:
        prasidh_img = commons[0]["url"]
        print(f"  ✓ Using Commons image: {prasidh_img[:80]}...")

if prasidh_img and not validate_image_url(prasidh_img):
    prasidh_img = None

# Also try Siraj since it's about the replacement
if not prasidh_img:
    print("  Trying Mohammed Siraj on Wikipedia...")
    prasidh_img = fetch_wikipedia_person_image("Mohammed Siraj")
    if prasidh_img and validate_image_url(prasidh_img):
        prasidh_img_source = "Wikimedia Commons"
    else:
        prasidh_img = None

# Final fallback — generic cricket bowling image from Pexels
if not prasidh_img:
    print("  Trying generic cricket bowling on Pexels...")
    prasidh_img = fetch_pexels_image("cricket fast bowler bowling")
    prasidh_img_source = "Pexels"
    if prasidh_img and not validate_image_url(prasidh_img):
        prasidh_img = None

article2_body = """Mohammed Siraj will not tour Ireland or England. The BCCI confirmed on Tuesday that the fast bowler has been withdrawn from both T20I squads as part of a workload management programme, with Prasidh Krishna named as his replacement for the seven-match assignment.

The decision was made after discussions between the BCCI's medical team and coach Gautam Gambhir's management staff. Siraj, who played all seventeen matches for Gujarat Titans during their run to the IPL 2026 final and then bowled thirteen overs in the one-off Test against Afghanistan in Mullanpur, has been advised to rest ahead of what the board described as "a long international season."

## Prasidh Steps In

Krishna's inclusion gives the tall Karnataka seamer a rare opportunity in the shortest format. His T20I record is modest — five caps, eight wickets, an economy rate of 11.00 — and his last appearance in the format came against Australia in Guwahati in November 2023, more than two and a half years ago.

But the 30-year-old's recent form in franchise cricket makes the selection logical. During IPL 2026, Krishna took sixteen wickets in twelve matches for Gujarat Titans. The season before that, he won the Purple Cap outright with twenty-five wickets from fifteen games at an economy of 8.27.

His red-ball credentials are equally strong. In the Mullanpur Test, Krishna picked up crucial wickets during India's record innings-and-300-run victory. He is already part of the ODI squad for the Afghanistan series starting Saturday in Dharamsala.

## The Bigger Picture

Siraj's withdrawal is the latest in a series of workload-driven squad decisions by the BCCI this summer. Jasprit Bumrah was rested for the Ireland and England T20Is but retained for the Asian Games. Siraj, conversely, was not named for the Asian Games squad but was originally picked for the bilateral tours — until Tuesday's reversal.

The arithmetic is straightforward. India play two T20Is in Belfast (June 26 and 28), five T20Is in England (July 1-11), and three ODIs in England (July 14-19), before hosting the West Indies and travelling to New Zealand. That is potentially fifteen or more white-ball matches in under two months. The board is choosing where to spend its fast bowlers' workloads.

## What It Means for Shreyas Iyer's Squad

The T20I squad, now led by newly appointed captain Shreyas Iyer with Tilak Varma as vice-captain, includes a compelling mix of experience and promise. Fifteen-year-old Vaibhav Sooryavanshi, fresh off an Orange Cap-winning IPL campaign with 776 runs, could become the youngest man to debut for India if he features in Belfast or England.

The pace attack now reads: Arshdeep Singh, Harshit Rana, Prasidh Krishna, and Prince Yadav. That is a young, fast, and varied unit — none of the four are over thirty — well-suited to the bounce and movement expected on Irish and English pitches.

**Updated India T20I squad for Ireland and England:** Shreyas Iyer (c), Tilak Varma (vc), Abhishek Sharma, Sanju Samson (wk), Ishan Kishan, Vaibhav Sooryavanshi, Shivam Dube, Nitish Kumar Reddy, Axar Patel, Washington Sundar, Varun Chakaravarthy, Ravi Bishnoi, Arshdeep Singh, Harshit Rana, Prasidh Krishna, Prince Yadav.

*India play two T20Is in Belfast on June 26 and 28, followed by five T20Is in England from July 1 to 11. NRI viewers can watch on Willow TV (US/Canada) and Sky Sports (UK).*"""

article2 = {
    "headline": "Siraj Is Rested. Prasidh Krishna Will Bowl in Ireland and England.",
    "subheadline": "The BCCI withdrew Mohammed Siraj from both T20I squads on workload management grounds. Prasidh Krishna, who last played a T20I in November 2023, has been drafted in for the seven-match tour under new captain Shreyas Iyer.",
    "body": article2_body,
    "slug": "siraj-rested-prasidh-krishna-replacement-ireland-england-t20i-shreyas-iyer-nri",
    "category": "sports",
    "vertical": "sports",
    "image_url": prasidh_img,
    "image_caption": "Prasidh Krishna bowling for India in international cricket",
    "image_attribution": prasidh_img_source,
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Sportskeeda", "url": "https://sportskeeda.com"},
        {"name": "Yardbarker", "url": "https://yardbarker.com"},
        {"name": "BCCI Official", "url": "https://bcci.tv"},
        {"name": "The Popular Story", "url": "https://thepopularstory.com"},
    ]),
    "published_at": datetime.now(timezone.utc).isoformat(),
}

if prasidh_img:
    print(f"\nInserting Article 2...")
    result2 = insert_article(article2)
else:
    print("\n  ✗ No valid image found for Article 2 — skipping insert")
    result2 = None

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Article 1 (Rohit Sharma): {'✓ Inserted' if result1 else '✗ Failed'}")
print(f"Article 2 (Siraj/Prasidh): {'✓ Inserted' if result2 else '✗ Failed'}")
print("Both articles set to status: review")
print("Done.")
