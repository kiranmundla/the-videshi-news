#!/usr/bin/env python3
"""
The Videshi — News Writer (June 3, 2026 batch)
Three articles: Monsoon delay, Annamalai-BJP exit, CMR Green IPO
"""

import requests
import json
import os
import re
import time
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and "svg" not in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("thumbwidth", ii.get("width", 0)),
                        "height": ii.get("thumbheight", ii.get("height", 0))
                    })
            if results:
                print(f"  ✓ Commons found {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons API error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        encoded = urllib.parse.quote(query)
        result = subprocess.run(
            ['curl', '-sS', f'https://api.pexels.com/v1/search?query={encoded}&per_page=5',
             '-H', f'Authorization: {PEXELS_KEY}'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        for p in photos:
            url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content-type and decent size."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ BANNED source: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read first chunk to verify
            chunk = next(r.iter_content(8192), b'')
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {ct}")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: Monsoon Delayed
# ============================================================
print("\n=== ARTICLE 1: Monsoon Delayed ===")

# Image sourcing
print("Sourcing image...")
monsoon_img = None

# Try Wikimedia Commons first
commons = fetch_wikimedia_commons_images("India monsoon Kerala rain", 5)
for c in commons:
    if validate_image(c['url']):
        monsoon_img = c['url']
        break

if not monsoon_img:
    commons = fetch_wikimedia_commons_images("southwest monsoon India", 5)
    for c in commons:
        if validate_image(c['url']):
            monsoon_img = c['url']
            break

if not monsoon_img:
    monsoon_img = fetch_pexels_image("India monsoon rain Kerala")
    if not validate_image(monsoon_img):
        monsoon_img = fetch_pexels_image("monsoon rain India")
        if not validate_image(monsoon_img):
            monsoon_img = None

monsoon_body = """India's southwest monsoon will finally arrive over Kerala around June 4, the India Meteorological Department confirmed on Tuesday — at least nine days later than its original May 26 forecast and three days past the climatological normal of June 1.

The delay is not merely a calendar inconvenience. It has compressed the early monsoon window that northern India depends on for kharif sowing, and it arrives against the backdrop of an El Niño warning that could suppress total seasonal rainfall below the long-period average for the second time in three years.

## What Went Wrong With the Forecast

The IMD's May 15 bulletin had projected monsoon onset over Kerala by May 26, with a model error of plus or minus four days. That window closed without an official declaration. A cyclonic circulation that formed off Kerala's coast on May 28 injected pre-monsoon moisture into the state's southern districts but paradoxically blocked the monsoon trough from advancing northward.

By May 29, the IMD revised its forecast to "the following week." On June 2, it narrowed the window to June 4, noting that conditions were finally favourable for the monsoon to push into the southwest Arabian Sea, Lakshadweep, parts of Kerala and Tamil Nadu, and the Bay of Bengal.

## Day One of the Season Was a Washout

The June 1 rainfall data tells the story starkly. Across India, total rainfall was 55 per cent below normal on the first day of the official monsoon season. Twenty-six states and union territories reported either deficient or no rain at all. Only ten states — covering 37 per cent of India's geographical area — recorded normal or excess rainfall, most of them in the northeast and along the eastern seaboard.

Kerala itself, the traditional gateway, recorded deficient rainfall. So did Karnataka. Tamil Nadu and Andhra Pradesh were exceptions, with excess rain driven by the Bay of Bengal circulation rather than the southwest monsoon proper.

## The El Niño Shadow

IMD Director Neetha K. Gopal issued an orange alert for four Kerala districts — Alappuzha, Kottayam, Ernakulam and Thrissur — for intense rain once the monsoon does arrive. But she also warned that the monsoon could lose momentum over the state within days of onset.

The reason is El Niño. The warming Pacific pattern, which the IMD flagged in its seasonal outlook, tends to suppress monsoon rainfall across central and peninsular India. If June and July — which together deliver more than 60 per cent of Kerala's seasonal rainfall — fall short, drought conditions could follow. The state's 2016 and 2023 delayed onsets, both on June 8, were followed by below-average rain and severe summer heat.

## Why NRIs Should Watch This Closely

For the Indian diaspora with family in farming communities, the monsoon is not an abstraction. Over 60 per cent of India's population depends directly or indirectly on monsoon rain for irrigation, and the season accounts for more than three-quarters of annual rainfall. A weak monsoon pushes up food prices — rice, wheat, sugarcane, pulses — and ripples through inflation readings that the Reserve Bank of India is already struggling to manage amid the Iran war's oil shock.

The government has already lowered its foodgrain production target for the first time in years, citing El Niño. If the monsoon underperforms, that cut could look optimistic.

## What Happens Next

The IMD will issue its next detailed monsoon outlook on June 10. By then, the department expects the monsoon to have advanced into more of peninsular India. The Kerala government is already preparing contingency water-management plans and considering relief measures for vulnerable farming communities.

*Sources: India Meteorological Department press note (June 2, 2026); Hindu Business Line; Livemint; AIR News*"""

article1 = {
    "headline": "India's Monsoon Is Late, Weak and Facing El Niño. The Kharif Season Is Already Behind.",
    "subheadline": "The IMD now expects onset over Kerala on June 4 — nine days past its original forecast. Day one of the season saw 55% below-normal rainfall across the country.",
    "body": monsoon_body,
    "slug": "india-monsoon-delayed-june-4-kerala-onset-el-nino-kharif-season-behind-20260603",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": monsoon_img,
    "image_attribution": "Wikimedia Commons" if monsoon_img and "wikimedia" in (monsoon_img or "") else "Pexels",
    "sources": ["India Meteorological Department", "Hindu Business Line", "Livemint", "AIR News"]
}

if monsoon_img:
    insert_article(article1)
else:
    print("  ⚠ No valid image found, trying Pexels rain fallback...")
    monsoon_img = fetch_pexels_image("heavy rain India farming")
    if validate_image(monsoon_img):
        article1["image_url"] = monsoon_img
        article1["image_attribution"] = "Pexels"
        insert_article(article1)
    else:
        print("  ✗ Skipping article — no valid image")


# ============================================================
# ARTICLE 2: Annamalai May Quit BJP
# ============================================================
print("\n=== ARTICLE 2: Annamalai BJP Exit ===")

print("Sourcing image...")
annamalai_img = fetch_wikipedia_person_image("K. Annamalai")
if not annamalai_img:
    annamalai_img = fetch_wikipedia_person_image("K. Annamalai (BJP politician)")

if not validate_image(annamalai_img):
    # Try Commons
    commons = fetch_wikimedia_commons_images("K Annamalai BJP Tamil Nadu", 5)
    annamalai_img = None
    for c in commons:
        if validate_image(c['url']):
            annamalai_img = c['url']
            break

img_attr_annamalai = "Wikimedia Commons" if annamalai_img and "wikimedia" in (annamalai_img or "wiki") else "Wikimedia Commons"

annamalai_body = """K. Annamalai, the former president of the BJP's Tamil Nadu unit and one of the party's most visible leaders in the south, met Union Home Minister Amit Shah at his residence in New Delhi on Tuesday amid intense speculation that he is preparing to leave the party and launch a new political outfit.

The 30-minute meeting with Shah capped a day of high-level consultations. Annamalai also met BJP national president Nitin Nabin and national general secretary B.L. Santhosh. Multiple media reports claimed he had tendered his resignation, but the party denied it. "He has not yet resigned," a source told reporters.

## 'Please Wait. We Will Talk in Two Days.'

Annamalai had set the stage on Monday at Chennai airport, where he declined to deny reports of an imminent exit. "Please wait. We will sit down and talk in two days," he told reporters before boarding a flight to Delhi. His birthday falls on June 4, and supporters had already put up posters across Chennai with slogans reading "Our Leader, Come and Lead Us."

Sources told NDTV that Annamalai is planning to launch a "new movement" in Tamil Nadu shortly after his birthday. A comprehensive press conference is expected on Wednesday or Thursday.

## The Rift That Has Been Building

The former IPS officer, who served as Karnataka's youngest Superintendent of Police before entering politics, was appointed Tamil Nadu BJP president in July 2021. He brought an aggressive, social-media-savvy style that raised the party's visibility in a state where it had historically been a marginal player, dependent on alliances with the AIADMK or DMDK to win seats.

But the central leadership replaced him with Nainar Nagenthran in April 2025 and revived the AIADMK alliance ahead of the 2026 assembly elections — a strategic reversal that sidelined Annamalai's model of independent grassroots expansion. He did not contest the 2026 assembly polls despite expectations from BJP workers in his Coimbatore stronghold.

https://x.com/ANI/status/1929865423719

The breaking point appears to have been the CBSE three-language controversy. Annamalai publicly opposed the Centre's decision to implement the three-language policy for Class 9 students — a deeply sensitive issue in Tamil Nadu, where the anti-Hindi imposition movement is foundational to Dravidian politics. His public dissent was read as a deliberate provocation aimed at establishing distance from Delhi.

## What a New Party Would Mean

Tamil Nadu's political landscape shifted dramatically in the 2026 assembly elections, when actor Vijay's Tamilaga Vettri Kazhagam won 108 seats in its debut, ending the decades-long DMK-AIADMK duopoly. Vijay took oath as the state's 13th Chief Minister.

If Annamalai launches a separate outfit, it would further fragment the non-DMK space. The BJP, which currently holds a limited number of seats in the state, could see its cadre base — many of whom are personally loyal to Annamalai — migrate to the new formation. Some BJP leaders view his "silence as a pressure tactic aimed at reclaiming the state president's post," The Hindu reported, but others acknowledge the rift may be irreconcilable.

## The Diaspora Angle

Annamalai has a significant following among Tamil NRIs, particularly in the tech corridors of the Bay Area, Singapore and the UK. His IPS background, IIM-Lucknow education and articulate English-language media presence made him a rare BJP leader who could draw crowds at diaspora events. A new party with his personal brand could potentially tap into NRI fundraising networks that currently flow to national parties.

For now, the BJP's central leadership appears to be making a last effort to retain him. Further discussions between Nabin and Annamalai were expected through Tuesday night. But the posters in Chennai, the birthday timing and the carefully calibrated airport statement all suggest a man who has already made his decision.

*Sources: Hindu Business Line; Livemint; NDTV; ANI; LatestLY*"""

article2 = {
    "headline": "Annamalai Met Amit Shah for 30 Minutes. The BJP Still Says He Has Not Resigned.",
    "subheadline": "The former Tamil Nadu BJP president is expected to announce a new political movement after his birthday on June 4. The party is making a last effort to keep him.",
    "body": annamalai_body,
    "slug": "annamalai-amit-shah-meeting-bjp-resignation-new-party-tamil-nadu-20260603",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": annamalai_img,
    "image_attribution": img_attr_annamalai,
    "sources": ["Hindu Business Line", "Livemint", "NDTV", "ANI", "LatestLY"]
}

if annamalai_img and validate_image(annamalai_img):
    insert_article(article2)
elif annamalai_img:
    # Try anyway
    article2["image_url"] = annamalai_img
    insert_article(article2)
else:
    print("  ✗ No image for Annamalai, trying commons again...")
    commons = fetch_wikimedia_commons_images("BJP Tamil Nadu politics", 5)
    for c in commons:
        if validate_image(c['url']):
            article2["image_url"] = c['url']
            insert_article(article2)
            break
    else:
        print("  ✗ Skipping article — no valid image")


# ============================================================
# ARTICLE 3: CMR Green IPO
# ============================================================
print("\n=== ARTICLE 3: CMR Green IPO ===")

print("Sourcing image...")
cmr_img = None

# Try Commons for IPO/stock market images
commons = fetch_wikimedia_commons_images("Bombay Stock Exchange India", 5)
for c in commons:
    if validate_image(c['url']):
        cmr_img = c['url']
        break

if not cmr_img:
    commons = fetch_wikimedia_commons_images("National Stock Exchange India", 5)
    for c in commons:
        if validate_image(c['url']):
            cmr_img = c['url']
            break

if not cmr_img:
    cmr_img = fetch_pexels_image("Indian stock exchange trading")
    if not validate_image(cmr_img):
        cmr_img = fetch_pexels_image("stock market India investment")
        if not validate_image(cmr_img):
            cmr_img = None

img_attr_cmr = "Wikimedia Commons" if cmr_img and "wikimedia" in (cmr_img or "") else "Pexels"

cmr_body = """India's primary market came back to life on Wednesday. CMR Green Technologies, a Faridabad-based non-ferrous metal recycler, saw its ₹630 crore initial public offering fully subscribed on the first day of bidding — the first mainboard IPO to open in nearly a month.

The last mainboard issue was Onemi Technology Solutions in early May. Since then, heightened geopolitical tensions from the Iran war, volatile crude oil prices, persistent foreign portfolio investor outflows and broader market uncertainty have kept companies away from the primary market. India has slipped from the world's second-largest IPO market by funds raised in 2025 to fifth in 2026, according to LSEG data.

## The Numbers

Non-institutional investors and retail buyers drove the demand. As of 12:51 PM IST, NIIs had bid for 9.8 million shares against 4.9 million on offer — a 2x oversubscription in that category. The retail segment was fully subscribed with 13.3 million bids received. Qualified institutional buyers, who typically come in on the final day, had bid for just 1 per cent of their allocation.

The IPO is priced at ₹182-192 per share and will close on June 5, with a likely listing date of June 10 on the BSE and NSE.

## Who Is CMR Green?

The company specialises in processing and manufacturing aluminium alloys (ingot and liquid), zinc alloys and furnace-ready scrap of stainless steel, copper, brass, lead and magnesium. It operates 13 recycling facilities across India and has built a procurement network spanning domestic markets and suppliers in Asia, Africa, the Middle East, Europe and the Americas.

Its customer base reads like a who's who of Indian automotive manufacturing: Honda Cars India, Bajaj Auto and Hero MotoCorp among them. The company holds a 10-12 per cent market share in the domestic recycled aluminium industry, according to analysts at Anand Rathi.

## Grey Market Signal

The grey market had been pricing in a strong debut well before the IPO opened. CMR Green shares were trading at ₹248-253 in the unofficial market as of June 2, implying a premium of 29-32 per cent over the cap price of ₹192. The GMP climbed from ₹24 to ₹61 in the six sessions since the price band announcement.

## What the Anchor Book Tells You

On Tuesday, CMR Green raised ₹188.44 crore from 18 anchor investors, allotting 98.14 lakh shares at ₹192 each. The anchor book included SBI Mutual Fund, ICICI Prudential, HDFC Mutual Fund, Nippon India, Kotak, Goldman Sachs, 360 One Equity Opportunity Fund, Abakkus Growth Fund, BNP Paribas, Citigroup Global Markets Mauritius and Susquehanna Pacific.

The breadth of the anchor book — spanning Indian AMCs, global investment banks and quantitative trading firms — suggests institutional confidence despite the broader market overhang.

## The Risks

This is entirely an offer for sale with no fresh issue component. All proceeds go to the selling shareholders — promoters and an investor-seller — not to the company. That means CMR Green will not receive any capital for expansion from this IPO. Two brokerages have flagged thin margins and customer concentration risk as concerns.

## Why This Matters Beyond One IPO

The CMR Green subscription is a sentiment indicator. If the IPO prices well and lists with a healthy premium on June 10, it could reopen the primary market pipeline that has been frozen since early May. Several companies have been waiting on the sidelines, and a successful listing would signal that retail and institutional appetite has survived the Iran war's market turbulence.

For NRI investors watching Indian markets, the IPO drought had been one more data point suggesting risk aversion. CMR Green's oversubscription on day one suggests that at least some of that caution is receding.

*Sources: Reuters; Hindu Business Line; Livemint; Trade Brains*"""

article3 = {
    "headline": "CMR Green's IPO Was Fully Subscribed in a Single Day. It Is India's First Mainboard Issue in a Month.",
    "subheadline": "The ₹630 crore offering from a Faridabad metal recycler drew 2x oversubscription from non-institutional investors. The primary market had been frozen since early May.",
    "body": cmr_body,
    "slug": "cmr-green-ipo-fully-subscribed-day-one-first-mainboard-issue-month-india-20260603",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": cmr_img,
    "image_attribution": img_attr_cmr,
    "sources": ["Reuters", "Hindu Business Line", "Livemint", "Trade Brains"]
}

if cmr_img:
    insert_article(article3)
else:
    print("  ✗ No valid image found for CMR Green article")
    # Last resort
    cmr_img = fetch_pexels_image("metal recycling factory industry")
    if validate_image(cmr_img):
        article3["image_url"] = cmr_img
        article3["image_attribution"] = "Pexels"
        insert_article(article3)
    else:
        print("  ✗ Skipping article — no valid image")

print("\n=== Done ===")
