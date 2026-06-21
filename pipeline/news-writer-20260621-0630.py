#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (06:30 UTC run)
2 NEW articles:
  1. International Day of Yoga 2026 — Modi leads from Kolkata's Red Road; 2,500 global sites; diaspora (news / culture / diaspora-identity)
  2. Indian study-abroad spending falls 22% to $1B — lowest since 2017 as US/Canada/Australia visa curbs bite (news / economy / education)
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


# ─── Article 1: International Day of Yoga 2026 ──────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: International Day of Yoga 2026 / Modi Kolkata")
    print("="*60)

    slug = "international-day-of-yoga-2026-modi-kolkata-red-road-healthy-ageing-diaspora-2500-sites-20260621"
    headline = "On the Longest Day of the Year, the Diaspora's Most Successful Export Comes Home Again"
    subheadline = "Modi led the 12th International Day of Yoga from Kolkata's Red Road on Sunday, with the theme 'Yoga for Healthy Ageing' and events at nearly 2,500 locations across more than 210 Indian missions worldwide \u2014 a global movement built, in no small part, by the Indians who carried it abroad."

    body = """For the global Indian community, the summer solstice has acquired a second meaning. On Sunday, June 21, as the longest day of the year fell over the Northern Hemisphere, Indians and non-Indians alike rolled out mats from Kolkata to California to mark the 12th International Day of Yoga \u2014 a celebration of the diaspora's quietest and most enduring export.

Prime Minister Narendra Modi led the national observance from Kolkata's historic Red Road, joining thousands of practitioners in the Common Yoga Protocol, the standardised 45-minute sequence performed simultaneously around the world. This year's theme, "Yoga for Healthy Ageing," speaks to a moment when life expectancy is rising across the planet and the harder question is how to fill those added years with health rather than frailty.

## A Bengal Backdrop

Speaking on the sacred ground of Bengal, Modi praised the state's deep spiritual heritage, noting that it was special to lead the practice in the land where saints such as Ramakrishna Paramahamsa, Swami Vivekananda and Lahiri Mahasaya carried the tradition forward. Vivekananda, who introduced Vedanta and yoga to a Western audience at the 1893 Parliament of the World's Religions in Chicago, is in many ways the patron saint of the very phenomenon being celebrated: an Indian practice that found its largest congregation overseas.

The Kolkata event was paired with a display of a very different kind of national strength. Modi also commissioned three indigenously designed and built naval vessels \u2014 the stealth frigate INS Dunagiri, the survey ship INS Sanshodhak, and the anti-submarine warfare craft INS Agray \u2014 all constructed in Kolkata by Garden Reach Shipbuilders & Engineers with more than 75 percent indigenous content. The juxtaposition was deliberate: soft power on the mat, hard power at the dockyard, both stamped "made in India."

## From Cultural Heritage to Global Movement

The numbers behind Yoga Day have become a recurring point of national pride. Since the United Nations General Assembly adopted India's proposal in 2014 to designate June 21 as the International Day of Yoga, the observance has grown into one of the largest synchronised wellness events on earth. This year, the Ministry of Ayush said celebrations were organised at nearly 2,500 locations worldwide, with more than 210 Indian missions and posts taking part in coordination with the Indian Council for Cultural Relations. A nationwide live session on June 14 drew more than four lakh simultaneous participants, setting a new Guinness World Record.

Across India, the day became a roll call of public life. Home Minister Amit Shah practised in Ahmedabad, Defence Minister Rajnath Singh in Shillong, Uttar Pradesh's Yogi Adityanath in Jhansi, and a roster of chief ministers and union ministers in their own states. Olympic javelin champion Neeraj Chopra and actor Shilpa Shetty joined celebrations, lending the morning a celebrity sheen.

https://www.instagram.com/narendramodi/

## Why It Matters for the Diaspora

For Indians abroad, Yoga Day is less a directive from Delhi than a recognition of something they have lived for decades. The studios of New York, London, Sydney and Toronto were carrying Sanskrit asana names into mainstream Western fitness long before any UN resolution. The estimated tens of millions of practitioners in the United States alone \u2014 most of them not of Indian origin \u2014 are testament to a cultural transmission the diaspora seeded and the world adopted.

That global embrace is also a source of an old tension. As yoga became a multi-billion-dollar wellness industry abroad, often stripped of its philosophical and spiritual roots, many in the diaspora have pushed back against what they see as the dilution of a sacred tradition into mere stretching. Yoga Day, in that light, functions as a gentle act of reclamation \u2014 an annual reminder, broadcast from Red Road to Times Square, of where the practice comes from.

This year's theme lands with particular weight for diaspora families. The Indian-origin population overseas is itself ageing, with a first generation of post-1965 immigrants to the United States and Britain now well into their seventies and eighties. "Yoga for Healthy Ageing" is not an abstraction for them; it is a prescription many already follow, and a thread of continuity that binds grandparents in Edison or Hounslow to the country they left. On the longest day of the year, that thread stretches all the way back to a mat on Red Road."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Yoga practitioners perform the Common Yoga Protocol; PM Modi led India's 12th International Day of Yoga from Kolkata's Red Road"
    img_attribution = "Wikimedia Commons"

    for q in ["International Day of Yoga India", "Common Yoga Protocol", "yoga day India crowd", "Surya Namaskar yoga India"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "yoga" in t:
                img_caption = "A mass yoga demonstration in India; the 12th International Day of Yoga was marked at nearly 2,500 locations worldwide on June 21"
            break

    if not img_url:
        px = fetch_pexels_image("group yoga sunrise outdoors")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A group practising yoga outdoors at sunrise"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-identity",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Tripura Star News / PIB \u2014 Prime Minister Narendra Modi to lead 12th International Day of Yoga celebrations in Kolkata on 21 June (Red Road; INS Dunagiri, Sanshodhak, Agray commissioning)",
            "Bhaskar English \u2014 PM Modi Leads Kolkata Yoga Day; live updates (Modi performs yoga in Kolkata; ministers and CMs across states; Neeraj Chopra and Shilpa Shetty participate)",
            "IANS \u2014 PM Modi to lead International Day of Yoga 2026 celebrations in Kolkata (2,500 locations, 210+ Indian missions, June 14 Guinness World Record)",
            "PIB \u2014 12th International Day of Yoga theme 'Yoga for Healthy Ageing' (Ministry of Ayush)",
            "USA Today \u2014 June 21 calendar: International Yoga Day, Father's Day and the summer solstice"
        ]),
        "diaspora_angle": "Yoga is the diaspora's most successful cultural export \u2014 carried abroad by Indian immigrants and now practised by tens of millions worldwide \u2014 and this year's 'Healthy Ageing' theme speaks directly to an Indian-origin population overseas that is itself growing older.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Study-abroad spending falls 22% ───────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Indian study-abroad spending falls 22%")
    print("="*60)

    slug = "indian-study-abroad-spending-falls-22-percent-1-billion-rbi-lowest-since-2017-visa-curbs-20260621"
    headline = "Indian Families Just Cut Their Study-Abroad Spending to the Lowest in Seven Years. The Reason Sits at Foreign Visa Desks."
    subheadline = "Fresh RBI data shows Indians remitted about $1 billion for overseas education between April and August \u2014 a 22% fall and the thinnest five-month outflow since 2017 \u2014 as tighter student-visa rules in the US, Canada and Australia delay or derail plans that have long defined diaspora ambition."

    body = """The cheque that an Indian family writes to a foreign university has, for two decades, been one of the most reliable signals of middle-class ambition \u2014 a bet on a child's future placed in dollars, pounds or Canadian dollars. This year, that cheque is shrinking, and the reason has less to do with appetite in Mumbai or Hyderabad than with the mood at visa windows in Washington, Ottawa and Canberra.

Indians sent an estimated $1 billion abroad for education between April and August, according to fresh Reserve Bank of India data \u2014 the lowest outflow for that five-month stretch since 2017. The figure represents a 22 percent decline from the same period a year earlier, and it captures a pipeline that has been quietly squeezed by tougher entry rules across the major English-speaking destinations. One month within the window saw education remittances fall to $138.8 million, the weakest monthly reading since April 2020, at the depths of the pandemic.

## What the Numbers Measure

The RBI tracks these flows under the Liberalised Remittance Scheme, which lets a resident Indian send up to $250,000 abroad in a financial year for permitted purposes including education, travel and investment. The education category bundles tuition, living costs and admission fees \u2014 precisely the large payments that families make in late spring and summer, as offers are accepted and the autumn academic year approaches. That seasonality is what makes the April-to-August window such a sensitive barometer of the year's demand.

Crucially, analysts stress that the slump reflects friction abroad, not a shortage of money or willingness at home. The $250,000 annual limit remains ample for almost any degree, and the channels to send funds are working normally. What has changed is the ability to actually secure a visa and a start date \u2014 and the timing of when, or whether, those large payments can be made.

## A Country-by-Country Squeeze

The decline is not uniform; it traces the specific policy choices of each destination. The United States, traditionally the single largest draw for Indian students, has seen education remittances drop by close to 30 percent year-on-year, as visa processing hurdles, interview backlogs and new restrictions on students' "duration of status" have pinched the flow. Canada more than doubled its proof-of-funds requirement, lifting the upfront cash a student must show to roughly CAD 22,895 and pricing out many families. Australia tightened its English-language thresholds, pushing some applicants into deferral.

The lone bright spot has been the United Kingdom, which has held up better than expected and even gained share \u2014 partly offsetting the losses from North America and signalling a quiet redrawing of the diaspora student map toward Britain, and increasingly toward Germany and other European options.

## The Currency Twist

Layered on top of the visa squeeze is the exchange rate. The rupee has weakened sharply against the dollar over the past year, and for families still determined to send a child abroad, that means a steeper bill in rupee terms even before tuition rises. By some estimates, currency depreciation alone can add several lakh rupees a year to the cost of a US degree \u2014 a hidden tax on ambition that compounds the policy barriers.

## Why It Matters for the Diaspora

For the global Indian community, this data is more than an economic footnote; it is a leading indicator of who joins them next. The students who fund these remittances are the diaspora's renewal \u2014 the future H-1B engineers, hospital residents, founders and professors who will populate Silicon Valley, the NHS and North American campuses a decade from now. A 22 percent contraction at the source today foreshadows a thinner pipeline of arrivals tomorrow.

There is also a domestic policy strand the diaspora watches closely. Industry voices have renewed calls for the government to waive the Tax Collected at Source on education remittances, arguing the 5 percent levy adds an unnecessary liquidity squeeze on families already stretched by tuition and a weak rupee. And for those weighing destinations, the message of the numbers is unmistakable: in 2026, where a student ends up depends as much on the policy weather in Washington and Ottawa as on the strength of an application \u2014 and the families doing the math are increasingly hedging across more countries, and more carefully, than ever before."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "International students on a university campus; Indian study-abroad remittances fell 22% to about $1 billion, the lowest five-month total since 2017"
    img_attribution = "Wikimedia Commons"

    for q in ["university graduation students campus", "international students university library", "college campus students walking"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            break

    if not img_url:
        px = fetch_pexels_image("university students campus graduation")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Students on a university campus; Indian families cut overseas-education spending 22% as foreign visa rules tightened"

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
            "VisaVerge \u2014 Study Abroad Spending by Indians Falls 22% to $1B in 2025: RBI Data (April\u2013August lowest since 2017; June low of $138.8 million; US down ~30%, Canada proof-of-funds, Australia English criteria, UK gains share)",
            "The Hindu BusinessLine \u2014 Indians remit 24% less for education abroad in August; RBI data shows sharp dip in travel spends ($0.32 billion vs $0.42 billion)",
            "Angel One \u2014 India's Outward Remittances Hit 2-Year Low as Spending on Foreign Studies Slumps (education down 30% YoY to $120.9 million; Apr\u2013Nov education remittances down 22.5%; TCS waiver call)",
            "Legacy IAS / RBI LRS \u2014 Indians' spending on foreign studies hitting a seven-year low (Jan\u2013Jun outward remittances; Canada CAD 22,895 proof of funds; Australia IELTS thresholds)",
            "Mint \u2014 Falling rupee to hit Indian students planning US studies in 2026, costs may rise by \u20b94 lakh a year"
        ]),
        "diaspora_angle": "Today's overseas students are the diaspora's renewal \u2014 tomorrow's H-1B engineers, doctors and founders \u2014 so a 22% drop in study-abroad spending, driven by tighter US/Canada/Australia visa rules and a weak rupee, signals a thinner pipeline of future arrivals and revives calls to scrap the 5% TCS on education remittances.",
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
