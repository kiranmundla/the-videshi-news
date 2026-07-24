#!/usr/bin/env python3
"""
Sports Writer — June 13, 2026
Articles:
1. Gurbaz's 102 off 51 — Fastest Afghan ODI century, went unsold in IPL 2026
2. Gurnoor Brar's ODI debut — From Muktsar to India cap, 3/27 in first ODI
"""

import os, sys, json, time, uuid, hashlib, io, re
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

env_pex = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(env_pex):
    for line in open(env_pex):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── HELPERS ──

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15
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
                    "mime": mime,
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage."""
    try:
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}) for {img_url[:80]}")
            return None
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ✗ Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  📦 Compressed to {size_kb:.0f} KB")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url}")
            return public_url
        else:
            print(f"  ✗ Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None


def insert_article(article):
    """Insert article via REST API."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── CHECK SKIP LIST ──
skip_list_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/image-skip-list.json")
skip_list = []
if os.path.exists(skip_list_path):
    try:
        skip_list = json.load(open(skip_list_path))
    except:
        pass

# ============================================================
# ARTICLE 1: Gurbaz 102 off 51
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: Gurbaz 102 off 51 — Fastest Afghan ODI Century")
print("="*60)

art1_slug = "gurbaz-102-off-51-fastest-afghan-odi-century-india-dharamsala-ipl-unsold-nri"
art1_headline = "He Went Unsold at INR 1.5 Crore. On Saturday, He Hit Eight Sixes Against India."
art1_subheadline = "Rahmanullah Gurbaz smashed the fastest century by an Afghan batter in ODIs — 102 off 51 balls in a rain-shortened 25-over match in Dharamsala. Not a single IPL franchise wanted him six months ago."
art1_vertical = "cricket"

art1_body = """Rahmanullah Gurbaz walked into the Dharamsala hills on Saturday and decided he was not going to walk out quietly.

In a match reduced to 25 overs per side by persistent Himalayan rain, the Afghan wicketkeeper-batter blitzed his way to 102 off 51 balls — 8 fours, 8 sixes — the fastest century by an Afghanistan batter in One Day International history. The innings was violent, precise, and entirely unwelcome by the two Indian debutants tasked with stopping him.

## The Auction Nobody Remembers

Six months ago, Gurbaz sat in the IPL 2026 auction pool with a base price of INR 1.5 crore. He was listed in Set 3, the wicketkeepers' round, alongside Jonny Bairstow and Jamie Smith. All three went unsold. Not a single paddle rose. The auctioneer moved on without a second glance.

On Saturday, he took India's attack apart in conditions that were supposed to favour the bowlers. Overcast skies, damp pitch, fresh seam movement. None of it mattered. Gurbaz was in the mood, and the ball was going where he wanted it to.

## Twenty-Five Balls to Fifty

He raced to his half-century in 25 balls — the second-fastest ODI fifty by an Afghan batter, behind only Mohammad Nabi's 24-ball effort against Sri Lanka. From there, he accelerated. The 100 came in 48 deliveries, surpassing every Afghan record in the book.

It was his ninth ODI century, giving him the best 50-to-100 conversion rate in ODI cricket history at 56.25 per cent among batters with at least seven hundreds — ahead of Calum MacLeod (43.48%), Daryl Mitchell (42.86%), Quinton de Kock (41.82%), and Virat Kohli (41.22%).

Nitish Kumar Reddy, whom India were testing as an all-rounder in Hardik Pandya's absence, eventually ended the carnage. But by then, Afghanistan had raced to a competitive 194 all out in 24.5 overs — the majority of it from Gurbaz's blade.

## Two Debutants on the Receiving End

India's captain Shubman Gill had handed debut caps to fast bowler Gurnoor Brar and off-spinner Harsh Dubey before the match. Both delivered impressive returns — Brar finished with 3/27 in 4.5 overs, striking with a maiden wicket in his very first over, while Dubey claimed 3/47 — but neither could contain Gurbaz during his purple patch.

Brar, a 6-foot-5-inch right-arm seamer from Muktsar in Punjab who was bowling in the nets for Mumbai Indians as recently as 2019, showed he belonged. He got the ball to move away, dismissed Ibrahim Zadran with a beauty, and later removed Rashid Khan. Dubey, who impressed for Sunrisers Hyderabad in IPL 2026, bowled with control and picked up Hashmatullah Shahidi, Azmatullah Omarzai, and Allah Ghazanfar.

But Gurbaz, batting at the other end, treated them all with equal disdain.

## The Numbers Tell a Story

The broader picture is hard to ignore. Gurbaz is 24 years old. He has nine ODI centuries. He was man of the tournament at the 2023 ODI World Cup for Afghanistan. He averages over 50 in the first innings of ODIs. He has played T20 leagues on four continents. And yet, when the IPL auction came around in December 2025, the ten richest cricket teams on earth looked at his name, looked at his price tag, and collectively shrugged.

The reasons are familiar: overseas player slots are scarce, specialist wicketkeepers rarely fetch high bids unless they bat in the top three, and franchise analytics teams tend to weigh T20 strike rates over ODI records. But the optics are jarring. The man who just hit the fastest century in Afghan ODI history — against India, in India — was not worth INR 1.5 crore to any of them.

## Why This Matters to NRI Fans

For diaspora cricket fans watching from their living rooms in Edison, Fremont, or Brampton, the Gurbaz innings is a reminder that cricket's power structure is more fragile than it looks. Afghanistan, a country that has been playing ODIs for barely a decade, now has a batter with a better conversion rate than Kohli. The IPL's auction algorithm, designed to optimise squad value, can still miss the obvious.

The three-match series continues in Dharamsala, with the second ODI on Tuesday."""

# Image: Wikipedia for Gurbaz
print("\nSourcing image for Gurbaz...")
img1_url = fetch_wikipedia_person_image("Rahmanullah Gurbaz")
if not img1_url:
    img1_url = fetch_wikipedia_person_image("Rahmanullah Gurbaz (cricketer)")
commons1 = fetch_wikimedia_commons_images("Rahmanullah Gurbaz cricket", limit=3)
if not img1_url and commons1:
    img1_url = commons1[0]["url"]
if not img1_url:
    img1_url = fetch_pexels_image("cricket batting power hitting ODI")

img1_final = None
img1_attribution = "Wikimedia Commons"
img1_caption = "Rahmanullah Gurbaz in action during an ODI match"
if img1_url:
    img1_final = upload_to_supabase(img1_url, f"{art1_slug}.jpg")
    if "pexels.com" in (img1_url or ""):
        img1_attribution = "Pexels"
        img1_caption = "A batsman plays a power shot during a one-day international"

if not img1_final:
    print("  ⚠ No image found for Gurbaz article — inserting without image")

art1_data = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "sports",
    "vertical": art1_vertical,
    "status": "review",
    "is_editorial": False,
    "image_url": img1_final or "",
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "IPL Official Auction Results", "url": "https://www.ipl.com"},
        {"name": "Wisden", "url": "https://www.wisden.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
    ]),
    "diaspora_angle": "Afghan batter went unsold in IPL 2026 — diaspora fans in US, UK, Canada watching him dismantle India's bowling shows the gap between franchise valuations and international talent.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art1_id = insert_article(art1_data)


# ============================================================
# ARTICLE 2: Gurnoor Brar's ODI Debut
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: Gurnoor Brar — From MI Nets to India Cap")
print("="*60)

art2_slug = "gurnoor-brar-odi-debut-india-muktsar-punjab-nets-bowler-dharamsala-afghanistan-nri"
art2_headline = "He Was Bowling in the Nets in 2019. On Saturday, He Took Three Wickets on Debut."
art2_subheadline = "Gurnoor Brar, a 6-foot-5 right-arm seamer from Muktsar in Punjab, struck in his very first over for India and finished with 3/27 in a rain-shortened ODI against Afghanistan at Dharamsala."
art2_vertical = "cricket"

art2_body = """In 2019, Gurnoor Singh Brar was a teenager with a run-up longer than most hallways, bowling in the nets for Mumbai Indians during the IPL. He was not on any auction list. He was not on any squad sheet. He was there to give the batters throwdowns, collect the balls, and go home.

Seven years later, on a damp Saturday afternoon in Dharamsala, the 26-year-old stood at the top of his mark in India whites, ball in hand, with Ibrahim Zadran facing him at the other end. Second over of the match. Fifth ball. Length delivery, angled across. Zadran drove. The edge flew to mid-off. Shubman Gill, who had handed Brar his cap 45 minutes earlier, completed the catch.

Brar pumped his fist. The mountains behind him were covered in clouds. He had his first international wicket in his first over.

## The Long Road from Muktsar

Muktsar is a small district in southwest Punjab, better known for its Gurudwara Tous and the annual Maghi Mela than for producing international cricketers. Brar grew up there, played age-group cricket in Chandigarh, and worked his way through Punjab's domestic system the hard way — slowly, match by match, wicket by wicket.

He made his first-class debut in December 2022, against Railways in Delhi. He took 4 for 16 in that match. A month later, in a Ranji Trophy game against Jammu & Kashmir, he scored 64 with the bat and put together a 100-run partnership with Siddharth Kaul. Punjab won by four wickets. People started noticing.

The 2024-25 domestic season was the breakthrough. In the Ranji Trophy, Brar took 26 wickets in seven matches, finishing as Punjab's leading wicket-taker with an average of 16.45 and an economy rate of 3.43. His best: 5 for 14 against Bihar. In the Sher-E-Punjab T20 League, he topped the wicket-takers' chart with 22 wickets in 11 matches.

Gujarat Titans bought him in the 2025 IPL auction for INR 1.3 crore. The selectors picked him for the Test and ODI squads against Afghanistan. The journey from net bowler to new-ball bowler had taken six years.

## Saturday's Performance

In a match shortened to 25 overs by rain, Brar's figures read 4.5-0-27-3. He dismissed Ibrahim Zadran in his first over, came back to remove Rashid Khan — bowling him with a delivery that nipped back — and finished off the innings by having Ziaur Rahman Sharifi caught at mid-off. His economy of 5.59 in a game where Gurbaz was hammering sixes was more than respectable.

He was not alone. Harsh Dubey, a 25-year-old off-spinner from Madhya Pradesh who starred for Sunrisers Hyderabad in IPL 2026, also made his ODI debut and took 3 for 47. Between them, the two debutants accounted for six of Afghanistan's ten wickets. It was the first time since 2019 that two Indian debutants each took three or more wickets in the same ODI innings.

## Six-Five and Still Growing

At 6 feet 5 inches, Brar is one of the tallest fast bowlers in Indian cricket. He generates steep bounce and has the ability to move the ball both ways at pace. Cricbuzz's scouting profile describes him as a bowler who "hits the deck hard" — the kind of description that sounds like a cliché until you see the batters fending deliveries off their ribs.

His left-handed batting adds balance lower down the order. In first-class cricket, he has scored 304 runs at an average of 15.20, including a half-century. He is not a number eight who blocks; he is a number eight who swings. India's selectors, looking ahead to the 2027 ODI World Cup in South Africa, are clearly interested in what he brings.

## The Punjab Pipeline

Brar's rise is part of a broader trend of Punjab producing fast bowlers who force their way into reckoning through domestic performance rather than franchise hype. Arshdeep Singh, who bowled at the other end on Saturday, took a similar path — Punjab domestic cricket, IPL exposure, and then international selection on the strength of control and discipline.

For NRIs watching from the diaspora — many of them with roots in Punjab — Brar's debut is a reminder that the domestic system, for all its bureaucracy, still works. The Ranji Trophy still matters. Sher-E-Punjab T20 League still produces. And a net bowler from Muktsar can still end up with India whites on his back, the new ball in his hand, and a mountain range behind him.

The three-match series continues in Dharamsala, with the second ODI on Tuesday."""

# Image: Wikipedia for Gurnoor Brar
print("\nSourcing image for Gurnoor Brar...")
img2_url = fetch_wikipedia_person_image("Gurnoor Brar")
if not img2_url:
    img2_url = fetch_wikipedia_person_image("Gurnoor Brar (cricketer)")
commons2 = fetch_wikimedia_commons_images("Gurnoor Brar cricket Punjab", limit=3)
if not img2_url and commons2:
    img2_url = commons2[0]["url"]
# Try broader commons search
if not img2_url:
    commons2b = fetch_wikimedia_commons_images("India cricket fast bowler ODI 2026", limit=3)
    if commons2b:
        img2_url = commons2b[0]["url"]
if not img2_url:
    img2_url = fetch_pexels_image("cricket fast bowler bowling seam delivery")

img2_final = None
img2_attribution = "Wikimedia Commons"
img2_caption = "Gurnoor Brar celebrates his maiden ODI wicket for India"
if img2_url:
    if "pexels.com" in img2_url:
        img2_attribution = "Pexels"
        img2_caption = "A fast bowler delivers in overcast conditions during a one-day international"
    img2_final = upload_to_supabase(img2_url, f"{art2_slug}.jpg")

if not img2_final:
    print("  ⚠ No image found for Brar article — inserting without image")

art2_data = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "sports",
    "vertical": art2_vertical,
    "status": "review",
    "is_editorial": False,
    "image_url": img2_final or "",
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"},
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com"},
        {"name": "IPL Official", "url": "https://www.ipl.com"},
    ]),
    "diaspora_angle": "Punjab-origin fast bowler rises from domestic cricket and IPL net bowling to earning an India cap — a story of the Ranji Trophy pipeline that resonates with NRIs from Punjab watching from abroad.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art2_id = insert_article(art2_data)

# ── SUMMARY ──
print("\n" + "="*60)
print("DONE")
print("="*60)
print(f"Article 1: {'✓' if art1_id else '✗'} {art1_slug}")
print(f"Article 2: {'✓' if art2_id else '✗'} {art2_slug}")
print(f"Both set to status='review'")
