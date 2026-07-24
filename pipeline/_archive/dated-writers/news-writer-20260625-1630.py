#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (16:30 UTC / 09:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. OCI rules overhaul 2026 — e-OCI digital system, USD 275 fresh fee,
     mandatory 3-month passport-update window + USD 25 late penalty,
     PIO cards dead after Dec 31 2025, six-month-stay rule dropped for
     in-country applicants. Direct diaspora compliance story. NOT covered.
  2. Adani Airports to invest 200 billion rupees ($2.12B) building airport
     cities across 6 Indian airports (Mumbai, Navi Mumbai, Ahmedabad,
     Lucknow, Jaipur, Guwahati). Announced June 25. NOT covered.
"""
import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# \u2500\u2500\u2500 Article 1: OCI rules overhaul 2026 \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: OCI rules overhaul 2026")
    print("="*60)

    slug = "oci-card-new-rules-2026-e-oci-digital-fee-275-passport-update-three-month-deadline-pio-cards-expire-20260625"
    headline = "India Has Quietly Rewritten the Rulebook for Its 4.5 Million OCI Holders. Here's What Changed."
    subheadline = "A new digital e-OCI system, a USD 275 fee for fresh cards, a hard three-month deadline to update your record after a new passport, and the death of the old PIO card add up to the biggest shake-up of the scheme in years."

    body = """For millions of people of Indian origin living abroad, the Overseas Citizen of India card is the document that keeps the door home open: lifelong visa-free travel to India, the right to live and work there indefinitely, parity with resident Indians on most things short of voting and farmland. This year, New Delhi has overhauled how that card is issued, priced and maintained \u2014 and many of the roughly 4.5 million OCI holders worldwide are only now catching up with rules that are already in force.

The changes are not a single dramatic announcement but a cluster of revisions that together reshape the scheme. Taken individually each looks like routine housekeeping. Taken together, they tighten compliance, raise costs, and tie the OCI record far more closely to a holder's current passport than ever before.

## The Card Goes Digital

The headline shift is the move to e-OCI, a digital system folded into India's upgraded Immigration, Visa and Foreigners Registration and Tracking (IVFRT 2.0) platform \u2014 the same backbone that powers the automated e-gates now appearing at major Indian airports. From May 1, 2026, every fresh OCI application and every "miscellaneous service" \u2014 a passport update, a re-issue, a replacement for a lost card, a renunciation \u2014 runs through the new digital pipeline.

There is reassuring news for existing holders: if you already have a valid physical OCI card, you do not need to rush to switch. Existing cards remain valid for travel. The digital regime bites when you next interact with the system \u2014 a new passport, a lost card, a fresh application for a family member.

## The New Price of Belonging

The fee structure was revised on April 1, 2026, and the numbers are meaningfully higher. A fresh e-OCI registration now costs USD 275 from outside India (or \u20b915,000 within India), up sharply from the older fee. Re-issuance after the first new passport following age 20 is listed at USD 25, a lost-or-damaged-card replacement at USD 100, and conversion from the old PIO card to OCI at USD 100. On top of every fee paid abroad sits a USD 3 ICWF (Indian Community Welfare Fund) surcharge, and debit-card payments add a roughly 1% processing charge. For a family of four applying together, the bill adds up quickly.

## The Three-Month Trap

The change most likely to catch holders off guard is the passport-update deadline. OCI holders must now update their OCI profile within three months of receiving a new foreign passport. Miss that window and a USD 25 late-update penalty kicks in. The rule ties the OCI record to passport-data integrity and biometric matching at those airport e-gates \u2014 a mismatch between your card's data and your current passport can mean trouble at immigration.

This lands hardest on the people who renew passports most often and juggle several at once: frequent flyers, students studying abroad whose passports expire mid-degree, and mixed-passport families running different renewal cycles for each member. The old, more forgiving grace periods are gone.

## PIO Cards Are Now Dead

For an older generation of the diaspora, the Persons of Indian Origin (PIO) card was the predecessor to OCI. That chapter is now closed: PIO cards ceased to be valid after December 31, 2025. Anyone still holding one must convert to OCI to retain visa-free access \u2014 at the USD 100 conversion fee \u2014 and those who let it lapse face applying afresh.

There is one easing in the package. India has dropped the earlier six-month continuous-stay requirement for eligible foreign nationals applying for OCI from within the country, making the in-country route simpler for those already in India on a qualifying visa. People in India on tourist, e-visa, missionary or mountaineering visas, however, still cannot apply for OCI while in the country.

## Why It Matters for the Diaspora

The OCI card is, for most of the diaspora, the single most important piece of paper connecting them to India \u2014 the difference between flying in on a whim and queuing for a visa. The 2026 overhaul does not threaten that connection, but it does demand more attention and more money to keep it in good standing. The practical takeaways are concrete: budget for higher fees, and above all, calendar the three-month passport-update deadline the moment a new passport arrives.

For a community that prides itself on staying tethered to home across continents and generations, the message from New Delhi is subtle but firm. The privileges of the OCI remain generous \u2014 but the paperwork that underpins them has just become a great deal less forgiving."""

    img_url, ititle = pick_commons([
        "Indian passport",
        "Overseas Citizen of India",
        "India passport document",
        "Bureau of Immigration India"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "An Indian passport; India has overhauled the rules tying OCI cards to a holder's current passport"

    if not img_url:
        px = fetch_pexels_image("passport travel documents")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India's 2026 overhaul of the OCI scheme ties the card more tightly to a holder's passport"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "VisaVerge (visaverge.com, 2026) \u2014 'India OCI Rules 2026: New Fees and Passport Update Deadlines': India set a new USD 275 fee for fresh OCI applications, requires most cardholders to update passport details within three months of receiving a new foreign passport or face a USD 25 penalty, lists reissuance at USD 25 and lost-card replacement at USD 100, and dropped an earlier six-month continuous-stay requirement for eligible applicants filing inside India; tourist, e-visa, missionary and mountaineering visa holders cannot apply for OCI while in India.",
            "Wego Travel Blog (blog.wego.com, 2026) \u2014 'India Introduces e-OCI: A Guide to the New Digital OCI System': the e-OCI system is tied into India's IVFRT 2.0 platform that powers automated airport e-gates; the shift to digital affects new applications and miscellaneous services from May 1, 2026, while existing physical cards remain valid; the revised April 1, 2026 fee structure sets a fresh OCI fee of USD 275 (\u20b915,000 within India), a USD 100 lost/damaged replacement, a USD 100 PIO-to-OCI conversion, plus a USD 3 ICWF surcharge and a ~1% debit-card processing charge on fees paid abroad.",
            "India Abroad / immigration advisories (2026) \u2014 coverage of the 2026 OCI changes: PIO cards ceased to be valid after December 31, 2025; OCI holders must complete passport updates within three months; physical card reissue is generally needed only once after age 20.",
            "Ministry of Home Affairs / Bureau of Immigration, India (mha.gov.in / boi.gov.in, 2026) \u2014 official framework for OCI registration, fees and the digital e-OCI / IVFRT 2.0 platform governing applications and miscellaneous services for Overseas Citizens of India."
        ]),
        "diaspora_angle": "The OCI card is the document that keeps roughly 4.5 million people of Indian origin connected to India \u2014 visa-free entry and the right to live and work there \u2014 and the 2026 overhaul raises fees, kills the old PIO card, and imposes a hard three-month deadline (with a penalty) to update the record after every new passport, hitting frequent flyers, overseas students and mixed-passport families hardest.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Adani Airports airport cities \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Adani Airports $2.12B airport cities")
    print("="*60)

    slug = "adani-airports-2-billion-airport-cities-six-airports-mumbai-navi-mumbai-ahmedabad-lucknow-jaipur-guwahati-20260625"
    headline = "Adani Is Betting $2 Billion That the Next City Grows Around the Airport, Not the Other Way Around"
    subheadline = "The group's airports arm will build 'airport cities' \u2014 hotels, offices, retail and entertainment \u2014 across more than 655 acres at six Indian airports, modelled on Singapore, Dubai and Amsterdam."

    body = """Adani Airports Holdings said on Thursday it will invest more than 200 billion rupees ($2.12 billion) to build airport-linked commercial districts \u2014 so-called airport cities \u2014 across six locations in India, a bet that the country's fastest-growing pieces of urban real estate will be the land that wraps around its runways.

The developments will span more than 655 acres at airports in Mumbai, Navi Mumbai, Ahmedabad, Lucknow, Jaipur and Guwahati. Nearly 70% of the planned investment is concentrated in Mumbai and Navi Mumbai, reflecting the region's position as India's leading commercial and financial hub and the home of the group's marquee new airport. Adani Airports, an Adani Group company, currently manages eight airports across the country.

## What an "Airport City" Actually Is

The concept, known in the industry as an "aerotropolis," inverts the usual relationship between a city and its airport. Instead of an airport sitting at the edge of a city it serves, a dense commercial district \u2014 hotels, retail centres, office space, logistics parks and entertainment venues \u2014 is built around and integrated with the airport itself, turning the terminal into the anchor of a self-contained economic zone. Adani said its developments were inspired by the airport-city models of Singapore (Changi's Jewel), Dubai, Amsterdam (Schiphol) and Seoul (Incheon), each of which has turned a transit hub into a destination in its own right.

The company has already signed agreements with IHG Hotels & Resorts for five hotels across the project, and said it is in talks with partners across the food-and-beverage and entertainment segments. The pitch to travellers and locals alike is familiar to anyone who has wandered Changi's indoor waterfall or shopped at Dubai's terminals: the airport as a place you might visit even when you are not flying.

## A Piece of a Much Bigger Push

The airport-cities plan is one slice of the Adani Group's enormous infrastructure spending. The same week, the conglomerate's broader ambitions have been on display across aviation, ports, energy and data centres. The bet rests on a simple demographic and economic wager: Indian air travel is expanding rapidly, the country is building and upgrading airports at a furious pace, and the commercial real estate around those hubs \u2014 long an afterthought in Indian aviation \u2014 represents a largely untapped revenue stream that can dwarf the income from aeronautical charges alone.

For Adani, airport cities also diversify the revenue mix of its airports business away from the volatile economics of running terminals and toward steadier, higher-margin streams: long leases on office and retail space, hotel partnerships, and the rising land values that come with concentrated development.

## The Mumbai Anchor

The heavy tilt toward Mumbai and Navi Mumbai is no accident. The new Navi Mumbai International Airport, one of India's most closely watched infrastructure projects, gives Adani a rare opportunity to design an airport city on relatively open land from the outset, rather than retrofitting around an existing, hemmed-in terminal. That greenfield canvas is precisely what makes the Singapore and Dubai comparisons plausible rather than aspirational.

## Why It Matters for the Diaspora

For the millions of non-resident Indians who pass through Mumbai, Ahmedabad and the other listed airports on every trip home, the practical effect over the coming years will be tangible: more hotels for the red-eye arrival, more business-grade office and meeting space for the diaspora entrepreneur with a foot in both countries, and terminals that increasingly resemble the world-class hubs in Dubai and Singapore that NRIs already use as their connecting points.

There is a sharper financial dimension, too. The Adani Group is a fixture of NRI investment portfolios, both directly through its listed companies and indirectly through the Indian index funds that overseas Indians pour remittances and savings into. A multi-billion-dollar diversification into airport real estate \u2014 if it delivers \u2014 reshapes the earnings story of a group many in the diaspora already own a piece of. For an audience that experiences India most often through its airports, watching those airports transform into cities is a particularly literal way of seeing the country's infrastructure ambitions take shape."""

    img_url, ititle = pick_commons([
        "Chhatrapati Shivaji International Airport Mumbai terminal",
        "Mumbai airport terminal 2",
        "Adani airport India",
        "Ahmedabad airport"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "An airport terminal in India; Adani Airports plans 'airport cities' across six Indian airports"

    if not img_url:
        px = fetch_pexels_image("modern airport terminal interior")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Adani Airports will build commercial 'airport cities' across six Indian airports"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, June 25, 2026) \u2014 'India's Adani Airports to invest over $2 billion in developing airport cities': Adani Airports will invest more than 200 billion rupees ($2.12 billion) to develop airport-linked commercial districts across six locations \u2014 Mumbai, Navi Mumbai, Ahmedabad, Lucknow, Jaipur and Guwahati \u2014 spanning more than 655 acres; nearly 70% of the investment is concentrated in Mumbai and Navi Mumbai; Adani Airports manages eight airports; developments include hotels, retail, office space and entertainment, inspired by airport-city models in Singapore, Dubai, Amsterdam and Seoul; agreements signed with IHG Hotels & Resorts for five hotels, with talks ongoing across food-and-beverage and entertainment ($1 = 94.3950 rupees).",
            "Adani Airports Holdings / Adani Group statements (adani.com, June 2026) \u2014 company announcement of the airport-city ('aerotropolis') strategy integrating commercial real estate with its airport portfolio and the IHG hotel partnership.",
            "Industry context (2026) \u2014 the 'aerotropolis' / airport-city concept, exemplified by Singapore's Changi (Jewel), Dubai, Amsterdam's Schiphol and Seoul's Incheon, builds dense commercial districts around an airport, turning terminals into destinations and creating non-aeronautical revenue streams; India's rapid air-traffic growth and airport-building programme underpin the bet."
        ]),
        "diaspora_angle": "NRIs experience India most often through its airports, and Adani's $2 billion bet on 'airport cities' at Mumbai, Ahmedabad and four other hubs means more hotels, business space and world-class terminals for diaspora travellers \u2014 while reshaping the earnings of a group that is a fixture of NRI investment portfolios directly and through Indian index funds.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-25 16:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (OCI rules overhaul): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Adani airport cities): {'OK id=' + str(id2) if id2 else 'FAILED'}")
