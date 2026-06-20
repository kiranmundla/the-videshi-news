#!/usr/bin/env python3
"""
Videshi News Writer — June 20, 2026 (12:30 UTC run)
2 NEW articles:
  1. July 2026 Visa Bulletin — EB-2 & EB-5 India marked "Unavailable", EB-1 India retrogresses (immigration / diaspora)
  2. Germany scraps airport transit visa for Indians; Lufthansa eyes more India traffic (travel / diaspora-mobility)
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
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
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


# ─── Article 1: July 2026 Visa Bulletin — EB-2/EB-5 India "Unavailable" ──

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: July 2026 Visa Bulletin — EB-2/EB-5 India shut")
    print("="*60)

    slug = "july-2026-visa-bulletin-eb2-eb5-india-unavailable-eb1-retrogression-green-card-20260620"
    headline = "India's Two Biggest Green-Card Doors Just Slammed Shut Until October. The July Visa Bulletin Spells It Out."
    subheadline = "The State Department's July 2026 Visa Bulletin marks EB-2 and EB-5 (unreserved) for India as 'Unavailable' and retrogresses EB-1 India by two months \u2014 a fiscal-year freeze that strands tens of thousands of skilled Indian professionals just weeks before the annual reset."

    body = """For the highly skilled Indian professional who has spent years inching toward a U.S. green card, the July 2026 Visa Bulletin delivered a blunt verdict: the two employment categories most Indians rely on are now closed for the rest of the fiscal year. The State Department's monthly bulletin, released ahead of July, marks both the EB-2 and the EB-5 (unreserved) Final Action Dates for India with a single, unforgiving letter \u2014 "U," for unavailable. No more visas in those lanes will be issued to Indian applicants until the numbers reset on October 1.

The freeze is not a glitch or a policy reversal. It is the arithmetic of a system that caps how many green cards any one country can claim in a year, finally catching up with the sheer scale of Indian demand.

## What the Bulletin Actually Says

The mechanics matter, because they determine who can still move forward. U.S. Citizenship and Immigration Services confirmed that employment-based filings in July must use the Final Action Dates chart \u2014 the stricter of the two tables the bulletin publishes. On that chart, India's EB-2 (advanced-degree and exceptional-ability professionals) and EB-5 unreserved (immigrant investors) are both shown as "U." A "U" means numbers are simply not authorized for issuance.

The damage isn't limited to those two categories. EB-1 \u2014 the top-priority lane for multinational executives, outstanding researchers and those of extraordinary ability \u2014 actually moved backward for India, with the cutoff date retrogressing two months to October 15, 2022. EB-3, the category for skilled workers and professionals, offered the only crumb of relief, advancing roughly two weeks to a cutoff of January 1, 2014. To put that in perspective: an Indian EB-3 applicant who filed in early 2014 is only now reaching the front of the line.

The contrast with the rest of the world is stark. For most other countries, including Mexico and the Philippines, EB-1, EB-2 and EB-5 remain current \u2014 meaning applicants can be processed immediately. China sits in the middle, with cutoffs years back but still moving. India alone hit a wall.

## Why the Doors Closed

The State Department was explicit about the cause. High demand and heavy "number use" by applicants chargeable to India in the EB-1 and EB-2 categories made it necessary to retrogress the dates \u2014 and ultimately mark them unavailable \u2014 to hold issuance within the fiscal year 2026 annual limit. The same logic applies to the EB-5 unreserved category.

Two statutory ceilings drive this. Under the Immigration and Nationality Act, the annual EB-2 allocation is capped at 28.6 percent of the worldwide employment-based limit, and no single country may receive more than 7 percent of all employment-based and family-sponsored visas in a year. For a country that supplies a wildly disproportionate share of America's engineers, doctors and researchers, that 7 percent ceiling is the binding constraint. The bulletin had already signaled trouble: the EB-2 India limit was reported exhausted as early as May 22, and the EB-5 unreserved cap was hit by June 5.

## Why It Matters for the Diaspora

For the roughly five-million-strong Indian-American community \u2014 and the still larger cohort on temporary visas hoping to put down permanent roots \u2014 this is not abstract bookkeeping. Tens of thousands of software engineers, physicians, AI researchers and biotech specialists sit in the EB-2 backlog, many of them on H-1B status, holding their breath for a priority date that just stopped moving entirely.

The practical fallout is immediate. Adjustment-of-status and consular cases in EB-2 and EB-5 will sit pending until October. Applicants must keep their underlying H-1B or L-1 status valid and their paperwork current through the wait, with no green card to show for it. Immigration attorneys are already nudging clients toward alternative routes \u2014 EB-1A for those who can credibly claim extraordinary ability, or strategic refiling \u2014 though those lanes, too, are tightening for India.

The deeper anxiety is structural. The Indian green-card backlog already stretches decades on paper, and a fiscal-year freeze like this one is a vivid reminder of how brittle the timeline really is. A reset arrives on October 1, when fiscal year 2027 brings fresh numbers and the categories should reopen. But "reopen" is not the same as "advance," and for a diaspora that measures its American future in priority dates, the message from the July bulletin is sobering: for the lanes that matter most to India, the line has stopped moving, and the clock now runs to October."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "A U.S. green card; the July 2026 Visa Bulletin marks EB-2 and EB-5 for India as 'Unavailable'"
    img_attribution = "Wikimedia Commons"

    for q in ["United States Permanent Resident Card green card", "US green card permanent resident", "United States visa document", "USCIS immigration document"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "green card" in t or "permanent resident" in t:
                img_caption = "A U.S. Permanent Resident Card; India's EB-2 and EB-5 green-card lanes are frozen until October 1"
            elif "visa" in t:
                img_caption = "A U.S. visa; the State Department's July 2026 bulletin halts EB-2 and EB-5 issuance for Indian applicants"
            break

    if not img_url:
        px = fetch_pexels_image("passport visa immigration documents")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Passport and immigration documents"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "U.S. Department of State \u2014 July 2026 Visa Bulletin (Final Action Dates chart)",
            "Berry Appleman & Leiden (BAL) \u2014 July 2026 Visa Bulletin: Most employment-based categories advance, with exceptions for India\u2019s Final Action Dates (June 18, 2026)",
            "BAL \u2014 EB-2 visa limit met for India",
            "BAL \u2014 EB-5 unreserved visa limit met for India (as of June 5, 2026)",
            "IndiaWest \u2014 India Hits EB-2 Visa Cap; Processing Paused Until October"
        ]),
        "diaspora_angle": "The July 2026 Visa Bulletin marks EB-2 and EB-5 (unreserved) for India as 'Unavailable' and retrogresses EB-1 India \u2014 freezing the green-card lanes that tens of thousands of Indian engineers, doctors and researchers rely on until the fiscal-year reset on October 1, 2026.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Germany scraps airport transit visa for Indians ─────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Germany scraps airport transit visa for Indians")
    print("="*60)

    slug = "germany-scraps-airport-transit-visa-indians-frankfurt-munich-lufthansa-diaspora-20260620"
    headline = "Germany Just Made Layovers Easier for Indian Travellers. Lufthansa Thinks That Changes the Map to America."
    subheadline = "As of June 3, Indian passport holders no longer need a Schengen airport transit visa to change planes at Frankfurt or Munich \u2014 a quiet bureaucratic win that the Lufthansa Group now expects to redraw how the diaspora flies between India, the UK and the Americas."

    body = """For years, the cheapest path home to India often came with an irritating asterisk. Book a one-stop fare through Frankfurt or Munich, and an Indian passport holder could find themselves needing a separate Schengen airport transit visa \u2014 a Type A visa \u2014 just to sit in the international transit zone and catch a connecting flight, even though they never set foot on German soil. That asterisk is now gone.

Germany formally scrapped the airport transit visa requirement for Indian nationals effective June 3, 2026, after the change was published in the Federal Law Gazette (Bundesgesetzblatt) on June 2. Indian travellers can now transit through German airports en route to a third country without applying for the Type A visa, the extra paperwork, the fee and the waiting that came with it.

## A Promise From January, Now Delivered

The move was no surprise to those tracking India-Germany diplomacy. During Federal Chancellor Friedrich Merz's visit to India on January 12\u201313, 2026, Berlin announced its intent to lift the requirement, and Prime Minister Narendra Modi publicly thanked him for a step that would "facilitate and ease travel for Indian nationals" and strengthen people-to-people links. India's Ministry of External Affairs welcomed the operationalisation in June, with spokesperson Randhir Jaiswal noting it would enhance ties between the two countries.

It also follows a parallel move by France earlier in 2026, which removed its own airport transit visa requirement for Indians travelling exclusively by air. Together, the two decisions chip away at one of the more obscure but persistent frictions in long-haul Indian travel.

## The Fine Print Still Matters

The exemption is generous but not unconditional, and diaspora travellers should read the boundaries carefully. The waiver applies only to genuine airport transit \u2014 changing planes within the international zone for an onward international flight. It does not let a passenger leave the airport, enter Germany, or travel into the wider Schengen area; anyone wanting to do that still needs the appropriate entry visa.

Crucially, the relief evaporates in a few common scenarios. The exemption does not apply if a traveller transits through two or more airports inside the Schengen area, has to collect and re-check baggage, has to check in again for the onward leg, or is holding an open ticket. For the many NRIs who book separate tickets to save money, that baggage-and-recheck carve-out is the catch worth planning around.

## Why Lufthansa Is Paying Attention

The most telling reaction came from the airlines. The Lufthansa Group \u2014 which operates more than 70 weekly flights from India, including over 50 to Germany, feeding onward connections to more than 200 destinations through its Frankfurt and Munich hubs \u2014 expects the change to lift passenger flows from India.

Kevin Markette, the group's Senior Director for Regional Sales South Asia, told businessline that the policy removes "a long-standing friction point" and could push more travellers toward one-stop connections via Germany. He singled out the United Kingdom as a clear beneficiary, alongside long-haul markets in Central and South America such as Brazil. Lufthansa calls India its largest market in Asia-Pacific and its second-largest intercontinental market globally, behind only the United States \u2014 a reminder of how central the diaspora's flying habits are to European carriers' bottom lines.

## Why It Matters for the Diaspora

For the millions of Indians scattered across North America, the UK and beyond, this is a small change with outsized everyday value. Students flying to or from campuses, professionals shuttling between India and the West, families making the long annual pilgrimage home \u2014 all of them routinely route through European hubs, and Germany's Frankfurt and Munich are among the busiest gateways.

Removing the transit visa cuts cost, paperwork and processing delay from those journeys, and it widens the menu of viable one-stop itineraries. Combined with France's earlier move, it signals that two of Europe's biggest economies see easing Indian mobility as part of deepening economic and educational ties \u2014 not a favour, but a recognition that the diaspora is a market and a bridge worth competing for. The next time a fare through Frankfurt looks cheaper, NRIs no longer have to factor in a separate visa to make the connection work."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Frankfurt Airport, a key transit hub for Indian travellers, where transit visas are no longer required"
    img_attribution = "Wikimedia Commons"

    for q in ["Frankfurt Airport terminal", "Munich Airport terminal", "Frankfurt Airport aerial", "Lufthansa aircraft Frankfurt"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "munich" in t:
                img_caption = "Munich Airport; Indian passport holders no longer need a transit visa to change planes in Germany"
            elif "lufthansa" in t:
                img_caption = "A Lufthansa aircraft; the group expects higher India traffic after Germany scrapped the transit visa"
            else:
                img_caption = "Frankfurt Airport, a key transit hub for Indian travellers, where transit visas are no longer required"
            break

    if not img_url:
        px = fetch_pexels_image("airport terminal departures international travel")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An international airport terminal"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-mobility",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Embassy of the Federal Republic of Germany, New Delhi \u2014 press note on lifting the airport transit visa requirement (Federal Law Gazette, June 2, 2026; effective June 3, 2026)",
            "LiveMint \u2014 Big relief for Indian flyers: After France, Germany lifts airport transit visa requirement",
            "The Hindu BusinessLine \u2014 Lufthansa eyes higher India traffic after Germany scraps airport transit visa requirement (June 19, 2026)",
            "Business Travel News Europe \u2014 Germany eliminates airport transit visa for Indian travellers",
            "Ministry of External Affairs (India) \u2014 statement by spokesperson Randhir Jaiswal, June 2, 2026"
        ]),
        "diaspora_angle": "Germany scrapped the Schengen airport transit visa for Indian passport holders effective June 3, 2026 \u2014 sparing students, professionals and families changing planes at Frankfurt or Munich the cost and paperwork of a Type A visa, and prompting Lufthansa to expect higher India traffic on routes to the UK and the Americas.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
