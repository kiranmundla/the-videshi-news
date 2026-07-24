#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-06-01 batch"""

import json, os, sys, time, uuid, re
from datetime import datetime, timezone

import requests
import urllib.parse

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ────────────────────────────────────────────────
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
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                "-H", f"Authorization: {PEXELS_KEY}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                src = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                alt = (photo.get("alt") or "").lower()
                # Filter bad images
                bad_alts = ["satellite", "aerial", "map", "flag", "icon", "logo"]
                if any(b in alt for b in bad_alts):
                    continue
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return img_url  # fallback to original URL if allowed
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return img_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return img_url

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {ur.status_code} {ur.text[:200]}")
            # For Wikipedia/Pexels, the original URL is permanent
            if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                return img_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
            return img_url
        return None


def sb_insert(table, payload):
    """Insert a row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, json=payload, headers=HEADERS, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────
articles = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: Zee Entertainment FIFA World Cup 2026 Broadcast Deal
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "Zee Has the World Cup. Ten Days Before Kickoff, India Finally Has a Broadcaster.",
    "subheadline": "Zee Entertainment secures FIFA World Cup 2026 rights for India and launches Unite8 Sports — four new channels covering football, cricket, kabaddi, and more through 2034.",
    "slug": "zee-entertainment-fifa-world-cup-2026-broadcast-rights-india-unite8-sports-nri",
    "category": "sports",
    "body": """The FIFA World Cup 2026 will be televised in India after all.

Zee Entertainment Enterprises confirmed on Monday that it has secured the rights to broadcast the 2026 FIFA World Cup and 38 other FIFA events in India through 2034, ending a months-long standoff over one of the last unsold major broadcast markets in the world.

The deal was announced just ten days before the tournament kicks off on June 11 across the United States, Canada, and Mexico — three countries that are home to an estimated five million Indian-origin residents.

## A Deal That Almost Didn't Happen

Financial terms were not disclosed, but the negotiations were anything but smooth. FIFA had initially sought approximately $100 million for the India package covering both the 2026 and 2030 World Cups. When no taker emerged at that price, the asking price was slashed to around $60 million, according to Reuters.

India's dominant sports broadcaster JioStar — the Reliance-Disney joint venture that aired the 2022 World Cup through its predecessor Viacom18 — offered approximately $20 million for the rights but was rejected by FIFA. Sony, which held the broadcast rights for the 2014 and 2018 tournaments, held discussions but ultimately did not bid.

The result was an uncomfortable standoff: the world's most-watched sporting event was heading to stadiums across North America with no confirmed broadcaster in a country of 1.4 billion people.

## Unite8 Sports: Zee's New Sports Network

As part of the deal, Zee announced the launch of Unite8 Sports, a dedicated sports network comprising four channels: Unite8 Sports 1 and Unite8 Sports 1 HD in Hindi, and Unite8 Sports 2 and Unite8 Sports 2 HD in English.

The channels will carry a range of sports beyond football, including cricket, kabaddi, badminton, wrestling, boxing, and combat sports. The announcement signals Zee's formal return to the sports broadcasting business — a space it had largely ceded to JioStar.

Punit Goenka, CEO of Zee Entertainment, called the acquisition a reflection of football's growing appeal. "Football cuts across regions and demographics, and the investments in garnering the media rights and launching dedicated sports channels reflect our clear belief in its long-term potential," he said.

## What NRIs Need to Know

For the Indian diaspora in the United States, Canada, and the United Kingdom, the deal has practical implications. Zee's streaming platform ZEE5 is available internationally, meaning fans who already subscribe — or who sign up ahead of the tournament — should be able to watch matches live.

This is particularly significant for NRIs in the US, where they live in the same time zone as most of the 48 group-stage matches. The expanded 48-team format means more games, more host cities, and — for the first time — a World Cup where walking to a stadium is a realistic option for millions of Indians living in North America.

The package also includes the 2027 FIFA Women's World Cup, the 2030 FIFA World Cup, and age-group tournaments through 2034. Zee will also air FIFA docu-series content covering grassroots communities and cultural dimensions of participating nations.

## Zee's Stock Jumps

Markets responded swiftly. Zee Entertainment shares rose approximately 7% following the announcement, reflecting investor confidence in the sports pivot.

The deal positions Zee as a credible challenger to JioStar in the Indian sports broadcasting landscape, even if cricket — which JioStar controls through its IPL and ICC rights — remains the dominant sport by viewership.

## The Bigger Picture

The 2026 FIFA World Cup will be the largest edition in history, featuring 48 teams across 16 host cities in the United States, Canada, and Mexico. For the Indian football fan, the wait is over. For the Indian diaspora living where the tournament is actually happening, it was never really about television. It was about whether anyone back home would be watching too.

Now they will be.

*Sources: Reuters, Mint, BestMediaInfo, The Hindu Business Line*""",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Mint", "url": "https://www.livemint.com/"},
        {"name": "BestMediaInfo", "url": "https://www.bestmediainfo.com/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "image_search": "FIFA World Cup football stadium",
    "image_fallback": "football soccer world cup",
    "image_person": None,
    "image_attribution": "Pexels",
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: Women's T20 World Cup 2026 Preview
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "India vs Pakistan on June 14. The Women's T20 World Cup in England Starts in Eleven Days.",
    "subheadline": "Harmanpreet Kaur leads a 15-player squad that includes debutant pacer Nandni Sharma and returning veterans Yastika Bhatia and Radha Yadav. India open against Pakistan at Edgbaston.",
    "slug": "women-t20-world-cup-2026-india-squad-harmanpreet-nandni-sharma-england-preview-nri",
    "category": "sports",
    "body": """The countdown to the Women's T20 World Cup has entered its final stretch. The tournament begins on June 12 in England and Wales, runs through July 5, and India's campaign opens against Pakistan at Edgbaston on June 14.

For the Indian diaspora in the United Kingdom — where hundreds of thousands of cricket-loving families have settled across Birmingham, London, Leeds, and Manchester — this is as close to a home World Cup as it gets without actually hosting one.

## India's Squad

The BCCI announced India's 15-player squad on May 2. Harmanpreet Kaur will captain the side for the fifth time in a T20 World Cup, making her one of the most experienced leaders in the tournament's history.

**India's T20 World Cup squad:** Harmanpreet Kaur (c), Smriti Mandhana (vc), Shafali Verma, Jemimah Rodrigues, Deepti Sharma, Richa Ghosh (wk), Arundhati Reddy, Renuka Thakur, Kranti Gaud, Shree Charani, Shreyanka Patil, Bharti Fulmali, Yastika Bhatia, Nandni Sharma, Radha Yadav.

The standout inclusion is Nandni Sharma, the 24-year-old pacer from Chandigarh who earned her maiden national call-up after a breakout Women's Premier League season with Delhi Capitals. She took 17 wickets in 10 WPL matches — joint-highest in the edition — including a hat-trick and a five-wicket haul in just her second appearance.

Sharma carried that momentum into international cricket, returning figures of 3/34 on her T20I debut against England at Chelmsford. The ICC has named her among five young stars to watch at the tournament.

## India's Form Heading In

India's recent T20I record tells a complicated story. Since the 2024 T20 World Cup, the team has won 13 out of 21 matches, including series victories in England and Australia. But in 2026, the numbers have dipped: three wins in eight T20Is, including four losses in a five-match series against South Africa.

The bilateral series against England that concluded this week was a morale-boosting affair. Jemimah Rodrigues rescued the opening match, and India's bowling showed teeth across the series. But inconsistency with the bat remains a concern — and the absence of injured all-rounder Amanjot Kaur leaves a gap in the middle order.

## India's Group-Stage Schedule

India have been drawn in Group B alongside Pakistan, the Netherlands, Australia, South Africa, and Bangladesh. The fixtures:

- **June 14** — India vs Pakistan, Edgbaston, Birmingham
- **June 17** — India vs Netherlands, Headingley, Leeds
- **June 20** — India vs South Africa, Old Trafford, Manchester
- **June 25** — India vs Bangladesh, Old Trafford, Manchester
- **June 28** — India vs Australia, Lord's, London

The India-Pakistan opener at Edgbaston is the marquee fixture of the group stage. Birmingham has one of the largest South Asian populations in the UK, and the ground — which has hosted iconic men's World Cup matches — is expected to be packed.

The semi-finals are scheduled for June 30 and July 2 at The Oval, with the final at Lord's on July 5.

## What NRIs Should Know

For the Indian diaspora in the UK, this is a once-in-a-generation opportunity to watch India play at historic English grounds. Tickets for India matches are available through the ICC's official channels, though the India-Pakistan fixture is expected to sell out quickly.

Fans in the US and Canada can follow the action through the ICC's digital platforms and broadcast partners. The tournament coincides with the FIFA World Cup, which begins a day earlier on June 11, making mid-June a uniquely packed period for Indian sports fans worldwide.

## The Stakes

India are the reigning 50-over World Cup champions but have never won a Women's T20 World Cup. The closest they came was the 2020 final in Melbourne, where they fell to Australia. With Harmanpreet's experience, Mandhana's elegance, and Sharma's raw pace, this squad has the tools. Whether they have the consistency is the question that Edgbaston will begin to answer.

*Sources: Cricbuzz, ICC Cricket, CricTracker*""",
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com/"},
        {"name": "ICC Cricket", "url": "https://www.icc-cricket.com/"},
        {"name": "CricTracker", "url": "https://www.crictracker.com/"}
    ]),
    "image_search": "women cricket match action",
    "image_fallback": "cricket stadium England",
    "image_person": "Harmanpreet Kaur",
    "image_attribution": "Wikimedia Commons",
})

# ── Publish loop ─────────────────────────────────────────────────
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
published_count = 0

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i+1}: {art['headline'][:60]}...")
    print(f"{'='*60}")

    # Image sourcing
    img_url = None

    # Step 1: Try Wikipedia for person articles
    if art.get("image_person"):
        print(f"  Trying Wikipedia for {art['image_person']}...")
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url:
            art["image_attribution"] = "Wikimedia Commons"

    # Step 2: Fall back to Pexels with specific terms
    if not img_url:
        print(f"  Trying Pexels for '{art['image_search']}'...")
        img_url = fetch_pexels_image(art["image_search"], art.get("image_fallback"))
        if img_url:
            art["image_attribution"] = "Pexels"

    # Step 3: Upload to Supabase storage
    final_img_url = None
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_img_url = upload_image_to_supabase(img_url, filename)

    if not final_img_url:
        print("  ⚠ No image found — publishing without image")

    # Build payload
    art_id = str(uuid.uuid4())
    # Count words
    word_count = len(art["body"].split())

    payload = {
        "id": art_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["category"],
        "body": art["body"],
        "sources": art["sources"],
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_attribution": art.get("image_attribution", ""),
        "word_count": word_count,
    }
    if final_img_url:
        payload["image_url"] = final_img_url

    # Insert
    print(f"  Inserting article: {art['slug']}")
    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {art['headline'][:50]}... (id: {art_id[:8]})")
        published_count += 1
    else:
        print(f"  ✗ FAILED: {art['headline'][:50]}...")

    # Small delay between articles
    time.sleep(1)

print(f"\n{'='*60}")
print(f"DONE: {published_count}/{len(articles)} articles published")
print(f"{'='*60}")
